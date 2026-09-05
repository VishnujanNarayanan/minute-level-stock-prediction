"""Synthetic fixtures shaped exactly like the NSE feeds.

Deliberately tiny and hand-computable: every expected number in the tests can be
worked out on paper, which is what makes a failure informative.
"""
import pandas as pd
import pytest

from nse_pipeline.config import QUOTE_COLUMNS, TRADE_COLUMNS


@pytest.fixture
def trade_rows():
    """Two symbols, three minutes, known prices and volumes."""
    rows = [
        # date, time, price, volume  (remaining columns are unused padding)
        ("04/01/2024", "09:15:10.100", 100.0, 10, "AAA"),
        ("04/01/2024", "09:15:40.200", 102.0, 30, "AAA"),
        ("04/01/2024", "09:16:05.000", 101.0, 10, "AAA"),
        ("04/01/2024", "09:17:05.000", 105.0, 10, "AAA"),
        ("04/01/2024", "09:15:20.000", 50.0, 5, "BBB"),
        ("04/01/2024", "09:16:20.000", 49.0, 5, "BBB"),
        ("04/01/2024", "09:17:20.000", 48.0, 5, "BBB"),
    ]
    df = pd.DataFrame(
        [(d, t, p, v) + ("",) * (len(TRADE_COLUMNS) - 4) for d, t, p, v, _ in rows],
        columns=TRADE_COLUMNS,
    )
    df["symbol"] = [r[4] for r in rows]
    return df


@pytest.fixture
def quote_rows():
    rows = [
        ("04/01/2024", "09:15:05.000", 99.0, 10, 101.0, 10, "AAA"),
        ("04/01/2024", "09:15:45.000", 99.5, 30, 100.5, 10, "AAA"),
        ("04/01/2024", "09:16:05.000", 100.0, 10, 102.0, 10, "AAA"),
        ("04/01/2024", "09:17:05.000", 104.0, 10, 106.0, 10, "AAA"),
        ("04/01/2024", "09:15:05.000", 49.0, 10, 51.0, 10, "BBB"),
        ("04/01/2024", "09:16:05.000", 48.0, 10, 50.0, 10, "BBB"),
        ("04/01/2024", "09:17:05.000", 47.0, 10, 49.0, 10, "BBB"),
    ]
    df = pd.DataFrame([r[:6] for r in rows], columns=QUOTE_COLUMNS)
    df["symbol"] = [r[6] for r in rows]
    return df


@pytest.fixture
def bars(trade_rows, quote_rows):
    """The merged minute-bar frame the feature code consumes."""
    from nse_pipeline.aggregate import merge_bars, minute_bars, quote_stats
    from nse_pipeline.ingest import add_minute

    return merge_bars(
        minute_bars(add_minute(trade_rows)), quote_stats(add_minute(quote_rows))
    )
