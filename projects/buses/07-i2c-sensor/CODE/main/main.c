#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stdint.h>
#include "driver/i2c_master.h"
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#define SDA GPIO_NUM_21
#define SCL GPIO_NUM_22
static esp_err_t read16(i2c_master_dev_handle_t d,uint8_t reg,uint16_t *out){
    uint8_t b[2]={0}; esp_err_t e=i2c_master_transmit_receive(d,&reg,1,b,2,100);
    *out=((uint16_t)b[0]<<8)|b[1]; return e;
}
static void recover(void){
    gpio_config_t c={.pin_bit_mask=(1ULL<<SDA)|(1ULL<<SCL),.mode=GPIO_MODE_INPUT_OUTPUT_OD,
        .pull_up_en=GPIO_PULLUP_ENABLE}; gpio_config(&c); gpio_set_level(SDA,1);
    for(int i=0;i<9;i++){gpio_set_level(SCL,0);esp_rom_delay_us(5);gpio_set_level(SCL,1);esp_rom_delay_us(5);}
    gpio_set_level(SDA,0);gpio_set_level(SCL,1);esp_rom_delay_us(5);gpio_set_level(SDA,1);
}
void app_main(void){
    recover();
    i2c_master_bus_handle_t bus; i2c_master_dev_handle_t dev;
    i2c_master_bus_config_t bc={.i2c_port=I2C_NUM_0,.sda_io_num=SDA,.scl_io_num=SCL,
        .clk_source=I2C_CLK_SRC_DEFAULT,.glitch_ignore_cnt=7,.flags.enable_internal_pullup=false};
    ESP_ERROR_CHECK(i2c_new_master_bus(&bc,&bus));
    for(int a=8;a<0x78;a++)if(i2c_master_probe(bus,a,20)==ESP_OK)printf("i2c_ack=0x%02x\n",a);
    i2c_device_config_t dc={.dev_addr_length=I2C_ADDR_BIT_LEN_7,.device_address=0x48,.scl_speed_hz=100000};
    ESP_ERROR_CHECK(i2c_master_bus_add_device(bus,&dc,&dev));
    uint16_t id=0,temp=0;
    esp_err_t e1=read16(dev,0x0F,&id),e2=read16(dev,0x00,&temp);
    printf("tmp117 id=0x%04x id_status=%s\n",id,(e1==ESP_OK&&id==0x0117)?"VALID":"REJECT");
    if(e2==ESP_OK)printf("raw_temp=0x%04x temp_c_x1000=%ld\n",temp,(long)((int16_t)temp*78125/10000));
    else printf("temperature_read=NACK value=UNKNOWN\n");
}
