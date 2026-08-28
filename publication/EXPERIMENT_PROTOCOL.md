# Experiment protocol

## Invariants inherited from original research

- Dataset: UCI AI4I 2020, fetched with `ucimlrepo` id 601.
- Features: Type, Air temperature, Process temperature, Rotational speed, Torque, Tool wear.
- Excluded from inputs: Machine failure, TWF, HDF, PWF, OSF, RNF.
- Split: 70% training, then the remaining 30% split equally into validation/test; both calls stratified with seed 42.
- Preprocessing: training-median numerical imputation and one-hot machine type; no scaling for the Random Forest.
- Primary model: unweighted 300-tree Random Forest, model seed 42, `n_jobs=-1`.
- Operating threshold: 0.20, selected using validation data and never optimized on test data.
- Metrics: Accuracy, Precision, Recall, F1, and Average Precision (AP).

## Original research procedures

### Sensor noise

For each numerical feature, the notebook computes standard deviation from the test feature itself, sets noise SD to severity times that SD, and draws Gaussian noise using `default_rng(42)`. Severities are 0, 5, 10, 20, and 30%. Each severity is one realization.

### Missing measurements

For each severity, `default_rng(42)` generates an independent cell mask over the five numerical test features. Masked cells are filled with training medians. The notebook calls this random missing sensor data. The publication paper uses the more precise phrase MCAR-style synthetic missingness.

### Label scarcity

For fractions 20, 40, 60, and 80%, one stratified subset is selected with seed 42. A fresh preprocessor and preserved forest are fitted. The clean test set and threshold remain fixed.

## Publication extension experiments

### Baseline verification

Reconstruct the original split/model and assert TN=1417, FP=32, FN=9, TP=42 at threshold 0.20. Re-run validation baselines at threshold 0.50. Record any environment sensitivity rather than overwriting notebook values.

### Threshold consistency

Reconstruct the original grid 0.05--0.50. Supplementary formal rule: maximize validation precision subject to validation recall >= 0.80. This selects 0.20. The test set is not queried for selection.

### Clean uncertainty

- Recall: Wilson 95% score interval on 42 successes among 51 failures.
- Precision, F1, AP: 5,000-replicate stratified percentile bootstrap with seed 2026, separately resampling positive and negative test records.

### Repeated Gaussian noise

Use training-feature standard deviations, severities 0/5/10/20/30%, and seeds 100--129 for every nonzero level. The clean point is deterministic. Report replicate records and mean, SD, and 95% interval for the mean.

### Repeated missingness

Use independent Bernoulli cell masks at 0/5/10/20/30%, seeds 100--129 for nonzero levels, and training-median imputation. Label the mechanism MCAR-style synthetic. Report realized cell counts.

### Repeated label scarcity

Use 20 stratified subsets (seeds 200--219) for 20/40/60/80%. Fit preprocessing within each subset and retrain the exact forest. Full data is deterministic and reported once.

### Calibration and explainability

Compute Brier score and a 10-quantile reliability diagram for unchanged scores. Do not recalibrate or change threshold. Compute 30-repeat AP permutation importance and aggregate absolute SHAP values by TP/FN/FP/TN. Use failure-mode columns only after prediction.

## Output containment

`output_path()` resolves and verifies every output below `publication/`. It rejects `..` traversal. The tests inspect script text for original-directory output patterns. Original tracked hashes are verified before delivery.
