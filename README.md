# SLAC Artifact: CPU-to-GPU SLC Side-Channel on Apple M1

This repository contains the artifact for our CCS 2026 submission:

> SLAC: Access-Driven CPU-to-GPU Side-Channel Attacks via System-Level Cache on Apple Silicon

## Scope

This artifact implements:
- CPrime + CProbe (CPU-only)
- GPrime + CProbe (GPU-assisted)

Reproduces:
- Figure 8 (multi-run averaging)
- Figure 9 (superset aggregation)

Note: No GNN/LLM attacks included.

## Installation

cd pylib
./com.sh

(Optional)
cd GetFrameNumber
make

## Run

CPrime:
python test_Cprime.py

GPrime:
python test_Gprime.py

Figure 8:
python plot_case1.py

Figure 9:
python plot_case2.py

## Structure

test_Cprime.py
test_Gprime.py
plot_case1.py
plot_case2.py
Target_address.txt
pylib/
GetFrameNumber/

## Notes

Close background apps for stability.
Use GPrime for cleaner results.

## Citation

@inproceedings{slac2026,
  title={SLAC: Access-Driven CPU-to-GPU Side-Channel Attacks via System-Level Cache on Apple Silicon},
  author={Anonymous Authors},
  booktitle={CCS},
  year={2026}
}
