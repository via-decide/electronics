#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stdint.h>
#include <string.h>
#include "driver/uart.h"
#define TX_PORT UART_NUM_1
#define RX_PORT UART_NUM_2
#define TX_BAUD 115200
#define RX_BAUD 115200
static uint8_t crc8(const uint8_t *p,size_t n){uint8_t c=0;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&0x80?(c<<1)^0x07:c<<1;}return c;}
void app_main(void){
    uart_config_t txc={.baud_rate=TX_BAUD,.data_bits=UART_DATA_8_BITS,.parity=UART_PARITY_DISABLE,
        .stop_bits=UART_STOP_BITS_1,.flow_ctrl=UART_HW_FLOWCTRL_DISABLE,.source_clk=UART_SCLK_DEFAULT};
    uart_config_t rxc=txc;rxc.baud_rate=RX_BAUD;
    ESP_ERROR_CHECK(uart_driver_install(TX_PORT,256,0,0,NULL,0));
    ESP_ERROR_CHECK(uart_driver_install(RX_PORT,256,0,0,NULL,0));
    ESP_ERROR_CHECK(uart_param_config(TX_PORT,&txc));ESP_ERROR_CHECK(uart_param_config(RX_PORT,&rxc));
    ESP_ERROR_CHECK(uart_set_pin(TX_PORT,GPIO_NUM_17,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE));
    ESP_ERROR_CHECK(uart_set_pin(RX_PORT,UART_PIN_NO_CHANGE,GPIO_NUM_16,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE));
    uint8_t seq=0,rx[32];
    while(1){
        uint8_t f[]={0xA5,seq++,3,'S','P','I',0}; f[6]=crc8(f,6);
        uart_write_bytes(TX_PORT,f,sizeof(f));
        int n=uart_read_bytes(RX_PORT,rx,sizeof(rx),pdMS_TO_TICKS(100));
        bool ok=n==7&&rx[0]==0xA5&&rx[2]==3&&crc8(rx,6)==rx[6];
        printf("tx_baud=%d rx_baud=%d uart_rx=%d frame=%s seq=%u\n",
            TX_BAUD,RX_BAUD,n,ok?"ACCEPT":"REJECT",n>1?rx[1]:0);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
