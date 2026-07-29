#include "usb/usb_service.h"

#include <stdio.h>
#include <string.h>

typedef struct {
    bool power_safe;
    bool current_available;
    payload_storage_result_t storage_result;
    uint64_t storage_calls;
} fake_adapter_t;

static int failures;
static int tests_run;

#define CHECK(condition)                                                        \
    do {                                                                        \
        if (!(condition)) {                                                      \
            fprintf(                                                            \
                stderr,                                                         \
                "%s:%d: check failed: %s\n",                                   \
                __FILE__,                                                       \
                __LINE__,                                                       \
                #condition);                                                    \
            failures++;                                                         \
            return;                                                             \
        }                                                                       \
    } while (0)

static bool fake_power_safe(void *context)
{
    return ((fake_adapter_t *)context)->power_safe;
}

static bool fake_current_available(void *context)
{
    return ((fake_adapter_t *)context)->current_available;
}

static payload_storage_result_t fake_submit_storage(
    void *context,
    const payload_storage_request_t *request,
    payload_storage_completion_fn completion,
    void *completion_context,
    uint64_t *request_sequence)
{
    fake_adapter_t *fake = context;
    (void)request;
    (void)completion;
    (void)completion_context;
    fake->storage_calls++;
    if (request_sequence != NULL) {
        *request_sequence = fake->storage_calls;
    }
    return fake->storage_result;
}

static usb_service_adapter_t make_adapter(fake_adapter_t *fake)
{
    usb_service_adapter_t adapter = {
        .context = fake,
        .power_safe = fake_power_safe,
        .configured_current_available = fake_current_available,
        .submit_storage = fake_submit_storage,
    };
    return adapter;
}

static usb_service_t *make_service(
    usb_service_storage_t *storage,
    fake_adapter_t *fake)
{
    usb_service_t *service = NULL;
    usb_service_adapter_t adapter = make_adapter(fake);
    if (usb_service_init(storage, &adapter, &service) != USB_SERVICE_OK) {
        fprintf(stderr, "%s:%d: USB service init failed\n", __FILE__, __LINE__);
        failures++;
        return NULL;
    }
    return service;
}

static void make_ready(usb_service_t *service)
{
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_ATTACH) ==
        USB_SERVICE_OK);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_BUS_RESET) ==
        USB_SERVICE_OK);
    CHECK(
        usb_service_set_configuration(
            service,
            USB_SERVICE_CONFIGURATION_VALUE) == USB_SERVICE_OK);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_CDC_OPEN) ==
        USB_SERVICE_OK);
}

static payload_storage_request_t read_request(void)
{
    static uint8_t output[16];
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_READ,
        .address = 0u,
        .length = sizeof(output),
        .write_data = NULL,
        .read_data = output,
    };
    return request;
}

static payload_storage_request_t mutation_request(void)
{
    static const uint8_t input[16] = {0};
    payload_storage_request_t request = {
        .operation = PAYLOAD_STORAGE_PROGRAM_PAGE,
        .address = 0u,
        .length = sizeof(input),
        .write_data = input,
        .read_data = NULL,
    };
    return request;
}

static void test_reject_incomplete_adapter(void)
{
    usb_service_storage_t storage;
    usb_service_t *service = NULL;
    usb_service_adapter_t adapter;
    memset(&adapter, 0, sizeof(adapter));
    CHECK(
        usb_service_init(&storage, &adapter, &service) ==
        USB_SERVICE_E_INVALID_ARGUMENT);
}

static void test_reject_configuration_before_attach(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    CHECK(
        usb_service_set_configuration(service, 1u) ==
        USB_SERVICE_E_INVALID_TRANSITION);
}

static void test_reject_unsupported_configuration(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_ATTACH) ==
        USB_SERVICE_OK);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_BUS_RESET) ==
        USB_SERVICE_OK);
    CHECK(
        usb_service_set_configuration(service, 2u) ==
        USB_SERVICE_E_UNSUPPORTED_CONFIGURATION);
}

static void test_reject_storage_before_service_ready(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = read_request();
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_NOT_READY);
    CHECK(fake.storage_calls == 0u);
}

static void test_reject_mutation_without_configured_current(void)
{
    fake_adapter_t fake = {true, false, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = mutation_request();
    make_ready(service);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_CURRENT_NOT_QUALIFIED);
    CHECK(fake.storage_calls == 0u);
}

static void test_reject_mutation_when_power_unsafe(void)
{
    fake_adapter_t fake = {false, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = mutation_request();
    make_ready(service);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_POWER_UNSAFE);
    CHECK(fake.storage_calls == 0u);
}

static void test_reject_storage_while_suspended(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = read_request();
    make_ready(service);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_SUSPEND) ==
        USB_SERVICE_OK);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_NOT_READY);
    CHECK(fake.storage_calls == 0u);
}

