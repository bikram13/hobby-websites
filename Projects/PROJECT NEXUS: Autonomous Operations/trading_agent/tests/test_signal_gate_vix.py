"""Tests for VIX-based threshold adjustment in SignalGate.approve()."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from ml.signal_gate import SignalGate


def _make_gate_trained(threshold: float = 0.55) -> SignalGate:
    """Create a gate with mock XGB+LGBM models that return a fixed probability."""
    gate = SignalGate(threshold=threshold)
    gate.trained = True
    gate.xgb_model = MagicMock()
    gate.lgbm_model = MagicMock()
    return gate


def _make_window(n: int = 80) -> pd.DataFrame:
    """Minimal OHLCV window for feature computation."""
    idx = pd.date_range("2022-01-01", periods=n, freq="B")
    price = 1000.0 + np.arange(n, dtype=float)
    return pd.DataFrame({
        "open": price * 0.999, "high": price * 1.005,
        "low": price * 0.995,  "close": price,
        "volume": np.ones(n) * 1e6,
    }, index=idx)


def _mock_features(nifty_above=1.0):
    return {
        "ema_ratio": 1.01, "price_vs_ema50": 0.02, "price_vs_ema200": 0.05,
        "adx": 28.0, "rsi": 55.0, "macd_hist": 0.5, "macd_hist_slope": 0.1,
        "ret_5d": 0.01, "ret_10d": 0.02, "ret_20d": 0.03,
        "bb_zscore": 0.5, "bb_width": 0.04, "dist_from_52wk_high": -0.02,
        "atr_pct": 0.015, "vol_ratio": 1.2, "trend_consistency": 0.7,
        "nifty_above_ema200": nifty_above, "nifty_pct_vs_ema200": 0.02,
        "earnings_momentum": 0.0, "sector_pct_vs_ema20": 0.0,
        "weekly_trend": 0.0, "weekly_rsi": 50.0,
        "stock_rs_vs_nifty": 0.0, "vol_price_trend": 0.0,
    }


# ── VIX threshold adjustments ─────────────────────────────────────────────────

def test_vix_high_raises_threshold_blocks_marginal_signal():
    """VIX > 25 raises threshold by 0.20 — a signal at prob=0.60 should be blocked."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 27.0   # > 25: +0.20 → effective_thresh = 0.75
    gate.xgb_model.predict_proba.return_value = np.array([[0.40, 0.60]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.40, 0.60]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 0, "prob=0.60 < 0.75 should be blocked when VIX > 25"


def test_vix_moderate_raises_threshold_by_10():
    """VIX between 20 and 25 raises threshold by 0.10."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 22.0   # > 20 but <= 25: +0.10 → effective_thresh = 0.65
    gate.xgb_model.predict_proba.return_value = np.array([[0.38, 0.62]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.38, 0.62]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        blocked = gate.approve(_make_window(), raw)
    assert blocked["signal"] == 0, "prob=0.62 < 0.65 (VIX-adjusted) should be blocked"


def test_vix_moderate_still_passes_strong_signal():
    """VIX = 22 raises threshold to 0.65; prob=0.70 should still pass."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 22.0
    gate.xgb_model.predict_proba.return_value = np.array([[0.30, 0.70]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.30, 0.70]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 1, "prob=0.70 > 0.65 should pass with VIX=22"


def test_vix_normal_no_adjustment():
    """VIX <= 20 applies no additional threshold adjustment."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 18.0
    gate.xgb_model.predict_proba.return_value = np.array([[0.44, 0.56]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.44, 0.56]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 1, "prob=0.56 > 0.55 should pass with normal VIX"


def test_vix_zero_no_adjustment():
    """vix_value == 0.0 (default) applies no adjustment."""
    gate = _make_gate_trained(threshold=0.55)
    gate.xgb_model.predict_proba.return_value = np.array([[0.44, 0.56]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.44, 0.56]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 1


def test_vix_does_not_weaken_bear_market_threshold():
    """In bear market (thresh=0.75), a low VIX should not lower the threshold."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 10.0
    gate.xgb_model.predict_proba.return_value = np.array([[0.33, 0.67]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.33, 0.67]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    bear_features = _mock_features(nifty_above=0.0)
    with patch("ml.signal_gate.compute_features", return_value=bear_features):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 0, "Bear market threshold (0.75) should block prob=0.67"


def test_approve_result_contains_vix_info():
    """Approved signal should include vix_value in the result."""
    gate = _make_gate_trained(threshold=0.55)
    gate.vix_value = 15.0
    gate.xgb_model.predict_proba.return_value = np.array([[0.30, 0.70]])
    gate.lgbm_model.predict_proba.return_value = np.array([[0.30, 0.70]])
    raw = {"signal": 1, "strength": 0.9, "symbol": "TEST.NS"}
    with patch("ml.signal_gate.compute_features", return_value=_mock_features()):
        result = gate.approve(_make_window(), raw)
    assert result["signal"] == 1
    assert "vix_value" in result


def test_vix_field_defaults_to_zero():
    """SignalGate.vix_value should default to 0.0."""
    gate = SignalGate()
    assert gate.vix_value == 0.0
