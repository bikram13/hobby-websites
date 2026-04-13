"""Tests for sentiment_scorer.py — FinBERT scoring and cache logic."""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
import ml.sentiment_scorer as scorer_mod
from ml.sentiment_scorer import (
    get_sentiment_score,
    _build_cache_key,
    _score_headlines_mock,
)


# ── _build_cache_key ──────────────────────────────────────────────────────────

def test_cache_key_includes_symbol():
    key = _build_cache_key("RELIANCE.NS", ["headline"], "2026-04-14")
    assert "RELIANCE.NS" in key

def test_cache_key_includes_date():
    key = _build_cache_key("TCS.NS", ["headline"], "2026-04-14")
    assert "2026-04-14" in key

def test_cache_key_different_headlines_give_different_keys():
    k1 = _build_cache_key("TCS.NS", ["good news"], "2026-04-14")
    k2 = _build_cache_key("TCS.NS", ["bad news"],  "2026-04-14")
    assert k1 != k2

def test_cache_key_same_inputs_give_same_key():
    k1 = _build_cache_key("TCS.NS", ["news A", "news B"], "2026-04-14")
    k2 = _build_cache_key("TCS.NS", ["news A", "news B"], "2026-04-14")
    assert k1 == k2


# ── _score_headlines_mock (used when transformers not installed) ──────────────

def test_mock_scorer_returns_zero_for_empty():
    assert _score_headlines_mock([]) == 0.0

def test_mock_scorer_returns_float():
    result = _score_headlines_mock(["some headline"])
    assert isinstance(result, float)
    assert -1.0 <= result <= 1.0


# ── get_sentiment_score ───────────────────────────────────────────────────────

def test_returns_zero_for_no_headlines():
    score = get_sentiment_score("RELIANCE.NS", [], date_str="2026-04-14")
    assert score == 0.0

def test_caches_result_to_disk(tmp_path):
    cache_file = tmp_path / "sentiment_cache.json"
    with patch.object(scorer_mod, "CACHE_PATH", cache_file):
        with patch.object(scorer_mod, "_score_headlines", return_value=0.42):
            score1 = get_sentiment_score("TCS.NS", ["TCS profit up"], date_str="2026-04-14")
            score2 = get_sentiment_score("TCS.NS", ["TCS profit up"], date_str="2026-04-14")
    assert score1 == 0.42
    assert score2 == 0.42  # served from cache
    assert cache_file.exists()

def test_score_is_in_valid_range(tmp_path):
    cache_file = tmp_path / "sentiment_cache.json"
    with patch.object(scorer_mod, "CACHE_PATH", cache_file):
        with patch.object(scorer_mod, "_score_headlines", return_value=0.75):
            score = get_sentiment_score("INFY.NS", ["Infosys wins big deal"], date_str="2026-04-14")
    assert -1.0 <= score <= 1.0

def test_negative_sentiment_returns_negative_score(tmp_path):
    cache_file = tmp_path / "sentiment_cache.json"
    with patch.object(scorer_mod, "CACHE_PATH", cache_file):
        with patch.object(scorer_mod, "_score_headlines", return_value=-0.6):
            score = get_sentiment_score("YESBANK.NS", ["Yes Bank fraud probe widens"], date_str="2026-04-14")
    assert score < 0
