#include <stdint.h>
#include "nand/nand.h"
#include "ftl/ftl.h"
int main(void){ nand_t n; uint8_t b[512]={0}; if(nand_init(&n,"synthetic_1g",0,0)!=NAND_OK) return 1; if(nand_write_enable(&n)!=NAND_OK) return 2; if(nand_program_page(&n,8,b,512)!=NAND_OK) return 3; if(nand_init(&n,"bad",0,0)==NAND_OK) return 4; if(nand_init(&n,"synthetic_1g",0,1)!=NAND_ERR_HARDWARE_GATED) return 5; ftl_t f; if(ftl_init(&f,4)) return 6; for(unsigned i=0;i<16;i++) if(ftl_write(&f,i,b)) return 7; if(ftl_trim(&f,1)) return 8; return ftl_check_invariants(&f); }
