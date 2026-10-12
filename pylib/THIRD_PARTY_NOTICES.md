# Third-party notices

The SLAC-authored software is licensed under [MIT](LICENSE). Third-party
material retains the notices and conditions below. The package's combined
license expression describes these components together; it does not replace
their individual licenses. The source distribution and wheel carry this file
and the license texts in `licenses/`.

## CISPA BranchDifferent: cache maintenance and timing

- Source: [cispa/BranchDifferent](https://github.com/cispa/BranchDifferent/tree/9a622451cb596ecd0f036f4ad931c777120c16f6).
- Copyright (c) 2022 CISPA.
- License: [MIT](licenses/CISPA-MIT.txt).
- Scope: `metal-cpp/common/cache.h`, `memory.h`, `timing.h`, `counter_thread.c`,
  `flushing.c`, `msr.c`, `eviction.c`, `ent.xml`, and `Readme.md` match or adapt
  the upstream `common/` files. `config.h` adapts `benchmark/config.h`.
- SLAC modifications include include paths, C++ casts, configuration constants,
  threshold comments, and logging. The upstream revision above is the reference
  used for comparison.

The `common/` directory is separate from Apple's Metal-cpp wrapper library,
despite being stored beneath the same directory.

## evsets: eviction-set construction

- Source: [cgvwzq/evsets](https://github.com/cgvwzq/evsets), through BranchDifferent.
- License: [Apache-2.0](licenses/evsets-Apache-2.0.txt), preserved from
  [BranchDifferent's evsets.LICENSE](https://github.com/cispa/BranchDifferent/blob/9a622451cb596ecd0f036f4ad931c777120c16f6/evsets.LICENSE).
- Scope: portions of `metal-cpp/common/eviction.c`, including linked-list and
  eviction-set reduction routines. BranchDifferent documents its adaptation of
  evsets; SLAC further adapts it for its configuration and C++ build.
- Research reference: Pepe Vila, Boris Köpf, and José F. Morales,
  *Theory and Practice of Finding Eviction Sets*, IEEE S&P 2019,
  [DOI: 10.1109/SP.2019.00042](https://doi.org/10.1109/SP.2019.00042).

## Apple Metal-cpp

- Source: [Apple Metal-cpp](https://developer.apple.com/metal/cpp/).
- Distribution: [metal-cpp_macOS12_iOS15.zip](https://developer.apple.com/metal/cpp/files/metal-cpp_macOS12_iOS15.zip).
- Copyright 2020–2021 Apple Inc., as stated in the supplied source headers.
- License: [Apache-2.0](licenses/Apple-metal-cpp-Apache-2.0.txt).
- Scope: `metal-cpp/Foundation/`, `Metal/`, `QuartzCore/`, and
  `SingleHeader/MakeSingleHeader.py`. The original headers and
  `metal-cpp/LICENSE.txt` are preserved. All 81 supplied files in these four
  directories match the Apple distribution above byte for byte.

## Metal shader sample

- Apple sample: [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu).
- C++ adaptation and tutorial: [larsgeb/m1-gpu-cpp](https://github.com/larsgeb/m1-gpu-cpp/blob/e782affdf2af19c2cfa29f03686bea7684391238/01-MetalAdder/add.metal)
  and Lars Gebraad's [M1 GPUs for C++ science: Getting started](https://larsgeb.github.io/2022/04/20/m1-gpu.html).
- Scope: the sample scaffold and inherited license reference in `src/add.metal`.
  The original file header matches the linked C++ sample. SLAC replaces array
  addition with GPU priming, writing, and read kernels.
- Preserved notices: [Apple sample MIT](licenses/Apple-sample-MIT.txt),
  Copyright © 2020 Apple Inc., and the adaptation project's
  [BSD-3-Clause notice](licenses/m1-gpu-cpp-BSD-3-Clause.txt),
  Copyright 2022 Lars Gebraad. These notices also accompany the compiled Metal
  library.

## pybind11

- Build dependency: [pybind11 v3.1.0](https://github.com/pybind/pybind11/tree/v3.1.0).
- License and copyright notices: [BSD-3-Clause](licenses/pybind11-BSD-3-Clause.txt).
- Scope: binding code compiled into `mymodule` from pybind11 headers. The full
  upstream license is included in both distribution formats.

## Other repository materials

Research data, model outputs, and the paper are not licensed by this software
package. In the full artifact, consult the root `DATA_SOURCES.md` and the paper's
CC BY 4.0 notice. The package contains no model weights or research datasets.
