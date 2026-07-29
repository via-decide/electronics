#include "usb/usb_service.h"

#include <string.h>

struct usb_service {
    usb_service_adapter_t adapter;
    usb_service_state_t state;
    usb_service_result_t last_error;
    bool configuration_active;
    bool cdc_open;
    usb_service_counters_t counters;
};

_Static_assert(
    sizeof(struct usb_service) <= USB_SERVICE_STORAGE_BYTES,
    "USB_SERVICE_STORAGE_BYTES is too small");

static usb_service_result_t record_result(
    usb_service_t *service,
    usb_service_result_t result)
{
    if (service != NULL) {
        service->last_error = result;
        if (result == USB_SERVICE_E_INVALID_TRANSITION) {
            service->counters.invalid_transitions++;
        }
    }
    return result;
}

static void clear_transport_readiness(usb_service_t *service)
{
    service->configuration_active = false;
    service->cdc_open = false;
}

static bool operation_is_mutating(payload_storage_operation_t operation)
{
    return operation == PAYLOAD_STORAGE_PROGRAM_PAGE ||
           operation == PAYLOAD_STORAGE_ERASE_SECTOR ||
           operation == PAYLOAD_STORAGE_ERASE_BLOCK_64K;
}

usb_service_result_t usb_service_init(
    usb_service_storage_t *storage,
    const usb_service_adapter_t *adapter,
    usb_service_t **service)
{
    usb_service_t *instance;

    if (storage == NULL || adapter == NULL || service == NULL ||
        adapter->power_safe == NULL ||
        adapter->configured_current_available == NULL ||
        adapter->submit_storage == NULL) {
        return USB_SERVICE_E_INVALID_ARGUMENT;
    }

    memset(storage, 0, sizeof(*storage));
    instance = (usb_service_t *)(void *)storage->bytes;
    instance->adapter = *adapter;
    instance->state = USB_SERVICE_DETACHED;
    instance->last_error = USB_SERVICE_OK;
    instance->counters.last_storage_result = PAYLOAD_STORAGE_OK;
    *service = instance;
    return USB_SERVICE_OK;
}

usb_service_result_t usb_service_handle_event(
    usb_service_t *service,
    usb_service_event_t event)
{
    if (service == NULL) {
        return USB_SERVICE_E_INVALID_ARGUMENT;
    }
    if (service->state == USB_SERVICE_FAULT_LOCKED) {
        return record_result(service, USB_SERVICE_E_FAULT_LOCKED);
    }

    service->counters.lifecycle_events++;
    switch (event) {
    case USB_SERVICE_EVENT_ATTACH:
        if (service->state != USB_SERVICE_DETACHED) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        clear_transport_readiness(service);
        service->state = USB_SERVICE_ATTACHED_DEFAULT;
        break;
    case USB_SERVICE_EVENT_BUS_RESET:
        if (service->state == USB_SERVICE_DETACHED ||
            service->state == USB_SERVICE_RECOVERY) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        clear_transport_readiness(service);
        service->state = USB_SERVICE_ENUMERATING;
        break;
    case USB_SERVICE_EVENT_CDC_OPEN:
        if (service->state != USB_SERVICE_CONFIGURED ||
            !service->configuration_active) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        service->cdc_open = true;
        service->state = USB_SERVICE_READY;
        break;
    case USB_SERVICE_EVENT_SUSPEND:
        if (service->state != USB_SERVICE_CONFIGURED &&
            service->state != USB_SERVICE_READY) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        service->cdc_open = false;
        service->state = USB_SERVICE_SUSPENDED;
        break;
    case USB_SERVICE_EVENT_RESUME:
        if (service->state != USB_SERVICE_SUSPENDED) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        service->cdc_open = false;
        service->state = USB_SERVICE_CONFIGURED;
        break;
    case USB_SERVICE_EVENT_DETACH:
        if (service->state == USB_SERVICE_DETACHED) {
            return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
        }
        clear_transport_readiness(service);
        service->state = USB_SERVICE_DETACHED;
        break;
    default:
        return record_result(service, USB_SERVICE_E_INVALID_ARGUMENT);
    }

    return record_result(service, USB_SERVICE_OK);
}

usb_service_result_t usb_service_set_configuration(
    usb_service_t *service,
    uint8_t configuration_value)
{
    if (service == NULL) {
        return USB_SERVICE_E_INVALID_ARGUMENT;
    }
    if (service->state == USB_SERVICE_FAULT_LOCKED) {
        return record_result(service, USB_SERVICE_E_FAULT_LOCKED);
    }
    if (configuration_value > USB_SERVICE_CONFIGURATION_VALUE) {
        return record_result(
            service,
            USB_SERVICE_E_UNSUPPORTED_CONFIGURATION);
    }
    if (service->state != USB_SERVICE_ENUMERATING &&
        service->state != USB_SERVICE_CONFIGURED &&
        service->state != USB_SERVICE_READY) {
        return record_result(service, USB_SERVICE_E_INVALID_TRANSITION);
    }

    service->counters.lifecycle_events++;
    service->cdc_open = false;
    if (configuration_value == 0u) {
        service->configuration_active = false;
        service->state = USB_SERVICE_ENUMERATING;
    } else {
        service->configuration_active = true;
        service->state = USB_SERVICE_CONFIGURED;
    }
    return record_result(service, USB_SERVICE_OK);
}

