# Supplementary extension notes

## What changed methodologically

- Noise scaling changed from original test-derived feature SDs to training-derived SDs for the extension only.
- Nonzero noise and missingness conditions changed from one seed to 30 seeds for the extension only.
- Reduced-data conditions changed from one stratified subset to 20 subsets for the extension only.
- Clean uncertainty, calibration, permutation importance, confusion-group SHAP, and failure-mode diagnostics were added only for publication support.

## What did not change

The dataset, original split, six predictors, excluded failure-mode inputs, preprocessing logic, Random Forest parameters, threshold 0.20, clean test set, and original artifacts were preserved.

## Interpretation boundary

Repeated corruption intervals describe Monte Carlo sensitivity of this fixed test set and model. They are not confidence intervals for performance across factories, machine fleets, or future time periods.
