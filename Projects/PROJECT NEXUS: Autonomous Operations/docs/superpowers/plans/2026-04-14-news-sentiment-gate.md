# News Sentiment Gate — Sprint 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add FinBERT-powered news sentiment as a live post-filter on the ML signal gate, vetoing trades on strongly negative news and boosting confidence on strongly positive news.

**Architecture:** Historical news is not available for free 10-year backtests, so sentiment is implemented as a live-only post-filter on `SignalGate.approve()` — not a GBM training feature. The GBM gate approves based on 19 technical features (unchanged). Then, if `gate.live_sentiment` is set, a second sentiment veto check runs: strongly negative news (-0.4 threshold) vetoes the trade; strongly positive news (>+0.3) lowers the required GBM probability by 0.05. At training time `live_sentiment` stays 0.0, so training is unaffected. During live trading, the caller sets `gate.live_sentiment = scorer.get_sentiment_score(...)` before each call to `approve()`.

**Tech Stack:** `transformers` (ProsusAI/finbert), `torch`, Python stdlib `urllib` + `xml.etree` for Google News RSS (no API key). File-based JSON cache at `data/ml/sentiment_cache.json`.

---

## File Map

| Action | File | Purpose |
|--------|------|---------|
| Create | `trading_agent/ml/news_fetcher.py` | Fetch headlines from Google News RSS per symbol |
| Create | `trading_agent/ml/sentiment_scorer.py` | FinBERT wrapper; disk-cached score [-1, +1] |
| Modify | `trading_agent/ml/signal_gate.py` | Add `live_sentiment` field + sentiment veto in `approve()` |
| Create | `trading_agent/tests/__init__.py` | Make tests a package |
| Create | `trading_agent/tests/test_news_fetcher.py` | Tests for headline fetching + parsing |
| Create | `trading_agent/tests/test_sentiment_scorer.py` | Tests for scoring logic + cache |
| Create | `trading_agent/tests/test_signal_gate_sentiment.py` | Tests for veto / boost logic in approve() |

---

## Task 1: `news_fetcher.py` — Google News RSS headline fetcher

**Files:**
- Create: `trading_agent/ml/news_fetcher.py`
- Create: `trading_agent/tests/__init__.py`
- Create: `trading_agent/tests/test_news_fetcher.py`

- [ ] **Step 1: Create the tests directory and write failing tests**

```bash
mkdir -p "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent/tests"
touch "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent/tests/__init__.py"
```

Write `trading_agent/tests/test_news_fetcher.py`:

```python
"""Tests for news_fetcher.py — headline fetching and parsing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from ml.news_fetcher import fetch_headlines, _build_rss_url, _parse_rss


# ── _build_rss_url ────────────────────────────────────────────────────────────

def test_build_url_strips_ns_suffix():
    url = _build_rss_url("RELIANCE.NS")
    assert "RELIANCE.NS" not in url
    assert "RELIANCE" in url

def test_build_url_strips_bo_suffix():
    url = _build_rss_url("HDFCBANK.BO")
    assert "HDFCBANK.BO" not in url
    assert "HDFCBANK" in url

def test_build_url_is_google_news_rss():
    url = _build_rss_url("TCS.NS")
    assert url.startswith("https://news.google.com/rss/search")
    assert "TCS" in url

def test_build_url_already_clean():
    url = _build_rss_url("INFY")
    assert "INFY" in url


# ── _parse_rss ────────────────────────────────────────────────────────────────

def test_parse_rss_extracts_titles():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title>TCS Q4 profit jumps 12%</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
      <item><title>TCS wins $500M deal</title><pubDate>Sun, 13 Apr 2026 09:00:00 GMT</pubDate></item>
    </channel></rss>"""
    results = _parse_rss(xml_bytes, max_articles=10)
    assert len(results) == 2
    assert results[0][0] == "TCS Q4 profit jumps 12%"
    assert results[1][0] == "TCS wins $500M deal"

def test_parse_rss_respects_max_articles():
    items = "".join(
        f"<item><title>News {i}</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>"
        for i in range(10)
    )
    xml_bytes = f"""<?xml version="1.0"?><rss><channel>{items}</channel></rss>""".encode()
    results = _parse_rss(xml_bytes, max_articles=3)
    assert len(results) == 3

def test_parse_rss_skips_empty_titles():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title></title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
      <item><title>Real headline</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
    </channel></rss>"""
    results = _parse_rss(xml_bytes, max_articles=10)
    assert len(results) == 1
    assert results[0][0] == "Real headline"

def test_parse_rss_returns_empty_on_malformed_xml():
    results = _parse_rss(b"this is not xml", max_articles=10)
    assert results == []


# ── fetch_headlines (network-mocked) ─────────────────────────────────────────

def test_fetch_headlines_returns_list_on_success():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title>Reliance Industries posts record revenue</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
    </channel></rss>"""

    with patch("ml.news_fetcher.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = xml_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        results = fetch_headlines("RELIANCE.NS")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0][0] == "Reliance Industries posts record revenue"

def test_fetch_headlines_returns_empty_on_network_error():
    with patch("ml.news_fetcher.urllib.request.urlopen", side_effect=Exception("timeout")):
        results = fetch_headlines("RELIANCE.NS")
        assert results == []

def test_fetch_headlines_returns_empty_for_empty_symbol():
    results = fetch_headlines("")
    assert results == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_news_fetcher.py -v 2>&1 | head -30
```

