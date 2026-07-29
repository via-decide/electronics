#ifndef PAYLOAD_STORAGE_SERVICE_H
#define PAYLOAD_STORAGE_SERVICE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PAYLOAD_STORAGE_QUEUE_DEPTH 8u
#define PAYLOAD_STORAGE_CAPACITY_BYTES 33554432u
#define PAYLOAD_STORAGE_MAX_READ_BYTES 4096u
#define PAYLOAD_STORAGE_PAGE_BYTES 256u
#define PAYLOAD_STORAGE_SECTOR_BYTES 4096u
#define PAYLOAD_STORAGE_BLOCK_BYTES 65536u
#define PAYLOAD_STORAGE_SERVICE_STORAGE_BYTES 4096u

typedef enum {
    PAYLOAD_STORAGE_UNINITIALIZED = 0,
    PAYLOAD_STORAGE_PROBING,
    PAYLOAD_STORAGE_IDLE,
    PAYLOAD_STORAGE_ACQUIRED,
    PAYLOAD_STORAGE_WAIT_BUSY,
    PAYLOAD_STORAGE_VERIFY,
    PAYLOAD_STORAGE_RECOVER,
    PAYLOAD_STORAGE_FAULT_LOCKED
} payload_storage_state_t;

typedef enum {
    PAYLOAD_STORAGE_PROBE = 0,
    PAYLOAD_STORAGE_READ,
    PAYLOAD_STORAGE_PROGRAM_PAGE,
    PAYLOAD_STORAGE_ERASE_SECTOR,
    PAYLOAD_STORAGE_ERASE_BLOCK_64K,
    PAYLOAD_STORAGE_GET_HEALTH
} payload_storage_operation_t;

typedef enum {
    PAYLOAD_STORAGE_OK = 0,
    PAYLOAD_STORAGE_E_SPI_NOT_OWNER,
    PAYLOAD_STORAGE_E_SPI_QUEUE_FULL,
    PAYLOAD_STORAGE_E_SPI_POWER_UNSAFE,
    PAYLOAD_STORAGE_E_SPI_ID_MISMATCH,
    PAYLOAD_STORAGE_E_SPI_BUSY,
    PAYLOAD_STORAGE_E_SPI_BOUNDS,
    PAYLOAD_STORAGE_E_SPI_ALIGNMENT,
    PAYLOAD_STORAGE_E_SPI_PAGE_CROSS,
    PAYLOAD_STORAGE_E_SPI_WEL,
    PAYLOAD_STORAGE_E_SPI_TIMEOUT,
    PAYLOAD_STORAGE_E_SPI_VERIFY,
    PAYLOAD_STORAGE_E_SPI_RESET_UNSAFE,
    PAYLOAD_STORAGE_E_SPI_UNKNOWN_OUTCOME,
    PAYLOAD_STORAGE_E_SPI_FAULT_LOCKED
} payload_storage_result_t;

typedef enum {
    PAYLOAD_STORAGE_TRANSPORT_OK = 0,
    PAYLOAD_STORAGE_TRANSPORT_TIMEOUT,
    PAYLOAD_STORAGE_TRANSPORT_RESET,
    PAYLOAD_STORAGE_TRANSPORT_IO_ERROR
} payload_storage_transport_result_t;

/*
 * The platform adapter must implement one polled, blocking SPI0 transfer and
 * manual GPIO17 chip-select. A NULL tx pointer means transmit 0xff while
 * receiving. PAYLOAD_STORAGE_SERVICE is the sole caller of these callbacks.
 */
typedef struct {
    void *context;
    payload_storage_transport_result_t (*transfer)(
        void *context,
        const uint8_t *tx,
        uint8_t *rx,
        size_t length);
    void (*set_chip_select)(void *context, bool asserted);
    uint64_t (*now_us)(void *context);
    void (*delay_us)(void *context, uint32_t delay_us);
    bool (*power_safe)(void *context);
} payload_storage_transport_t;

typedef struct {
    payload_storage_operation_t operation;
    uint32_t address;
    size_t length;
    const uint8_t *write_data;
    uint8_t *read_data;
} payload_storage_request_t;

typedef struct {
    uint64_t request_sequence;
    payload_storage_operation_t operation;
    uint32_t address;
    size_t length;
    uint64_t start_us;
    uint64_t end_us;
    uint8_t status_before;
    uint8_t status_after;
    payload_storage_result_t result;
    uint32_t reset_generation;
} payload_storage_request_record_t;

typedef struct {
    uint64_t requests_completed;
    uint64_t requests_rejected;
    uint64_t program_timeouts;
    uint64_t erase_timeouts;
    uint64_t verification_failures;
    uint64_t recoveries;
    uint64_t unknown_outcomes;
    uint64_t identity_mismatches;
} payload_storage_counters_t;

typedef struct {
    payload_storage_state_t state;
    size_t queued_requests;
    bool request_active;
    bool identity_verified;
    uint32_t reset_generation;
    payload_storage_result_t last_error;
    payload_storage_counters_t counters;
    payload_storage_request_record_t last_request;
} payload_storage_health_t;

typedef void (*payload_storage_completion_fn)(
    void *context,
    uint64_t request_sequence,
    payload_storage_result_t result);

typedef union {
    max_align_t alignment;
    uint8_t bytes[PAYLOAD_STORAGE_SERVICE_STORAGE_BYTES];
} payload_storage_service_storage_t;

typedef struct payload_storage_service payload_storage_service_t;

payload_storage_result_t payload_storage_service_init(
    payload_storage_service_storage_t *storage,
    const payload_storage_transport_t *transport,
    payload_storage_service_t **service);

payload_storage_result_t payload_storage_service_submit(
    payload_storage_service_t *service,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence);

payload_storage_result_t payload_storage_service_cancel(
    payload_storage_service_t *service,
    uint64_t request_sequence);

payload_storage_result_t payload_storage_service_run_once(
    payload_storage_service_t *service,
    bool *did_work);

payload_storage_result_t payload_storage_service_recover(
    payload_storage_service_t *service,
    bool issue_software_reset);

void payload_storage_service_notify_reset(payload_storage_service_t *service);
void payload_storage_service_shutdown(payload_storage_service_t *service);
void payload_storage_service_get_health(
    const payload_storage_service_t *service,
    payload_storage_health_t *health);

bool payload_storage_service_command_allowed(uint8_t opcode, bool recovery_context);
const char *payload_storage_result_name(payload_storage_result_t result);
const char *payload_storage_state_name(payload_storage_state_t state);

#ifdef __cplusplus
}
#endif

#endif
