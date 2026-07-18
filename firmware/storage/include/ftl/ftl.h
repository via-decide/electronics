#ifndef FTL_H
#define FTL_H
#include <stdint.h>
#include "ftl_types.h"
#include "ftl_metrics.h"
typedef struct { int32_t l2p[FTL_MAX_LPN]; int32_t p2l[FTL_MAX_PPN]; ppn_state_t state[FTL_MAX_PPN]; unsigned next_ppn; unsigned emergency_reserve; ftl_metrics_t metrics; } ftl_t;
int ftl_init(ftl_t *f, unsigned reserve);
int ftl_write(ftl_t *f, uint32_t lpn, const uint8_t *data);
int ftl_read(ftl_t *f, uint32_t lpn, uint8_t *data);
int ftl_trim(ftl_t *f, uint32_t lpn);
int ftl_check_invariants(const ftl_t *f);
#endif