usb_service_result_t usb_service_submit_storage(
    usb_service_t *service,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence)
{
    payload_storage_result_t storage_result;

    if (service == NULL || request == NULL) {
        return USB_SERVICE_E_INVALID_ARGUMENT;
    }
    if (service->state == USB_SERVICE_FAULT_LOCKED) {
        service->counters.storage_requests_rejected++;
        return record_result(service, USB_SERVICE_E_FAULT_LOCKED);
    }
    if (service->state != USB_SERVICE_READY ||
        !service->configuration_active || !service->cdc_open) {
        service->counters.storage_requests_rejected++;
        return record_result(service, USB_SERVICE_E_NOT_READY);
    }
    if (operation_is_mutating(request->operation) &&
        !service->adapter.configured_current_available(
            service->adapter.context)) {
        service->counters.storage_requests_rejected++;
        return record_result(
            service,
            USB_SERVICE_E_CURRENT_NOT_QUALIFIED);
    }
    if (operation_is_mutating(request->operation) &&
        !service->adapter.power_safe(service->adapter.context)) {
        service->counters.storage_requests_rejected++;
        return record_result(service, USB_SERVICE_E_POWER_UNSAFE);
    }

    storage_result = service->adapter.submit_storage(
        service->adapter.context,
        request,
        completion,
        completion_context,
        request_sequence);
    service->counters.last_storage_result = storage_result;
    if (storage_result != PAYLOAD_STORAGE_OK) {
        service->counters.storage_requests_rejected++;
        return record_result(service, USB_SERVICE_E_STORAGE_REJECTED);
    }
    service->counters.storage_requests_forwarded++;
    return record_result(service, USB_SERVICE_OK);
}

usb_service_result_t usb_service_request_recovery(
    usb_service_t *service,
    usb_service_recovery_origin_t origin)
{
    if (service == NULL) {
        return USB_SERVICE_E_INVALID_ARGUMENT;
    }
    if (service->state == USB_SERVICE_FAULT_LOCKED) {
        return record_result(service, USB_SERVICE_E_FAULT_LOCKED);
    }
    if (origin == USB_SERVICE_RECOVERY_REMOTE) {
        service->counters.remote_recovery_rejections++;
        return record_result(
            service,
            USB_SERVICE_E_REMOTE_RECOVERY_FORBIDDEN);
    }
    if (origin != USB_SERVICE_RECOVERY_PHYSICAL_BOOTSEL &&
        origin != USB_SERVICE_RECOVERY_PHYSICAL_RUN &&
        origin != USB_SERVICE_RECOVERY_SWD) {
        return record_result(service, USB_SERVICE_E_INVALID_ARGUMENT);
    }

    clear_transport_readiness(service);
    service->state = USB_SERVICE_RECOVERY;
    service->counters.lifecycle_events++;
    return record_result(service, USB_SERVICE_OK);
}

void usb_service_fault_lock(usb_service_t *service)
{
    if (service != NULL) {
        clear_transport_readiness(service);
        service->state = USB_SERVICE_FAULT_LOCKED;
        service->last_error = USB_SERVICE_E_FAULT_LOCKED;
    }
}

void usb_service_get_health(
    const usb_service_t *service,
    usb_service_health_t *health)
{
    if (service == NULL || health == NULL) {
        return;
    }
    health->state = service->state;
    health->configuration_active = service->configuration_active;
    health->cdc_open = service->cdc_open;
    health->last_error = service->last_error;
    health->counters = service->counters;
}

bool usb_service_endpoint_allowed(uint8_t endpoint_address)
{
    switch (endpoint_address) {
    case 0x00:
    case 0x80:
    case 0x81:
    case 0x02:
    case 0x82:
        return true;
    default:
        return false;
    }
}

const char *usb_service_result_name(usb_service_result_t result)
{
    static const char *const names[] = {
        "OK",
        "E_INVALID_ARGUMENT",
        "E_INVALID_TRANSITION",
        "E_UNSUPPORTED_CONFIGURATION",
        "E_NOT_READY",
        "E_CURRENT_NOT_QUALIFIED",
        "E_POWER_UNSAFE",
        "E_REMOTE_RECOVERY_FORBIDDEN",
        "E_ENDPOINT_NOT_DECLARED",
        "E_STORAGE_REJECTED",
        "E_FAULT_LOCKED",
    };
    if ((unsigned int)result >= sizeof(names) / sizeof(names[0])) {
        return "E_UNKNOWN";
    }
    return names[result];
}

const char *usb_service_state_name(usb_service_state_t state)
{
    static const char *const names[] = {
        "DETACHED",
        "ATTACHED_DEFAULT",
        "ENUMERATING",
        "CONFIGURED",
        "SERVICE_READY",
        "SUSPENDED",
        "RECOVERY",
        "FAULT_LOCKED",
    };
    if ((unsigned int)state >= sizeof(names) / sizeof(names[0])) {
        return "UNKNOWN";
    }
    return names[state];
}
