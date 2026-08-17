"""Evaluation utilities for binary failure classifiers."""

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    average_precision_score,
    confusion_matrix
)


def evaluate_classifier(model, features, target):
    """Evaluate a trained binary classifier."""

    # Produce final class decisions
    predictions = model.predict(features)

    # Obtain class-1 failure probabilities
    probabilities = model.predict_proba(features)[:, 1]

    # Calculate evaluation metrics
    metrics = {
        "Accuracy": accuracy_score(
            target,
            predictions
        ),
        "Precision": precision_score(
            target,
            predictions,
            zero_division=0
        ),
        "Recall": recall_score(
            target,
            predictions
        ),
        "F1-score": f1_score(
            target,
            predictions
        ),
        "Average precision": average_precision_score(
            target,
            probabilities
        )
    }

    matrix = confusion_matrix(
        target,
        predictions
    )

    return metrics, matrix, predictions, probabilities