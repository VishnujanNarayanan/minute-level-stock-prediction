"""Read the raw per-symbol NSE trade and quote files into DataFrames.

One file per symbol per side of the book, headerless, columns per the NSE
file-format documentation. The notebook did this inline for one hardcoded
directory; here it is a function so it can be pointed anywhere and tested.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import QUOTE_COLUMNS, TRADE_COLUMNS


def symbol_from_filename(name: str) -> str:
    """``TCS_2024_04_01_T.asc`` -> ``TCS``.

    The symbol is everything before the first date-like component, so it
    survives symbols that contain underscores or digits.
    """
    stem = Path(name).stem
    parts = stem.split("_")
    for i, part in enumerate(parts):
        if len(part) == 4 and part.isdigit():          # the year
            return "_".join(parts[:i])
    return "_".join(parts[:-1]) if len(parts) > 1 else stem


def _read_one(path: Path, columns: list[str], symbol: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=columns)
    df["symbol"] = symbol if symbol is not None else symbol_from_filename(path.name)
    return df


def read_trade_file(path: str | Path) -> pd.DataFrame:
    return _read_one(Path(path), TRADE_COLUMNS)


def read_quote_file(path: str | Path) -> pd.DataFrame:
    return _read_one(Path(path), QUOTE_COLUMNS)


def _load_dir(directory: str | Path, suffix: str, columns: list[str]) -> pd.DataFrame:
    directory = Path(directory)
    files = sorted(p for p in directory.iterdir() if p.name.endswith(suffix))
    if not files:
        raise FileNotFoundError(f"no {suffix} files under {directory}")
    return pd.concat([_read_one(p, columns) for p in files], ignore_index=True)


def load_trades(directory: str | Path) -> pd.DataFrame:
    """Every ``*_T.asc`` under ``directory``, concatenated and symbol-tagged."""
    return _load_dir(directory, "_T.asc", TRADE_COLUMNS)


def load_quotes(directory: str | Path) -> pd.DataFrame:
    """Every ``*_Q.asc`` under ``directory``, concatenated and symbol-tagged."""
    return _load_dir(directory, "_Q.asc", QUOTE_COLUMNS)


def add_minute(df: pd.DataFrame) -> pd.DataFrame:
    """Attach a ``minute`` column by flooring the parsed date+time timestamp.

    Returns a new frame; the caller's is untouched.
    """
    out = df.copy()
    stamp = pd.to_datetime(
        out["date"].astype(str) + " " + out["time"].astype(str), format="mixed"
    )
    out["timestamp"] = stamp
    out["minute"] = stamp.dt.floor("min")
    return out
