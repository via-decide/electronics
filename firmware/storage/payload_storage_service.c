#include "storage/payload_storage_service.h"

#include <string.h>

enum {
    OPCODE_WRITE_ENABLE = 0x06,
    OPCODE_WRITE_DISABLE = 0x04,
    OPCODE_READ_STATUS_1 = 0x05,
    OPCODE_READ_STATUS_2 = 0x35,
    OPCODE_READ_STATUS_3 = 0x15,
    OPCODE_READ_JEDEC_ID = 0x9f,
    OPCODE_READ_DATA_4_BYTE = 0x13,
    OPCODE_PAGE_PROGRAM_4_BYTE = 0x12,
    OPCODE_SECTOR_ERASE_4_BYTE = 0x21,
    OPCODE_BLOCK_ERASE_4_BYTE = 0xdc,
    OPCODE_ENABLE_RESET = 0x66,
    OPCODE_RESET_DEVICE = 0x99
};

enum {
    STATUS_1_BUSY = 1u << 0,
    STATUS_1_WEL = 1u << 1,
    STATUS_2_QE = 1u << 1,
    STATUS_2_SUS = 1u << 7,
    STATUS_3_ADS = 1u << 0,
    READ_TIMEOUT_US = 5000u,
    PAGE_PROGRAM_TIMEOUT_US = 5000u,
    SECTOR_ERASE_TIMEOUT_US = 500000u,
    BLOCK_ERASE_TIMEOUT_US = 2500000u,
    RECOVERY_BUSY_TIMEOUT_US = 2500000u,
    RESET_DELAY_US = 100u,
    STATUS_POLL_INTERVAL_US = 100u,
    POWER_UP_READ_DELAY_US = 20u,
    POWER_UP_MUTATION_DELAY_US = 5000u,
    CHIP_SELECT_HIGH_US = 1u
};

typedef struct {
    payload_storage_request_t request;
    payload_storage_completion_fn completion;
    void *completion_context;
    uint64_t sequence;
    uint8_t program_data[PAYLOAD_STORAGE_PAGE_BYTES];
} queued_request_t;

struct payload_storage_service {
    payload_storage_transport_t transport;
    queued_request_t queue[PAYLOAD_STORAGE_QUEUE_DEPTH];
    size_t queue_count;
    bool request_active;
    bool shutdown;
    bool reset_seen;
    bool mutation_accepted;
    bool active_mutation;
    bool identity_verified;
    uint64_t next_sequence;
    uint64_t boot_time_us;
    uint32_t reset_generation;
    uint32_t verified_generation;
    payload_storage_state_t state;
    payload_storage_result_t last_error;
    payload_storage_counters_t counters;
    payload_storage_request_record_t last_request;
    uint8_t last_status_1;
    uint8_t verify_buffer[PAYLOAD_STORAGE_PAGE_BYTES];
};

_Static_assert(
    sizeof(struct payload_storage_service) <= PAYLOAD_STORAGE_SERVICE_STORAGE_BYTES,
    "PAYLOAD_STORAGE_SERVICE_STORAGE_BYTES is too small");

static bool operation_is_mutating(payload_storage_operation_t operation)
{
    return operation == PAYLOAD_STORAGE_PROGRAM_PAGE ||
           operation == PAYLOAD_STORAGE_ERASE_SECTOR ||
           operation == PAYLOAD_STORAGE_ERASE_BLOCK_64K;
}

static bool range_is_valid(uint32_t address, size_t length, size_t maximum_length)
{
    if (length == 0u || length > maximum_length ||
        length > PAYLOAD_STORAGE_CAPACITY_BYTES) {
        return false;
    }
    return (uint64_t)address <=
           (uint64_t)PAYLOAD_STORAGE_CAPACITY_BYTES - (uint64_t)length;
}