Expected: `ImportError` or `ModuleNotFoundError: No module named 'ml.news_fetcher'`

- [ ] **Step 3: Write `trading_agent/ml/news_fetcher.py`**

```python
"""
Fetch financial news headlines for an NSE symbol via Google News RSS.
No API key required. Returns recent articles only (not historical).

Used at live inference time only — not during GBM gate training.
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


def _build_rss_url(symbol: str) -> str:
    """Build Google News RSS URL for a symbol."""
    clean = symbol.replace(".NS", "").replace(".BO", "")
    query = f"{clean} NSE stock India"
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"


def _parse_rss(content: bytes, max_articles: int) -> list[tuple[str, str]]:
    """Parse RSS XML bytes into list of (headline, pub_date) tuples."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []
    channel = root.find("channel")
    if channel is None:
        return []
    results = []
    for item in channel.findall("item")[:max_articles]:
        title = (item.findtext("title") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if title:
            results.append((title, pub_date))
    return results


def fetch_headlines(symbol: str, max_articles: int = 20) -> list[tuple[str, str]]:
    """
    Fetch news headlines for an NSE symbol from Google News RSS.

    Parameters
    ----------
    symbol       : NSE ticker e.g. "RELIANCE.NS" (exchange suffix is stripped)
    max_articles : maximum number of headlines to return

    Returns
    -------
    List of (headline_str, pub_date_str) tuples. Empty list on any failure.
    """
    if not symbol:
        return []
    url = _build_rss_url(symbol)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
        return _parse_rss(content, max_articles)
    except Exception:
        return []
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_news_fetcher.py -v
```

