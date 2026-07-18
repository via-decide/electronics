#include <stdint.h>
#include <stddef.h>
int nand_hal_mock_component_present(void) { return 1; }
int nand_hal_mock_transfer(uint8_t op, const uint8_t *tx, size_t tx_len, uint8_t *rx, size_t rx_len){ (void)op;(void)tx;(void)tx_len; for(size_t i=0;i<rx_len;i++) rx[i]=0; return 0; }
