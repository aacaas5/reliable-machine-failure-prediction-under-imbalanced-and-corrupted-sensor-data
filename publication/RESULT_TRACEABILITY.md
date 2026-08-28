# Result traceability

All paper headline numbers are listed below. `Original` means already present in executed notebooks; `Extension` means generated later under `publication/`.

| Paper claim | Value | Original or extension? | Source file | Generating code |
|---|---:|---|---|---|
| Dataset records / failures | 10,000 / 339 | Original, verified | `notebooks/01_data_exploration.ipynb`; `publication/results/baseline_verification/split_distribution.csv` | original notebook; publication analysis split |
| Split sizes | 7000/1500/1500 | Original, verified | `notebooks/02_baseline_models.ipynb`; split CSV | original cell 4; publication script |
| Threshold | 0.20 | Original | `notebooks/02_baseline_models.ipynb` cells 22--26 | original threshold grid |
| Formal recall-constrained threshold | 0.20 | Extension | `publication/results/baseline_verification/threshold_analysis.csv` | publication script |
| Clean accuracy | 0.9727 | Original, exactly reproduced | `publication/results/baseline_verification/clean_test_metrics.csv` | publication script |
| Clean precision | 0.5676 | Original, exactly reproduced | same | publication script |
| Clean recall | 0.8235 | Original, exactly reproduced | same | publication script |
| Clean F1 | 0.6720 | Original, exactly reproduced | same | publication script |
| Clean AP | 0.7803 | Original, exactly reproduced | same | publication script |
| Clean confusion matrix | TN 1417, FP 32, FN 9, TP 42 | Original, exactly reproduced | same | publication script assertion |
| Precision 95% interval | 0.4824--0.6667 | Extension | `publication/results/confidence_intervals/clean_test_intervals.csv` | 5,000 stratified bootstrap |
| Recall 95% interval | 0.6975--0.9043 | Extension | same | Wilson interval |
| F1 95% interval | 0.5891--0.7563 | Extension | same | 5,000 stratified bootstrap |
| AP 95% interval | 0.6816--0.8717 | Extension | same | 5,000 stratified bootstrap |
| Original 30% noise recall / AP | 0.6667 / 0.5417 | Original | `notebooks/03_robustness_experiments.ipynb` cell 26 | original single seed, test-derived scale |
| Repeated 30% noise mean precision | 0.3129 (SD 0.0261) | Extension | `publication/results/repeated_experiments/sensor_noise_summary.csv` | 30 seeds, training-derived scale |
| Repeated 30% noise mean recall | 0.6791 (SD 0.0493) | Extension | same | publication script |
| Repeated 30% noise mean F1 | 0.4282 (SD 0.0326) | Extension | same | publication script |
| Repeated 30% noise mean AP | 0.4596 (SD 0.0540) | Extension | same | publication script |
| Original 30% missing recall / accuracy | 0.5098 / 0.9687 | Original | `notebooks/03_robustness_experiments.ipynb` cell 40 | original single seed |
| Repeated 30% missing mean recall | 0.5229 (SD 0.0528) | Extension | `publication/results/repeated_experiments/missing_data_summary.csv` | 30 MCAR-style seeds |
| Repeated 30% missing mean accuracy | 0.9703 (SD 0.0031) | Extension | same | publication script |
| Repeated 30% missing mean AP | 0.4918 (SD 0.0596) | Extension | same | publication script |
| Original 20% labels recall / AP | 0.6667 / 0.6546 | Original | `notebooks/03_robustness_experiments.ipynb` cell 47 | original one subset |
| Repeated 20% labels mean recall | 0.6510 (SD 0.0799) | Extension | `publication/results/repeated_experiments/label_scarcity_summary.csv` | 20 stratified seeds |
| Repeated 20% labels mean AP | 0.5854 (SD 0.0584) | Extension | same | publication script |
| Brier score | 0.01542 | Extension | `publication/results/calibration/reliability_data.csv` | publication script |
| Torque impurity importance | 0.3245 | Original | `notebooks/04_explainability.ipynb` cell 8 | original forest |
| Torque AP permutation decrease | 0.5107 | Extension | `publication/results/explainability/permutation_importance.csv` | 30 shuffles |
| TP vs FN mean absolute torque SHAP | 0.2123 vs 0.0237 | Extension | `publication/results/explainability/confusion_group_shap.csv` | publication script |
| Failure-mode diagnostic counts | TWF 2/8; HDF 16/18; PWF 12/13; OSF 15/15; RNF 0/2 detected | Extension | `publication/results/explainability/failure_mode_diagnostics.csv` | post-hoc publication script |

## Reproduction nuance

The original default-threshold validation Random Forest reported 5 false positives and precision 0.8387. Current scikit-learn 1.9.0 reproduction produced 6 false positives and precision 0.8125 while matching AP 0.7349. The paper reports original baseline values and discloses the reproduction difference. The selected-threshold held-out test result reproduces exactly.
