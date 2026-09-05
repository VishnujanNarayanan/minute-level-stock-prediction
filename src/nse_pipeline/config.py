"""Where the data lives.

The original notebook hardcoded Windows desktop paths, which meant the analysis
only ran on one machine. Paths now come from the environment with a sane default,
so the same code runs on a laptop, in Docker and in CI.
"""
from __future__ import annotations

import os
from pathlib import Path

#: Repository root (two parents up from this file: src/nse_pipeline/config.py).
ROOT = Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Root of the raw data tree. Override with NSE_DATA_DIR."""
    return Path(os.environ.get("NSE_DATA_DIR", ROOT / "data" / "raw"))


def trades_dir() -> Path:
    """Directory of per-symbol ``*_T.asc`` trade files."""
    return Path(os.environ.get("NSE_TRADES_DIR", data_dir() / "trades"))


def quotes_dir() -> Path:
    """Directory of per-symbol ``*_Q.asc`` quote files."""
    return Path(os.environ.get("NSE_QUOTES_DIR", data_dir() / "quotes"))


def database_path() -> Path:
    """SQLite database holding the minute bars. Override with NSE_DB_PATH."""
    return Path(os.environ.get("NSE_DB_PATH", ROOT / "data" / "nse.db"))


#: Column names, taken from the NSE file-format documentation.
TRADE_COLUMNS = [
    "date", "time", "price", "volume", "aggressor_side", "trade_period",
    "trade_id", "buyer", "buy_algo_type", "buy_order_capacity",
    "seller", "sell_algo_type", "sell_order_capacity",
]

QUOTE_COLUMNS = ["date", "time", "bid_price", "bid_size", "ask_price", "ask_size"]
