# SLAC Artifact

This repository contains the open-source artifact for **SLAC: Access-Driven CPU-to-GPU Side-channel Attacks via System-Level Cache on Apple Silicon**.  The artifact includes the low-level CPrime+CProbe and GPrime+CProbe side-channel code, validation scripts for the two side-channel variants, and reproduction scripts for the GNN and LLM case studies described in Section 5 of the paper.

The code is intended for artifact evaluation and research reproduction on Apple Silicon systems.

---

## 1. Project Structure

```text
SLAC/
├── GetFrameNumber/
│   ├── Info.plist
│   ├── Makefile
│   ├── MyKext.cpp
│   ├── MyKext.h
│   ├── MyUserClient.cpp
│   └── MyUserClient.h
│
├── pylib/
│   ├── com.sh
│   ├── pyproject.toml
│   ├── setup.py
│   ├── plot2.py
│   ├── dist/
│   │   ├── mymodule-0.1-cp313-cp313-macosx_14_0_arm64.whl
│   │   └── mymodule-0.1.tar.gz
│   ├── src/
│   │   ├── add.metal
│   │   ├── metal_handler.mm
│   │   ├── default.metallib
│   │   ├── MyLibrary.air
│   │   └── mymodule.egg-info/
│   └── metal-cpp/
│       ├── LICENSE.txt
│       ├── Readme.md
│       ├── common/
│       │   ├── cache.h
│       │   ├── config.h
│       │   ├── counter_thread.c
│       │   ├── eviction.c
│       │   ├── flushing.c
│       │   ├── memory.h
│       │   ├── msr.c
│       │   └── timing.h
│       ├── Foundation/
│       ├── Metal/
│       ├── QuartzCore/
│       └── SingleHeader/
│
├── Side_channel/
│   ├── Target_address.txt
│   ├── trace.txt
│   ├── test_Cprime.py
│   ├── test_Gprime.py
│   ├── plot_case1.py
│   └── plot_case2.py
│
├── GNN_Attack/
│   ├── node_recovery.py
│   ├── data/
│   │   ├── Cora/
│   │   │   └── Cora/
│   │   │       ├── raw/
│   │   │       │   ├── ind.cora.allx
│   │   │       │   ├── ind.cora.ally
│   │   │       │   ├── ind.cora.graph
│   │   │       │   ├── ind.cora.test.index
│   │   │       │   ├── ind.cora.tx
│   │   │       │   ├── ind.cora.ty
│   │   │       │   ├── ind.cora.x
│   │   │       │   └── ind.cora.y
│   │   │       └── processed/
│   │   │           ├── data.pt
│   │   │           ├── pre_filter.pt
│   │   │           └── pre_transform.pt
│   │   └── Amazon/
│   │       └── Photo/
│   │           ├── raw/
│   │           │   └── amazon_electronics_photo.npz
│   │           └── processed/
│   │               ├── data.pt
│   │               ├── pre_filter.pt
│   │               └── pre_transform.pt
│   ├── nodes_matrix/
│   │   ├── amazon_photo.npy
│   │   └── cora.npy
│   ├── index_select_traces_noise/
│   │   ├── amazon_photo_index_select_trace.npy
│   │   └── cora_index_select_trace.npy
│   └── recovery_results/
│       ├── all_metrics.json
│       ├── amazon_photo_gprime_debug.pkl
│       ├── amazon_photo_gprime_metrics.json
│       ├── amazon_photo_gprime_pred_edges.txt
│       ├── amazon_photo_gprime_recovered_sets.pkl
│       ├── cora_gprime_debug.pkl
│       ├── cora_gprime_metrics.json
│       ├── cora_gprime_pred_edges.txt
│       └── cora_gprime_recovered_sets.pkl
│
└── LLM_Attack/
    ├── Key_word_recovery/
    │   ├── focus_area_side_channel_traces.csv
    │   ├── question_side_channel_traces.csv
    │   └── key_word_recovery.py
    └── Output_recovery/
        ├── output_recovery.py
        ├── output_recovery_results.csv
        ├── output_side_channel_traces.csv
        └── top3000_superset_token_mapping.csv
```

