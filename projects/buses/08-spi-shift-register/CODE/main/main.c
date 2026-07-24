#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stdint.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#define LATCH GPIO_NUM_32
#define SHIFT_LSB_FIRST 0
static uint8_t reverse8(uint8_t x){x=(x&0xF0)>>4|(x&0x0F)<<4;x=(x&0xCC)>>2|(x&0x33)<<2;return (x&0xAA)>>1|(x&0x55)<<1;}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=-1,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=1};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=-1,.queue_size=1};
    spi_device_handle_t dev; ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_DISABLED));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev)); gpio_set_direction(LATCH,GPIO_MODE_OUTPUT);
    while(1)for(int i=0;i<8;i++){
        uint8_t v=1u<<i,tx=SHIFT_LSB_FIRST?reverse8(v):v;
        spi_transaction_t t={.length=8,.tx_buffer=&tx}; gpio_set_level(LATCH,0);
        ESP_ERROR_CHECK(spi_device_polling_transmit(dev,&t)); gpio_set_level(LATCH,1);
        printf("shifted=0x%02x visible=0x%02x lsb_first=%d\n",tx,v,SHIFT_LSB_FIRST);
        vTaskDelay(pdMS_TO_TICKS(350));
    }
}
