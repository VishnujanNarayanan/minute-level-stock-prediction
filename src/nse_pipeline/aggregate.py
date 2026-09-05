"""Collapse ticks into one row per symbol per minute.

Roughly nine million ticks become a few thousand bars, which is what makes the
rest of the analysis tractable. Weighted prices are computed as a ratio of two
sums rather than a per-group lambda over the parent frame -- same numbers,
without reaching outside the group.
"""
from __future__ import annotations

import pandas as pd

KEY = ["symbol", "minute"]


def _weighted(df: pd.DataFrame, value: str, weight: str, name: str) -> pd.Series:
    """Weighted mean of ``value`` by ``weight`` per key, 0 where weight sums to 0."""
    frame = df[KEY].copy()
    frame["_num"] = df[value].astype(float) * df[weight].astype(float)
    frame["_den"] = df[weight].astype(float)
    sums = frame.groupby(KEY, sort=True)[["_num", "_den"]].sum()
    den = sums["_den"]
    out = pd.Series(0.0, index=sums.index, name=name)
    nonzero = den != 0
    out[nonzero] = sums.loc[nonzero, "_num"] / den[nonzero]
    return out


def minute_bars(trades: pd.DataFrame) -> pd.DataFrame:
    """Open/high/low/close, traded volume, trade count and VWAP per minute."""
    bars = trades.groupby(KEY, sort=True).agg(
        o=("price", "first"),
        h=("price", "max"),
        l=("price", "min"),      # noqa: E741 - matches the column name used downstream
        c=("price", "last"),
        total_volume=("volume", "sum"),
        num_trades=("price", "count"),
    )
    bars = bars.join(_weighted(trades, "price", "volume", "weighted_price"))
    return bars.reset_index()


def quote_stats(quotes: pd.DataFrame) -> pd.DataFrame:
    """Spread statistics and resting size per minute, plus size-weighted quotes."""
    q = quotes.copy()
    q["spread"] = q["ask_price"] - q["bid_price"]
    stats = q.groupby(KEY, sort=True).agg(
        avg_spread=("spread", "mean"),
        max_spread=("spread", "max"),
        min_spread=("spread", "min"),
        total_bid_size=("bid_size", "sum"),
        total_ask_size=("ask_size", "sum"),
    )
    stats = stats.join(_weighted(q, "bid_price", "bid_size", "weighted_avg_bid_price"))
    stats = stats.join(_weighted(q, "ask_price", "ask_size", "weighted_avg_ask_price"))
    return stats.reset_index()


def merge_bars(bars: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    """Inner-join trades to quotes on the composite (symbol, minute) key.

    Inner is deliberate: a minute with trades but no quotes has no spread, and a
    half-populated row would quietly become a feature vector full of nulls.
    """
    merged = bars.merge(stats, on=KEY, how="inner")
    return merged.sort_values(KEY).reset_index(drop=True)
