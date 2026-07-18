#include <string.h>
#include "nand/nand.h"
#include "nand/nand_profile.h"
nand_status_t nand_init(nand_t *n, const char *profile_hash, int read_only, int hardware_allowed){ if(!n||strcmp(profile_hash,NAND_PROFILE_HASH)) return NAND_ERR_PROFILE; if(hardware_allowed) return NAND_ERR_HARDWARE_GATED; n->initialized=1; n->read_only=read_only; n->write_enable=0; return NAND_OK; }
nand_status_t nand_write_enable(nand_t *n){ if(!n||!n->initialized) return NAND_ERR_PREREQ; if(n->read_only) return NAND_ERR_DESTRUCTIVE_RANGE; n->write_enable=1; return NAND_OK; }
nand_status_t nand_program_page(nand_t *n, uint32_t ppn, const uint8_t *data, uint32_t len){ (void)data; if(!n||!n->initialized||!n->write_enable) return NAND_ERR_PREREQ; if(ppn>=NAND_BLOCKS*NAND_PAGES_PER_BLOCK||len<NAND_PAGE_SIZE) return NAND_ERR_DESTRUCTIVE_RANGE; n->write_enable=0; return NAND_OK; }
nand_status_t nand_read_page(nand_t *n, uint32_t ppn, uint8_t *data, uint32_t len){ if(!n||!n->initialized) return NAND_ERR_PREREQ; if(ppn>=NAND_BLOCKS*NAND_PAGES_PER_BLOCK||len<NAND_PAGE_SIZE) return NAND_ERR_DESTRUCTIVE_RANGE; memset(data,0xff,len); return NAND_OK; }
nand_status_t nand_erase_block(nand_t *n, uint32_t block){ if(!n||!n->initialized||!n->write_enable) return NAND_ERR_PREREQ; if(block>=NAND_BLOCKS) return NAND_ERR_DESTRUCTIVE_RANGE; n->write_enable=0; return NAND_OK; }