static payload_storage_result_t validate_request(
    const payload_storage_request_t *request)
{
    if (request == NULL) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }

    switch (request->operation) {
    case PAYLOAD_STORAGE_PROBE:
    case PAYLOAD_STORAGE_GET_HEALTH:
        return request->length == 0u && request->write_data == NULL &&
                       request->read_data == NULL
                   ? PAYLOAD_STORAGE_OK
                   : PAYLOAD_STORAGE_E_SPI_BOUNDS;
    case PAYLOAD_STORAGE_READ:
        if (!range_is_valid(
                request->address,
                request->length,
                PAYLOAD_STORAGE_MAX_READ_BYTES) ||
            request->read_data == NULL || request->write_data != NULL) {
            return PAYLOAD_STORAGE_E_SPI_BOUNDS;
        }
        return PAYLOAD_STORAGE_OK;
    case PAYLOAD_STORAGE_PROGRAM_PAGE:
        if (!range_is_valid(
                request->address,
                request->length,
                PAYLOAD_STORAGE_PAGE_BYTES) ||
            request->write_data == NULL || request->read_data != NULL) {
            return PAYLOAD_STORAGE_E_SPI_BOUNDS;
        }
        if ((request->address % PAYLOAD_STORAGE_PAGE_BYTES) + request->length >
            PAYLOAD_STORAGE_PAGE_BYTES) {
            return PAYLOAD_STORAGE_E_SPI_PAGE_CROSS;
        }
        return PAYLOAD_STORAGE_OK;
    case PAYLOAD_STORAGE_ERASE_SECTOR:
        if (request->length != PAYLOAD_STORAGE_SECTOR_BYTES ||
            !range_is_valid(
                request->address,
                request->length,
                PAYLOAD_STORAGE_SECTOR_BYTES)) {
            return PAYLOAD_STORAGE_E_SPI_BOUNDS;
        }
        return request->address % PAYLOAD_STORAGE_SECTOR_BYTES == 0u
                   ? PAYLOAD_STORAGE_OK
                   : PAYLOAD_STORAGE_E_SPI_ALIGNMENT;
    case PAYLOAD_STORAGE_ERASE_BLOCK_64K:
        if (request->length != PAYLOAD_STORAGE_BLOCK_BYTES ||
            !range_is_valid(
                request->address,
                request->length,
                PAYLOAD_STORAGE_BLOCK_BYTES)) {
            return PAYLOAD_STORAGE_E_SPI_BOUNDS;
        }
        return request->address % PAYLOAD_STORAGE_BLOCK_BYTES == 0u
                   ? PAYLOAD_STORAGE_OK
                   : PAYLOAD_STORAGE_E_SPI_ALIGNMENT;
    default:
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }
}

bool payload_storage_service_command_allowed(
    uint8_t opcode,
    bool recovery_context)
{
    switch (opcode) {
    case OPCODE_WRITE_ENABLE:
    case OPCODE_WRITE_DISABLE:
    case OPCODE_READ_STATUS_1:
    case OPCODE_READ_STATUS_2:
    case OPCODE_READ_STATUS_3:
    case OPCODE_READ_JEDEC_ID:
    case OPCODE_READ_DATA_4_BYTE:
    case OPCODE_PAGE_PROGRAM_4_BYTE:
    case OPCODE_SECTOR_ERASE_4_BYTE:
    case OPCODE_BLOCK_ERASE_4_BYTE:
        return true;
    case OPCODE_ENABLE_RESET:
    case OPCODE_RESET_DEVICE:
        return recovery_context;
    default:
        return false;
    }
}

static void wait_until_elapsed(
    payload_storage_service_t *service,
    uint64_t base_us,
    uint64_t required_us)
{
    uint64_t now_us = service->transport.now_us(service->transport.context);
    uint64_t elapsed_us = now_us - base_us;
    if (elapsed_us < required_us) {
        service->transport.delay_us(
            service->transport.context,
            (uint32_t)(required_us - elapsed_us));
    }
}

static payload_storage_transport_result_t transfer_bytes(
    payload_storage_service_t *service,
    const uint8_t *tx,
    uint8_t *rx,
    size_t length)
{
    payload_storage_transport_result_t result =
        service->transport.transfer(service->transport.context, tx, rx, length);
    if (service->reset_seen) {
        return PAYLOAD_STORAGE_TRANSPORT_RESET;
    }
    return result;
}

