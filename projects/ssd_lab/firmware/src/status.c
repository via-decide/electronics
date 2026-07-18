#include "ssd/status.h"
const char *ssd_status_string(int code) { return code == 0 ? "OK" : "ERROR"; }
