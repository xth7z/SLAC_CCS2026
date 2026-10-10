/*
 * Copyright (c) 2022 CISPA.
 * Adapted from cispa/BranchDifferent; see ../../THIRD_PARTY_NOTICES.md.
 * Original MIT license: ../../licenses/CISPA-MIT.txt.
 * SLAC modifications adjust configuration, includes, and C++ integration.
 */

#ifndef CACHE_H
#define CACHE_H

#include "config.h"


#if CACHE == EVICTION
    struct cache_ctx;
    typedef struct cache_ctx* cache_ctx_t;
#elif CACHE == FLUSHING
    typedef void* cache_ctx_t;
#else
    #error CACHE is set to invalid value!
#endif /* CACHE */

cache_ctx_t cache_remove_prepare(char* address);

void cache_remove(cache_ctx_t ctx);

#endif /* CACHE_H */