static payload_storage_transport_result_t send_command(
    payload_storage_service_t *service,
    uint8_t opcode,
    bool has_address,
    uint32_t address,
    const uint8_t *write_data,
    size_t write_length,
    uint8_t *read_data,
    size_t read_length,
    bool recovery_context)
{
    uint8_t address_bytes[4];
    payload_storage_transport_result_t result;

    if (!payload_storage_service_command_allowed(opcode, recovery_context)) {
        return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
    }

    address_bytes[0] = (uint8_t)(address >> 24);
    address_bytes[1] = (uint8_t)(address >> 16);
    address_bytes[2] = (uint8_t)(address >> 8);
    address_bytes[3] = (uint8_t)address;

    service->transport.set_chip_select(service->transport.context, true);
    result = transfer_bytes(service, &opcode, NULL, 1u);
    if (result == PAYLOAD_STORAGE_TRANSPORT_OK && has_address) {
        result = transfer_bytes(service, address_bytes, NULL, sizeof(address_bytes));
    }
    if (result == PAYLOAD_STORAGE_TRANSPORT_OK && write_length != 0u) {
        result = transfer_bytes(service, write_data, NULL, write_length);
    }
    if (result == PAYLOAD_STORAGE_TRANSPORT_OK && read_length != 0u) {
        result = transfer_bytes(service, NULL, read_data, read_length);
    }
    service->transport.set_chip_select(service->transport.context, false);
    service->transport.delay_us(
        service->transport.context,
        CHIP_SELECT_HIGH_US);
    return result;
}

static payload_storage_result_t transport_failure(
    payload_storage_service_t *service,
    payload_storage_transport_result_t transport_result)
{
    if (service->active_mutation && service->mutation_accepted &&
        (transport_result == PAYLOAD_STORAGE_TRANSPORT_TIMEOUT ||
         transport_result == PAYLOAD_STORAGE_TRANSPORT_RESET)) {
        service->counters.unknown_outcomes++;
        service->state = PAYLOAD_STORAGE_RECOVER;
        service->identity_verified = false;
        return PAYLOAD_STORAGE_E_SPI_UNKNOWN_OUTCOME;
    }
    if (transport_result == PAYLOAD_STORAGE_TRANSPORT_TIMEOUT ||
        transport_result == PAYLOAD_STORAGE_TRANSPORT_RESET) {
        service->state = PAYLOAD_STORAGE_RECOVER;
        service->identity_verified = false;
        return PAYLOAD_STORAGE_E_SPI_TIMEOUT;
    }
    service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
    service->identity_verified = false;
    return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
}

static payload_storage_result_t read_status(
    payload_storage_service_t *service,
    uint8_t opcode,
    uint8_t *status)
{
    payload_storage_transport_result_t transport_result = send_command(
        service,
        opcode,
        false,
        0u,
        NULL,
        0u,
        status,
        1u,
        false);
    if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
        return transport_failure(service, transport_result);
    }
    if (opcode == OPCODE_READ_STATUS_1) {
        service->last_status_1 = *status;
    }
    return PAYLOAD_STORAGE_OK;
}

static payload_storage_result_t poll_busy(
    payload_storage_service_t *service,
    uint64_t timeout_us)
{
    uint64_t start_us = service->transport.now_us(service->transport.context);
    uint8_t status = 0u;

    for (;;) {
        payload_storage_result_t result =
            read_status(service, OPCODE_READ_STATUS_1, &status);
        if (result != PAYLOAD_STORAGE_OK) {
            return result;
        }
        if ((status & STATUS_1_BUSY) == 0u) {
            return PAYLOAD_STORAGE_OK;
        }
        if (service->transport.now_us(service->transport.context) - start_us >=
            timeout_us) {
            return transport_failure(
                service,
                PAYLOAD_STORAGE_TRANSPORT_TIMEOUT);
        }
        service->transport.delay_us(
            service->transport.context,
            STATUS_POLL_INTERVAL_US);
    }
}

