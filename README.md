# Reliable Machine-Failure Prediction

## Project Overview

This project investigates reliable machine-failure prediction under difficult real-world data conditions.

Machine-learning models will predict whether a machine will fail using operating measurements such as temperature, rotational speed, torque, and tool wear.

## Research Question

How do class imbalance, sensor noise, missing measurements, and limited training data affect machine-learning models used for predictive maintenance?

## Dataset

This project uses the UCI AI4I 2020 Predictive Maintenance Dataset.

## Models

- Dummy Classifier
- Logistic Regression
- Random Forest

## Evaluation Metrics

- Precision
- Recall
- F1-score
- PR-AUC
- Confusion matrix

## Research Experiments

The models will be evaluated under:

- Imbalanced failure data
- Noisy sensor measurements
- Missing sensor values
- Limited training data

## Project Structure

- `data/` — datasets
- `figures/` — generated graphs
- `notebooks/` — Jupyter notebooks
- `reports/` — project reports
- `results/` — experiment results
- `src/` — reusable Python code

## Status

Project setup completed. Dataset exploration is the next stage.