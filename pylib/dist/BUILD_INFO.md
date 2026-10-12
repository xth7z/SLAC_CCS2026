# Distribution build record

Version 0.2.1 includes the updated upstream references and license notices.
These distributions were built from source commit
`c549a4462382d782d8054f638759b5e79d48abef` by the
[successful macOS packaging workflow](https://github.com/xth7z/SLAC_CCS2026/actions/runs/38281195369).

- Platform: Apple Silicon (`arm64`), minimum macOS 14.0.
- Builder: GitHub-hosted macOS 15, Xcode 16.4, CPython 3.12 / 3.13.
- Binding dependency: pybind11 3.1.0.
- Each wheel was built from its source distribution, checked for source and
  license completeness, installed, and imported outside the checkout.
- The source archive below is from the Python 3.13 job. Both jobs checked their
  archive contents against the same source tree.
- These checks validate packaging and importability, not reproduction of the
  paper's hardware measurements or accuracy results.

SHA-256 checksums:

```text
789a7ab129eaec84f5806c9730b80e0aafbf8f305127a905b5cac268476e6b8a  mymodule-0.2.1-cp312-cp312-macosx_14_0_arm64.whl
6909952f5bc63ef2c2dfe9766d7e01ee647c3a567e63d6fc3bee854503b1d43b  mymodule-0.2.1-cp313-cp313-macosx_14_0_arm64.whl
cd60247f6f9853260cee404b1f404711c66d9ef446b26d34637884cb0cd1a4cd  mymodule-0.2.1.tar.gz
```
