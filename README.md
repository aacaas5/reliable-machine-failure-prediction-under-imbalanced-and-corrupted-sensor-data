# Reliable Machine-Failure Prediction Under Imbalanced and Corrupted Sensor Data

## Research Report

[View the full IEEE-style research report](reports/Reliable_Machine_Failure_Prediction_Report.pdf)

## Key Results

- Clean-test accuracy: **97.27%**
- Clean-test precision: **56.76%**
- Clean-test recall: **82.35%**
- Clean-test F1-score: **67.20%**
- Clean-test Average Precision: **78.03%**
- Recall at 30% sensor noise: **66.67%**
- Recall at 30% missing sensor measurements: **50.98%**
- Recall with only 20% training data: **66.67%**
- Most influential Random Forest feature: **Torque (~32.45%)**
- Selected decision threshold: **0.20**

---

## Project Overview

This project investigates the reliability of machine-failure prediction under realistic data-quality limitations.

Rather than evaluating a predictive-maintenance model only on clean test data, the project examines how the same selected system behaves when:

* sensor measurements become noisy,
* sensor values are missing,
* labelled training data are limited,
* and individual model decisions need to be explained.

The project uses the **UCI AI4I 2020 Predictive Maintenance Dataset** and focuses on failure detection under a strongly imbalanced target distribution.

The final selected system is an **unweighted Random Forest** evaluated using a fixed decision threshold of **0.20**.

---

## Research Question

**How reliable is a machine-failure prediction model when class imbalance, sensor noise, missing measurements, and limited labelled training data are considered, and what feature patterns drive its predictions?**

The project addresses three connected questions:

1. Can the model detect machine failures effectively under clean-data conditions?
2. How does failure-detection reliability change under imperfect sensor and training conditions?
3. Which features influence the model's decisions, and why are some failures detected while others are missed?

---

## Dataset

The project uses the **AI4I 2020 Predictive Maintenance Dataset** from the UCI Machine Learning Repository.

The model uses six original input variables:

* Machine type
* Air temperature
* Process temperature
* Rotational speed
* Torque
* Tool wear

The target variable represents:

* `0` — No machine failure
* `1` — Machine failure

Because failures represent only a small proportion of the dataset, evaluation focuses on metrics that are informative under class imbalance.

---

## Models Evaluated

The baseline modelling stage compared:

* Dummy Classifier
* Logistic Regression
* Random Forest

The final selected model was an **unweighted Random Forest** configured with:

```python
RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)
```

A validation-selected decision threshold of **0.20** was fixed and used consistently throughout the final evaluation, robustness experiments, and explainability analysis.

---

## Evaluation Metrics

Because machine failures are rare, accuracy alone is not sufficient.

The project therefore evaluates:

* Accuracy
* Precision
* Recall
* F1-score
* Average Precision
* Confusion matrix

**Recall is particularly important** because it measures how many actual machine failures are successfully detected.

---

## Clean-Data Performance

The selected Random Forest achieved the following performance on the clean test set:

| Metric             | Result |
| ------------------ | -----: |
| Accuracy           | 97.27% |
| Precision          | 56.76% |
| Recall             | 82.35% |
| F1-score           | 67.20% |
| Average Precision  | 78.03% |
| Decision threshold |   0.20 |

The clean confusion matrix was:

```text
[[1417   32]
 [   9   42]]
```

Out of **51 actual machine failures**, the model:

* correctly detected **42 failures**,
* missed **9 failures**.

The high overall accuracy is partly influenced by the strong class imbalance, making recall and Average Precision more useful indicators of actual failure-detection performance.

---

## Robustness Experiments

The same selected system was evaluated under three challenging conditions.

### 1. Sensor Noise

Gaussian-style measurement noise was introduced relative to the natural scale of each numerical sensor variable.

Noise levels tested:

* 0%
* 5%
* 10%
* 20%
* 30%

At **30% sensor noise**:

| Metric            |  Clean | 30% Noise |
| ----------------- | -----: | --------: |
| Precision         | 56.76% |    30.09% |
| Recall            | 82.35% |    66.67% |
| F1-score          | 67.20% |    41.46% |
| Average Precision | 78.03% |    54.17% |
| Accuracy          | 97.27% |   ~93.60% |

The results show substantial deterioration in failure-detection reliability as sensor noise becomes more severe.

---

### 2. Missing Sensor Measurements

Random numerical sensor measurements were replaced with missing values.

Median imputation was calculated using **training data only** and then applied to corrupted test data to avoid data leakage.

At **30% missing sensor measurements**:

* Recall decreased from **82.35% to 50.98%**
* Accuracy remained approximately **96.87%**

This demonstrates why accuracy alone can be misleading in imbalanced failure-detection problems.

Among the severe corruption conditions tested, **missing measurements produced the strongest reduction in failure recall**.

---

### 3. Limited Training Data

The Random Forest was retrained using reduced stratified fractions of the original training data.

Training fractions:

* 20%
* 40%
* 60%
* 80%
* 100%

Average Precision improved as more labelled data became available:

| Training Data | Average Precision |
| ------------- | ----------------: |
| 20%           |            65.46% |
| 40%           |            69.78% |
| 60%           |            74.84% |
| 80%           |            77.81% |
| 100%          |            78.03% |

