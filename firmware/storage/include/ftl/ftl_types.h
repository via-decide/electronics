#ifndef FTL_TYPES_H
#define FTL_TYPES_H
#include <stdint.h>
#define FTL_MAX_LPN 32u
#define FTL_MAX_PPN 128u
typedef enum { PPN_FREE, PPN_VALID, PPN_INVALID, PPN_RESERVED, PPN_BAD } ppn_state_t;
#endif