Expected: all 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations"
git add trading_agent/ml/news_fetcher.py trading_agent/tests/__init__.py trading_agent/tests/test_news_fetcher.py
git commit -m "feat(sentiment): add news_fetcher.py with Google News RSS + 10 tests"
```

---

## Task 2: `sentiment_scorer.py` — FinBERT wrapper with disk cache

**Files:**
- Create: `trading_agent/ml/sentiment_scorer.py`
- Create: `trading_agent/tests/test_sentiment_scorer.py`

- [ ] **Step 1: Write failing tests**

Write `trading_agent/tests/test_sentiment_scorer.py`:

```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_sentiment_scorer.py -v 2>&1 | head -20
```

Expected: `ImportError: cannot import name '_score_headlines_mock' from 'ml.sentiment_scorer'`

- [ ] **Step 3: Write `trading_agent/ml/sentiment_scorer.py`**

```python
"""
FinBERT-based news sentiment scorer for NEXUS.
Computes a sentiment score in [-1, +1] from a list of headlines.
Caches results to data/ml/sentiment_cache.json (keyed by symbol + date + headline hash).

Score interpretation:
  +1.0  : all headlines strongly positive
   0.0  : neutral / no headlines / model unavailable
  -1.0  : all headlines strongly negative

FinBERT is loaded lazily on first call (~440 MB, CPU-only fine for <=20 headlines).
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent.parent / "data" / "ml" / "sentiment_cache.json"

# Lazy globals — loaded on first _score_headlines() call
_tokenizer = None
_model = None
_id2label = None
_device = None
_finbert_available = None   # None = not yet attempted; True/False after attempt


def _load_finbert() -> bool:
    """Load ProsusAI/finbert from HuggingFace. Returns True if successful."""
    global _tokenizer, _model, _id2label, _device, _finbert_available
    if _finbert_available is not None:
        return _finbert_available
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        _model.to(_device)
        _model.eval()
        # Read label mapping from model config (robust to label order changes)
        _id2label = {v.lower(): k for k, v in _model.config.id2label.items()}
        _finbert_available = True
        return True
    except Exception:
        _finbert_available = False
        return False


def _score_headlines(headlines: list[str]) -> float:
    """
    Run FinBERT on headlines. Returns average sentiment in [-1, +1].
    Falls back to _score_headlines_mock() if transformers is not installed.
    """
    if not headlines:
        return 0.0
    if not _load_finbert():
        return _score_headlines_mock(headlines)

    import torch

    pos_idx = _id2label.get("positive", 0)
    neg_idx = _id2label.get("negative", 1)
    scores = []
    for text in headlines:
        inputs = _tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=128, padding=True
        )
        inputs = {k: v.to(_device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = _model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        scores.append(float(probs[pos_idx]) - float(probs[neg_idx]))

    return round(sum(scores) / len(scores), 4)


def _score_headlines_mock(headlines: list[str]) -> float:
    """
    Keyword-based fallback when transformers is not installed.
    Used in tests and environments without GPU/transformers.
    Returns a rough sentiment in [-1, +1].
    """
    if not headlines:
        return 0.0
    pos_words = {"profit", "gain", "record", "win", "growth", "surge", "beat", "strong", "upgrade", "buy"}
    neg_words = {"loss", "fraud", "probe", "fall", "decline", "downgrade", "sell", "miss", "cut", "weak"}
    scores = []
    for h in headlines:
        words = set(h.lower().split())
        p = len(words & pos_words)
        n = len(words & neg_words)
        if p + n > 0:
            scores.append((p - n) / (p + n))
        else:
            scores.append(0.0)
    return round(sum(scores) / len(scores), 4)


def _build_cache_key(symbol: str, headlines: list[str], date_str: str) -> str:
    """Build a deterministic cache key from symbol + date + headline content."""
    headline_hash = hashlib.md5("|".join(headlines).encode()).hexdigest()[:8]
    return f"{symbol}:{date_str}:{headline_hash}"


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def get_sentiment_score(
    symbol: str,
    headlines: list[str],
    date_str: str = "live",
) -> float:
    """
    Compute (or retrieve from cache) the sentiment score for a symbol.

    Parameters
    ----------
    symbol    : e.g. "RELIANCE.NS"
    headlines : list of headline strings from news_fetcher.fetch_headlines()
    date_str  : ISO date string used in cache key (default "live")

    Returns
    -------
    float in [-1.0, +1.0]. 0.0 if no headlines.
    """
    if not headlines:
        return 0.0

    key = _build_cache_key(symbol, headlines, date_str)
    cache = _load_cache()
    if key in cache:
        return cache[key]["score"]

    score = _score_headlines(headlines)
    cache[key] = {
        "score": score,
        "n_headlines": len(headlines),
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_cache(cache)
    return score
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_sentiment_scorer.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations"
git add trading_agent/ml/sentiment_scorer.py trading_agent/tests/test_sentiment_scorer.py
git commit -m "feat(sentiment): add sentiment_scorer.py with FinBERT + keyword fallback + disk cache"
```

---

## Task 3: Wire sentiment veto into `SignalGate.approve()`

**Files:**
- Modify: `trading_agent/ml/signal_gate.py`
- Create: `trading_agent/tests/test_signal_gate_sentiment.py`

The change: add `self.live_sentiment: float = 0.0` to `__init__`. In `approve()`, after the GBM approves a signal, run a second sentiment veto check:
- `live_sentiment < -0.4` → veto (override to signal=0 regardless of GBM)
- `live_sentiment > +0.3` → confidence boost (effective threshold reduced by 0.05)
- `live_sentiment` between -0.4 and +0.3 → no change (neutral zone)

**When to set `live_sentiment`:** The caller (live trading loop or agent) sets `gate.live_sentiment` before each stock's signal is evaluated. At training time it defaults to 0.0, so training is completely unaffected.

- [ ] **Step 1: Write failing tests**

Write `trading_agent/tests/test_signal_gate_sentiment.py`:

```python
"""Tests for sentiment veto/boost logic added to SignalGate.approve()."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from ml.signal_gate import SignalGate


