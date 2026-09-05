"""The warehouse, and every .sql file that reads from it.

Each query runs against an in-memory database built from the fixtures, so a
broken statement fails here rather than the next time someone opens the notebook.
"""
from sqlite3 import IntegrityError

import pandas as pd
import pytest

from nse_pipeline import db


@pytest.fixture
def conn(bars):
    connection = db.connect(":memory:")
    db.load_minute_bars(connection, bars)
    yield connection
    connection.close()


def test_load_writes_every_bar_and_the_schema_holds(conn, bars):
    count = conn.execute("SELECT COUNT(*) FROM minute_bars").fetchone()[0]
    assert count == len(bars)
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(minute_bars)")}
    assert {"symbol", "minute", "c", "weighted_price", "avg_spread"} <= cols


def test_primary_key_stops_a_symbol_minute_being_stored_twice(conn):
    row = conn.execute("SELECT * FROM minute_bars LIMIT 1").fetchone()
    with pytest.raises(IntegrityError):
        conn.execute(
            "INSERT INTO minute_bars (symbol, minute, o, h, l, c, total_volume,"
            " num_trades, weighted_price) VALUES (?,?,?,?,?,?,?,?,?)",
            (row["symbol"], row["minute"], 1, 1, 1, 1, 1, 1, 1),
        )


def test_reload_replaces_rather_than_appends(bars):
    connection = db.connect(":memory:")
    db.load_minute_bars(connection, bars)
    db.load_minute_bars(connection, bars)
    assert connection.execute("SELECT COUNT(*) FROM minute_bars").fetchone()[0] == len(bars)
    connection.close()


def test_missing_columns_are_refused_before_anything_is_written(bars):
    connection = db.connect(":memory:")
    with pytest.raises(ValueError, match="missing columns"):
        db.load_minute_bars(connection, bars.drop(columns=["weighted_price"]))
    connection.close()


def test_minutes_are_stored_as_sortable_iso_text(conn):
    minutes = [r["minute"] for r in conn.execute("SELECT minute FROM minute_bars ORDER BY minute")]
    assert minutes == sorted(minutes)
    assert minutes[0].startswith("2024-04-01 09:1")


def test_unknown_query_name_fails_loudly():
    with pytest.raises(FileNotFoundError):
        db.read_sql_file("no_such_query.sql")


# --- the .sql files themselves -------------------------------------------------

def test_liquidity_by_symbol_ranks_by_traded_volume(conn):
    out = db.query(conn, "liquidity_by_symbol.sql")
    assert list(out.columns) == [
        "symbol", "bars", "traded_volume", "trades",
        "mean_spread", "mean_spread_bps", "mean_resting_size",
    ]
    assert out["traded_volume"].is_monotonic_decreasing
    assert out.loc[0, "symbol"] == "AAA"          # 50 traded vs BBB's 15


def test_spread_by_time_of_day_extracts_the_clock_hour(conn):
    out = db.query(conn, "spread_by_time_of_day.sql")
    assert set(out["hour"]) == {"09"}
    assert out["bars"].sum() == conn.execute(
        "SELECT COUNT(*) FROM minute_bars"
    ).fetchone()[0]


def test_wide_spread_minutes_flags_only_genuine_blowouts(conn):
    out = db.query(conn, "wide_spread_minutes.sql")
    assert out.empty          # the fixture's spreads are all within 3x of usual
    conn.execute(
        "UPDATE minute_bars SET avg_spread = 99 "
        "WHERE symbol='AAA' AND minute LIKE '%09:16%'"
    )
    flagged = db.query(conn, "wide_spread_minutes.sql")
    assert len(flagged) == 1
    assert flagged.loc[0, "times_usual"] > 3


def test_direction_base_rate_matches_the_python_target(conn, bars):
    from nse_pipeline.features import add_direction_target

    sql_side = db.query(conn, "direction_base_rate.sql").set_index("symbol")
    py_side = add_direction_target(bars).groupby("symbol")["target"].agg(["count", "sum"])
    for symbol in py_side.index:
        assert sql_side.loc[symbol, "labelled_bars"] == py_side.loc[symbol, "count"]
        assert sql_side.loc[symbol, "up_bars"] == py_side.loc[symbol, "sum"]


def test_every_sql_file_is_valid_sql(conn):
    """A query nobody has run is a query that does not work."""
    import pathlib

    for path in sorted((db.SQL_DIR).glob("*.sql")):
        if path.name == "schema.sql":
            continue
        pd.read_sql_query(path.read_text(), conn)
    assert pathlib.Path(db.SQL_DIR).exists()
