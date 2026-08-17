"""Preprocessing utilities for machine-failure models."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "Air temperature",
    "Process temperature",
    "Rotational speed",
    "Torque",
    "Tool wear"
]

CATEGORICAL_FEATURES = [
    "Type"
]


def create_preprocessor(scale_numeric=True):
    """Create preprocessing for numerical and categorical features."""

    # Replace missing numerical values using training medians
    numeric_steps = [
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]

    # Logistic Regression needs scaling
    if scale_numeric:
        numeric_steps.append(
            (
                "scaler",
                StandardScaler()
            )
        )

    numeric_pipeline = Pipeline(
        steps=numeric_steps
    )

    # Replace missing Type values and convert L/M/H into numbers
    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            )
        ]
    )

    # Apply the correct processing to each feature group
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            )
        ]
    )

    return preprocessor