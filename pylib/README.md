# SLAC native Python library

`mymodule` exposes SLAC's Apple Silicon CPU/GPU cache primitives. Its source and
Metal shader are built together; the installed wheel contains the shader library
and all software license notices.

## Build and install

Use Apple Silicon macOS, Python 3.9 or later, and Xcode with its command-line and
Metal compiler tools. The default minimum macOS deployment target is 14.0.
The build discovers the selected Xcode SDK with `xcrun`; Homebrew LLVM and OpenMP
are not required by this implementation.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
sh ./com.sh
```

`com.sh` installs the current source for the active interpreter. It does not
select a pre-existing wheel by filename or modify the system Python environment.
You may also install a source archive with `python -m pip install mymodule-0.2.0.tar.gz`.
Builds need access to the declared build dependencies unless they are already
provided by your build environment.

To produce both distribution formats:

```sh
python -m pip install build
python -m build
```

The standard build command first makes the source archive, then builds the wheel
from that archive. Source archives include the cache helper headers, Metal
source, resource-loader package, notices, and license texts. Wheels include a
compiled extension and `slac_resources/default.metallib`; their Python and macOS
compatibility is encoded in the wheel filename. Build a new wheel for a different
Python ABI. Wheel resources are resolved relative to the installed package,
independently of the working directory.

Importing `mymodule` only checks that the native extension loads. Constructing
`mymodule.Attacker()` starts the hardware collection machinery. For physical
address access, first follow the full artifact's kernel-extension setup.

## Licenses and releases

SLAC-authored software uses [MIT](LICENSE). The combined package includes
third-party MIT, Apache-2.0, and BSD-3-Clause material; consult
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Version 0.2.0 replaces the earlier 0.1 distributions, which omitted license files
and required source headers and did not match the current source tree. The old
archives are retained in Git history, but are no longer the distributions offered
by the current tree. Artifact-level GitHub/Zenodo versions are separate from this
Python package version.
