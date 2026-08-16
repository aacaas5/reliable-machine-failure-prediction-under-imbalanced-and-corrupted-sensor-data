"""Utilities for loading the AI4I machine-failure dataset."""

import pandas as pd
from ucimlrepo import fetch_ucirepo


# Valid model-input columns
FEATURE_COLUMNS = [
    "Type",
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear"
]

# Main prediction target
TARGET_COLUMN = "Machine failure"

# Used only for later error analysis
FAILURE_MODE_COLUMNS = [
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF"
]


def load_ai4i_data():
    """Download and return the complete AI4I dataset."""

    dataset = fetch_ucirepo(id=601)

    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()

    data = pd.concat(
        [features, targets],
        axis=1
    )

    return data


def create_model_data(data):
    """Separate valid model inputs from the prediction target."""

    features = data[FEATURE_COLUMNS].copy()
    target = data[TARGET_COLUMN].copy()

    return features, target