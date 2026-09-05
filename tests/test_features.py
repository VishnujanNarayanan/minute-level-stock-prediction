import pandas as pd

from nse_pipeline.features import add_direction_target, add_rolling_features, feature_columns


def test_rolling_windows_do_not_all_collapse_to_the_last_one(bars):
    """The late-binding bug the notebook had: every window produced window-20 numbers."""
    out = add_rolling_features(bars, windows=(2, 3), columns=("c",))
    assert not out["c_rolling_mean_2"].equals(out["c_rolling_mean_3"])


def test_rolling_mean_is_computed_within_a_symbol(bars):
    out = add_rolling_features(bars, windows=(10,), columns=("c",))
    first_of_bbb = out[out.symbol == "BBB"].iloc[0]
    # first bar of a symbol can only average itself, never the previous symbol's
    assert first_of_bbb["c_rolling_mean_10"] == first_of_bbb["c"]


def test_std_of_a_single_observation_is_zero_not_nan(bars):
    out = add_rolling_features(bars, windows=(5,), columns=("c",))
    assert out.groupby("symbol")["c_rolling_std_5"].first().eq(0).all()


def test_target_labels_a_rise_and_drops_the_unknowable_last_bar(bars):
    out = add_direction_target(bars)
    aaa = out[out.symbol == "AAA"].sort_values("minute")
    assert aaa.iloc[0]["target"] == 0     # 102.0 -> 101.0 is a fall
    assert aaa.iloc[1]["target"] == 1     # 101.0 -> 105.0 is a rise
    # the final bar of each symbol has no future and must not be labelled
    assert len(aaa) == 2
    assert pd.Timestamp("2024-04-01 09:17:00") not in set(aaa["minute"])


def test_feature_columns_exclude_everything_derived_from_the_future(bars):
    out = add_direction_target(add_rolling_features(bars))
    cols = feature_columns(out)
    assert "target" not in cols
    assert "future_price" not in cols
    assert "future_return" not in cols
    assert "c_rolling_mean_20" in cols
    assert "avg_spread" in cols