def _make_gate_with_mock_model(threshold: float = 0.55):
    """Create a SignalGate with a mock model that always returns prob=0.70."""
    gate = SignalGate(threshold=threshold)
    gate.trained = True
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.30, 0.70]])
    gate.model = mock_model
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_signal_gate_sentiment.py -v 2>&1 | head -30
```

Expected: tests involving `live_sentiment` veto/boost fail because the logic doesn't exist yet.

- [ ] **Step 3: Edit `trading_agent/ml/signal_gate.py`**

Change 1 — add `live_sentiment` field in `__init__` (after `self.nifty_df = None` on line 42):

```python
        self.nifty_df     = None   # set before inference so approve() can pass it to features
        self.live_sentiment: float = 0.0  # set by caller before each stock's approve() call
```

Change 2 — replace the entire `approve()` method body (starting at `if not self.trained...`) with this updated version:

```python
    def approve(self, df_window: pd.DataFrame, raw_signal: dict) -> dict:
        """
        Given the OHLCV window up to the signal date and the raw strategy signal,
        return the signal if approved, else a zero-signal dict.

        Two-stage filter:
          Stage 1 — GBM gate: 19 technical features, P(win) >= effective_thresh
          Stage 2 — Sentiment veto/boost (live only, no effect during training):
            live_sentiment < -0.4  → veto even if GBM approved
            live_sentiment > +0.3  → lower effective threshold by 0.05
        """
        if not self.trained or raw_signal["signal"] != 1:
            return raw_signal

        features = compute_features(df_window, nifty_df=self.nifty_df)
        if features is None:
            return {"signal": 0, "strength": 0, "reason": "Gate: insufficient features"}

        X    = np.array([[features[c] for c in FEATURE_COLS]])
        prob = float(self.model.predict_proba(X)[0, 1])

        # Stage 1: Nifty bear-market soft gate
        bear_market      = features.get("nifty_above_ema200", 1.0) == 0.0
        effective_thresh = 0.75 if bear_market else self.threshold

        # Stage 2: Sentiment boost (applied before threshold check)
        sentiment_boost = False
        if self.live_sentiment > 0.3:
            effective_thresh = max(0.40, effective_thresh - 0.05)
            sentiment_boost  = True

        if prob >= effective_thresh:
            # Stage 2: Sentiment veto (applied after GBM approves)
            if self.live_sentiment < -0.4:
                return {
                    "signal":           0,
                    "strength":         0,
                    "reason":           f"Sentiment veto (score={self.live_sentiment:.2f} < -0.40)",
                    "gate_prob":        round(prob, 3),
                    "gate_approved":    False,
                    "sentiment_vetoed": True,
                    "bear_market":      bear_market,
                }
            approved = dict(raw_signal)
            approved["strength"]        = round(prob, 3)
            approved["gate_prob"]       = round(prob, 3)
            approved["gate_approved"]   = True
            approved["bear_market"]     = bear_market
            approved["sentiment_boost"] = sentiment_boost
            approved["sentiment_score"] = self.live_sentiment
            return approved

        return {
            "signal":        0,
            "strength":      0,
            "reason":        f"Gate blocked (P={prob:.2f} < {effective_thresh:.2f}{'  [bear]' if bear_market else ''})",
            "gate_prob":     round(prob, 3),
            "gate_approved": False,
            "bear_market":   bear_market,
        }
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python -m pytest tests/test_signal_gate_sentiment.py -v
```

Expected: all 9 tests PASS.

Also run the full test suite to ensure no regressions:

```bash
python -m pytest tests/ -v
```

Expected: all tests across all 3 test files PASS.

- [ ] **Step 5: Commit**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations"
git add trading_agent/ml/signal_gate.py trading_agent/tests/test_signal_gate_sentiment.py
git commit -m "feat(sentiment): add sentiment veto/boost to SignalGate.approve() with 9 tests"
```

---

## Task 4: Integration smoke test — live headlines + scoring for 3 symbols

**Files:**
- No new files — run a short script to verify the full chain end-to-end

This task verifies: fetch_headlines → get_sentiment_score → score is reasonable, and that the chain doesn't crash on a real network call.

- [ ] **Step 1: Write and run the smoke test script**

From the `trading_agent/` directory, run:

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python3 -c "
import sys
sys.path.insert(0, '.')
from ml.news_fetcher import fetch_headlines
from ml.sentiment_scorer import get_sentiment_score
from datetime import date

