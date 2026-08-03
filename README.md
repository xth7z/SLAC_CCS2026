# SLAC Artifact

[**Interactive project website**](https://xth7z.github.io/SLAC_CCS2026/) · [**Browse the artifact**](https://github.com/xth7z/SLAC_CCS2026)

This repository contains the open-source artifact for **SLAC: Access-Driven CPU-to-GPU Side-channel Attacks via System-Level Cache on Apple Silicon**, accepted at the ACM SIGSAC Conference on Computer and Communications Security (CCS) 2026. The artifact provides the low-level Apple Silicon SLC side-channel implementation and small reproduction scripts for the paper's main case studies: CPrime+CProbe / GPrime+CProbe validation, GNN edge recovery, and LLM keyword/output recovery.

## Authors

- Tianhong Xu (Northeastern University) — xu.tianh@northeastern.edu
- Saion Kumar Roy (Northeastern University) — sai.roy@northeastern.edu
- Ruyi Ding (Louisiana State University) — ruyiding@lsu.edu
- A. Adam Ding (Northeastern University) — a.ding@northeastern.edu
- Yunsi Fei (Northeastern University) — y.fei@northeastern.edu

For questions about this artifact, please contact Tianhong Xu (xu.tianh@northeastern.edu).

## Project Structure

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

## What This Artifact Does

- **`GetFrameNumber/`** contains the macOS kernel extension used to read physical addresses. This artifact directly uses physical addresses to construct SLC eviction sets. The paper also discusses how to construct eviction sets without kernel privilege, but that approach is much slower and is not included here.

- **`pylib/`** contains the low-level C++/Metal implementation required by CPrime+CProbe and GPrime+CProbe. It is packaged as a Python library named `mymodule`.

- **`Side_channel/`** validates the two side-channel primitives. `test_Cprime.py` and `test_Gprime.py` profile a simple GPU read kernel, save the side-channel trace, and record the SLC sets corresponding to the GPU-accessed data addresses. `plot_case1.py` and `plot_case2.py` reproduce the two noise-mitigation examples in Section 5.1: multi-run averaging and cache-set aggregation. A sample GPrime trace is included for testing these scripts.

- **`GNN_Attack/`** contains the Section 5.2 GNN edge-recovery artifact. We provide pre-collected node profiling matrices `M_G` and observed access vectors `v` for Cora and Amazon Photo. Running `node_recovery.py` recovers node neighborhoods and full-graph edges, then writes precision/recall metrics and recovered edge files.

- **`LLM_Attack/`** contains the Section 5.3 LLM privacy attacks using pre-collected CPrime+CProbe traces. The target model is TinyLlama, and the prompt dataset is MedQuad. `Key_word_recovery/` recovers the input focus-area keyword, while `Output_recovery/` recovers output tokens using the superset-token mapping and a language-model prior.

## Requirements

This artifact is intended for Apple Silicon macOS machines. The side-channel code requires Apple Metal support and a working C++/Python build environment.

Python packages used by the reproduction scripts include:

```bash
pip install numpy pandas matplotlib torch torch-geometric transformers
```

Depending on your PyTorch / PyG installation, `torch-geometric` may require platform-specific installation steps.

## Setup

### 1. Install the physical-address kernel extension

Build and load the kext:

```bash
cd GetFrameNumber
make
sudo chown -R 0:0 build/MyKext.kext
sudo kmutil load -p build/MyKext.kext
```

If macOS reports a signing or permission error, make sure the kext is correctly built, owned by `root:wheel`, and allowed under your macOS security settings.

### 2. Build and install the Python side-channel library

```bash
cd ../pylib
./com.sh
```

This compiles the Metal/C++ code and installs the Python package used by the side-channel scripts.

## Running the Artifact

### Side-channel validation

```bash
cd Side_channel
python3 test_Cprime.py
python3 test_Gprime.py
python3 plot_case1.py
python3 plot_case2.py
```

The test scripts collect traces for a simple GPU read kernel. The plotting scripts use the included sample trace to visualize the two noise-mitigation methods.

### GNN edge recovery

```bash
cd GNN_Attack
python3 node_recovery.py
```

This runs recovery on the included Cora and Amazon Photo traces and writes results to `recovery_results/`.

### LLM keyword recovery

```bash
cd LLM_Attack/Key_word_recovery
python3 key_word_recovery.py
```

This compares keyword profiles with question traces and writes the recovered labels to `keyword_recovery_results.csv`.

### LLM output recovery

```bash
cd LLM_Attack/Output_recovery
python3 output_recovery.py
```

This loads TinyLlama through Hugging Face Transformers, uses `top3000_superset_token_mapping.csv` and `output_side_channel_traces.csv`, and writes recovered outputs to `output_recovery_results.csv`.

## Notes

- The included traces are pre-collected examples for artifact evaluation.
- The artifact is for research and reproducibility purposes only.