static payload_storage_result_t execute_probe(
    payload_storage_service_t *service)
{
    static const uint8_t expected_id[3] = {0xef, 0x40, 0x19};
    uint8_t id[3] = {0u};
    uint8_t status_1 = 0u;
    uint8_t status_2 = 0u;
    uint8_t status_3 = 0u;
    payload_storage_transport_result_t transport_result;
    payload_storage_result_t result;

    if (!service->transport.power_safe(service->transport.context)) {
        return PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE;
    }

    service->state = PAYLOAD_STORAGE_PROBING;
    wait_until_elapsed(service, service->boot_time_us, POWER_UP_READ_DELAY_US);
    transport_result = send_command(
        service,
        OPCODE_READ_JEDEC_ID,
        false,
        0u,
        NULL,
        0u,
        id,
        sizeof(id),
        false);
    if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
        return transport_failure(service, transport_result);
    }
    if (memcmp(id, expected_id, sizeof(id)) != 0) {
        service->counters.identity_mismatches++;
        service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
        service->identity_verified = false;
        return PAYLOAD_STORAGE_E_SPI_ID_MISMATCH;
    }

    result = read_status(service, OPCODE_READ_STATUS_1, &status_1);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    if ((status_1 & STATUS_1_BUSY) != 0u) {
        result = poll_busy(service, RECOVERY_BUSY_TIMEOUT_US);
        if (result != PAYLOAD_STORAGE_OK) {
            service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
            return result;
        }
        status_1 = service->last_status_1;
    }
    result = read_status(service, OPCODE_READ_STATUS_2, &status_2);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    result = read_status(service, OPCODE_READ_STATUS_3, &status_3);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    if ((status_2 & (STATUS_2_QE | STATUS_2_SUS)) != 0u ||
        (status_3 & STATUS_3_ADS) != 0u) {
        service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
        service->identity_verified = false;
        return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
    }

    service->identity_verified = true;
    service->verified_generation = service->reset_generation;
    service->state = PAYLOAD_STORAGE_IDLE;
    service->reset_seen = false;
    return PAYLOAD_STORAGE_OK;
}

static payload_storage_result_t execute_read(
    payload_storage_service_t *service,
    uint32_t address,
    uint8_t *data,
    size_t length)
{
    uint64_t start_us = service->transport.now_us(service->transport.context);
    payload_storage_transport_result_t transport_result = send_command(
        service,
        OPCODE_READ_DATA_4_BYTE,
        true,
        address,
        NULL,
        0u,
        data,
        length,
        false);
    if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
        return transport_failure(service, transport_result);
    }
    if (service->transport.now_us(service->transport.context) - start_us >
        READ_TIMEOUT_US) {
        return transport_failure(
            service,
            PAYLOAD_STORAGE_TRANSPORT_TIMEOUT);
    }
    return PAYLOAD_STORAGE_OK;
}

static payload_storage_result_t verify_range(
    payload_storage_service_t *service,
    uint32_t address,
    const uint8_t *expected,
    size_t length,
    bool erased)
{
    size_t offset = 0u;
    while (offset < length) {
        size_t chunk = length - offset;
        size_t index;
        payload_storage_result_t result;
        if (chunk > sizeof(service->verify_buffer)) {
            chunk = sizeof(service->verify_buffer);
        }
        result = execute_read(
            service,
            address + (uint32_t)offset,
            service->verify_buffer,
            chunk);
        if (result != PAYLOAD_STORAGE_OK) {
            return result;
        }
        for (index = 0u; index < chunk; ++index) {
            uint8_t expected_byte = erased ? 0xffu : expected[offset + index];
            if (service->verify_buffer[index] != expected_byte) {
                service->counters.verification_failures++;
                service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
                return PAYLOAD_STORAGE_E_SPI_VERIFY;
            }
        }
        offset += chunk;
    }
    return PAYLOAD_STORAGE_OK;
}

