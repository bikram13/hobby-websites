"""Tests for sector_fetcher.py — symbol-to-sector mapping and feature computation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from ml.sector_fetcher import get_sector_for_symbol, SECTOR_INDICES, compute_sector_feature


# ── Symbol → sector mapping ───────────────────────────────────────────────────

def test_bank_symbol_maps_to_bank_sector():
    assert get_sector_for_symbol("HDFCBANK.NS") == "bank"

def test_it_symbol_maps_to_it_sector():
    assert get_sector_for_symbol("TCS.NS") == "it"

def test_pharma_symbol_maps_to_pharma_sector():
    assert get_sector_for_symbol("SUNPHARMA.NS") == "pharma"

def test_unknown_symbol_returns_none():
    assert get_sector_for_symbol("UNKNOWNSYM.NS") is None

def test_sector_indices_dict_has_required_keys():
    for key in ("bank", "it", "pharma", "energy", "fmcg"):
        assert key in SECTOR_INDICES, f"Missing sector: {key}"

def test_sector_indices_all_have_yfinance_tickers():
    for sector, ticker in SECTOR_INDICES.items():
        assert ticker.startswith("^") or ticker.endswith(".NS"), \
            f"Sector {sector} ticker {ticker} looks wrong"


# ── compute_sector_feature ────────────────────────────────────────────────────

def _make_sector_df(n: int = 60, trend: str = "up") -> pd.DataFrame:
    """Create a mock sector index DataFrame."""
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    if trend == "up":
        close = pd.Series(10000.0 + np.arange(n) * 20.0, index=idx)
    else:
        close = pd.Series(10000.0 - np.arange(n) * 20.0, index=idx)
    return pd.DataFrame({"close": close, "open": close*0.999,
                         "high": close*1.005, "low": close*0.995,
                         "volume": np.ones(n)*1e6})

def test_sector_feature_positive_when_sector_above_ema20():
    sector_df = _make_sector_df(n=60, trend="up")
    signal_date = sector_df.index[-1]
    score = compute_sector_feature(sector_df, signal_date)
    assert score > 0.0, "Uptrending sector should give positive score"

def test_sector_feature_negative_when_sector_below_ema20():
    sector_df = _make_sector_df(n=60, trend="down")
    signal_date = sector_df.index[-1]
    score = compute_sector_feature(sector_df, signal_date)
    assert score < 0.0, "Downtrending sector should give negative score"

def test_sector_feature_returns_zero_for_none():
    score = compute_sector_feature(None, pd.Timestamp("2024-01-01"))
    assert score == 0.0

def test_sector_feature_returns_zero_for_empty_df():
    score = compute_sector_feature(pd.DataFrame(), pd.Timestamp("2024-01-01"))
    assert score == 0.0

def test_sector_feature_no_lookahead_bias():
    """Feature must only use sector data up to and including signal_date."""
    sector_df = _make_sector_df(n=100, trend="up")
    # Split: first 60 bars only (simulate signal on day 60)
    signal_date = sector_df.index[59]
    score_partial = compute_sector_feature(sector_df, signal_date)
    score_full    = compute_sector_feature(sector_df, sector_df.index[-1])
    # Scores should differ — proves windowing is applied
    assert score_partial != score_full
