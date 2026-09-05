"""Paths must come from the environment, not from one person's desktop."""

from nse_pipeline import config


def test_defaults_sit_under_the_repo():
    assert config.trades_dir() == config.ROOT / "data" / "raw" / "trades"
    assert config.quotes_dir() == config.ROOT / "data" / "raw" / "quotes"


def test_environment_overrides_every_path(monkeypatch, tmp_path):
    monkeypatch.setenv("NSE_TRADES_DIR", str(tmp_path / "t"))
    monkeypatch.setenv("NSE_QUOTES_DIR", str(tmp_path / "q"))
    monkeypatch.setenv("NSE_DB_PATH", str(tmp_path / "x.db"))
    assert config.trades_dir() == tmp_path / "t"
    assert config.quotes_dir() == tmp_path / "q"
    assert config.database_path() == tmp_path / "x.db"


def test_data_dir_override_cascades(monkeypatch, tmp_path):
    monkeypatch.setenv("NSE_DATA_DIR", str(tmp_path))
    assert config.trades_dir() == tmp_path / "trades"


def test_column_lists_match_the_nse_file_format():
    assert len(config.TRADE_COLUMNS) == 13
    assert len(config.QUOTE_COLUMNS) == 6
    assert config.QUOTE_COLUMNS[2:] == ["bid_price", "bid_size", "ask_price", "ask_size"]