static payload_storage_result_t prepare_mutation(
    payload_storage_service_t *service)
{
    uint8_t status = 0u;
    payload_storage_transport_result_t transport_result;
    payload_storage_result_t result;

    if (!service->transport.power_safe(service->transport.context)) {
        return PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE;
    }
    if (!service->identity_verified ||
        service->verified_generation != service->reset_generation) {
        service->state = PAYLOAD_STORAGE_RECOVER;
        return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
    }
    wait_until_elapsed(
        service,
        service->boot_time_us,
        POWER_UP_MUTATION_DELAY_US);
    result = read_status(service, OPCODE_READ_STATUS_1, &status);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    if ((status & STATUS_1_BUSY) != 0u) {
        return PAYLOAD_STORAGE_E_SPI_BUSY;
    }

    transport_result = send_command(
        service,
        OPCODE_WRITE_ENABLE,
        false,
        0u,
        NULL,
        0u,
        NULL,
        0u,
        false);
    if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
        return transport_failure(service, transport_result);
    }
    result = read_status(service, OPCODE_READ_STATUS_1, &status);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    if ((status & STATUS_1_WEL) == 0u) {
        return PAYLOAD_STORAGE_E_SPI_WEL;
    }
    return PAYLOAD_STORAGE_OK;
}

static payload_storage_result_t execute_mutation(
    payload_storage_service_t *service,
    const queued_request_t *queued)
{
    uint8_t opcode;
    uint64_t timeout_us;
    size_t target_length;
    const uint8_t *write_data = NULL;
    size_t write_length = 0u;
    bool erased = false;
    uint8_t status = 0u;
    payload_storage_transport_result_t transport_result;
    payload_storage_result_t result = prepare_mutation(service);

    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }

    switch (queued->request.operation) {
    case PAYLOAD_STORAGE_PROGRAM_PAGE:
        opcode = OPCODE_PAGE_PROGRAM_4_BYTE;
        timeout_us = PAGE_PROGRAM_TIMEOUT_US;
        target_length = queued->request.length;
        write_data = queued->program_data;
        write_length = queued->request.length;
        break;
    case PAYLOAD_STORAGE_ERASE_SECTOR:
        opcode = OPCODE_SECTOR_ERASE_4_BYTE;
        timeout_us = SECTOR_ERASE_TIMEOUT_US;
        target_length = PAYLOAD_STORAGE_SECTOR_BYTES;
        erased = true;
        break;
    default:
        opcode = OPCODE_BLOCK_ERASE_4_BYTE;
        timeout_us = BLOCK_ERASE_TIMEOUT_US;
        target_length = PAYLOAD_STORAGE_BLOCK_BYTES;
        erased = true;
        break;
    }

    service->mutation_accepted = true;
    transport_result = send_command(
        service,
        opcode,
        true,
        queued->request.address,
        write_data,
        write_length,
        NULL,
        0u,
        false);
    if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
        if (transport_result == PAYLOAD_STORAGE_TRANSPORT_TIMEOUT) {
            if (queued->request.operation == PAYLOAD_STORAGE_PROGRAM_PAGE) {
                service->counters.program_timeouts++;
            } else {
                service->counters.erase_timeouts++;
            }
        }
        return transport_failure(service, transport_result);
    }

    service->state = PAYLOAD_STORAGE_WAIT_BUSY;
    result = poll_busy(service, timeout_us);
    if (result != PAYLOAD_STORAGE_OK) {
        if (queued->request.operation == PAYLOAD_STORAGE_PROGRAM_PAGE) {
            service->counters.program_timeouts++;
        } else {
            service->counters.erase_timeouts++;
        }
        return result;
    }

    service->state = PAYLOAD_STORAGE_VERIFY;
    result = read_status(service, OPCODE_READ_STATUS_1, &status);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    if ((status & STATUS_1_WEL) != 0u) {
        service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
        return PAYLOAD_STORAGE_E_SPI_WEL;
    }
    return verify_range(
        service,
        queued->request.address,
        queued->program_data,
        target_length,
        erased);
}

