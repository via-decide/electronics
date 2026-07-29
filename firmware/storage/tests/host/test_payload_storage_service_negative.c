#include "storage/payload_storage_service.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MOCK_MEDIA_BYTES PAYLOAD_STORAGE_BLOCK_BYTES
#define ARRAY_LENGTH(value) (sizeof(value) / sizeof((value)[0]))
#define STATE_BIT(state) (1u << (unsigned)(state))

#define CHECK(condition)                                                        \
    do {                                                                        \
        if (!(condition)) {                                                      \
            fprintf(                                                            \
                stderr,                                                          \
                "%s:%d: check failed: %s\n",                                    \
                __func__,                                                        \
                __LINE__,                                                        \
                #condition);                                                     \
            return 1;                                                           \
        }                                                                       \
    } while (0)

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

typedef struct {
    payload_storage_service_storage_t storage;
    payload_storage_service_t *service;
    uint8_t *media;
    uint64_t now_us;
    bool power_safe;
    bool chip_select_asserted;
    bool frame_aborted;
    uint8_t opcode;
    unsigned frame_phase;
    uint32_t address;
    bool address_seen;
    bool program_data_seen;
    size_t program_length;
    bool write_enable_latch;
    bool fail_write_enable;
    bool force_busy;
    bool busy_forever_after_mutation;
    unsigned busy_polls;
    uint8_t status_2;
    uint8_t status_3;
    uint8_t jedec_id[3];
    bool corrupt_verify;
    uint32_t last_mutation_address;
    size_t last_mutation_length;
    bool mutation_seen;
    uint8_t timeout_opcode;
    bool timeout_once;
    bool timeout_busy_poll;
    uint8_t reset_opcode;
    uint8_t reenter_opcode;
    payload_storage_result_t reenter_result;
    uint8_t cancel_opcode;
    uint64_t cancel_sequence;
    payload_storage_result_t cancel_result;
    bool slow_read;
    uint8_t opcode_log[4096];
    size_t opcode_log_length;
    size_t readback_bytes;
    uint32_t observed_states;
} fixture_t;

static uint32_t decode_address(const uint8_t *bytes)
{
    return ((uint32_t)bytes[0] << 24) | ((uint32_t)bytes[1] << 16) |
           ((uint32_t)bytes[2] << 8) | (uint32_t)bytes[3];
}

static size_t opcode_count(const fixture_t *fixture, uint8_t opcode)
{
    size_t count = 0u;
    size_t index;
    for (index = 0u; index < fixture->opcode_log_length; ++index) {
        if (fixture->opcode_log[index] == opcode) {
            count++;
        }
    }
    return count;
}

static void observe_state(fixture_t *fixture)
{
    payload_storage_health_t health;
    if (fixture->service == NULL) {
        return;
    }
    payload_storage_service_get_health(fixture->service, &health);
    fixture->observed_states |= STATE_BIT(health.state);
}

static void mock_set_chip_select(void *context, bool asserted)
{
    fixture_t *fixture = context;
    if (asserted) {
        fixture->chip_select_asserted = true;
        fixture->frame_aborted = false;
        fixture->opcode = 0u;
        fixture->frame_phase = 0u;
        fixture->address = 0u;
        fixture->address_seen = false;
        fixture->program_data_seen = false;
        fixture->program_length = 0u;
        return;
    }

    if (fixture->chip_select_asserted && !fixture->frame_aborted) {
        if (fixture->opcode == OPCODE_WRITE_ENABLE) {
            fixture->write_enable_latch = !fixture->fail_write_enable;
        } else if (fixture->opcode == OPCODE_WRITE_DISABLE) {
            fixture->write_enable_latch = false;
        } else if (fixture->opcode == OPCODE_PAGE_PROGRAM_4_BYTE &&
                   fixture->address_seen && fixture->program_data_seen &&
                   fixture->write_enable_latch) {
            fixture->busy_polls = 1u;
            fixture->mutation_seen = true;
            fixture->last_mutation_address = fixture->address;
            fixture->last_mutation_length = fixture->program_length;
        } else if (
            fixture->opcode == OPCODE_SECTOR_ERASE_4_BYTE &&
            fixture->address_seen && fixture->write_enable_latch) {
            if (fixture->address < MOCK_MEDIA_BYTES) {
                memset(
                    fixture->media + fixture->address,
                    0xff,
                    PAYLOAD_STORAGE_SECTOR_BYTES);
            }
            fixture->busy_polls = 1u;
            fixture->mutation_seen = true;
            fixture->last_mutation_address = fixture->address;
            fixture->last_mutation_length = PAYLOAD_STORAGE_SECTOR_BYTES;
        } else if (
            fixture->opcode == OPCODE_BLOCK_ERASE_4_BYTE &&
            fixture->address_seen && fixture->write_enable_latch) {
            memset(fixture->media, 0xff, MOCK_MEDIA_BYTES);
            fixture->busy_polls = 1u;
            fixture->mutation_seen = true;
            fixture->last_mutation_address = fixture->address;
            fixture->last_mutation_length = PAYLOAD_STORAGE_BLOCK_BYTES;
        } else if (fixture->opcode == OPCODE_RESET_DEVICE) {
            fixture->write_enable_latch = false;
            fixture->busy_polls = 0u;
            fixture->force_busy = false;
            fixture->status_2 = 0u;
            fixture->status_3 = 0u;
        }
    }
    fixture->chip_select_asserted = false;
}

static uint8_t mock_status_1(fixture_t *fixture)
{
    uint8_t status = 0u;
    if (fixture->force_busy ||
        (fixture->busy_forever_after_mutation && fixture->mutation_seen) ||
        fixture->busy_polls != 0u) {
        status |= 0x01u;
    }
    if (fixture->write_enable_latch) {
        status |= 0x02u;
    }
    if (!fixture->force_busy && !fixture->busy_forever_after_mutation &&
        fixture->busy_polls != 0u) {
        fixture->busy_polls--;
        if (fixture->busy_polls == 0u) {
            fixture->write_enable_latch = false;
        }
    }
    return status;
}

static payload_storage_transport_result_t mock_transfer(
    void *context,
    const uint8_t *tx,
    uint8_t *rx,
    size_t length)
{
    fixture_t *fixture = context;
    size_t index;

    observe_state(fixture);
    if (!fixture->chip_select_asserted || length == 0u) {
        return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
    }

    if (fixture->frame_phase == 0u) {
        if (tx == NULL || length != 1u) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        fixture->opcode = tx[0];
        fixture->frame_phase = 1u;
        if (fixture->opcode_log_length < ARRAY_LENGTH(fixture->opcode_log)) {
            fixture->opcode_log[fixture->opcode_log_length++] = fixture->opcode;
        }
        if (fixture->reenter_opcode == fixture->opcode) {
            bool did_work = false;
            fixture->reenter_opcode = 0u;
            fixture->reenter_result =
                payload_storage_service_run_once(fixture->service, &did_work);
        }
        if (fixture->cancel_opcode == fixture->opcode) {
            fixture->cancel_opcode = 0u;
            fixture->cancel_result = payload_storage_service_cancel(
                fixture->service,
                fixture->cancel_sequence);
        }
        if (fixture->reset_opcode == fixture->opcode) {
            fixture->reset_opcode = 0u;
            payload_storage_service_notify_reset(fixture->service);
            return PAYLOAD_STORAGE_TRANSPORT_OK;
        }
        if (fixture->timeout_opcode == fixture->opcode) {
            if (fixture->timeout_once) {
                fixture->timeout_opcode = 0u;
            }
            fixture->frame_aborted = true;
            return PAYLOAD_STORAGE_TRANSPORT_TIMEOUT;
        }
        if (fixture->timeout_busy_poll &&
            fixture->opcode == OPCODE_READ_STATUS_1 &&
            fixture->mutation_seen) {
            fixture->timeout_busy_poll = false;
            fixture->frame_aborted = true;
            return PAYLOAD_STORAGE_TRANSPORT_TIMEOUT;
        }
        return PAYLOAD_STORAGE_TRANSPORT_OK;
    }

    if ((fixture->opcode == OPCODE_READ_DATA_4_BYTE ||
         fixture->opcode == OPCODE_PAGE_PROGRAM_4_BYTE ||
         fixture->opcode == OPCODE_SECTOR_ERASE_4_BYTE ||
         fixture->opcode == OPCODE_BLOCK_ERASE_4_BYTE) &&
        !fixture->address_seen) {
        if (tx == NULL || length != 4u) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        fixture->address = decode_address(tx);
        fixture->address_seen = true;
        fixture->frame_phase++;
        return PAYLOAD_STORAGE_TRANSPORT_OK;
    }

    switch (fixture->opcode) {
    case OPCODE_READ_JEDEC_ID:
        if (rx == NULL || length != sizeof(fixture->jedec_id)) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        memcpy(rx, fixture->jedec_id, length);
        break;
    case OPCODE_READ_STATUS_1:
        if (rx == NULL || length != 1u) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        rx[0] = mock_status_1(fixture);
        break;
    case OPCODE_READ_STATUS_2:
        if (rx == NULL || length != 1u) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        rx[0] = fixture->status_2;
        break;
    case OPCODE_READ_STATUS_3:
        if (rx == NULL || length != 1u) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        rx[0] = fixture->status_3;
        break;
    case OPCODE_READ_DATA_4_BYTE:
        if (rx == NULL || tx != NULL) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        for (index = 0u; index < length; ++index) {
            uint64_t location = (uint64_t)fixture->address + index;
            uint8_t value =
                location < MOCK_MEDIA_BYTES ? fixture->media[location] : 0xffu;
            if (fixture->corrupt_verify && fixture->mutation_seen &&
                location ==
                    (uint64_t)fixture->last_mutation_address +
                        fixture->last_mutation_length - 1u) {
                value ^= 0x01u;
            }
            rx[index] = value;
        }
        fixture->readback_bytes += length;
        if (fixture->slow_read) {
            fixture->now_us += 6000u;
        }
        break;
    case OPCODE_PAGE_PROGRAM_4_BYTE:
        if (tx == NULL || rx != NULL || !fixture->address_seen ||
            (uint64_t)fixture->address + length > MOCK_MEDIA_BYTES) {
            return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
        }
        if (fixture->write_enable_latch) {
            for (index = 0u; index < length; ++index) {
                fixture->media[fixture->address + index] &= tx[index];
            }
        }
        fixture->program_data_seen = true;
        fixture->program_length = length;
        break;
    default:
        return PAYLOAD_STORAGE_TRANSPORT_IO_ERROR;
    }

    fixture->frame_phase++;
    return PAYLOAD_STORAGE_TRANSPORT_OK;
}

static uint64_t mock_now_us(void *context)
{
    fixture_t *fixture = context;
    return fixture->now_us;
}

static void mock_delay_us(void *context, uint32_t delay_us)
{
    fixture_t *fixture = context;
    fixture->now_us += delay_us;
}

static bool mock_power_safe(void *context)
{
    fixture_t *fixture = context;
    return fixture->power_safe;
}

static int fixture_init(fixture_t *fixture)
{
    payload_storage_transport_t transport;
    memset(fixture, 0, sizeof(*fixture));
    fixture->media = malloc(MOCK_MEDIA_BYTES);
    if (fixture->media == NULL) {
        return 1;
    }
    memset(fixture->media, 0xff, MOCK_MEDIA_BYTES);
    fixture->power_safe = true;
    fixture->jedec_id[0] = 0xefu;
    fixture->jedec_id[1] = 0x40u;
    fixture->jedec_id[2] = 0x19u;
    memset(&transport, 0, sizeof(transport));
    transport.context = fixture;
    transport.transfer = mock_transfer;
    transport.set_chip_select = mock_set_chip_select;
    transport.now_us = mock_now_us;
    transport.delay_us = mock_delay_us;
    transport.power_safe = mock_power_safe;
    if (payload_storage_service_init(
            &fixture->storage,
            &transport,
            &fixture->service) != PAYLOAD_STORAGE_OK) {
        free(fixture->media);
        fixture->media = NULL;
        return 1;
    }
    return 0;
}

static void fixture_destroy(fixture_t *fixture)
{
    free(fixture->media);
    fixture->media = NULL;
}

static payload_storage_result_t submit_and_run(
    fixture_t *fixture,
    const payload_storage_request_t *request,
    uint64_t *sequence)
{
    bool did_work = false;
    payload_storage_result_t result = payload_storage_service_submit(
        fixture->service,
        request,
        NULL,
        NULL,
        sequence);
    if (result != PAYLOAD_STORAGE_OK) {
        return result;
    }
    result = payload_storage_service_run_once(fixture->service, &did_work);
    if (!did_work) {
        return PAYLOAD_STORAGE_E_SPI_NOT_OWNER;
    }
    return result;
}

static payload_storage_result_t probe(fixture_t *fixture)
{
    const payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROBE,
    };
    return submit_and_run(fixture, &request, NULL);
}

