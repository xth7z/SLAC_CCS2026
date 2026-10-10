/*
 * Copyright (c) 2022 CISPA.
 * Adapted from cispa/BranchDifferent; see ../../THIRD_PARTY_NOTICES.md.
 * Original MIT license: ../../licenses/CISPA-MIT.txt.
 * SLAC modifications adjust configuration, includes, and C++ integration.
 */

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
