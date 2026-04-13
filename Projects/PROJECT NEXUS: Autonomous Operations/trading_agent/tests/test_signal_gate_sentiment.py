"""Tests for sentiment veto/boost logic added to SignalGate.approve()."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from ml.signal_gate import SignalGate


def _make_gate_with_mock_model(threshold: float = 0.55):
    """Create a SignalGate with mock XGB+LGBM models that always return prob=0.70."""
    gate = SignalGate(threshold=threshold)
    gate.trained = True
    mock_xgb = MagicMock()
    mock_xgb.predict_proba.return_value = np.array([[0.30, 0.70]])
    gate.xgb_model = mock_xgb
    mock_lgbm = MagicMock()
    mock_lgbm.predict_proba.return_value = np.array([[0.30, 0.70]])
    gate.lgbm_model = mock_lgbm
    return gate


def _make_df(n: int = 80) -> pd.DataFrame:
    """Create a minimal OHLCV DataFrame with enough rows for feature extraction."""
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(100.0 + np.cumsum(np.random.randn(n) * 0.5), index=idx)
    return pd.DataFrame({
        "open":   close * 0.999,
        "high":   close * 1.005,
        "low":    close * 0.995,
        "close":  close,
        "volume": np.ones(n) * 1_000_000,
    })


_RAW_BUY = {"signal": 1, "strength": 0.8, "reason": "ADX breakout"}


# ── Default behaviour (live_sentiment = 0.0, neutral zone) ───────────────────

def test_neutral_sentiment_does_not_change_approved_signal():
    gate = _make_gate_with_mock_model(threshold=0.55)
    gate.live_sentiment = 0.0   # neutral
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    # GBM returns 0.70 >= 0.55 → approved; neutral sentiment doesn't change that
    assert result["signal"] == 1
    assert result.get("gate_approved") is True


def test_neutral_sentiment_does_not_change_blocked_signal():
    gate = _make_gate_with_mock_model(threshold=0.80)  # threshold above 0.70
    gate.live_sentiment = 0.0
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    # GBM returns 0.70 < 0.80 → blocked; neutral sentiment doesn't change that
    assert result["signal"] == 0


# ── Negative sentiment veto ───────────────────────────────────────────────────

def test_strongly_negative_sentiment_vetoes_approved_signal():
    gate = _make_gate_with_mock_model(threshold=0.55)  # GBM would approve at 0.70
    gate.live_sentiment = -0.5   # strongly negative — below -0.4 threshold
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 0
    assert "sentiment" in result.get("reason", "").lower()

def test_mildly_negative_sentiment_does_not_veto():
    gate = _make_gate_with_mock_model(threshold=0.55)
    gate.live_sentiment = -0.2   # mildly negative — within neutral zone
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 1  # still approved


# ── Positive sentiment boost ─────────────────────────────────────────────────

def test_positive_sentiment_boosts_borderline_signal():
    # GBM returns 0.70; without boost, threshold=0.72 → blocked
    # With boost: effective_thresh = 0.72 - 0.05 = 0.67 → approved
    gate = _make_gate_with_mock_model(threshold=0.72)
    gate.live_sentiment = +0.5   # strongly positive
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 1
    assert result.get("sentiment_boost") is True

def test_weakly_positive_sentiment_does_not_boost():
    # GBM returns 0.70; threshold=0.72 → blocked; sentiment=+0.1 (below +0.3 threshold)
    gate = _make_gate_with_mock_model(threshold=0.72)
    gate.live_sentiment = +0.1
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 0  # not boosted


# ── Non-buy signals are unaffected ───────────────────────────────────────────

def test_sell_signal_passes_through_unchanged():
    gate = _make_gate_with_mock_model()
    gate.live_sentiment = -0.9
    df = _make_df()
    raw_sell = {"signal": -1, "strength": 0.5, "reason": "SELL"}
    result = gate.approve(df, raw_sell)
    assert result["signal"] == -1   # sell signals bypass gate entirely

def test_zero_signal_passes_through_unchanged():
    gate = _make_gate_with_mock_model()
    gate.live_sentiment = -0.9
    df = _make_df()
    raw_hold = {"signal": 0, "strength": 0, "reason": "hold"}
    result = gate.approve(df, raw_hold)
    assert result["signal"] == 0


# ── Boundary conditions ──────────────────────────────────────────────────────

def test_sentiment_exactly_at_veto_boundary_does_not_veto():
    # live_sentiment == -0.4: condition is strictly less-than, so no veto
    gate = _make_gate_with_mock_model(threshold=0.55)
    gate.live_sentiment = -0.4   # exactly at boundary — should NOT veto
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 1  # not vetoed

def test_sentiment_exactly_at_boost_boundary_does_not_boost():
    # live_sentiment == +0.3: condition is strictly greater-than, so no boost
    gate = _make_gate_with_mock_model(threshold=0.72)
    gate.live_sentiment = +0.3   # exactly at boundary — should NOT boost
    df = _make_df()
    result = gate.approve(df, _RAW_BUY)
    assert result["signal"] == 0  # not boosted (0.70 < 0.72, no boost fires)
