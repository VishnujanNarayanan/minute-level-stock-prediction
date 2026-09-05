"""What the signal would have earned, and what that number is worth.

The original backtest bought a fixed amount whenever the model was confident and
summed the outcome. It reported a profit. What it did not report was that the
profit was smaller than the transaction costs of the trades that produced it,
which is the only thing that decides whether a strategy is real.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

#: A retail-ish round-trip cost in basis points, applied per trade. NSE charges
#: brokerage, STT, exchange fees, GST and stamp duty; 10bp round trip is a
#: conservative-but-not-generous stand-in.
DEFAULT_COST_BPS = 10.0


def run(prices: pd.DataFrame, signals: np.ndarray, stake: float = 200.0,
        starting_capital: float = 3000.0, cost_bps: float = DEFAULT_COST_BPS) -> dict:
    """Enter at ``c`` whenever the signal fires, exit at ``future_price``.

    Deliberately simple: no position sizing, no stops, one bar of holding. The
    question is whether the signal has an edge at all, not whether a particular
    execution scheme is optimal.
    """
    if len(prices) != len(signals):
        raise ValueError("prices and signals must be the same length")

    entry = prices["c"].to_numpy(dtype=float)
    exit_ = prices["future_price"].to_numpy(dtype=float)
    fired = (np.asarray(signals) == 1) & ~np.isnan(exit_)

    returns = np.zeros(len(entry))
    returns[fired] = (exit_[fired] - entry[fired]) / entry[fired]

    gross = returns * stake
    costs = np.where(fired, stake * cost_bps / 10_000.0, 0.0)
    net = gross - costs

    trades = int(fired.sum())
    wins = int((gross[fired] > 0).sum()) if trades else 0
    return {
        "trades": trades,
        "win_rate": wins / trades if trades else 0.0,
        "gross_pnl": float(gross.sum()),
        "costs": float(costs.sum()),
        "net_pnl": float(net.sum()),
        "starting_capital": starting_capital,
        "final_capital": float(starting_capital + net.sum()),
        "gross_return_pct": float(100 * gross.sum() / starting_capital),
        "net_return_pct": float(100 * net.sum() / starting_capital),
        "survives_costs": bool(net.sum() > 0),
    }


def buy_and_hold(prices: pd.DataFrame, stake: float = 200.0) -> dict:
    """The benchmark the strategy has to beat: hold every bar, trade nothing.

    A strategy that makes money is not interesting if doing nothing made more.
    """
    entry = prices["c"].to_numpy(dtype=float)
    exit_ = prices["future_price"].to_numpy(dtype=float)
    valid = ~np.isnan(exit_)
    returns = (exit_[valid] - entry[valid]) / entry[valid]
    return {"bars": int(valid.sum()), "pnl": float((returns * stake).sum())}
