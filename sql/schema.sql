-- Minute bars: one row per symbol per minute, trades joined to quotes.
-- This is the table every downstream query and the model both read from, so it
-- is declared once here rather than implied by whatever pandas last wrote.

DROP TABLE IF EXISTS minute_bars;

CREATE TABLE minute_bars (
    symbol                  TEXT    NOT NULL,
    minute                  TEXT    NOT NULL,   -- ISO-8601, UTC-naive exchange local time
    o                       REAL    NOT NULL,   -- open
    h                       REAL    NOT NULL,   -- high
    l                       REAL    NOT NULL,   -- low
    c                       REAL    NOT NULL,   -- close
    total_volume            INTEGER NOT NULL,
    num_trades              INTEGER NOT NULL,
    weighted_price          REAL    NOT NULL,   -- VWAP, weighted by traded volume
    avg_spread              REAL,
    max_spread              REAL,
    min_spread              REAL,
    total_bid_size          INTEGER,
    total_ask_size          INTEGER,
    weighted_avg_bid_price  REAL,
    weighted_avg_ask_price  REAL,
    PRIMARY KEY (symbol, minute)
);

CREATE INDEX IF NOT EXISTS idx_minute_bars_minute ON minute_bars (minute);
CREATE INDEX IF NOT EXISTS idx_minute_bars_symbol ON minute_bars (symbol);