symbols = ['RELIANCE.NS', 'TCS.NS', 'YESBANK.NS']
today = date.today().isoformat()

print(f'Smoke test: live news sentiment ({today})')
print('-' * 55)
for sym in symbols:
    headlines = fetch_headlines(sym, max_articles=10)
    score = get_sentiment_score(sym, [h for h, _ in headlines], date_str=today)
    print(f'{sym:<20} headlines={len(headlines):<3} score={score:+.3f}')
    if headlines:
        print(f'  Sample: {headlines[0][0][:70]}')
print()
print('Cache written to data/ml/sentiment_cache.json')
"
```

Expected output (exact values will vary by day):
```
Smoke test: live news sentiment (2026-04-14)
-------------------------------------------------------
RELIANCE.NS          headlines=10  score=+0.123
  Sample: Reliance Industries Q4 results beat estimates...
TCS.NS               headlines=10  score=+0.045
  Sample: TCS signs $400M deal with European bank...
YESBANK.NS           headlines=10  score=-0.210
  Sample: Yes Bank shares fall on profit-taking...

Cache written to data/ml/sentiment_cache.json
```

Acceptable: `headlines=0` for any symbol (Google News has rate limits). Score must be a float in [-1, +1].

- [ ] **Step 2: Verify cache file was created**

```bash
cat "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/data/ml/sentiment_cache.json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d)} entries cached')"
```

Expected: `3 entries cached` (one per symbol, or 0 if no headlines returned).

- [ ] **Step 3: Install transformers if not already present**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
pip install transformers torch --quiet 2>&1 | tail -5
```

If transformers installs successfully, re-run the smoke test from Step 1 — scores should now use FinBERT instead of the keyword fallback.

- [ ] **Step 4: Add `transformers` and `torch` to requirements.txt**

Read `trading_agent/requirements.txt`, then add the two lines if not already present:

```
transformers>=4.40.0
torch>=2.2.0
```

- [ ] **Step 5: Commit**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations"
git add trading_agent/requirements.txt
git commit -m "feat(sentiment): add transformers + torch to requirements for FinBERT"
```

---

## Task 5: Run full backtest and verify gate still works correctly

The existing training pipeline is unchanged — `live_sentiment` defaults to 0.0 throughout training, so win rate should not regress. This task confirms that, then documents the readiness for live trading.

- [ ] **Step 1: Run the existing backtest-only check**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python ml/train_gate.py --backtest-only --threshold 0.55 --years 3
```

Expected: win rate ≥ 60% (should match prior results of ~62.6% — no regression from sentiment changes).

- [ ] **Step 2: Confirm the sentiment fields appear in signal output**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/trading_agent"
python3 -c "
import sys, numpy as np, pandas as pd
sys.path.insert(0, '.')
from ml.signal_gate import SignalGate

gate = SignalGate()
gate.load()
gate.live_sentiment = 0.65  # simulate positive news

# Tiny OHLCV df (won't have enough rows for features, but tests approve() path)
print('gate.live_sentiment:', gate.live_sentiment)
print('Approve returns sentinel for short df:', gate.approve(pd.DataFrame(), {'signal': 1, 'strength': 0.8}))
print('Sell signal bypassed:', gate.approve(pd.DataFrame(), {'signal': -1, 'strength': 0.5}))
"
```

Expected output:
```
gate.live_sentiment: 0.65
Approve returns sentinel for short df: {'signal': 0, 'strength': 0, 'reason': 'Gate: insufficient features'}
Sell signal bypassed: {'signal': -1, 'strength': 0.5}
```

- [ ] **Step 3: Commit final state**

```bash
cd "/Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations"
git add -A
git commit -m "feat(sentiment): Sprint 1 complete — FinBERT sentiment veto/boost wired into SignalGate"
```

---

## How To Use In Live Trading

When wiring into the live agent (`agent.py` — update deferred per CLAUDE.md):

```python
from ml.news_fetcher import fetch_headlines
from ml.sentiment_scorer import get_sentiment_score
from datetime import date

# Before evaluating each symbol's signal:
today = date.today().isoformat()
headlines = fetch_headlines(symbol, max_articles=15)
gate.live_sentiment = get_sentiment_score(symbol, [h for h, _ in headlines], date_str=today)

# Then call gate as normal:
approved = gate.approve(df_window, raw_signal)
```

The gate will automatically veto trades on strongly negative news and boost borderline signals on strongly positive news.
