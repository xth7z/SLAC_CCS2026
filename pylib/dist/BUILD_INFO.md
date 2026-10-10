# Distribution build record

These distributions were built from source commit
`46711ea2a85012aca8e692159c00e8aa73095999` by the
[successful macOS packaging workflow](https://github.com/xth7z/SLAC_CCS2026/actions/runs/38007659127).

- Platform: Apple Silicon (`arm64`), minimum macOS 14.0.
- Builder: GitHub-hosted macOS 15, Xcode 16.4, CPython 3.12 / 3.13.
- Binding dependency: pybind11 3.1.0.
- Each wheel was built from its source distribution, then checked for complete
  source inputs/license notices, installed, and imported outside the checkout.
- The source archive below is from the Python 3.13 job. Both jobs checked their
  archive contents against the same source tree.
- These checks validate packaging and importability, not reproduction of the
  paper's hardware measurements or accuracy results.

SHA-256 checksums:

```text
fd4276a118d635c380b59dc9d8cf9fdcee8964f88bed9a39b26fcf261020860e  mymodule-0.2.0-cp312-cp312-macosx_14_0_arm64.whl
b68f054ea8b304990f67a067a52633c0d9bb1b2ba18c5b8ccc6c3169d834dff0  mymodule-0.2.0-cp313-cp313-macosx_14_0_arm64.whl
8f98a58419b2fc3fbe6c6d9ba3e3f85efe8c8b390b496048fa393e5401a24d71  mymodule-0.2.0.tar.gz
```
