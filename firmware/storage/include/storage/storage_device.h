#ifndef STORAGE_DEVICE_H
#define STORAGE_DEVICE_H
#include "nand/nand.h"
#include "ftl/ftl.h"
typedef struct { nand_t nand; ftl_t ftl; } storage_device_t;
#endif