static int test_probe_read_and_state_machine(void)
{
    fixture_t fixture;
    uint8_t value = 0u;
    payload_storage_health_t health;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_READ,
        .address = 42u,
        .length = 1u,
        .read_data = &value,
    };
    CHECK(fixture_init(&fixture) == 0);
    CHECK(!fixture.chip_select_asserted);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.media[42] = 0xa5u;
    CHECK(submit_and_run(&fixture, &request, NULL) == PAYLOAD_STORAGE_OK);
    CHECK(value == 0xa5u);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_IDLE);
    CHECK(health.identity_verified);
    CHECK(health.counters.requests_completed == 2u);
    CHECK(health.last_request.operation == PAYLOAD_STORAGE_READ);
    CHECK(
        (fixture.observed_states & STATE_BIT(PAYLOAD_STORAGE_PROBING)) != 0u);
    CHECK(
        (fixture.observed_states & STATE_BIT(PAYLOAD_STORAGE_ACQUIRED)) != 0u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_bounds_alignment_page_cross_and_queue(void)
{
    fixture_t fixture;
    uint8_t data[257] = {0u};
    payload_storage_health_t health;
    payload_storage_request_t request;
    uint64_t sequences[PAYLOAD_STORAGE_QUEUE_DEPTH];
    bool did_work;
    size_t index;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);

    memset(&request, 0, sizeof(request));
    request.operation = PAYLOAD_STORAGE_READ;
    request.address = PAYLOAD_STORAGE_CAPACITY_BYTES - 1u;
    request.length = 2u;
    request.read_data = data;
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_BOUNDS);
    request.address = 0u;
    request.length = (size_t)-1;
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_BOUNDS);

    memset(&request, 0, sizeof(request));
    request.operation = PAYLOAD_STORAGE_PROGRAM_PAGE;
    request.address = 255u;
    request.length = 2u;
    request.write_data = data;
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_PAGE_CROSS);
    request.address = 0u;
    request.length = sizeof(data);
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_BOUNDS);

    memset(&request, 0, sizeof(request));
    request.operation = PAYLOAD_STORAGE_ERASE_SECTOR;
    request.address = 1u;
    request.length = PAYLOAD_STORAGE_SECTOR_BYTES;
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_ALIGNMENT);
    request.operation = PAYLOAD_STORAGE_ERASE_BLOCK_64K;
    request.length = PAYLOAD_STORAGE_BLOCK_BYTES;
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_ALIGNMENT);

    memset(&request, 0, sizeof(request));
    request.operation = PAYLOAD_STORAGE_GET_HEALTH;
    for (index = 0u; index < PAYLOAD_STORAGE_QUEUE_DEPTH; ++index) {
        CHECK(
            payload_storage_service_submit(
                fixture.service,
                &request,
                NULL,
                NULL,
                &sequences[index]) == PAYLOAD_STORAGE_OK);
    }
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_QUEUE_FULL);
    CHECK(
        payload_storage_service_cancel(fixture.service, sequences[3]) ==
        PAYLOAD_STORAGE_OK);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.queued_requests == PAYLOAD_STORAGE_QUEUE_DEPTH - 1u);
    for (index = 0u; index < PAYLOAD_STORAGE_QUEUE_DEPTH - 1u; ++index) {
        did_work = false;
        CHECK(
            payload_storage_service_run_once(fixture.service, &did_work) ==
            PAYLOAD_STORAGE_OK);
        CHECK(did_work);
    }
    fixture_destroy(&fixture);
    return 0;
}

