import pandas as pd
import pytest

from nse_pipeline.split import time_ordered_split


@pytest.fixture
def frame():
    return pd.DataFrame({
        "symbol": ["AAA"] * 10 + ["BBB"] * 10,
        "minute": list(pd.date_range("2024-04-01 09:15", periods=10, freq="min")) * 2,
        "c": range(20),
    })


def test_holdout_is_the_tail_of_each_symbol(frame):
    train, test = time_ordered_split(frame, holdout=3)
    assert len(test) == 6                       # 3 per symbol
    assert set(test["symbol"]) == {"AAA", "BBB"}
    for sym in ("AAA", "BBB"):
        assert test[test.symbol == sym]["minute"].min() > train[train.symbol == sym]["minute"].max()


def test_no_row_appears_in_both_halves(frame):
    train, test = time_ordered_split(frame, holdout=4)
    assert len(train) + len(test) == len(frame)
    merged = train.merge(test, on=["symbol", "minute"], how="inner")
    assert merged.empty


def test_holdout_must_be_positive(frame):
    with pytest.raises(ValueError):
        time_ordered_split(frame, holdout=0)
