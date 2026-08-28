# Publication package

This directory is a separate publication and reproducibility layer for the preserved project. No original research file is an output target.

## Integrity model

- `original_tracked_hashes.sha256` records the pre-publication SHA-256 digest of every original tracked file.
- `scripts/check_original_integrity.ps1` verifies those digests.
- `scripts/run_publication_analysis.py` resolves every output below `publication/` and rejects parent traversal.
- `tests/test_publication_safeguards.py` checks feature exclusions, output containment, threshold uncertainty utilities, and corruption reproducibility.
- Original and extension evidence are distinguished in `ORIGINAL_RESEARCH_MAP.md`, `EXPERIMENT_PROTOCOL.md`, and `RESULT_TRACEABILITY.md`.

## Directory guide

- `paper/`: IEEEtran manuscript, bibliography, and compiled PDF.
- `scripts/`: publication-only analysis and integrity utilities.
- `tests/`: standard-library safeguard tests.
- `results/baseline_verification/`: independent reconstruction of split, threshold analysis, and clean result.
- `results/confidence_intervals/`: Wilson and bootstrap uncertainty.
- `results/repeated_experiments/`: repeated noise, missingness, and label-scarcity results.
- `results/calibration/`: reliability data and Brier score.
- `results/explainability/`: permutation, confusion-group SHAP, and failure-mode diagnostics.
- `figures/`: publication figures in vector PDF and 300-DPI PNG.
- `tables/`: traceable LaTeX tables.
- `supplementary/`: compact supplementary notes and review material.

## Reproduce

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s publication\tests -v
.\.venv\Scripts\python.exe publication\scripts\run_publication_analysis.py
powershell -ExecutionPolicy Bypass -File publication\scripts\check_original_integrity.ps1
Set-Location publication\paper
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error main.tex
```

The analysis downloads UCI dataset 601 through the original loader. It may therefore require network access on the first run. It asserts the preserved clean confusion matrix `[[1417, 32], [9, 42]]` before generating extensions.

## Experimental labels

The point estimates already present in notebooks are **Original research**. Repeated-seed analyses, uncertainty intervals, calibration, permutation importance, confusion-group SHAP, and failure-mode detection are **Publication extension experiments**. Extensions strengthen characterization but are not presented as work originally performed.

## Environment

The original environment is preserved in the root `requirements.txt`. Publication analysis versions are separately recorded in `requirements-publication.txt`. The clean selected-threshold test result reproduces exactly in the current environment; the default-threshold validation forest differs by one false positive, as documented in the audit and paper.
