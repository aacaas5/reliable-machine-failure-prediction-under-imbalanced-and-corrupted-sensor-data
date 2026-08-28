"""Run publication-only verification and extension analyses.

All writes are constrained to the repository's publication/ directory. The
original notebooks, source, results, figures, reports, README, and requirements
are read-only inputs and are never modified.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


SCRIPT_PATH = Path(__file__).resolve()
PUBLICATION_ROOT = SCRIPT_PATH.parents[1]
PROJECT_ROOT = PUBLICATION_ROOT.parent
ORIGINAL_SOURCE = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import (  # noqa: E402
    FAILURE_MODE_COLUMNS,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_ai4i_data,
    create_model_data,
)
from src.preprocessing import create_preprocessor  # noqa: E402


RANDOM_STATE = 42
THRESHOLD = 0.20
NUMERIC_FEATURES = [
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear",
]
SEVERITIES = [0.00, 0.05, 0.10, 0.20, 0.30]
CORRUPTION_SEEDS = list(range(100, 130))
SCARCITY_SEEDS = list(range(200, 220))
BOOTSTRAP_SEED = 2026
BOOTSTRAP_REPLICATES = 5000

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def output_path(relative: str) -> Path:
    """Return a safe output path that must remain below publication/."""
    candidate = (PUBLICATION_ROOT / relative).resolve()
    candidate.relative_to(PUBLICATION_ROOT.resolve())
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


def save_frame(frame: pd.DataFrame, relative: str, index: bool = False) -> None:
    frame.to_csv(output_path(relative), index=index)


def metrics(
    y_true: pd.Series | np.ndarray,
    probabilities: np.ndarray,
    threshold: float = THRESHOLD,
) -> dict:
    predictions = (probabilities >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, predictions),
        "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "average_precision": average_precision_score(y_true, probabilities),
        "tn": int(confusion_matrix(y_true, predictions).ravel()[0]),
        "fp": int(confusion_matrix(y_true, predictions).ravel()[1]),
        "fn": int(confusion_matrix(y_true, predictions).ravel()[2]),
        "tp": int(confusion_matrix(y_true, predictions).ravel()[3]),
    }


def wilson_interval(successes: int, total: int, alpha: float = 0.05) -> tuple[float, float]:
    z = norm.ppf(1 - alpha / 2)
    p = successes / total
    denominator = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denominator
    half = z * np.sqrt((p * (1 - p) / total) + z**2 / (4 * total**2)) / denominator
    return centre - half, centre + half


def stratified_bootstrap_intervals(
    y_true: np.ndarray, probabilities: np.ndarray
) -> pd.DataFrame:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    positive = np.flatnonzero(y_true == 1)
    negative = np.flatnonzero(y_true == 0)
    records = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = np.concatenate(
            [rng.choice(positive, len(positive), replace=True),
             rng.choice(negative, len(negative), replace=True)]
        )
        rng.shuffle(sample)
        result = metrics(y_true[sample], probabilities[sample])
        records.append({key: result[key] for key in ("precision", "f1", "average_precision")})
    boot = pd.DataFrame(records)
    rows = []
    point = metrics(y_true, probabilities)
    for metric_name in boot.columns:
        low, high = np.percentile(boot[metric_name], [2.5, 97.5])
        rows.append({"metric": metric_name, "estimate": point[metric_name],
                     "lower_95": low, "upper_95": high,
                     "method": f"stratified percentile bootstrap, B={BOOTSTRAP_REPLICATES}"})
    recall_low, recall_high = wilson_interval(point["tp"], point["tp"] + point["fn"])
    rows.append({"metric": "recall", "estimate": point["recall"],
                 "lower_95": recall_low, "upper_95": recall_high,
                 "method": "Wilson score interval"})
    return pd.DataFrame(rows)


def summarize_repeats(frame: pd.DataFrame, condition: str) -> pd.DataFrame:
    metric_columns = ["accuracy", "precision", "recall", "f1", "average_precision"]
    grouped = frame.groupby(condition)[metric_columns]
    summary = grouped.agg(["mean", "std", "count"])
    rows = []
    for value in summary.index:
        for metric_name in metric_columns:
            mean = summary.loc[value, (metric_name, "mean")]
            std = summary.loc[value, (metric_name, "std")]
            count = summary.loc[value, (metric_name, "count")]
            if np.isnan(std):
                std = 0.0
            half = 1.96 * std / np.sqrt(count) if count else np.nan
            rows.append({condition: value, "metric": metric_name, "mean": mean,
                         "std": std, "lower_95": mean - half, "upper_95": mean + half,
                         "n": int(count)})
    return pd.DataFrame(rows)


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(output_path(f"figures/{stem}.pdf"), bbox_inches="tight")
    fig.savefig(output_path(f"figures/{stem}.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    data = load_ai4i_data()
    X, y = create_model_data(data)
    assert list(X.columns) == FEATURE_COLUMNS
    assert TARGET_COLUMN not in X.columns
    assert not set(FAILURE_MODE_COLUMNS).intersection(X.columns)

    X_train, X_temporary, y_train, y_temporary = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y
    )
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temporary, y_temporary, test_size=0.50,
        random_state=RANDOM_STATE, stratify=y_temporary
    )
    split = pd.DataFrame([
        {"partition": "train", "n": len(y_train), "failures": int(y_train.sum())},
        {"partition": "validation", "n": len(y_validation), "failures": int(y_validation.sum())},
        {"partition": "test", "n": len(y_test), "failures": int(y_test.sum())},
    ])
    save_frame(split, "results/baseline_verification/split_distribution.csv")

    tree_preprocessor: ColumnTransformer = create_preprocessor(scale_numeric=False)
    X_train_tree = tree_preprocessor.fit_transform(X_train)
    X_validation_tree = tree_preprocessor.transform(X_validation)
    X_test_tree = tree_preprocessor.transform(X_test)
    forest = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
    forest.fit(X_train_tree, y_train)
    validation_probabilities = forest.predict_proba(X_validation_tree)[:, 1]
    test_probabilities = forest.predict_proba(X_test_tree)[:, 1]

    clean = metrics(y_test, test_probabilities)
    clean["threshold"] = THRESHOLD
    save_frame(pd.DataFrame([clean]), "results/baseline_verification/clean_test_metrics.csv")
    expected = {"tn": 1417, "fp": 32, "fn": 9, "tp": 42}
    assert all(clean[k] == v for k, v in expected.items()), clean

    # Reproduce validation baselines without changing the original notebook.
    linear = create_preprocessor(scale_numeric=True)
    X_train_linear = linear.fit_transform(X_train)
    X_validation_linear = linear.transform(X_validation)
    baseline_records = []
    for name, model, train_matrix, validation_matrix in [
        ("Dummy Classifier", DummyClassifier(strategy="most_frequent", random_state=42),
         X_train_linear, X_validation_linear),
        ("Logistic Regression", LogisticRegression(max_iter=1000, random_state=42),
         X_train_linear, X_validation_linear),
        ("Random Forest", forest, X_train_tree, X_validation_tree),
    ]:
        if name != "Random Forest":
            model.fit(train_matrix, y_train)
        probabilities = model.predict_proba(validation_matrix)[:, 1]
        result = metrics(y_validation, probabilities, threshold=0.5)
        result.update({"model": name, "decision_threshold": 0.5})
        baseline_records.append(result)
    save_frame(pd.DataFrame(baseline_records), "results/baseline_verification/validation_baselines.csv")

    # Exact original threshold grid plus a formal constrained rule.
    threshold_records = []
    for threshold in np.arange(0.05, 0.55, 0.05):
        predictions = (validation_probabilities >= threshold).astype(int)
        threshold_records.append({
            "threshold": threshold,
            "precision": precision_score(y_validation, predictions, zero_division=0),
            "recall": recall_score(y_validation, predictions),
            "f1": f1_score(y_validation, predictions),
            "false_positives": int(confusion_matrix(y_validation, predictions).ravel()[1]),
            "false_negatives": int(confusion_matrix(y_validation, predictions).ravel()[2]),
        })
    threshold_frame = pd.DataFrame(threshold_records)
    eligible = threshold_frame[threshold_frame["recall"] >= 0.80]
    formal_threshold = float(eligible.sort_values(["precision", "threshold"], ascending=False).iloc[0]["threshold"])
    threshold_frame["original_selected"] = np.isclose(threshold_frame["threshold"], THRESHOLD)
    threshold_frame["formal_recall_constrained_selected"] = np.isclose(threshold_frame["threshold"], formal_threshold)
    save_frame(threshold_frame, "results/baseline_verification/threshold_analysis.csv")

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for column, label in [("precision", "Precision"), ("recall", "Recall"), ("f1", "F1")]:
        ax.plot(threshold_frame["threshold"], threshold_frame[column], marker="o", label=label)
    ax.axvline(THRESHOLD, color="#b22222", linestyle="--", label="Selected threshold 0.20")
    ax.set(xlabel="Validation decision threshold", ylabel="Score", ylim=(0, 1))
    ax.grid(alpha=0.25); ax.legend(frameon=False, ncol=2)
    save_figure(fig, "validation_threshold_tradeoff")

    intervals = stratified_bootstrap_intervals(y_test.to_numpy(), test_probabilities)
    save_frame(intervals, "results/confidence_intervals/clean_test_intervals.csv")

    # Repeated leakage-safe Gaussian sensor-noise analysis (training-derived scale).
    train_std = X_train[NUMERIC_FEATURES].std()
    noise_records = []
    for severity in SEVERITIES:
        seeds = [RANDOM_STATE] if severity == 0 else CORRUPTION_SEEDS
        for seed in seeds:
            corrupted = X_test.copy()
            rng = np.random.default_rng(seed)
            for feature in NUMERIC_FEATURES:
                corrupted[feature] = corrupted[feature] + rng.normal(
                    0, severity * train_std[feature], len(corrupted)
                )
            result = metrics(y_test, forest.predict_proba(tree_preprocessor.transform(corrupted))[:, 1])
            result.update({"severity": severity, "seed": seed, "scale_source": "training standard deviation"})
            noise_records.append(result)
    noise = pd.DataFrame(noise_records)
    noise_summary = summarize_repeats(noise, "severity")
    save_frame(noise, "results/repeated_experiments/sensor_noise_replicates.csv")
    save_frame(noise_summary, "results/repeated_experiments/sensor_noise_summary.csv")

    # Repeated MCAR-style synthetic missingness with training-median imputation.
    medians = X_train[NUMERIC_FEATURES].median()
    missing_records = []
    for severity in SEVERITIES:
        seeds = [RANDOM_STATE] if severity == 0 else CORRUPTION_SEEDS
        for seed in seeds:
            corrupted = X_test.copy()
            corrupted[NUMERIC_FEATURES] = corrupted[NUMERIC_FEATURES].astype(float)
            rng = np.random.default_rng(seed)
            mask = rng.random((len(corrupted), len(NUMERIC_FEATURES))) < severity
            corrupted[NUMERIC_FEATURES] = corrupted[NUMERIC_FEATURES].mask(mask).fillna(medians)
            result = metrics(y_test, forest.predict_proba(tree_preprocessor.transform(corrupted))[:, 1])
            result.update({"severity": severity, "seed": seed,
                           "missing_cells": int(mask.sum()), "mechanism": "MCAR-style synthetic"})
            missing_records.append(result)
    missing = pd.DataFrame(missing_records)
    missing_summary = summarize_repeats(missing, "severity")
    save_frame(missing, "results/repeated_experiments/missing_data_replicates.csv")
    save_frame(missing_summary, "results/repeated_experiments/missing_data_summary.csv")

    # Repeated stratified labelled-data scarcity analysis.
    scarcity_records = []
    for fraction in [0.20, 0.40, 0.60, 0.80, 1.00]:
        seeds = SCARCITY_SEEDS if fraction < 1 else [RANDOM_STATE]
        for seed in seeds:
            if fraction == 1:
                X_subset, y_subset = X_train.copy(), y_train.copy()
            else:
                X_subset, _, y_subset, _ = train_test_split(
                    X_train, y_train, train_size=fraction, stratify=y_train, random_state=seed
                )
            preprocessor = create_preprocessor(scale_numeric=False)
            subset_train = preprocessor.fit_transform(X_subset)
            subset_test = preprocessor.transform(X_test)
            model = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1)
            model.fit(subset_train, y_subset)
            result = metrics(y_test, model.predict_proba(subset_test)[:, 1])
            result.update({"training_fraction": fraction, "seed": seed,
                           "training_size": len(y_subset), "training_failures": int(y_subset.sum())})
            scarcity_records.append(result)
    scarcity = pd.DataFrame(scarcity_records)
    scarcity_summary = summarize_repeats(scarcity, "training_fraction")
    save_frame(scarcity, "results/repeated_experiments/label_scarcity_replicates.csv")
    save_frame(scarcity_summary, "results/repeated_experiments/label_scarcity_summary.csv")

    def robustness_plot(summary: pd.DataFrame, condition: str, xlabel: str, stem: str) -> None:
        fig, ax = plt.subplots(figsize=(6.8, 4.2))
        for metric_name, label, color in [
            ("recall", "Recall", "#b22222"), ("average_precision", "Average Precision", "#1f77b4")
        ]:
            part = summary[summary["metric"] == metric_name]
            x = part[condition].to_numpy() * 100
            ax.plot(x, part["mean"], marker="o", label=label, color=color)
            ax.fill_between(x, part["lower_95"], part["upper_95"], alpha=0.18, color=color)
        ax.set(xlabel=xlabel, ylabel="Score", ylim=(0, 1))
        ax.grid(alpha=0.25); ax.legend(frameon=False)
        save_figure(fig, stem)

    robustness_plot(noise_summary, "severity", "Gaussian noise severity (%)", "repeated_sensor_noise")
    robustness_plot(missing_summary, "severity", "Missing sensor cells (%)", "repeated_missing_data")
    robustness_plot(scarcity_summary, "training_fraction", "Labelled training data used (%)", "repeated_label_scarcity")

    # Calibration evidence for the unchanged original classifier.
    prob_true, prob_pred = calibration_curve(y_test, test_probabilities, n_bins=10, strategy="quantile")
    calibration = pd.DataFrame({"mean_predicted_probability": prob_pred, "observed_failure_rate": prob_true})
    calibration["brier_score"] = brier_score_loss(y_test, test_probabilities)
    save_frame(calibration, "results/calibration/reliability_data.csv")
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot([0, 1], [0, 1], color="0.5", linestyle="--", label="Ideal")
    ax.plot(prob_pred, prob_true, marker="o", color="#1f77b4", label="Random Forest")
    ax.set(xlabel="Mean predicted probability", ylabel="Observed failure frequency", xlim=(0, 1), ylim=(0, 1))
    ax.grid(alpha=0.25); ax.legend(frameon=False)
    save_figure(fig, "reliability_diagram")

    # Precision-recall curve for the held-out test scores (no threshold selection).
    pr_precision, pr_recall, pr_threshold = precision_recall_curve(y_test, test_probabilities)
    pr_frame = pd.DataFrame({"recall": pr_recall, "precision": pr_precision,
                             "threshold": np.append(pr_threshold, np.nan)})
    save_frame(pr_frame, "results/baseline_verification/test_precision_recall_curve.csv")
    fig, ax = plt.subplots(figsize=(5.8, 4.4))
    ax.step(pr_recall, pr_precision, where="post", color="#1f77b4")
    ax.axhline(y_test.mean(), color="0.5", linestyle="--", label=f"Prevalence = {y_test.mean():.3f}")
    ax.set(xlabel="Recall", ylabel="Precision", xlim=(0, 1), ylim=(0, 1))
    ax.grid(alpha=0.25); ax.legend(frameon=False)
    save_figure(fig, "test_precision_recall_curve")

    # Post-hoc failure-mode diagnostics; modes never enter model inputs.
    predictions = (test_probabilities >= THRESHOLD).astype(int)
    mode_rows = []
    for mode in FAILURE_MODE_COLUMNS:
        mode_values = data.loc[y_test.index, mode].to_numpy()
        count = int(mode_values.sum())
        detected = int(((mode_values == 1) & (predictions == 1)).sum())
        mode_rows.append({"failure_mode": mode, "occurrences": count, "detected": detected,
                          "missed": count - detected, "mechanism_recall": detected / count if count else np.nan})
    save_frame(pd.DataFrame(mode_rows), "results/explainability/failure_mode_diagnostics.csv")

    # Publication-extension permutation importance and confusion-group SHAP.
    perm = permutation_importance(
        forest, X_test_tree, y_test, scoring="average_precision", n_repeats=30,
        random_state=RANDOM_STATE, n_jobs=-1
    )
    transformed_names = tree_preprocessor.get_feature_names_out()
    perm_frame = pd.DataFrame({"feature": transformed_names,
                               "ap_decrease_mean": perm.importances_mean,
                               "ap_decrease_std": perm.importances_std}).sort_values(
        "ap_decrease_mean", ascending=False
    )
    save_frame(perm_frame, "results/explainability/permutation_importance.csv")

    try:
        import shap
        explainer = shap.TreeExplainer(forest)
        values = explainer.shap_values(X_test_tree)
        failure_values = values[:, :, 1] if isinstance(values, np.ndarray) and values.ndim == 3 else values[1]
        groups = np.select(
            [(y_test.to_numpy() == 1) & (predictions == 1),
             (y_test.to_numpy() == 1) & (predictions == 0),
             (y_test.to_numpy() == 0) & (predictions == 1)],
            ["TP", "FN", "FP"], default="TN"
        )
        shap_rows = []
        for group in ["TP", "FN", "FP", "TN"]:
            mask = groups == group
            means = np.abs(failure_values[mask]).mean(axis=0)
            for feature, value in zip(transformed_names, means):
                shap_rows.append({"confusion_group": group, "n": int(mask.sum()),
                                  "feature": feature, "mean_absolute_shap": value})
        save_frame(pd.DataFrame(shap_rows), "results/explainability/confusion_group_shap.csv")
    except ImportError:
        output_path("results/explainability/SHAP_NOT_RUN.txt").write_text(
            "SHAP package unavailable; original SHAP artifacts remain preserved.\n", encoding="utf-8"
        )

    provenance = {
        "analysis_type": "Publication extension experiment",
        "original_files_modified": False,
        "random_forest": {"n_estimators": 300, "random_state": 42, "class_weight": None},
        "original_threshold": THRESHOLD,
        "corruption_seeds": CORRUPTION_SEEDS,
        "scarcity_seeds": SCARCITY_SEEDS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "feature_columns": FEATURE_COLUMNS,
        "excluded_failure_mode_columns": FAILURE_MODE_COLUMNS,
        "formal_recall_constrained_threshold": formal_threshold,
        "notes": [
            "Original sensor noise used test-set feature standard deviations; extension uses training-set standard deviations.",
            "Original robustness experiments used one fixed seed; extensions repeat nonzero corruption conditions over 30 seeds.",
            "All output paths are constrained below publication/.",
        ],
    }
    output_path("results/run_metadata.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps({"clean": clean, "formal_threshold": formal_threshold,
                      "brier_score": brier_score_loss(y_test, test_probabilities)}, indent=2))


if __name__ == "__main__":
    main()
