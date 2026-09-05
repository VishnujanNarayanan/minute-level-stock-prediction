"""Rolling features and the prediction target.

The notebook built these inside ``for window in ...`` loops whose lambdas closed
over the loop variable -- the classic late-binding trap, and ten ruff B023
warnings. Binding the window as a default argument fixes it, and makes the
feature set something a test can assert on.
"""
from __future__ import annotations

import pandas as pd

DEFAULT_WINDOWS = (3, 5, 10, 20)
DEFAULT_COLUMNS = ("c", "total_volume", "avg_spread")


def add_rolling_features(
    df: pd.DataFrame,
    windows: tuple[int, ...] = DEFAULT_WINDOWS,
    columns: tuple[str, ...] = DEFAULT_COLUMNS,
    group: str = "symbol",
) -> pd.DataFrame:
    """Rolling mean and standard deviation per symbol, one pair per column/window."""
    out = df.copy()
    for window in windows:
        for column in columns:
            grouped = out.groupby(group)[column]
            out[f"{column}_rolling_mean_{window}"] = grouped.transform(
                lambda s, w=window: s.rolling(w, min_periods=1).mean()
            )
            out[f"{column}_rolling_std_{window}"] = grouped.transform(
                lambda s, w=window: s.rolling(w, min_periods=1).std().fillna(0)
            )
    return out


def add_direction_target(
    df: pd.DataFrame, horizon: int = 1, group: str = "symbol", price: str = "c"
) -> pd.DataFrame:
    """Label each bar 1 when the price is higher ``horizon`` bars later.

    Uses a forward shift within the symbol, so a bar never sees another symbol's
    future and the last bars of a day -- which have no future -- are dropped.
    """
    out = df.copy()
    out["future_price"] = out.groupby(group)[price].shift(-horizon)
    out["future_return"] = (out["future_price"] - out[price]) / out[price]
    out["target"] = (out["future_return"] > 0).astype(int)
    return out.dropna(subset=["future_price"]).reset_index(drop=True)


def feature_columns(df: pd.DataFrame) -> list[str]:
    """Model inputs: the rolling features plus the raw per-minute measurements.

    Everything derived from the future -- ``future_price``, ``future_return``,
    ``target`` -- is excluded by construction, which is the whole leakage guard.
    """
    base = [
        "o", "h", "l", "c", "total_volume", "num_trades", "weighted_price",
        "avg_spread", "max_spread", "min_spread",
        "total_bid_size", "total_ask_size",
        "weighted_avg_bid_price", "weighted_avg_ask_price",
    ]
    rolling = [c for c in df.columns if "_rolling_" in c]
    return [c for c in base if c in df.columns] + rolling
