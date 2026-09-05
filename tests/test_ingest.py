import pandas as pd
import pytest

from nse_pipeline.config import QUOTE_COLUMNS, TRADE_COLUMNS
from nse_pipeline.ingest import (
    add_minute,
    load_quotes,
    load_trades,
    read_trade_file,
    symbol_from_filename,
)


@pytest.mark.parametrize(
    "name,expected",
    [
        ("TCS_2024_04_01_T.asc", "TCS"),
        ("BAJAJ_AUTO_2024_04_01_Q.asc", "BAJAJ_AUTO"),
        ("M_M_2024_04_01_T.asc", "M_M"),
        ("HEROMOTOCO_2024_04_01_Q.asc", "HEROMOTOCO"),
    ],
)
def test_symbol_survives_underscores_in_the_name(name, expected):
    assert symbol_from_filename(name) == expected


def test_reads_a_headerless_file_and_tags_the_symbol(tmp_path):
    path = tmp_path / "TCS_2024_04_01_T.asc"
    path.write_text("04/01/2024,09:15:00.100,100.5,7," + ",".join([""] * 9) + "\n")
    df = read_trade_file(path)
    assert list(df.columns) == TRADE_COLUMNS + ["symbol"]
    assert df.loc[0, "price"] == 100.5
    assert df.loc[0, "symbol"] == "TCS"


def test_load_dir_concatenates_every_symbol(tmp_path):
    for sym in ("AAA", "BBB"):
        (tmp_path / f"{sym}_2024_04_01_T.asc").write_text(
            "04/01/2024,09:15:00.100,1,1," + ",".join([""] * 9) + "\n"
        )
        (tmp_path / f"{sym}_2024_04_01_Q.asc").write_text("04/01/2024,09:15:00.100,1,1,2,1\n")
    trades, quotes = load_trades(tmp_path), load_quotes(tmp_path)
    assert set(trades["symbol"]) == {"AAA", "BBB"}
    assert list(quotes.columns) == QUOTE_COLUMNS + ["symbol"]


def test_load_dir_refuses_to_return_an_empty_frame(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_trades(tmp_path)


def test_minute_floors_the_timestamp_and_leaves_the_input_alone(trade_rows):
    out = add_minute(trade_rows)
    assert out.loc[0, "minute"] == pd.Timestamp("2024-04-01 09:15:00")
    assert out.loc[1, "minute"] == pd.Timestamp("2024-04-01 09:15:00")
    assert out.loc[2, "minute"] == pd.Timestamp("2024-04-01 09:16:00")
    assert "minute" not in trade_rows.columns   # the caller's frame is untouched
