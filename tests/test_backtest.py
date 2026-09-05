import numpy as np
import pandas as pd
import pytest

from nse_pipeline.backtest import buy_and_hold, run


@pytest.fixture
def prices():
    """Four bars: two rise by 1%, two fall by 1%."""
    return pd.DataFrame({
        "c": [100.0, 100.0, 100.0, 100.0],
        "future_price": [101.0, 99.0, 101.0, 99.0],
    })


def test_a_signal_that_only_catches_winners_makes_money(prices):
    out = run(prices, np.array([1, 0, 1, 0]), stake=200.0, cost_bps=0)
    assert out["trades"] == 2
    assert out["win_rate"] == 1.0
    assert out["gross_pnl"] == pytest.approx(4.0)      # 2 x 1% x 200
    assert out["survives_costs"] is True


def test_costs_are_charged_per_trade_and_can_erase_the_edge(prices):
    free = run(prices, np.array([1, 0, 1, 0]), stake=200.0, cost_bps=0)
    charged = run(prices, np.array([1, 0, 1, 0]), stake=200.0, cost_bps=200)
    assert charged["costs"] > 0
    assert charged["net_pnl"] < free["net_pnl"]
    assert charged["survives_costs"] is False          # the edge did not survive
    assert charged["gross_pnl"] == free["gross_pnl"]   # gross is unchanged


def test_a_bar_with_no_future_price_is_never_traded():
    frame = pd.DataFrame({"c": [100.0, 100.0], "future_price": [np.nan, 101.0]})
    out = run(frame, np.array([1, 1]), cost_bps=0)
    assert out["trades"] == 1                          # the unknowable bar is skipped


def test_doing_nothing_costs_nothing(prices):
    out = run(prices, np.array([0, 0, 0, 0]))
    assert out["trades"] == 0
    assert out["net_pnl"] == 0.0
    assert out["final_capital"] == out["starting_capital"]


def test_mismatched_lengths_are_refused(prices):
    with pytest.raises(ValueError, match="same length"):
        run(prices, np.array([1, 0]))


def test_the_benchmark_holds_every_bar(prices):
    out = buy_and_hold(prices, stake=200.0)
    assert out["bars"] == 4
    assert out["pnl"] == pytest.approx(0.0)            # two up, two down, flat