static int test_forbidden_opcode_policy(void)
{
    static const uint8_t forbidden[] = {
        0xc7, 0x60, 0x03, 0x02, 0x20, 0xd8, 0xb7,
        0xe9, 0x01, 0x31, 0x11, 0x32, 0x38,
    };
    static const uint8_t normal_allowed[] = {
        0x06, 0x04, 0x05, 0x35, 0x15,
        0x9f, 0x13, 0x12, 0x21, 0xdc,
    };
    size_t index;
    for (index = 0u; index < ARRAY_LENGTH(forbidden); ++index) {
        CHECK(!payload_storage_service_command_allowed(forbidden[index], false));
        CHECK(!payload_storage_service_command_allowed(forbidden[index], true));
    }
    for (index = 0u; index < ARRAY_LENGTH(normal_allowed); ++index) {
        CHECK(payload_storage_service_command_allowed(normal_allowed[index], false));
    }
    CHECK(!payload_storage_service_command_allowed(OPCODE_ENABLE_RESET, false));
    CHECK(!payload_storage_service_command_allowed(OPCODE_RESET_DEVICE, false));
    CHECK(payload_storage_service_command_allowed(OPCODE_ENABLE_RESET, true));
    CHECK(payload_storage_service_command_allowed(OPCODE_RESET_DEVICE, true));
    return 0;
}

