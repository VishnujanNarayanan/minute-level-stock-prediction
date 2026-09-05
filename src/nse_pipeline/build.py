"""Build the warehouse end to end: raw .asc files in, SQLite out.

    python -m nse_pipeline.build --db data/nse.db

This is the entry point the notebook and the tests both lean on, so the pipeline
has exactly one definition rather than one per caller.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import aggregate, config, db, ingest

log = logging.getLogger("nse_pipeline.build")


def build_bars(trades_dir: Path, quotes_dir: Path):
    """Raw per-symbol files -> one merged minute-bar frame."""
    log.info("reading trades from %s", trades_dir)
    trades = ingest.add_minute(ingest.load_trades(trades_dir))
    log.info("reading quotes from %s", quotes_dir)
    quotes = ingest.add_minute(ingest.load_quotes(quotes_dir))
    log.info("aggregating %d trade ticks and %d quote ticks", len(trades), len(quotes))
    bars = aggregate.merge_bars(aggregate.minute_bars(trades), aggregate.quote_stats(quotes))
    log.info("built %d minute bars across %d symbols", len(bars), bars["symbol"].nunique())
    return bars


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trades", type=Path, default=None)
    parser.add_argument("--quotes", type=Path, default=None)
    parser.add_argument("--db", type=Path, default=None)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    bars = build_bars(args.trades or config.trades_dir(), args.quotes or config.quotes_dir())
    conn = db.connect(args.db)
    try:
        written = db.load_minute_bars(conn, bars)
    finally:
        conn.close()
    log.info("wrote %d rows to %s", written, args.db or config.database_path())
    return 0


if __name__ == "__main__":
    sys.exit(main())
