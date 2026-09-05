"""Time-ordered train/test split.

A random split would let the model train on minutes that come after the ones it
is scored on, and the backtest would look far better than the strategy is. The
holdout is therefore the tail of each symbol's own day.
"""
from __future__ import annotations

import pandas as pd


def time_ordered_split(
    df: pd.DataFrame, holdout: int = 100, group: str = "symbol", order: str = "minute"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(train, test)`` where test is the last ``holdout`` bars per symbol."""
    if holdout <= 0:
        raise ValueError("holdout must be positive")
    ordered = df.sort_values([group, order])
    tail = ordered.groupby(group).tail(holdout)
    train = ordered.drop(index=tail.index)
    return train.reset_index(drop=True), tail.reset_index(drop=True)
