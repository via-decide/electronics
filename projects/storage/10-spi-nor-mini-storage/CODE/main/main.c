#include <stdbool.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "driver/spi_master.h"
#define CS GPIO_NUM_32
#define SECTOR 4096u
#define SLOT0 0x000000u
#define SLOT1 0x001000u
#define PREPARED 0x7Fu
#define COMMITTED 0x3Fu
#define RUN_RESERVED_SECTOR_WRITE_DEMO 0
typedef struct __attribute__((packed)){uint32_t magic;uint16_t schema;uint32_t generation;uint16_t length;uint32_t payload_crc;uint32_t header_crc;uint8_t commit;} record_t;
static spi_device_handle_t dev;
static uint32_t crc32(const uint8_t*p,size_t n){uint32_t c=~0u;while(n--){c^=*p++;for(int i=0;i<8;i++)c=c&1?(c>>1)^0xEDB88320:c>>1;}return~c;}
static esp_err_t xfer(const void*tx,void*rx,size_t n){spi_transaction_t t={.length=n*8,.tx_buffer=tx,.rx_buffer=rx};return spi_device_polling_transmit(dev,&t);}
static uint8_t sr(void){uint8_t tx[2]={0x05,0},rx[2]={0};xfer(tx,rx,2);return rx[1];}
static void wren(void){uint8_t c=0x06;xfer(&c,NULL,1);}
static bool ready(const char*op,int ms){for(int i=0;i<ms;i++){if(!(sr()&1)){printf("%s_busy_polls=%d\n",op,i);return true;}vTaskDelay(pdMS_TO_TICKS(1));}return false;}
static void readn(uint32_t a,void*out,size_t n){uint8_t tx[300]={0x03,a>>16,a>>8,a},rx[300]={0};xfer(tx,rx,n+4);memcpy(out,rx+4,n);}
static bool erase4k(uint32_t a){
    if(a%SECTOR)return false;uint8_t c[4]={0x20,a>>16,a>>8,a};wren();if(!(sr()&2))return false;
    return xfer(c,NULL,4)==ESP_OK&&ready("erase",5000);
}
static bool program(uint32_t a,const void*p,size_t n){
    if(!n||n>256||((a&255)+n)>256)return false;uint8_t tx[260]={0x02,a>>16,a>>8,a};memcpy(tx+4,p,n);
    wren();if(!(sr()&2))return false;return xfer(tx,NULL,n+4)==ESP_OK&&ready("program",100);
}
static bool valid(uint32_t a,record_t*h,uint8_t*p){
    readn(a,h,sizeof(*h));if(h->magic!=0x455A4631||h->schema!=1||h->length>128||h->commit!=COMMITTED)return false;
    uint32_t saved=h->header_crc;h->header_crc=0;
    bool hh=crc32((uint8_t*)h,offsetof(record_t,header_crc))==saved;h->header_crc=saved;
    readn(a+sizeof(*h),p,h->length);return hh&&crc32(p,h->length)==h->payload_crc;
}
static bool stage(uint32_t a,uint32_t gen,const uint8_t*p,uint16_t n,bool commit){
    if(!n||n>128)return false;
    record_t h={.magic=0x455A4631,.schema=1,.generation=gen,.length=n,.payload_crc=crc32(p,n),.header_crc=0,.commit=PREPARED};
    h.header_crc=crc32((uint8_t*)&h,offsetof(record_t,header_crc));
    if(!erase4k(a)||!program(a,&h,sizeof(h))||!program(a+sizeof(h),p,n))return false;
    uint8_t verify[128];record_t rh;readn(a,&rh,sizeof(rh));readn(a+sizeof(rh),verify,n);
    uint32_t saved=rh.header_crc;rh.header_crc=0;
    bool header_ok=rh.magic==h.magic&&rh.schema==h.schema&&rh.generation==h.generation&&rh.length==n&&
        crc32((uint8_t*)&rh,offsetof(record_t,header_crc))==saved;
    if(!header_ok||rh.payload_crc!=crc32(verify,n))return false;
    if(!commit)return true;
    return program(a+offsetof(record_t,commit),&(uint8_t){COMMITTED},1);
}
void app_main(void){
    spi_bus_config_t b={.mosi_io_num=GPIO_NUM_23,.miso_io_num=GPIO_NUM_19,.sclk_io_num=GPIO_NUM_18,
        .quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=300};
    spi_device_interface_config_t d={.clock_speed_hz=1000000,.mode=0,.spics_io_num=CS,.queue_size=1};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_CH_AUTO));ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&d,&dev));
    uint8_t idtx[4]={0x9F,0,0,0},idrx[4]={0};xfer(idtx,idrx,4);
    printf("jedec=%02x-%02x-%02x status_initial=%02x expected_macronix_mfr=c2\n",idrx[1],idrx[2],idrx[3],sr());
    if(idrx[1]!=0xC2||idrx[2]!=0x20||idrx[3]!=0x16){printf("device=REJECT expected=c2-20-16\n");return;}
    record_t a,bh;uint8_t pa[128],pb[128];bool va=valid(SLOT0,&a,pa),vb=valid(SLOT1,&bh,pb);
    if(!RUN_RESERVED_SECTOR_WRITE_DEMO){
        printf("write_demo=BLOCKED set RUN_RESERVED_SECTOR_WRITE_DEMO=1 only for a dedicated lab part\n");
        printf("slot0_valid=%d slot1_valid=%d\n",va,vb);return;
    }
    if(!va&&!vb){uint8_t p[]="generation-one";ESP_ERROR_CHECK(stage(SLOT0,1,p,sizeof(p),true)?ESP_OK:ESP_FAIL);va=valid(SLOT0,&a,pa);}
    if(va&&!vb){uint8_t p[]="generation-two";ESP_ERROR_CHECK(stage(SLOT1,a.generation+1,p,sizeof(p),true)?ESP_OK:ESP_FAIL);vb=valid(SLOT1,&bh,pb);}
    uint32_t winner=(vb&&(!va||bh.generation>a.generation))?SLOT1:SLOT0;
    uint32_t generation=winner==SLOT1?bh.generation:a.generation;
    uint32_t loser=winner==SLOT1?SLOT0:SLOT1;uint8_t interrupted[]="prepared-not-committed";
    ESP_ERROR_CHECK(stage(loser,generation+1,interrupted,sizeof(interrupted),false)?ESP_OK:ESP_FAIL);
    va=valid(SLOT0,&a,pa);vb=valid(SLOT1,&bh,pb);
    uint32_t recovered=(vb&&(!va||bh.generation>a.generation))?bh.generation:(va?a.generation:0);
    printf("slot0_valid=%d slot1_valid=%d recovery_generation=%lu\n",va,vb,(unsigned long)recovered);
}
