#ifndef TIMING_H
#define TIMING_H

#include <stdint.h>

#include "config.h"
#include "memory.h"

// Read the shared timestamp counter maintained by the counter thread
extern uint64_t timestamp;
#define timer_read(x) x = timestamp


static inline __attribute__((always_inline)) uint64_t probe(char* address){
    uint64_t start, end;
    memory_fence();
    timer_read(start);
    memory_fence();
    memory_access(address);
    memory_fence();
    timer_read(end);
    memory_fence();
    return end - start;
}

void timer_start();

void timer_stop();

#endif /* TIMING_H */
