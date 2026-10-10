/*
 * Copyright (c) 2022 CISPA.
 * Adapted from cispa/BranchDifferent; see ../../THIRD_PARTY_NOTICES.md.
 * Original MIT license: ../../licenses/CISPA-MIT.txt.
 * SLAC modifications adjust configuration, includes, and C++ integration.
 */

#ifndef MEMORY_H
#define MEMORY_H

// memory barrier
#define memory_fence() __asm__ volatile("DMB SY\nISB SY" ::: "memory")

// memory load
#define memory_access(x) __asm__ volatile("LDR x10, [%[addr]]" :: [addr] "r" (x) : "x10", "memory")

#endif /* MEMORY_H */
