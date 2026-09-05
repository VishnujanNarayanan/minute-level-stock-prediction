import pandas as pd

from nse_pipeline.aggregate import merge_bars, minute_bars, quote_stats
from nse_pipeline.ingest import add_minute


def test_ohlc_and_volume_come_from_the_ticks_in_that_minute(trade_rows):
    bars = minute_bars(add_minute(trade_rows)).set_index(["symbol", "minute"])
    row = bars.loc[("AAA", pd.Timestamp("2024-04-01 09:15:00"))]
    assert (row.o, row.h, row.l, row.c) == (100.0, 102.0, 100.0, 102.0)
    assert row.total_volume == 40
    assert row.num_trades == 2


def test_vwap_weights_by_volume_not_by_tick_count(trade_rows):
    bars = minute_bars(add_minute(trade_rows)).set_index(["symbol", "minute"])
    row = bars.loc[("AAA", pd.Timestamp("2024-04-01 09:15:00"))]
    # (100*10 + 102*30) / 40 = 101.5, vs an unweighted mean of 101.0
    assert row.weighted_price == 101.5
    assert row.weighted_price != (100.0 + 102.0) / 2


def test_zero_resting_size_gives_zero_not_a_divide_by_zero(quote_rows):
    q = quote_rows.copy()
    q.loc[:, "bid_size"] = 0
    stats = quote_stats(add_minute(q))
    assert (stats["weighted_avg_bid_price"] == 0).all()
    assert stats["weighted_avg_bid_price"].notna().all()


def test_spread_statistics_per_minute(quote_rows):
    stats = quote_stats(add_minute(quote_rows)).set_index(["symbol", "minute"])
    row = stats.loc[("AAA", pd.Timestamp("2024-04-01 09:15:00"))]
    assert row.min_spread == 1.0        # 100.5 - 99.5
    assert row.max_spread == 2.0        # 101.0 - 99.0
    assert row.avg_spread == 1.5
    assert row.total_bid_size == 40


def test_merge_keeps_only_minutes_present_on_both_sides(trade_rows, quote_rows):
    bars = minute_bars(add_minute(trade_rows))
    stats = quote_stats(add_minute(quote_rows))
    stats = stats[~((stats.symbol == "AAA") & (stats.minute.dt.minute == 16))]
    merged = merge_bars(bars, stats)
    gone = merged[(merged.symbol == "AAA") & (merged.minute.dt.minute == 16)]
    assert gone.empty
    assert merged.notna().all().all()   # no half-populated rows survive
