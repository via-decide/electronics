#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#define GATE GPIO_NUM_25
void app_main(void) {
    gpio_config_t c={.pin_bit_mask=1ULL<<GATE,.mode=GPIO_MODE_OUTPUT};
    gpio_config(&c); gpio_set_level(GATE,0);
    while (1) {
        gpio_set_level(GATE,1); printf("gate_command=ON expected_vgs_near_3v3 measure=required\n");
        vTaskDelay(pdMS_TO_TICKS(1500));
        gpio_set_level(GATE,0); printf("gate_command=OFF expected_vgs_near_0 measure=required\n");
        vTaskDelay(pdMS_TO_TICKS(1500));
    }
}