---

## 2. Repository Overview

The artifact is organized around the same workflow used in the paper:

1. **Low-level side-channel implementation** in `pylib/`.
2. **Physical-address helper kernel extension** in `GetFrameNumber/`.
3. **CPrime+CProbe and GPrime+CProbe validation** in `Side_channel/`.
4. **GNN edge-recovery attack reproduction** in `GNN_Attack/`.
5. **LLM input/output recovery attack reproduction** in `LLM_Attack/`.

The paper uses a three-phase methodology: profiling target items to obtain an access mapping matrix, collecting observed side-channel traces, and recovering secrets by comparing the observed trace against the profiled mapping.  In this repository, several pre-collected side-channel traces are provided so that the recovery algorithms can be evaluated without re-running all low-level measurements.

---

## 3. Requirements

### Hardware and OS

The low-level side-channel code is designed for Apple Silicon systems with an integrated GPU and a shared System-Level Cache (SLC).  The artifact was developed for Apple M-series systems and uses Apple Metal for GPU kernels.

Recommended environment:

```text
Apple Silicon Mac
macOS with Metal support
Xcode Command Line Tools
Python 3.13 for the provided prebuilt wheel
```

The recovery-only scripts in `GNN_Attack/` and `LLM_Attack/` can be inspected or run on other platforms if the required Python packages and input files are available, but the real side-channel collection code requires Apple Silicon.

### Python Packages

