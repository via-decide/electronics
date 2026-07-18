#ifndef NAND_HAL_H
#define NAND_HAL_H
#include <stddef.h>
#include <stdint.h>
typedef struct { int hardware; int platform_bench_verified; } nand_hal_t;
int nand_hal_mock_transfer(uint8_t op, const uint8_t *tx, size_t tx_len, uint8_t *rx, size_t rx_len);
#endif