static int test_mutation_preconditions(void)
{
    fixture_t fixture;
    uint8_t data = 0x55u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROGRAM_PAGE,
        .address = 0u,
        .length = 1u,
        .write_data = &data,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.power_safe = false;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 0u);
    fixture.power_safe = true;
    fixture.force_busy = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_BUSY);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 0u);
    fixture.force_busy = false;
    fixture.fail_write_enable = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_WEL);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 0u);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_IDLE);
    fixture_destroy(&fixture);
    return 0;
}

static int test_program_verify_and_fault_lock(void)
{
    fixture_t fixture;
    uint8_t data[PAYLOAD_STORAGE_PAGE_BYTES];
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROGRAM_PAGE,
        .address = 0u,
        .length = sizeof(data),
        .write_data = data,
    };
    payload_storage_health_t health;

    memset(data, 0x5au, sizeof(data));
    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    CHECK(submit_and_run(&fixture, &request, NULL) == PAYLOAD_STORAGE_OK);
    CHECK(memcmp(fixture.media, data, sizeof(data)) == 0);
    CHECK(
        (fixture.observed_states & STATE_BIT(PAYLOAD_STORAGE_WAIT_BUSY)) != 0u);
    CHECK(
        (fixture.observed_states & STATE_BIT(PAYLOAD_STORAGE_VERIFY)) != 0u);
    fixture_destroy(&fixture);

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.corrupt_verify = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_VERIFY);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_FAULT_LOCKED);
    CHECK(health.counters.verification_failures == 1u);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 1u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_full_erase_readback_verification(void)
{
    fixture_t fixture;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_ERASE_BLOCK_64K,
        .address = 0u,
        .length = PAYLOAD_STORAGE_BLOCK_BYTES,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    memset(fixture.media, 0u, MOCK_MEDIA_BYTES);
    fixture.corrupt_verify = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_VERIFY);
    CHECK(fixture.readback_bytes == PAYLOAD_STORAGE_BLOCK_BYTES);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.counters.verification_failures == 1u);
    CHECK(opcode_count(&fixture, OPCODE_BLOCK_ERASE_4_BYTE) == 1u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_timeout_unknown_outcome_never_replays(void)
{
    fixture_t fixture;
    uint8_t data = 0xa5u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROGRAM_PAGE,
        .address = 0u,
        .length = 1u,
        .write_data = &data,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.timeout_opcode = OPCODE_PAGE_PROGRAM_4_BYTE;
    fixture.timeout_once = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_UNKNOWN_OUTCOME);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 1u);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_RECOVER);
    CHECK(health.counters.program_timeouts == 1u);
    CHECK(health.counters.unknown_outcomes == 1u);
    CHECK(payload_storage_service_recover(fixture.service, false) ==
          PAYLOAD_STORAGE_OK);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 1u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_reset_unknown_outcome_never_replays(void)
{
    fixture_t fixture;
    uint8_t data = 0x33u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROGRAM_PAGE,
        .address = 0u,
        .length = 1u,
        .write_data = &data,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.reset_opcode = OPCODE_PAGE_PROGRAM_4_BYTE;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_UNKNOWN_OUTCOME);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.reset_generation == 1u);
    CHECK(health.counters.unknown_outcomes == 1u);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 1u);
    CHECK(payload_storage_service_recover(fixture.service, false) ==
          PAYLOAD_STORAGE_OK);
    CHECK(opcode_count(&fixture, OPCODE_PAGE_PROGRAM_4_BYTE) == 1u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_erase_timeout_never_replays(void)
{
    fixture_t fixture;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_ERASE_SECTOR,
        .address = 0u,
        .length = PAYLOAD_STORAGE_SECTOR_BYTES,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.busy_forever_after_mutation = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_UNKNOWN_OUTCOME);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.counters.erase_timeouts == 1u);
    CHECK(health.counters.unknown_outcomes == 1u);
    CHECK(opcode_count(&fixture, OPCODE_SECTOR_ERASE_4_BYTE) == 1u);
    fixture.busy_forever_after_mutation = false;
    fixture.mutation_seen = false;
    CHECK(payload_storage_service_recover(fixture.service, false) ==
          PAYLOAD_STORAGE_OK);
    CHECK(opcode_count(&fixture, OPCODE_SECTOR_ERASE_4_BYTE) == 1u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_owner_reentrancy_and_active_cancellation(void)
{
    fixture_t fixture;
    uint8_t value = 0u;
    uint64_t sequence = 0u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_READ,
        .address = 0u,
        .length = 1u,
        .read_data = &value,
    };

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, &sequence) ==
        PAYLOAD_STORAGE_OK);
    fixture.reenter_opcode = OPCODE_READ_DATA_4_BYTE;
    fixture.cancel_opcode = OPCODE_READ_DATA_4_BYTE;
    fixture.cancel_sequence = sequence;
    {
        bool did_work = false;
        CHECK(
            payload_storage_service_run_once(fixture.service, &did_work) ==
            PAYLOAD_STORAGE_OK);
        CHECK(did_work);
    }
    CHECK(fixture.reenter_result == PAYLOAD_STORAGE_E_SPI_NOT_OWNER);
    CHECK(fixture.cancel_result == PAYLOAD_STORAGE_E_SPI_BUSY);
    fixture_destroy(&fixture);
    return 0;
}

