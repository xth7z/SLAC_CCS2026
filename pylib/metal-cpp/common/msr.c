#include "metal-cpp/common/config.h"

#if TIMER == MSR 

#include "metal-cpp/common/timing.h"

void timer_start(){
    // MSR-based timer needs no explicit start
}

void timer_stop(){
    // MSR-based timer needs no explicit stop
}

#endif /* TIMER */
