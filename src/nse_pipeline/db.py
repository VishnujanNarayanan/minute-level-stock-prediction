"""SQLite warehouse for the minute bars.

The aggregation used to exist only as a pandas frame inside a notebook session,
so every question about the data meant re-running the whole pipeline. Loading
the bars into SQLite once turns them into something queryable: the files under
``sql/`` are the questions, and they run without Python in the loop.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from .config import ROOT, database_path

SQL_DIR = ROOT / "sql"

BAR_COLUMNS = [
    "symbol", "minute", "o", "h", "l", "c", "total_volume", "num_trades",
    "weighted_price", "avg_spread", "max_spread", "min_spread",
    "total_bid_size", "total_ask_size",
    "weighted_avg_bid_price", "weighted_avg_ask_price",
]


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    """Open the warehouse. ``:memory:`` is accepted, which is what tests use."""
    target = str(path if path is not None else database_path())
    if target != ":memory:":
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    return conn


def read_sql_file(name: str) -> str:
    """Load a statement from ``sql/``, so queries live in .sql not in strings."""
    path = SQL_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"no such query: {path}")
    return path.read_text(encoding="utf-8")


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(read_sql_file("schema.sql"))
    conn.commit()


def load_minute_bars(conn: sqlite3.Connection, bars: pd.DataFrame) -> int:
    """Replace the ``minute_bars`` table with ``bars``. Returns rows written.

    Minutes are stored as ISO-8601 text, which sorts and compares correctly in
    SQLite and keeps ``SUBSTR(minute, 12, 2)`` a usable hour extraction.
    """
    frame = bars.copy()
    frame["minute"] = pd.to_datetime(frame["minute"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    missing = [c for c in BAR_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"bars is missing columns: {missing}")
    create_schema(conn)
    frame[BAR_COLUMNS].to_sql("minute_bars", conn, if_exists="append", index=False)
    conn.commit()
    return len(frame)


def query(conn: sqlite3.Connection, name: str) -> pd.DataFrame:
    """Run one of the files in ``sql/`` and hand back the result."""
    return pd.read_sql_query(read_sql_file(name), conn)