static int test_reset_is_recovery_only_and_requires_safe_status(void)
{
    fixture_t fixture;
    uint8_t value = 0u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_READ,
        .address = 0u,
        .length = 1u,
        .read_data = &value,
    };

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    CHECK(
        payload_storage_service_recover(fixture.service, true) ==
        PAYLOAD_STORAGE_E_SPI_RESET_UNSAFE);
    CHECK(opcode_count(&fixture, OPCODE_ENABLE_RESET) == 0u);
    CHECK(opcode_count(&fixture, OPCODE_RESET_DEVICE) == 0u);

    fixture.timeout_opcode = OPCODE_READ_DATA_4_BYTE;
    fixture.timeout_once = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_TIMEOUT);
    fixture.force_busy = true;
    CHECK(
        payload_storage_service_recover(fixture.service, true) ==
        PAYLOAD_STORAGE_E_SPI_RESET_UNSAFE);
    CHECK(opcode_count(&fixture, OPCODE_ENABLE_RESET) == 0u);
    CHECK(opcode_count(&fixture, OPCODE_RESET_DEVICE) == 0u);
    fixture_destroy(&fixture);
    return 0;
}

static int test_identity_policy_and_shutdown_fault_lock(void)
{
    fixture_t fixture;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_GET_HEALTH,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    fixture.jedec_id[2] = 0x18u;
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_E_SPI_ID_MISMATCH);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_FAULT_LOCKED);
    CHECK(health.counters.identity_mismatches == 1u);
    fixture_destroy(&fixture);

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    payload_storage_service_shutdown(fixture.service);
    CHECK(!fixture.chip_select_asserted);
    CHECK(
        payload_storage_service_submit(
            fixture.service, &request, NULL, NULL, NULL) ==
        PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED);
    fixture_destroy(&fixture);
    return 0;
}