static payload_storage_result_t execute_request(
    payload_storage_service_t *service,
    const queued_request_t *queued)
{
    payload_storage_result_t result;

    if (queued->request.operation == PAYLOAD_STORAGE_GET_HEALTH) {
        return PAYLOAD_STORAGE_OK;
    }
    if (queued->request.operation == PAYLOAD_STORAGE_PROBE) {
        return execute_probe(service);
    }
    if (!service->identity_verified ||
        service->verified_generation != service->reset_generation) {
        return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
    }

    service->state = PAYLOAD_STORAGE_ACQUIRED;
    if (queued->request.operation == PAYLOAD_STORAGE_READ) {
        result = execute_read(
            service,
            queued->request.address,
            queued->request.read_data,
            queued->request.length);
    } else {
        service->active_mutation = true;
        result = execute_mutation(service, queued);
    }
    if (result == PAYLOAD_STORAGE_OK) {
        service->state = PAYLOAD_STORAGE_IDLE;
    } else if (!service->mutation_accepted &&
               (result == PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE ||
                result == PAYLOAD_STORAGE_E_SPI_BUSY ||
                result == PAYLOAD_STORAGE_E_SPI_WEL)) {
        service->state = PAYLOAD_STORAGE_IDLE;
    }
    return result;
}

payload_storage_result_t payload_storage_service_init(
    payload_storage_service_storage_t *storage,
    const payload_storage_transport_t *transport,
    payload_storage_service_t **service)
{
    payload_storage_service_t *instance;
    if (storage == NULL || transport == NULL || service == NULL ||
        transport->transfer == NULL || transport->set_chip_select == NULL ||
        transport->now_us == NULL || transport->delay_us == NULL ||
        transport->power_safe == NULL) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }

    memset(storage->bytes, 0, sizeof(storage->bytes));
    instance = (payload_storage_service_t *)(void *)storage->bytes;
    instance->transport = *transport;
    instance->state = PAYLOAD_STORAGE_UNINITIALIZED;
    instance->last_error = PAYLOAD_STORAGE_OK;
    instance->next_sequence = 1u;
    instance->boot_time_us = transport->now_us(transport->context);
    transport->set_chip_select(transport->context, false);
    *service = instance;
    return PAYLOAD_STORAGE_OK;
}

payload_storage_result_t payload_storage_service_submit(
    payload_storage_service_t *service,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence)
{
    payload_storage_result_t result;
    queued_request_t *slot;

    if (service == NULL) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }
    result = validate_request(request);
    if (result != PAYLOAD_STORAGE_OK) {
        service->counters.requests_rejected++;
        service->last_error = result;
        return result;
    }
    if (service->shutdown) {
        service->counters.requests_rejected++;
        service->last_error = PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
        return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
    }
    if (request->operation != PAYLOAD_STORAGE_GET_HEALTH) {
        if (service->state == PAYLOAD_STORAGE_FAULT_LOCKED ||
            service->state == PAYLOAD_STORAGE_RECOVER) {
            service->counters.requests_rejected++;
            service->last_error = PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
            return PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED;
        }
        if (request->operation != PAYLOAD_STORAGE_PROBE &&
            service->state != PAYLOAD_STORAGE_IDLE) {
            service->counters.requests_rejected++;
            service->last_error = PAYLOAD_STORAGE_E_SPI_BUSY;
            return PAYLOAD_STORAGE_E_SPI_BUSY;
        }
    }
    if (service->queue_count == PAYLOAD_STORAGE_QUEUE_DEPTH) {
        service->counters.requests_rejected++;
        service->last_error = PAYLOAD_STORAGE_E_SPI_QUEUE_FULL;
        return PAYLOAD_STORAGE_E_SPI_QUEUE_FULL;
    }

    slot = &service->queue[service->queue_count++];
    memset(slot, 0, sizeof(*slot));
    slot->request = *request;
    slot->completion = completion;
    slot->completion_context = completion_context;
    slot->sequence = service->next_sequence++;
    if (slot->sequence == 0u) {
        slot->sequence = service->next_sequence++;
    }
    if (request->operation == PAYLOAD_STORAGE_PROGRAM_PAGE) {
        memcpy(slot->program_data, request->write_data, request->length);
        slot->request.write_data = slot->program_data;
    }
    if (request_sequence != NULL) {
        *request_sequence = slot->sequence;
    }
    return PAYLOAD_STORAGE_OK;
}

