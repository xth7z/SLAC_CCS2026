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
  threshold comments, and logging. The upstream revision above records the
  comparison source; the original import revision was not recorded.

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
- Copyright 2020–2021 Apple Inc., as stated in the supplied source headers.
- License: [Apache-2.0](licenses/Apple-metal-cpp-Apache-2.0.txt).
- Scope: `metal-cpp/Foundation/`, `Metal/`, `QuartzCore/`, and
  `SingleHeader/MakeSingleHeader.py`. The original headers and
  `metal-cpp/LICENSE.txt` are preserved. The original downloaded release is not
  recorded, so no exact vendor version is asserted here.

## Metal shader sample

The original comment in `src/add.metal` points to `LICENSE-original.txt` and is
identical to the comment in
[`larsgeb/m1-gpu-cpp/01-MetalAdder/add.metal`](https://github.com/larsgeb/m1-gpu-cpp/blob/e782affdf2af19c2cfa29f03686bea7684391238/01-MetalAdder/add.metal).
That source supplies an [Apple sample license](licenses/Apple-sample-MIT.txt)
with Copyright © 2020 Apple Inc. and MIT terms. It is preserved here for the
inherited sample material. The matching project's
[BSD-3-Clause notice](licenses/m1-gpu-cpp-BSD-3-Clause.txt), Copyright 2022
Lars Gebraad, is also preserved for any material inherited through that project.

SLAC replaces the sample's array addition with GPU priming, writing, and read
kernels. The exact import route was not recorded; the matching header does not
establish that all current kernel bodies originate from that project. These
notices preserve the identified source terms without asserting an unverified
history. They also accompany the Metal library compiled from `src/add.metal`.

## pybind11

- Build dependency: [pybind11 v3.1.0](https://github.com/pybind/pybind11/tree/v3.1.0).
- License and copyright notices: [BSD-3-Clause](licenses/pybind11-BSD-3-Clause.txt).
- Scope: binding code compiled into `mymodule` from pybind11 headers. The full
  upstream license is included in both distribution formats.

## Other repository materials

Research data, model outputs, and the paper are not licensed by this software
package. In the full artifact, consult the root `DATA_SOURCES.md` and the paper's
CC BY 4.0 notice. The package contains no model weights or research datasets.

No external source has been established from the available records for the
`GetFrameNumber/` implementation or for small pictograms embedded in the project
figures. Their initial creation/import histories still need maintainer
confirmation. This file does not claim that an automated similarity search can
prove those materials are original or grant rights held by unidentified parties.
