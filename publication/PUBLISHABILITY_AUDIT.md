# Publishability audit

## Current strengths

The project has a coherent reliability question, a fixed stratified train/validation/test split, leakage-aware preprocessing, an operating threshold selected on validation data, a genuinely untouched test evaluation, imbalance-aware metrics, controlled robustness experiments, and both global and local explainability. The original notebooks contain executed outputs, and the final report and README agree on the principal results.

## Research question represented by the existing work

**Original research:** How reliably does a machine-failure classifier detect rare failures when sensor measurements are clean, noisy, missing, or supported by less labelled training data, and what learned feature patterns are associated with its decisions?

The strongest paper framing is a controlled robustness study, not a novel Random Forest algorithm and not a claim of industrial deployment.

## Dataset and features

The study uses UCI AI4I 2020: 10,000 synthetic records, 339 failures (3.39%), six predictors, and no naturally missing inputs. Predictors are Type, Air temperature, Process temperature, Rotational speed, Torque, and Tool wear. TWF, HDF, PWF, OSF, and RNF are excluded from predictors and are suitable only for post-hoc diagnostics.

## Current experimental design

The split is 7,000/1,500/1,500 using two stratified `train_test_split` calls with seed 42. Failure counts are 237/51/51. Preprocessing is fitted on training data. Baseline models use validation data. Threshold 0.20 is selected on validation data, fixed, and applied once to the test set.

## Existing baseline models

The original validation notebook evaluates a majority Dummy Classifier, unweighted Logistic Regression, unweighted Random Forest, balanced Logistic Regression, and balanced Random Forest. The core three-model table is Dummy, Logistic Regression, and Random Forest.

## Existing selected model

The selected model is an unweighted `RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)` using median imputation and one-hot encoding. It remains the primary model.

## Existing threshold-selection approach

The original grid spans 0.05 to 0.50 in increments of 0.05. The notebook states that 0.20 was selected as a safety-oriented point giving at least 80% validation recall with a manageable false-positive rate. Threshold 0.40 was retained as the F1-optimal comparison. A new formal check maximizing validation precision subject to recall >= 0.80 independently selects 0.20 on this grid.

## Existing clean-test results

At threshold 0.20: accuracy 0.9727, precision 0.5676, recall 0.8235, F1 0.6720, AP 0.7803, TN 1417, FP 32, FN 9, TP 42. The publication script independently reproduces these values exactly.

## Existing robustness experiments

**Original research:** Each nonzero condition is one seed-42 realization.

- Gaussian-style noise uses the standard deviation of each numerical feature computed from the test set. At 30%: precision 0.3009, recall 0.6667, F1 0.4146, AP 0.5417, accuracy 0.9360.
- Missing numerical cells are selected independently, then filled with training medians. At 30%: precision 0.5417, recall 0.5098, F1 0.5253, AP 0.5432, accuracy 0.9687.
- Reduced labelled data uses one stratified subset at each fraction. At 20%: 1,400 records, 47 failures, precision 0.5152, recall 0.6667, F1 0.5812, AP 0.6546.

## Existing explainability analysis

Impurity importance ranks torque first (0.3245), rotational speed second (0.2372), and tool wear third (0.1671). Global SHAP is present. One true positive at probability 0.94 and one false negative at probability 0.1367 are compared. The wording correctly treats attributions as model associations rather than causes.

## Reproducibility strengths

Fixed seeds, explicit split logic, reusable feature definitions, training-only preprocessing, an untouched test set, executed notebook outputs, and a compiled report are strengths. Publication safeguards now assert the clean confusion matrix and constrain output paths.

## Reproducibility weaknesses

Original notebooks write to paths inferred from the working directory and previously overwrote result CSVs. Most original CSV/figure artifacts referenced by notebook outputs are not tracked in Git, although their values remain embedded in notebook outputs. The dataset is downloaded at run time. The root requirements are very broad and include future-version packages. No serialized split indices, predictions, or model artifact were saved. Under scikit-learn 1.9.0, the selected-threshold clean test reproduces exactly, but the default-threshold validation forest changes by one false positive relative to the notebook.

## Experimental limitations

One synthetic dataset, one primary split, one primary model, artificial corruption, independent cell missingness, no temporal structure, no drift, no correlated sensor failure, no maintenance-cost model, and no prospective deployment.

## Statistical limitations

Only 51 failures are in the test set. Original corruption and scarcity experiments are single runs. Test metrics are point estimates without original uncertainty. Failure-mode groups are extremely small and overlapping. Publication extensions address some Monte Carlo variation but not dataset-to-dataset or site-to-site generalization.

## Publication-writing limitations

The original report has only four references, no explicit original-versus-extension labels, limited statistical uncertainty, and no result provenance table. Its contributions and limitations are directionally sound but too compact for peer review.

## Related-work gaps

The original bibliography lacks predictive-maintenance reviews, imbalanced learning, thresholding, missing-data theory, bootstrap/Wilson uncertainty, calibration, and permutation importance. The new bibliography contains 26 traceable primary or methodological sources.

## Recommended publication extensions

### Original research

Retain the split, six features, model, threshold, clean test, single-seed robustness results, and SHAP examples unchanged.

### Recommended publication extension

Completed: 30-seed leakage-safe noise and MCAR-style missingness, 20-seed stratified scarcity, clean uncertainty intervals, formal threshold consistency, Brier/reliability analysis, permutation importance, confusion-group SHAP, failure-mode diagnostics, claim provenance, and integrity tests.

Still recommended before a strong journal submission: external real-machine datasets; a pre-registered cost model; temporal or grouped validation; realistic correlated faults and drift; additional preserved-protocol model benchmarks; prospective monitoring; and independent replication.