static void test_reject_remote_recovery(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    usb_service_health_t health;
    CHECK(
        usb_service_request_recovery(
            service,
            USB_SERVICE_RECOVERY_REMOTE) ==
        USB_SERVICE_E_REMOTE_RECOVERY_FORBIDDEN);
    usb_service_get_health(service, &health);
    CHECK(health.state == USB_SERVICE_DETACHED);
    CHECK(health.counters.remote_recovery_rejections == 1u);
    CHECK(
        usb_service_request_recovery(
            service,
            USB_SERVICE_RECOVERY_PHYSICAL_BOOTSEL) ==
        USB_SERVICE_OK);
    usb_service_get_health(service, &health);
    CHECK(health.state == USB_SERVICE_RECOVERY);
}

static void test_bus_reset_drops_service_ready(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    usb_service_health_t health;
    make_ready(service);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_BUS_RESET) ==
        USB_SERVICE_OK);
    usb_service_get_health(service, &health);
    CHECK(health.state == USB_SERVICE_ENUMERATING);
    CHECK(!health.configuration_active);
    CHECK(!health.cdc_open);
}

static void test_detach_drops_service_ready(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = read_request();
    usb_service_health_t health;
    make_ready(service);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_DETACH) ==
        USB_SERVICE_OK);
    usb_service_get_health(service, &health);
    CHECK(health.state == USB_SERVICE_DETACHED);
    CHECK(!health.configuration_active);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_NOT_READY);
}

static void test_reject_undeclared_endpoint(void)
{
    CHECK(usb_service_endpoint_allowed(0x00u));
    CHECK(usb_service_endpoint_allowed(0x80u));
    CHECK(usb_service_endpoint_allowed(0x81u));
    CHECK(usb_service_endpoint_allowed(0x02u));
    CHECK(usb_service_endpoint_allowed(0x82u));
    CHECK(!usb_service_endpoint_allowed(0x01u));
    CHECK(!usb_service_endpoint_allowed(0x83u));
    CHECK(!usb_service_endpoint_allowed(0x8fu));
}

static void test_propagate_storage_rejection_without_retry(void)
{
    fake_adapter_t fake = {
        true,
        true,
        PAYLOAD_STORAGE_E_SPI_QUEUE_FULL,
        0u,
    };
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = read_request();
    usb_service_health_t health;
    make_ready(service);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_STORAGE_REJECTED);
    CHECK(fake.storage_calls == 1u);
    usb_service_get_health(service, &health);
    CHECK(
        health.counters.last_storage_result ==
        PAYLOAD_STORAGE_E_SPI_QUEUE_FULL);
}

static void test_fault_lock_rejects_traffic(void)
{
    fake_adapter_t fake = {true, true, PAYLOAD_STORAGE_OK, 0u};
    usb_service_storage_t storage;
    usb_service_t *service = make_service(&storage, &fake);
    payload_storage_request_t request = read_request();
    make_ready(service);
    usb_service_fault_lock(service);
    CHECK(
        usb_service_submit_storage(
            service,
            &request,
            NULL,
            NULL,
            NULL) == USB_SERVICE_E_FAULT_LOCKED);
    CHECK(
        usb_service_handle_event(service, USB_SERVICE_EVENT_DETACH) ==
        USB_SERVICE_E_FAULT_LOCKED);
    CHECK(fake.storage_calls == 0u);
}

typedef void (*test_fn)(void);

static void run_test(const char *name, test_fn test)
{
    int failures_before = failures;
    tests_run++;
    test();
    if (failures == failures_before) {
        printf("PASS %s\n", name);
    }
}

int main(void)
{
    run_test("reject incomplete adapter", test_reject_incomplete_adapter);
    run_test(
        "reject configuration before attach",
        test_reject_configuration_before_attach);
    run_test(
        "reject unsupported configuration",
        test_reject_unsupported_configuration);
    run_test(
        "reject storage before service ready",
        test_reject_storage_before_service_ready);
    run_test(
        "reject mutation without configured current",
        test_reject_mutation_without_configured_current);
    run_test(
        "reject mutation when power unsafe",
        test_reject_mutation_when_power_unsafe);
    run_test(
        "reject storage while suspended",
        test_reject_storage_while_suspended);
    run_test("reject remote recovery", test_reject_remote_recovery);
    run_test(
        "bus reset drops service ready",
        test_bus_reset_drops_service_ready);
    run_test(
        "detach drops service ready",
        test_detach_drops_service_ready);
    run_test(
        "reject undeclared endpoint",
        test_reject_undeclared_endpoint);
    run_test(
        "propagate storage rejection without retry",
        test_propagate_storage_rejection_without_retry);
    run_test(
        "fault lock rejects traffic",
        test_fault_lock_rejects_traffic);

    if (failures != 0) {
        fprintf(
            stderr,
            "%d failure(s) across %d USB service host tests\n",
            failures,
            tests_run);
        return 1;
    }
    printf("%d USB service negative host tests passed\n", tests_run);
    return 0;
}
