import numpy as np
import pandas as pd
import pytest

from nse_pipeline.model import DEFAULT_THRESHOLDS, evaluate_at, summarise, threshold_sweep, train


@pytest.fixture
def probabilities():
    """Confident-and-right at the top, confident-and-wrong in the middle."""
    y = pd.Series([1] * 10 + [0] * 10)
    p = np.concatenate([np.linspace(0.95, 0.60, 10), np.linspace(0.58, 0.05, 10)])
    return y, p


def test_a_higher_cutoff_trades_less(probabilities):
    y, p = probabilities
    sweep = threshold_sweep(y, p)
    assert sweep["trades"].is_monotonic_decreasing
    assert sweep["threshold"].tolist() == list(DEFAULT_THRESHOLDS)


def test_precision_is_always_reported_beside_the_base_rate(probabilities):
    y, p = probabilities
    row = evaluate_at(y, p, 0.7)
    assert row["base_rate"] == 0.5
    assert row["edge_over_base"] == row["precision"] - row["base_rate"]


def test_a_cutoff_that_fires_on_nothing_claims_no_edge(probabilities):
    y, p = probabilities
    row = evaluate_at(y, p, 0.999)
    assert row["trades"] == 0
    assert row["edge_over_base"] == 0.0        # not a spurious 100% precision


def test_a_perfectly_separating_model_scores_perfectly(probabilities):
    y, p = probabilities
    row = evaluate_at(y, p, 0.60)
    assert row["precision"] == 1.0
    assert row["trades"] == 10


def test_summary_carries_the_confusion_matrix_and_auc(probabilities):
    y, p = probabilities
    out = summarise(y, p, 0.6)
    assert out["roc_auc"] == 1.0
    assert np.array(out["confusion_matrix"]).shape == (2, 2)


def test_training_is_seeded():
    rng = np.random.default_rng(0)
    x = pd.DataFrame(rng.normal(size=(200, 4)), columns=list("abcd"))
    y = pd.Series((x["a"] > 0).astype(int))
    assert np.allclose(train(x, y).predict_proba(x)[:, 1], train(x, y).predict_proba(x)[:, 1])
