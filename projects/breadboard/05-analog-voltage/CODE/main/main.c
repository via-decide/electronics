#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
void app_main(void) {
    adc_oneshot_unit_handle_t unit;
    adc_oneshot_unit_init_cfg_t u={.unit_id=ADC_UNIT_1};
    adc_oneshot_new_unit(&u,&unit);
    adc_oneshot_chan_cfg_t c={.atten=ADC_ATTEN_DB_11,.bitwidth=ADC_BITWIDTH_12};
    adc_oneshot_config_channel(unit,ADC_CHANNEL_6,&c);
    adc_cali_handle_t cal=NULL;
    adc_cali_line_fitting_config_t lc={.unit_id=ADC_UNIT_1,.atten=ADC_ATTEN_DB_11,
        .bitwidth=ADC_BITWIDTH_12,.default_vref=0};
    bool calibrated=(adc_cali_create_scheme_line_fitting(&lc,&cal)==ESP_OK);
    while (1) {
        int sum=0, raw=0, mv=-1;
        for(int i=0;i<64;i++){ adc_oneshot_read(unit,ADC_CHANNEL_6,&raw); sum+=raw; }
        raw=sum/64;
        if(calibrated) adc_cali_raw_to_voltage(cal,raw,&mv);
        printf("adc_raw_mean=%d calibrated_mv=%d calibrated=%d dmm_mv=RECORD\n",raw,mv,calibrated);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