payload_storage_result_t payload_storage_service_cancel(
    payload_storage_service_t *service,
    uint64_t request_sequence)
{
    size_t index;
    if (service == NULL || request_sequence == 0u) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }
    if (service->request_active &&
        service->last_request.request_sequence == request_sequence) {
        return PAYLOAD_STORAGE_E_SPI_BUSY;
    }
    for (index = 0u; index < service->queue_count; ++index) {
        if (service->queue[index].sequence == request_sequence) {
            if (index + 1u < service->queue_count) {
                memmove(
                    &service->queue[index],
                    &service->queue[index + 1u],
                    (service->queue_count - index - 1u) *
                        sizeof(service->queue[0]));
            }
            service->queue_count--;
            memset(
                &service->queue[service->queue_count],
                0,
                sizeof(service->queue[0]));
            return PAYLOAD_STORAGE_OK;
        }
    }
    return PAYLOAD_STORAGE_E_SPI_BOUNDS;
}

payload_storage_result_t payload_storage_service_run_once(
    payload_storage_service_t *service,
    bool *did_work)
{
    queued_request_t queued;
    payload_storage_result_t result;

    if (service == NULL || did_work == NULL) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }
    *did_work = false;
    if (service->request_active) {
        return PAYLOAD_STORAGE_E_SPI_NOT_OWNER;
    }
    if (service->queue_count == 0u) {
        return PAYLOAD_STORAGE_OK;
    }

    queued = service->queue[0];
    if (service->queue_count > 1u) {
        memmove(
            &service->queue[0],
            &service->queue[1],
            (service->queue_count - 1u) * sizeof(service->queue[0]));
    }
    service->queue_count--;
    memset(
        &service->queue[service->queue_count],
        0,
        sizeof(service->queue[0]));

    service->request_active = true;
    service->reset_seen = false;
    service->mutation_accepted = false;
    service->active_mutation = operation_is_mutating(queued.request.operation);
    memset(&service->last_request, 0, sizeof(service->last_request));
    service->last_request.request_sequence = queued.sequence;
    service->last_request.operation = queued.request.operation;
    service->last_request.address = queued.request.address;
    service->last_request.length = queued.request.length;
    service->last_request.start_us =
        service->transport.now_us(service->transport.context);
    service->last_request.status_before = service->last_status_1;

    result = execute_request(service, &queued);
    service->last_request.end_us =
        service->transport.now_us(service->transport.context);
    service->last_request.status_after = service->last_status_1;
    service->last_request.result = result;
    service->last_request.reset_generation = service->reset_generation;
    service->last_error = result;
    service->counters.requests_completed++;
    service->request_active = false;
    service->active_mutation = false;
    service->mutation_accepted = false;
    *did_work = true;

    if (queued.completion != NULL) {
        queued.completion(queued.completion_context, queued.sequence, result);
    }
    return result;
}