Install the common Python dependencies with:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install numpy scipy pandas matplotlib scikit-learn tqdm
```

For the GNN experiments:

```bash
python3 -m pip install torch torch_geometric
```

For the LLM experiments:

```bash
python3 -m pip install torch transformers sentencepiece tokenizers
```

Depending on your Python and PyTorch versions, `torch_geometric` may require a version-specific installation command.  Please follow the official PyTorch Geometric installation instructions if the generic command above fails.

### macOS Build Tools

Install Xcode Command Line Tools if they are not already installed:

```bash
xcode-select --install
```

---

## 4. Physical-Address Helper: `GetFrameNumber/`

This artifact directly reads physical addresses to construct the eviction sets used by the side-channel.  Therefore, before running the low-level side-channel profiling scripts, install the kernel function in `GetFrameNumber/`.

```bash
cd GetFrameNumber
make
sudo chown -R 0:0 build/MyKext.kext
sudo kmutil load -p build/MyKext.kext
```

If `build/MyKext.kext` is already provided, `make` may be unnecessary.  If the `kmutil load` command fails, check macOS kernel-extension security settings, code-signing requirements, and whether kernel-extension loading is enabled on the test machine.

The paper also discusses how eviction sets can be constructed without kernel privileges using side-channel-only methods.  However, that process is much slower.  For artifact reproducibility and faster evaluation, this repository provides the physical-address-assisted eviction-set construction method.

---

## 5. Low-Level Side-Channel Library: `pylib/`

The `pylib/` directory contains the low-level implementation required by CPrime+CProbe and GPrime+CProbe.  It wraps Metal kernels and native code into a Python library so that the side-channel scripts can invoke the CPU/GPU priming and CPU probing routines from Python.

Important files:

```text
pylib/
├── com.sh                  # Build/install helper script
├── setup.py                # Python package setup script
├── pyproject.toml          # Build configuration
├── src/add.metal           # Metal kernel source
├── src/metal_handler.mm    # Objective-C++/Metal bridge
├── src/default.metallib    # Compiled Metal library
├── dist/*.whl              # Prebuilt Python wheel
└── metal-cpp/              # Metal C++ headers and helper code
```

To build and install the Python library:

```bash
cd pylib
chmod +x com.sh
./com.sh
```

After installation, verify that the module can be imported:

```bash
python3 -c "import mymodule; print('mymodule imported successfully')"
```

---

## 6. Side-Channel Validation: `Side_channel/`

The `Side_channel/` directory validates the two side-channel mechanisms:

```text
Side_channel/
├── test_Cprime.py       # Runs CPrime+CProbe validation
├── test_Gprime.py       # Runs GPrime+CProbe validation
├── plot_case1.py        # Reproduces Method 1: multi-run averaging
├── plot_case2.py        # Reproduces Method 2: cache-set aggregation
├── trace.txt            # Example GPrime trace
└── Target_address.txt   # SLC-set mapping for the GPU-read target data
```

The validation scripts profile a simple GPU read kernel using the side-channel.  They save:

- the side-channel trace, and
- the SLC sets corresponding to the data addresses accessed by the GPU read kernel.

These saved outputs are then used to validate whether the observed SLC footprints match the ground-truth target addresses.

### Run CPrime+CProbe

```bash
cd Side_channel
python3 test_Cprime.py
```

### Run GPrime+CProbe

```bash
cd Side_channel
python3 test_Gprime.py
```

### Reproduce the Noise-Mitigation Examples

Section 5.1 of the paper introduces two noise-mitigation methods.  This repository provides one example trace collected with GPrime so that both mitigations can be tested without re-running the full side-channel collection.

#### Method 1: Multi-run Averaging

`plot_case1.py` presents the multi-run averaging method.  It plots a trace similar to Figure 7 in the paper and computes the corresponding accuracy.

```bash
cd Side_channel
python3 plot_case1.py
```

#### Method 2: Cache-Set Aggregation

`plot_case2.py` presents the cache-set aggregation method.  It groups cache sets into supersets, plots a trace similar to Figure 8 in the paper, and computes the corresponding accuracy.

```bash
cd Side_channel
python3 plot_case2.py
```

---

## 7. GNN Edge-Recovery Attack: `GNN_Attack/`

The `GNN_Attack/` directory contains the reproduction code for the GNN edge-recovery attack described in Section 5.2 of the paper.

```text
GNN_Attack/
├── node_recovery.py
├── data/
├── nodes_matrix/
├── index_select_traces_noise/
└── recovery_results/
```

### Data

Two datasets are included:

```text
GNN_Attack/data/Cora/
GNN_Attack/data/Amazon/Photo/
```

The raw and processed files are included under each dataset directory.

### Pre-Collected Side-Channel Inputs

The repository provides pre-collected inputs for two datasets:

```text
GNN_Attack/nodes_matrix/
├── cora.npy
└── amazon_photo.npy
```

These files contain the node profiling results, i.e., the access mapping matrix `M_G`, where each row corresponds to the profiled SLC footprint of a graph node.

```text
GNN_Attack/index_select_traces_noise/
├── cora_index_select_trace.npy
└── amazon_photo_index_select_trace.npy
```

These files contain the observed access vectors `v` collected from the victim `index_select` operation.  The recovery algorithm compares the observed vector `v` against the profiled matrix `M_G` to infer the accessed neighbor nodes and recover graph edges.

### Run the GNN Recovery

```bash
cd GNN_Attack
python3 node_recovery.py
```

The script writes recovered edges, debug information, and evaluation metrics to:

```text
GNN_Attack/recovery_results/
```

Important outputs include:

```text
all_metrics.json
cora_gprime_metrics.json
amazon_photo_gprime_metrics.json
cora_gprime_pred_edges.txt
amazon_photo_gprime_pred_edges.txt
```

The provided files allow the Section 5.2 recovery algorithm to be reproduced without collecting new side-channel traces.

---

## 8. LLM Privacy Attacks: `LLM_Attack/`

The `LLM_Attack/` directory contains the reproduction code for the two LLM attacks described in Section 5.3 of the paper.

```text
LLM_Attack/
├── Key_word_recovery/
└── Output_recovery/
```

The target model for the provided traces is **TinyLlama**, and the prompt dataset is **MedQuad**.  The repository includes side-channel traces already collected using CPrime+CProbe so that the recovery logic can be evaluated directly.

### 8.1 Keyword Recovery: `LLM_Attack/Key_word_recovery/`

```text
LLM_Attack/Key_word_recovery/
├── focus_area_side_channel_traces.csv
├── question_side_channel_traces.csv
└── key_word_recovery.py
```

This directory reproduces the input-side keyword recovery attack.  The provided CSV files contain side-channel traces for the MedQuad prompt fields.

Run:

```bash
cd LLM_Attack/Key_word_recovery
python3 key_word_recovery.py
```

### 8.2 Output Response Recovery: `LLM_Attack/Output_recovery/`

```text
LLM_Attack/Output_recovery/
├── output_recovery.py
├── output_recovery_results.csv
├── output_side_channel_traces.csv
└── top3000_superset_token_mapping.csv
```

This directory reproduces the output-token recovery attack.  The side-channel trace identifies the accessed SLC superset for each generated token.  Because multiple tokens may map to the same superset, `top3000_superset_token_mapping.csv` provides the candidate token set for each superset.  The recovery script then uses language-model probabilities to disambiguate candidates and reconstruct the output response.

Run:

```bash
cd LLM_Attack/Output_recovery
python3 output_recovery.py
```

The script reads the provided side-channel traces and token-superset mapping, then writes or updates:

```text
output_recovery_results.csv
```

---

## 9. Expected Results and Reproducibility Notes

The results produced by this artifact may not exactly match the numbers reported in the paper.  The paper reports averages over multiple repeated experiments, while this repository includes representative traces and pre-collected datasets for artifact evaluation.  Small differences are expected due to:

- system background activity,
- macOS scheduling noise,
- thermal and frequency variation,
- differences across Apple M-series chips and macOS versions,
- whether the script is run with CPrime+CProbe or GPrime+CProbe, and
- whether the run uses newly collected traces or the provided example traces.

For the most stable measurements, close unnecessary applications, avoid display- or GPU-intensive background tasks, and repeat each measurement multiple times.

---

## 10. Suggested Reproduction Order

For a full low-level reproduction:

```bash
# 1. Load the physical-address helper.
cd GetFrameNumber
make
sudo chown -R 0:0 build/MyKext.kext
sudo kmutil load -p build/MyKext.kext

# 2. Build and install the Python side-channel library.
cd ../pylib
chmod +x com.sh
./com.sh

# 3. Validate the side-channel mechanisms.
cd ../Side_channel
python3 test_Gprime.py
python3 test_Cprime.py

# 4. Reproduce the two noise-mitigation plots.
python3 plot_case1.py
python3 plot_case2.py

# 5. Reproduce the GNN edge-recovery attack.
cd ../GNN_Attack
python3 node_recovery.py

# 6. Reproduce the LLM keyword-recovery attack.
cd ../LLM_Attack/Key_word_recovery
python3 key_word_recovery.py

# 7. Reproduce the LLM output-recovery attack.
cd ../Output_recovery
python3 output_recovery.py
```

For algorithm-only reproduction, start directly from `GNN_Attack/` or `LLM_Attack/` using the provided pre-collected traces.

---

## 11. Troubleshooting

### `kmutil load` fails

Check the following:

- the kext bundle exists at `GetFrameNumber/build/MyKext.kext`;
- the bundle owner is `root:wheel`, which is set by `sudo chown -R 0:0 build/MyKext.kext`;
- kernel-extension loading is allowed on the machine;
- the kext is correctly signed or approved according to the macOS security policy of the test machine.

### `mymodule` cannot be imported

Rebuild and reinstall the Python package:

```bash
cd pylib
./com.sh
python3 -c "import mymodule"
```

Also check that the Python version matches the installed wheel.  The provided wheel is built for CPython 3.13 on macOS arm64.

### Results are noisy

Side-channel results are sensitive to background activity.  Close unnecessary applications, especially GPU- or display-intensive applications, and repeat the measurement multiple times.  For quick testing of the mitigation scripts, use the provided `Side_channel/trace.txt`.

---

## 12. Citation

If you use this artifact, please cite the corresponding paper:

```bibtex
@inproceedings{slac2026,
  title     = {SLAC: Access-Driven CPU-to-GPU Side-channel Attacks via System-Level Cache on Apple Silicon},
  author    = {Anonymous},
  booktitle = {Proceedings of the ACM Conference on Computer and Communications Security},
  year      = {2026}
}
```

Please replace the placeholder citation fields with the final publication metadata when available.
