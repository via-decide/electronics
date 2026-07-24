#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stdint.h>
#include <string.h>
#include "driver/spi_master.h"
#define CS GPIO_NUM_32
static spi_device_handle_t dev;
static esp_err_t xfer(const void *tx,void *rx,size_t n){spi_transaction_t t={.length=n*8,.tx_buffer=tx,.rx_buffer=rx};return spi_device_polling_transmit(dev,&t);}
static uint8_t status(void){uint8_t tx[2]={0x05,0},rx[2]={0};xfer(tx,rx,2);return rx[1];}
static void wren(void){uint8_t c=0x06;xfer(&c,NULL,1);}
static void wrdi(void){uint8_t c=0x04;xfer(&c,NULL,1);}
static bool wait_ready(void){for(int i=0;i<100;i++){if(!(status()&1))return true;vTaskDelay(pdMS_TO_TICKS(1));}return false;}
static uint32_t crc32(const uint8_t*p,size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&1?(c>>1)^0xEDB88320:c>>1;}return~c;}
static esp_err_t write_page(uint16_t a,const uint8_t*p,size_t n){
    if(!n||n>64||((a&63)+n)>64||(uint32_t)a+n>32768)return ESP_ERR_INVALID_ARG;
    uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wren();esp_err_t e=xfer(tx,NULL,n+3);
    return e==ESP_OK&&wait_ready()?ESP_OK:ESP_ERR_TIMEOUT;
}
static esp_err_t start_write_no_wait(uint16_t a,const uint8_t*p,size_t n){
    if(!n||n>64||((a&63)+n)>64||(uint32_t)a+n>32768)return ESP_ERR_INVALID_ARG;
    uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wren();return xfer(tx,NULL,n+3);
}
static void read_bytes(uint16_t a,uint8_t*p,size_t n){uint8_t tx[67]={0x03,a>>8,a},rx[67]={0};xfer(tx,rx,n+3);memcpy(p,rx+3,n);}
static void write_without_wren(uint16_t a,const uint8_t*p,size_t n){uint8_t tx[67]={0x02,a>>8,a};memcpy(tx+3,p,n);wrdi();xfer(tx,NULL,n+3);}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=GPIO_NUM_19,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=80};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=CS,.queue_size=1};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_CH_AUTO));ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev));
    uint8_t status_initial=status();wren();uint8_t status_wren=status();wrdi();uint8_t status_wrdi=status();
    printf("status_initial=%02x status_after_wren=%02x wel_after_wren=%u status_after_wrdi=%02x\n",
        status_initial,status_wren,(status_wren&2)!=0,status_wrdi);
    uint8_t payload[]="EEPROM-PAGE-OK",rx[sizeof(payload)]={0};
    esp_err_t cross=write_page(63,payload,sizeof(payload));
    ESP_ERROR_CHECK(write_page(0x0100,payload,sizeof(payload)));read_bytes(0x0100,rx,sizeof(rx));
    uint8_t before[4],after[4],blocked[4]={0x11,0x22,0x33,0x44};read_bytes(0x0140,before,4);
    write_without_wren(0x0140,blocked,4);vTaskDelay(pdMS_TO_TICKS(10));read_bytes(0x0140,after,4);
    uint8_t pending[4]={0xA5,0x5A,0xC3,0x3C},early[4]={0},final[4]={0};
    ESP_ERROR_CHECK(start_write_no_wait(0x0180,pending,sizeof(pending)));uint8_t early_status=status();
    read_bytes(0x0180,early,sizeof(early));ESP_ERROR_CHECK(wait_ready()?ESP_OK:ESP_ERR_TIMEOUT);read_bytes(0x0180,final,sizeof(final));
    printf("no_wren=%s page_cross=%s premature_wip=%u premature_match=%u final_match=%u crc_write=%08lx crc_read=%08lx verify=%s\n",
        memcmp(before,after,4)?"UNEXPECTED_CHANGE":"REJECT",
        cross==ESP_ERR_INVALID_ARG?"REJECT":"BUG",(early_status&1)!=0,!memcmp(early,pending,sizeof(early)),
        !memcmp(final,pending,sizeof(final)),(unsigned long)crc32(payload,sizeof(payload)),
        (unsigned long)crc32(rx,sizeof(rx)),memcmp(payload,rx,sizeof(rx))?"FAIL":"PASS");
}
