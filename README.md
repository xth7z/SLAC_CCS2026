# SLAC Artifact: CPU-to-GPU SLC Side-Channel on Apple M1

This repository contains the artifact for our CCS 2026 submission:

> **SLAC: Access-Driven CPU-to-GPU Side-Channel Attacks via System-Level Cache on Apple Silicon**

---

## 📋 Scope of This Artifact

This artifact provides a **minimal implementation** of our Apple M1 SLC side-channel, including:

- **CPrime + CProbe** (CPU-only side channel)
- **GPrime + CProbe** (GPU-assisted side channel)

Using the provided scripts, evaluators can reproduce the key experimental results reported in:

- **Figure 8** – Multi-run averaging (Method 1)
- **Figure 9** – Cache-set aggregation / superset (Method 2)

⚠️ **Note:**  
This artifact focuses **only on side-channel construction and trace analysis (Section 4 and Section 5.1)**.  
It does **NOT include end-to-end attacks** (e.g., GNN or LLM attacks).

---

## ✨ What is Implemented

### Side-Channel Primitives (Section 4)

- **CPrime + CProbe**
  - Fully CPU-based Prime+Probe on SLC

- **GPrime + CProbe**
  - GPU-accelerated priming using Apple Metal

### Trace Analysis (Section 5.1)

- **Method 1: Multi-run averaging** → Figure 8
- **Method 2: Superset aggregation** → Figure 9

---

## 🖥️ System Requirements

- **Hardware**: Apple M1 (or compatible M-series)
- **OS**: macOS
- **Python**: 3.8+
- **Xcode Command Line Tools**

---

## 📦 Installation

### Step 1: Build Side-Channel Library

```bash
cd pylib
./com.sh
```

This step compiles:

- Metal kernels (for GPrime)
- Python bindings (`mymodule`)
- Cache utilities

---

### Step 2 (Optional): Build Kernel Extension

The directory `GetFrameNumber/` provides a kernel extension for physical address translation.

```bash
cd GetFrameNumber
make
```

⚠️ Note:

- May require developer mode / SIP configuration
- If already installed, this step can be skipped

---

## 🚀 Running the Side Channels

### ▶ CPrime + CProbe (CPU-only)

```bash
python test_Cprime.py
```

- CPU-only implementation
- No GPU access required
- Default setup used in experiments

---

### ▶ GPrime + CProbe (GPU-assisted)

```bash
python test_Gprime.py
```

- Uses GPU for faster SLC priming
- Lower noise and higher efficiency

---

## 🔬 Reproducing Paper Results

### ▶ Figure 8 — Multi-run Averaging (Method 1)

```bash
python plot_case1.py
```

This script:

- Collects multiple traces
- Averages per-set eviction counts
- Produces stable clustering behavior

---

### ▶ Figure 9 — Superset Aggregation (Method 2)

```bash
python plot_case2.py
```

This script:

- Groups cache sets into supersets
- Outputs binary access pattern
- Uses thresholding for classification

---

## 📁 Repository Structure

```text
.
├── test_Cprime.py        # CPrime + CProbe example
├── test_Gprime.py        # GPrime + CProbe example
├── plot_case1.py         # Method 1 (Figure 8)
├── plot_case2.py         # Method 2 (Figure 9)
├── Target_address.txt    # Target addresses
│
├── pylib/                # Core side-channel implementation
│   ├── com.sh
│   ├── src/
│   ├── metal-cpp/
│   └── dist/
│
├── GetFrameNumber/       # Kernel extension
│   └── build/MyKext.kext
```

---

## ⚙️ Notes on Measurement

### Noise Sources

- OS background activity
- Cache contention
- Scheduling jitter

### Noise Mitigation

This artifact implements the two trace-analysis methods described in Section 5.1:

- **Multi-run averaging** for reducing run-to-run variance
- **Superset aggregation** for obtaining a cleaner single-trial signal

---

## ⚠️ Important Notes

### Artifact Limitations

This artifact:

- ✅ Implements side-channel primitives
- ✅ Reproduces Figure 8 & Figure 9
- ❌ Does NOT include:
  - GNN attacks
  - LLM attacks
  - Full attack pipeline

### Stability Tips

- Close background applications
- Run multiple trials
- Prefer GPrime for cleaner results

---

## 📄 Citation

```bibtex
@inproceedings{slac2026,
  title={SLAC: Access-Driven CPU-to-GPU Side-Channel Attacks via System-Level Cache on Apple Silicon},
  author={Anonymous Authors},
  booktitle={CCS},
  year={2026}
}
```

---

## 📬 Contact

For questions, please open an issue in this repository.
