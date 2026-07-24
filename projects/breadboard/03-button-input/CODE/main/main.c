#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#define BUTTON GPIO_NUM_27
void app_main(void) {
    gpio_config_t c = {.pin_bit_mask=1ULL<<BUTTON,.mode=GPIO_MODE_INPUT,
        .pull_up_en=GPIO_PULLUP_ENABLE,.pull_down_en=GPIO_PULLDOWN_DISABLE,.intr_type=GPIO_INTR_DISABLE};
    gpio_config(&c);
    int raw=gpio_get_level(BUTTON), stable=raw, candidate=raw, count=0;
    printf("button raw=%d stable=%d active_low=1\n", raw, stable);
    while (1) {
        raw=gpio_get_level(BUTTON);
        if (raw != candidate) { candidate=raw; count=1; printf("raw=%d\n",raw); }
        else if (count && ++count >= 3) {
            count=0;
            if (stable != candidate) { stable=candidate; printf("debounced=%d\n",stable); }
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
