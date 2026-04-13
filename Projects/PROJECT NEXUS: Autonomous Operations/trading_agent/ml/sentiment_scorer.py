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
import logging
from datetime import datetime, timezone
from pathlib import Path

_log = logging.getLogger(__name__)

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
    except Exception as exc:
        _log.warning("sentiment_scorer: FinBERT unavailable (%s), using keyword fallback", exc)
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