static int test_slow_read_timeout_and_private_health_surface(void)
{
    fixture_t fixture;
    uint8_t value = 0u;
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_READ,
        .address = 0u,
        .length = 1u,
        .read_data = &value,
    };
    payload_storage_health_t health;

    CHECK(fixture_init(&fixture) == 0);
    CHECK(probe(&fixture) == PAYLOAD_STORAGE_OK);
    fixture.slow_read = true;
    CHECK(
        submit_and_run(&fixture, &request, NULL) ==
        PAYLOAD_STORAGE_E_SPI_TIMEOUT);
    payload_storage_service_get_health(fixture.service, &health);
    CHECK(health.state == PAYLOAD_STORAGE_RECOVER);
    CHECK(health.last_request.address == 0u);
    CHECK(health.last_request.length == 1u);
    CHECK(health.last_request.result == PAYLOAD_STORAGE_E_SPI_TIMEOUT);
    CHECK(
        strcmp(
            payload_storage_result_name(health.last_request.result),
            "E_SPI_TIMEOUT") == 0);
    CHECK(
        strcmp(payload_storage_state_name(health.state), "RECOVER") == 0);
    fixture_destroy(&fixture);
    return 0;
}

typedef int (*test_fn)(void);

typedef struct {
    const char *name;
    test_fn run;
} test_case_t;