payload_storage_result_t payload_storage_service_recover(
    payload_storage_service_t *service,
    bool issue_software_reset)
{
    uint8_t status_1 = 0u;
    uint8_t status_2 = 0u;
    payload_storage_result_t result;
    payload_storage_transport_result_t transport_result;

    if (service == NULL) {
        return PAYLOAD_STORAGE_E_SPI_BOUNDS;
    }
    if (service->request_active) {
        return PAYLOAD_STORAGE_E_SPI_NOT_OWNER;
    }
    if (service->state != PAYLOAD_STORAGE_RECOVER &&
        service->state != PAYLOAD_STORAGE_FAULT_LOCKED) {
        return PAYLOAD_STORAGE_E_SPI_RESET_UNSAFE;
    }
    if (!service->transport.power_safe(service->transport.context)) {
        return PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE;
    }

    service->request_active = true;
    service->reset_seen = false;
    result = read_status(service, OPCODE_READ_STATUS_1, &status_1);
    if (result == PAYLOAD_STORAGE_OK) {
        result = read_status(service, OPCODE_READ_STATUS_2, &status_2);
    }
    if (result != PAYLOAD_STORAGE_OK) {
        service->request_active = false;
        service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
        return result;
    }
    if (issue_software_reset &&
        ((status_1 & STATUS_1_BUSY) != 0u ||
         (status_2 & STATUS_2_SUS) != 0u)) {
        service->request_active = false;
        service->state = PAYLOAD_STORAGE_FAULT_LOCKED;
        return PAYLOAD_STORAGE_E_SPI_RESET_UNSAFE;
    }

    if (issue_software_reset) {
        transport_result = send_command(
            service,
            OPCODE_ENABLE_RESET,
            false,
            0u,
            NULL,
            0u,
            NULL,
            0u,
            true);
        if (transport_result == PAYLOAD_STORAGE_TRANSPORT_OK) {
            transport_result = send_command(
                service,
                OPCODE_RESET_DEVICE,
                false,
                0u,
                NULL,
                0u,
                NULL,
                0u,
                true);
        }
        if (transport_result != PAYLOAD_STORAGE_TRANSPORT_OK) {
            service->request_active = false;
            return transport_failure(service, transport_result);
        }
        service->transport.delay_us(
            service->transport.context,
            RESET_DELAY_US);
        service->reset_generation++;
        service->boot_time_us =
            service->transport.now_us(service->transport.context);
    }

    service->state = PAYLOAD_STORAGE_UNINITIALIZED;
    service->identity_verified = false;
    result = execute_probe(service);
    service->request_active = false;
    if (result == PAYLOAD_STORAGE_OK) {
        service->counters.recoveries++;
        service->last_error = PAYLOAD_STORAGE_OK;
    }
    return result;
}

void payload_storage_service_notify_reset(payload_storage_service_t *service)
{
    if (service == NULL) {
        return;
    }
    service->reset_generation++;
    service->boot_time_us =
        service->transport.now_us(service->transport.context);
    service->identity_verified = false;
    service->reset_seen = true;
    service->state = PAYLOAD_STORAGE_RECOVER;
    service->transport.set_chip_select(service->transport.context, false);
}

void payload_storage_service_shutdown(payload_storage_service_t *service)
{
    if (service == NULL) {
        return;
    }
    service->shutdown = true;
    service->transport.set_chip_select(service->transport.context, false);
}

void payload_storage_service_get_health(
    const payload_storage_service_t *service,
    payload_storage_health_t *health)
{
    if (service == NULL || health == NULL) {
        return;
    }
    memset(health, 0, sizeof(*health));
    health->state = service->state;
    health->queued_requests = service->queue_count;
    health->request_active = service->request_active;
    health->identity_verified = service->identity_verified;
    health->reset_generation = service->reset_generation;
    health->last_error = service->last_error;
    health->counters = service->counters;
    health->last_request = service->last_request;
}

const char *payload_storage_result_name(payload_storage_result_t result)
{
    static const char *const names[] = {
        "OK",
        "E_SPI_NOT_OWNER",
        "E_SPI_QUEUE_FULL",
        "E_SPI_POWER_UNSAFE",
        "E_SPI_ID_MISMATCH",
        "E_SPI_BUSY",
        "E_SPI_BOUNDS",
        "E_SPI_ALIGNMENT",
        "E_SPI_PAGE_CROSS",
        "E_SPI_WEL",
        "E_SPI_TIMEOUT",
        "E_SPI_VERIFY",
        "E_SPI_RESET_UNSAFE",
        "E_SPI_UNKNOWN_OUTCOME",
        "E_SPI_FAULT_LOCKED",
    };
    size_t index = (size_t)result;
    return index < sizeof(names) / sizeof(names[0]) ? names[index] : "E_SPI_INVALID";
}

const char *payload_storage_state_name(payload_storage_state_t state)
{
    static const char *const names[] = {
        "UNINITIALIZED",
        "PROBING",
        "IDLE",
        "ACQUIRED",
        "WAIT_BUSY",
        "VERIFY",
        "RECOVER",
        "FAULT_LOCKED",
    };
    size_t index = (size_t)state;
    return index < sizeof(names) / sizeof(names[0]) ? names[index] : "INVALID";
}
