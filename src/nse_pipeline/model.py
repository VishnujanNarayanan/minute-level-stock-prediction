"""Train the direction classifier, and choose a confidence cutoff.

The point of the threshold is not accuracy. A model that is right 51% of the
time on every minute is useless; one that is right 60% of the time on the few
minutes it is confident about can be traded. So the model is scored on
precision at a cutoff, and always against the base rate -- the share of minutes
that rise anyway -- because precision below the base rate is worse than buying
at random.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score, roc_auc_score

DEFAULT_THRESHOLDS = (0.50, 0.55, 0.60, 0.63, 0.65, 0.70)


def train(x_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> RandomForestClassifier:
    """Fit the forest. Seeded, so the reported numbers can be reproduced."""
    params = {"n_estimators": 100, "random_state": 42, "n_jobs": -1}
    params.update(kwargs)
    model = RandomForestClassifier(**params)
    model.fit(x_train, y_train)
    return model


def evaluate_at(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict:
    """Precision, recall and trade count at one cutoff, beside the base rate."""
    predictions = (probabilities >= threshold).astype(int)
    base_rate = float(np.mean(y_true))
    precision = float(precision_score(y_true, predictions, zero_division=0))
    return {
        "threshold": float(threshold),
        "trades": int(predictions.sum()),
        "precision": precision,
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "base_rate": base_rate,
        "edge_over_base": precision - base_rate if predictions.sum() else 0.0,
    }


def threshold_sweep(y_true: pd.Series, probabilities: np.ndarray,
                    thresholds=DEFAULT_THRESHOLDS) -> pd.DataFrame:
    """Every cutoff at once -- the precision/volume trade-off, in one table.

    Raising the cutoff buys precision with trade count. Past some point the
    remaining sample is too small for the precision to mean anything, which the
    ``trades`` column is there to make visible.
    """
    return pd.DataFrame([evaluate_at(y_true, probabilities, t) for t in thresholds])


def summarise(y_true: pd.Series, probabilities: np.ndarray, threshold: float) -> dict:
    """Everything worth reporting about one model at one cutoff."""
    out = evaluate_at(y_true, probabilities, threshold)
    predictions = (probabilities >= threshold).astype(int)
    out["roc_auc"] = float(roc_auc_score(y_true, probabilities))
    out["confusion_matrix"] = confusion_matrix(y_true, predictions).tolist()
    return out
