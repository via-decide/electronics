#ifndef NAND_H
#define NAND_H
#include <stdint.h>
#include "nand_status.h"
typedef struct { int initialized; int read_only; unsigned write_enable; } nand_t;
nand_status_t nand_init(nand_t *n, const char *profile_hash, int read_only, int hardware_allowed);
nand_status_t nand_write_enable(nand_t *n);
nand_status_t nand_program_page(nand_t *n, uint32_t ppn, const uint8_t *data, uint32_t len);
nand_status_t nand_read_page(nand_t *n, uint32_t ppn, uint8_t *data, uint32_t len);
nand_status_t nand_erase_block(nand_t *n, uint32_t block);
#endif