int main(void)
{
    static const test_case_t tests[] = {
        {"probe/read/state machine", test_probe_read_and_state_machine},
        {"bounds/alignment/page/queue", test_bounds_alignment_page_cross_and_queue},
        {"forbidden opcode policy", test_forbidden_opcode_policy},
        {"mutation preconditions", test_mutation_preconditions},
        {"program verify/fault lock", test_program_verify_and_fault_lock},
        {"full erase verification", test_full_erase_readback_verification},
        {"timeout unknown/no replay", test_timeout_unknown_outcome_never_replays},
        {"reset unknown/no replay", test_reset_unknown_outcome_never_replays},
        {"erase timeout/no replay", test_erase_timeout_never_replays},
        {"owner/cancellation", test_owner_reentrancy_and_active_cancellation},
        {"safe recovery reset", test_reset_is_recovery_only_and_requires_safe_status},
        {"identity/shutdown", test_identity_policy_and_shutdown_fault_lock},
        {"read timeout/health", test_slow_read_timeout_and_private_health_surface},
    };
    size_t index;

    for (index = 0u; index < ARRAY_LENGTH(tests); ++index) {
        int result = tests[index].run();
        if (result != 0) {
            fprintf(stderr, "FAIL: %s\n", tests[index].name);
            return result;
        }
        printf("PASS: %s\n", tests[index].name);
    }
    printf("PASS: %zu PAYLOAD_STORAGE_SERVICE host tests\n", ARRAY_LENGTH(tests));
    return 0;
}
