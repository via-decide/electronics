#include <stdio.h>
#include "ssd/platform.h"
#include "ssd/status.h"
int main(void){ printf("ssd_lab %s %s\n", ssd_platform_name(), ssd_status_string(0)); return 0; }
