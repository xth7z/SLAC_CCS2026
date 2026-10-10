# Research data, models, and paper

The root MIT license applies to SLAC-authored software and accompanying software
documentation. It does **not** grant a new license for the authors' measurement
arrays, traces, reconstruction results, model outputs, or third-party content
embedded in the data files. No additional license is assigned to those original
research data in this update. Existing upstream rights and permissions continue
to apply. Contact Tianhong Xu (`xu.tianh@northeastern.edu`) for questions about
reuse of the authors' research data.

## MedQuAD questions and labels

- Original dataset: [MedQuAD](https://github.com/abachaa/MedQuAD), by Asma Ben
  Abacha and Dina Demner-Fushman.
- Upstream license: [Creative Commons Attribution 4.0 International](https://github.com/abachaa/MedQuAD/blob/master/LICENSE.txt).
- Dataset paper: *A Question-Entailment Approach to Question Answering*, BMC
  Bioinformatics 20, 511 (2019), [DOI: 10.1186/s12859-019-3119-4](https://doi.org/10.1186/s12859-019-3119-4).
- Acquisition source cited in the SLAC paper:
  [Afroz's Kaggle redistribution](https://www.kaggle.com/datasets/pythonafroz/medquad-medical-question-answer-for-ai-research).
  The exact downloaded revision was not recorded.

`LLM_Attack/Key_word_recovery/question_side_channel_traces.csv` includes 7,243
question records with question text, focus-area labels, and measurements.
`focus_area_side_channel_traces.csv` contains 1,000 selected focus-area labels
and their measured profiles. SLAC selects and reorganizes the upstream questions
and labels and attaches side-channel traces; those measurements are separate
from the upstream text. Retain the MedQuAD attribution and license when reusing
its material, and identify the subset/transformation used.

The upstream README explains that answers were removed from three MedlinePlus
subsets because of their original copyright terms. Access to a question or URL
does not establish permission to redistribute a separately retrieved answer.

## LLM output traces and recovery results

`LLM_Attack/Output_recovery/output_side_channel_traces.csv` contains 4,253 records
of victim-output text, token IDs, and measured traces.
`output_recovery_results.csv` contains the corresponding reconstructed outputs
and evaluation fields. `top3000_superset_token_mapping.csv` maps 128 supersets to
candidate token IDs. The artifact describes these as TinyLlama model-output and
recovery data; they are not presented as a re-release of all MedQuAD answers.

The exact collection-time model revision and complete generation parameters
were not recorded in this artifact. The runnable script identifies its model in
`MODEL_NAME` and downloads it through Hugging Face Transformers. No model weights
are bundled here. Consult that model's upstream card and license for its terms;
this document grants no new license to the model or generated-output records.

## GNN benchmarks and derived measurements

`GNN_Attack/node_recovery.py` loads the public Cora and Amazon Photo benchmarks
through PyTorch Geometric's `Planetoid` and `Amazon` dataset loaders.

- Cora/Planetoid: [kimiyoung/planetoid](https://github.com/kimiyoung/planetoid);
  Zhilin Yang et al., *Revisiting Semi-Supervised Learning with Graph Embeddings*,
  ICML 2016, [paper](https://proceedings.mlr.press/v48/yanga16.html).
- Amazon Photo: [shchur/gnn-benchmark](https://github.com/shchur/gnn-benchmark);
  Oleksandr Shchur et al., *Pitfalls of Graph Neural Network Evaluation*, 2018,
  [paper](https://arxiv.org/abs/1811.05868).

`nodes_matrix/` and `index_select_traces_noise/` contain SLAC profiles and access
measurements for those benchmarks. `recovery_results/` contains derived
neighborhoods/edges, metrics, and debug records. The original download revisions
and a complete capture manifest were not recorded. These files are not raw
upstream dataset archives; recovered graph structures and source datasets may
nevertheless carry upstream rights. Consult the actual dataset sources for their
terms; the software license of a loader does not assign a license to its data.

## Primitive-validation traces

`Side_channel/trace.txt` and `Target_address.txt` are the supplied SLAC experiment
trace and associated address/set records. They receive no additional data
license in this update. The Python scripts operating on them remain within the
software-license scope.

## Paper and project figures

`paper/SLAC_CCS2026.pdf` explicitly carries **CC BY 4.0**, Copyright © 2026 held
by the owner/authors. Cite the published paper using
[DOI: 10.1145/3830454.3846599](https://doi.org/10.1145/3830454.3846599).

The images in `website/assets/figures/` are SLAC project illustrations and plots
associated with the paper. When reproducing paper figures, retain attribution
to the paper and identify any changes. The original sources of small embedded
pictograms were not recorded; no new claim of ownership or additional license
for independently owned assets is made here.
