# Publication package

This directory contains the submission-ready manuscript and its reproducibility materials. All generated outputs remain below `publication/`; the pre-existing project files are not modified.

## Current manuscript

**Primary submission PDF:** [Open the latest `main.pdf`](paper/main.pdf)

- LaTeX source: [`paper/main.tex`](paper/main.tex)
- Bibliography: [`paper/references.bib`](paper/references.bib)
- Format: IEEEtran conference, US Letter, two columns
- Length: 6 pages
- References: 26
- Status: compiled and visually inspected with no undefined references, overfull boxes, or Type 3 fonts

The manuscript now presents one unified reliability study. The latest revision:

- replaces manuscript-preparation terms such as "original research," "publication extension," and "preserved system" with study-focused language;
- describes the added analyses as repeated robustness experiments or repeated robustness evaluation;
- defines Gaussian corruption explicitly as
  $x'_{ij}=x_{ij}+\epsilon_{ij}$, where
  $\epsilon_{ij}\sim\mathcal{N}(0,(s\sigma^{\mathrm{train}}_j)^2)$;
- identifies the training partition as the source of each numerical feature scale;
- enlarges figure labels, tick text, and legends; and
- embeds figure fonts without Type 3 output.

## Integrity model

- `original_tracked_hashes.sha256` records the pre-publication SHA-256 digest of every original tracked file.
- `scripts/check_original_integrity.ps1` verifies those digests.
- `scripts/run_publication_analysis.py` resolves every output below `publication/` and rejects parent traversal.
- `tests/test_publication_safeguards.py` checks feature exclusions, output containment, threshold uncertainty utilities, and corruption reproducibility.
- Historical single-seed evidence and repeated analyses remain traceable in `ORIGINAL_RESEARCH_MAP.md`, `EXPERIMENT_PROTOCOL.md`, and `RESULT_TRACEABILITY.md`.

## Directory guide

- `paper/`: IEEEtran manuscript, bibliography, and the primary compiled [`main.pdf`](paper/main.pdf).
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

The analysis downloads UCI dataset 601 through the existing loader. It may therefore require network access on the first run. It asserts the clean confusion matrix `[[1417, 32], [9, 42]]` before generating repeated robustness results.

## Evidence provenance

The paper is written as one unified research study. For auditability, the traceability documents separately identify historical single-seed outputs and the later repeated-seed analyses, uncertainty intervals, calibration, permutation importance, confusion-group SHAP, and failure-mode diagnostics. This provenance distinction is retained for reproducibility and is not used as manuscript-preparation framing in the abstract, contributions, results headings, figure captions, or conclusion.

## Environment

The pre-existing environment remains recorded in the root `requirements.txt`. Publication analysis versions are separately recorded in `requirements-publication.txt`. The clean selected-threshold test result reproduces exactly in the current environment; the default-threshold validation forest differs by one false positive, as documented in the audit and paper.

## Final verification

The latest manuscript build was checked as follows:

- all 6 publication safeguard tests passed;
- all pre-existing tracked files matched their recorded SHA-256 hashes;
- the clean test result remained TN=1417, FP=32, FN=9, and TP=42;
- the selected threshold remained 0.20;
- all 6 PDF pages were visually inspected;
- all 26 bibliography entries were present; and
- the PDF contained embedded Type 1 or CID TrueType fonts and no Type 3 fonts.