At only **20% of the training data**, recall was approximately **66.67%**, compared with **82.35%** when using the full training set.

---

## Robustness Summary

Representative recall values were:

| Condition                | Recall |
| ------------------------ | -----: |
| Clean data               | 82.35% |
| 30% sensor noise         | 66.67% |
| 30% missing measurements | 50.98% |
| 20% training data        | 66.67% |

The experiments demonstrate that strong clean-data performance does not guarantee equally reliable behaviour under imperfect operating conditions.

---

## Model Explainability

Two complementary explainability approaches were used:

### Random Forest Feature Importance

Impurity-based feature importance identified **torque** as the most influential feature overall, accounting for approximately **32.45%** of the model's total feature importance.

Rotational speed and tool wear were also influential, while machine-type features contributed relatively little.

Feature importance describes how strongly the model uses a feature and should not be interpreted as physical causation.

---

### SHAP Analysis

SHAP analysis was used to understand both global model behaviour and individual predictions.

Globally, the most influential variables included:

* Rotational speed
* Torque
* Tool wear
* Temperature measurements

Machine-type variables generally produced much smaller SHAP effects.

---

## Correctly Detected Failure

A correctly detected failed machine received:

```text
Actual class: 1
Predicted failure probability: 0.94
Predicted class: 1
```

Its strongest SHAP contributions were:

| Feature          |    Value |    SHAP |
| ---------------- | -------: | ------: |
| Rotational speed | 2737 rpm | +0.5036 |
| Torque           |      8.8 | +0.3625 |

These two features dominated the high-confidence failure prediction.

---

## Missed Failure

A false-negative example received:

```text
Actual class: 1
Predicted failure probability: 0.1367
Predicted class: 0
```

Important SHAP contributions included:

| Feature             |    Value |    SHAP |
| ------------------- | -------: | ------: |
| Rotational speed    | 1371 rpm | +0.0910 |
| Air temperature     |  303.6 K | +0.0906 |
| Process temperature |  312.2 K | -0.0684 |
| Tool wear           |      112 | -0.0206 |
| Torque              |     54.6 | +0.0143 |

The missed failure contained weaker and partly conflicting model evidence, preventing the predicted probability from crossing the fixed **0.20 threshold**.

---

## Main Findings

The project supports three main conclusions:

1. **Strong clean-data performance does not guarantee robustness under realistic data imperfections.**
2. **Missing sensor information can substantially reduce failure-detection recall even when overall accuracy remains high.**
3. **Explainability helps reveal why some failures are detected confidently while others are missed.**

The experiments also demonstrate why predictive-maintenance models should not be evaluated using accuracy alone.

A more reliable assessment requires:

* class-imbalance-aware metrics,
* robustness testing,
* consistent decision thresholds,
* analysis of missed failures,
* and model explainability.

---

## Project Structure

```text
reliable-machine-failure-prediction/
│
├── data/
│   └── dataset files
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_baseline_models.ipynb
│   ├── 03_robustness_experiments.ipynb
│   ├── 04_explainability.ipynb
│   └── 05_final_research_interpretation.ipynb
│
├── src/
│   └── reusable preprocessing and project utilities
│
├── results/
│   ├── robustness result CSV files
│   ├── SHAP explanation tables
│   └── comparison outputs
│
├── figures/
│   └── generated plots and explainability figures
│
├── reports/
│   └── project documentation
│
├── requirements.txt
└── README.md
```

---

## Reproducibility

The project uses a fixed:

```python
random_state = 42
```

to maintain reproducible data splits, random sampling, model training, and corruption experiments.

Preprocessing is fitted using training data only and then applied to validation, clean test, and corrupted test data to avoid data leakage.

---

## Limitations

The study has several limitations:

* evaluation is based on one benchmark dataset,
* sensor corruption is simulated rather than collected from real industrial sensor faults,
* reduced-training-data experiments use individual stratified subsets,
* one selected Random Forest is the primary system studied in depth,
* SHAP and feature importance explain learned model associations rather than physical causation.

---

## Future Work

Possible extensions include:

* testing additional predictive-maintenance datasets,
* simulating persistent sensor drift and complete sensor dropout,
* comparing advanced missing-data strategies,
* repeating reduced-data experiments across multiple random subsets,
* evaluating gradient-boosted trees and neural models,
* probability calibration and uncertainty estimation,
* cost-sensitive learning,
* threshold optimization for different maintenance priorities,
* broader SHAP analysis across false positives, false negatives, true positives, and true negatives.

---

## Conclusion

This project demonstrates that machine-failure prediction should be evaluated as a **reliability problem**, not simply as a classification problem.

The selected Random Forest performed strongly under clean conditions but became less reliable when sensor measurements were noisy, unavailable, or labelled training data were limited.

Explainability analysis further demonstrated that different combinations of operating measurements can lead to confident failure detection or missed failures.

The central result is therefore:

> **A predictive-maintenance model should not be considered reliable simply because it achieves high clean-data accuracy. Reliability also depends on failure recall, robustness to imperfect data, and an understanding of the model's decision-making behaviour.**
