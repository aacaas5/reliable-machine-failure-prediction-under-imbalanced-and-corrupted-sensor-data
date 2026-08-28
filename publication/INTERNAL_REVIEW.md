# Internal peer-review assessment

## Scores (1 = weak, 5 = strong)

| Criterion | Score | Reviewer assessment |
|---|---:|---|
| Research significance | 3 | Reliability under degraded sensing is practically relevant, but evidence comes from one synthetic benchmark. |
| Novelty | 2 | Random Forest, SHAP, and corruption testing are established; contribution is integration and transparent characterization. |
| Experimental rigor | 3 | Preserved holdout and threshold discipline are good; one primary split/model remains limiting. |
| Robustness design | 4 | Repeated noise, missingness, and label scarcity are clear and reproducible; degradation mechanisms remain simple. |
| Statistical uncertainty | 4 | Wilson and stratified bootstrap intervals are appropriate for the stated estimands; external variability is not addressed. |
| Baseline adequacy | 3 | Dummy, Logistic, weighted variants, and Random Forest exist; modern supplementary benchmarks were not added. |
| Explainability | 3 | Impurity, permutation, global/local SHAP, and confusion groups are useful but model-specific and associative. |
| Reproducibility | 4 | Exact clean assertion, separated outputs, seeds, hashes, tests, and provenance are strong. Network-loaded data and library sensitivity remain. |
| Writing | 4 | Claims are deliberately narrow and original/extension history is explicit. |
| Figures | 4 | Vector plots, readable labels, and uncertainty bands are suitable for a conference manuscript. |
| Related work | 4 | Twenty-six verified primary/methodological sources cover the needed themes. |
| Limitations | 5 | Synthetic data, small positive count, simulated corruption, missingness assumptions, and non-deployment are explicit. |

## Overall recommendation

**Major Revision** for a journal or selective applied-ML venue. The work is suitable as a transparent preprint, university research paper, or workshop/student-conference submission in its current form. It may become a stronger applied industrial-AI submission after external validation.

## Main reviewer objections

1. The entire empirical claim rests on one synthetic AI4I dataset and one preserved split.
2. No real industrial sensor fault, temporal drift, asset grouping, or prospective maintenance outcome is evaluated.
3. Gaussian independent noise and MCAR-style missing cells are limited stressors.
4. The primary model comparison is modest, and the publication extensions deliberately avoid replacing the original Random Forest.
5. Fifty-one test failures yield wide uncertainty; failure-mode subgroups are too small for strong conclusions.
6. Repeated seeds quantify perturbation/subset variability, not independent dataset generalization.
7. The operating threshold lacks an application-specific economic or safety cost model.
8. A current-library validation result differs by one false positive, underscoring environment sensitivity.

## Required revisions for a stronger venue

- Add at least one real, temporally structured predictive-maintenance dataset.
- Use grouped or temporal validation that prevents asset/time leakage.
- Predefine false-negative/false-positive costs with domain input.
- Test persistent drift, bias, correlated missingness, and complete sensor dropout.
- Compare additional models under the identical corruption protocol without erasing the original system.
- Report external or nested validation and uncertainty across datasets/sites.
- Include practitioner-facing error analysis and a deployment monitoring plan.
