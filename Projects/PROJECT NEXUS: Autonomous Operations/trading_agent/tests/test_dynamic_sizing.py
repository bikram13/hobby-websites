"""Tests for dynamic position sizing based on gate_prob."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config
from risk_manager import RiskManager


def _rm():
    return RiskManager(config)


def test_base_prob_gives_min_position():
    """gate_prob=0.55 → ~8% of portfolio."""
    rm = _rm()
    qty = rm.calculate_position_size(100_000, 1000.0, gate_prob=0.55)
    capital_used = qty * 1000.0
    assert 7_000 <= capital_used <= 9_000, f"Expected ~8000, got {capital_used}"


def test_high_prob_gives_max_position():
    """gate_prob=1.0 → ~15% of portfolio."""
    rm = _rm()
    qty = rm.calculate_position_size(100_000, 1000.0, gate_prob=1.0)
    capital_used = qty * 1000.0
    assert 14_000 <= capital_used <= 15_000, f"Expected ~15000, got {capital_used}"


def test_mid_prob_gives_mid_position():
    """gate_prob=0.775 (midpoint) → ~11.5% of portfolio."""
    rm = _rm()
    qty = rm.calculate_position_size(100_000, 1000.0, gate_prob=0.775)
    capital_used = qty * 1000.0
    assert 10_500 <= capital_used <= 12_500, f"Expected ~11500, got {capital_used}"


def test_no_gate_prob_uses_default():
    """Calling without gate_prob uses base (0.55 → ~8%)."""
    rm = _rm()
    qty_default  = rm.calculate_position_size(100_000, 1000.0)
    qty_explicit = rm.calculate_position_size(100_000, 1000.0, gate_prob=0.55)
    assert qty_default == qty_explicit


def test_gate_prob_below_threshold_clamped():
    """gate_prob below 0.55 is clamped to 0.55 (minimum position)."""
    rm = _rm()
    qty_clamped = rm.calculate_position_size(100_000, 1000.0, gate_prob=0.30)
    qty_base    = rm.calculate_position_size(100_000, 1000.0, gate_prob=0.55)
    assert qty_clamped == qty_base


def test_gate_prob_above_one_clamped():
    """gate_prob above 1.0 is clamped to 1.0 (maximum position)."""
    rm = _rm()
    qty_over = rm.calculate_position_size(100_000, 1000.0, gate_prob=1.5)
    qty_max  = rm.calculate_position_size(100_000, 1000.0, gate_prob=1.0)
    assert qty_over == qty_max


def test_returns_zero_for_tiny_portfolio():
    """Returns 0 when position is too small to buy 1 share."""
    rm = _rm()
    qty = rm.calculate_position_size(100, 1000.0, gate_prob=0.55)
    assert qty == 0


def test_gate_prob_overrides_signal_strength():
    """gate_prob takes precedence over legacy signal_strength."""
    rm = _rm()
    qty1 = rm.calculate_position_size(100_000, 1000.0, signal_strength=1.0, gate_prob=0.55)
    qty2 = rm.calculate_position_size(100_000, 1000.0, signal_strength=0.5, gate_prob=0.55)
    assert qty1 == qty2
