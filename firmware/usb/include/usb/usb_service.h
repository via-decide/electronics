#ifndef USB_SERVICE_H
#define USB_SERVICE_H

#include "storage/payload_storage_service.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define USB_SERVICE_STORAGE_BYTES 512u
#define USB_SERVICE_CONFIGURATION_VALUE 1u
#define USB_SERVICE_CONFIGURATION_MAX_POWER_MA 300u
#define USB_SERVICE_PRECONFIGURATION_TARGET_MA 100u

typedef enum {
    USB_SERVICE_DETACHED = 0,
    USB_SERVICE_ATTACHED_DEFAULT,
    USB_SERVICE_ENUMERATING,
    USB_SERVICE_CONFIGURED,
    USB_SERVICE_READY,
    USB_SERVICE_SUSPENDED,
    USB_SERVICE_RECOVERY,
    USB_SERVICE_FAULT_LOCKED
} usb_service_state_t;

typedef enum {
    USB_SERVICE_EVENT_ATTACH = 0,
    USB_SERVICE_EVENT_BUS_RESET,
    USB_SERVICE_EVENT_CDC_OPEN,
    USB_SERVICE_EVENT_SUSPEND,
    USB_SERVICE_EVENT_RESUME,
    USB_SERVICE_EVENT_DETACH
} usb_service_event_t;

typedef enum {
    USB_SERVICE_RECOVERY_REMOTE = 0,
    USB_SERVICE_RECOVERY_PHYSICAL_BOOTSEL,
    USB_SERVICE_RECOVERY_PHYSICAL_RUN,
    USB_SERVICE_RECOVERY_SWD
} usb_service_recovery_origin_t;

typedef enum {
    USB_SERVICE_OK = 0,
    USB_SERVICE_E_INVALID_ARGUMENT,
    USB_SERVICE_E_INVALID_TRANSITION,
    USB_SERVICE_E_UNSUPPORTED_CONFIGURATION,
    USB_SERVICE_E_NOT_READY,
    USB_SERVICE_E_CURRENT_NOT_QUALIFIED,
    USB_SERVICE_E_POWER_UNSAFE,
    USB_SERVICE_E_REMOTE_RECOVERY_FORBIDDEN,
    USB_SERVICE_E_ENDPOINT_NOT_DECLARED,
    USB_SERVICE_E_STORAGE_REJECTED,
    USB_SERVICE_E_FAULT_LOCKED
} usb_service_result_t;

typedef payload_storage_result_t (*usb_service_storage_submit_fn)(
    void *context,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence);

typedef struct {
    void *context;
    bool (*power_safe)(void *context);
    bool (*configured_current_available)(void *context);
    usb_service_storage_submit_fn submit_storage;
} usb_service_adapter_t;

typedef struct {
    uint64_t lifecycle_events;
    uint64_t invalid_transitions;
    uint64_t storage_requests_forwarded;
    uint64_t storage_requests_rejected;
    uint64_t remote_recovery_rejections;
    uint64_t endpoint_rejections;
    payload_storage_result_t last_storage_result;
} usb_service_counters_t;

typedef struct {
    usb_service_state_t state;
    bool configuration_active;
    bool cdc_open;
    usb_service_result_t last_error;
    usb_service_counters_t counters;
} usb_service_health_t;

typedef union {
    max_align_t alignment;
    uint8_t bytes[USB_SERVICE_STORAGE_BYTES];
} usb_service_storage_t;

typedef struct usb_service usb_service_t;

usb_service_result_t usb_service_init(
    usb_service_storage_t *storage,
    const usb_service_adapter_t *adapter,
    usb_service_t **service);

usb_service_result_t usb_service_handle_event(
    usb_service_t *service,
    usb_service_event_t event);

usb_service_result_t usb_service_set_configuration(
    usb_service_t *service,
    uint8_t configuration_value);

usb_service_result_t usb_service_submit_storage(
    usb_service_t *service,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence);

usb_service_result_t usb_service_request_recovery(
    usb_service_t *service,
    usb_service_recovery_origin_t origin);

void usb_service_fault_lock(usb_service_t *service);
void usb_service_get_health(
    const usb_service_t *service,
    usb_service_health_t *health);

bool usb_service_endpoint_allowed(uint8_t endpoint_address);
const char *usb_service_result_name(usb_service_result_t result);
const char *usb_service_state_name(usb_service_state_t state);

#ifdef __cplusplus
}
#endif

#endif
