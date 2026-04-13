# NEXUS BRAIN — Feature Engineer
# Computes 19 features at each BUY signal date for the GBM gate.
#
# Feature groups:
#   Trend       : ADX, EMA ratio, price vs EMA50/EMA200
#   Momentum    : RSI, MACD histogram+slope, 5/10/20-day returns
#   Mean-rev    : BB z-score, distance from 52-week high
#   Volatility  : ATR%, BB width
#   Volume      : volume ratio vs 20d avg
#   Market      : trend consistency (% bars above EMA21 in last 20 days)
#   Regime      : nifty_above_ema200, nifty_pct_vs_ema200  (NEW)
#   Fundamental : earnings_momentum_score                   (NEW)

import numpy as np
import pandas as pd
from ml.earnings_detector import earnings_momentum_score as _earnings_score


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(span=period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(span=period, adjust=False).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def _adx(df: pd.DataFrame, period: int = 14) -> float:
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    dm_plus  = (high - high.shift(1)).clip(lower=0)
    dm_minus = (low.shift(1) - low).clip(lower=0)
    dm_plus  = dm_plus.where(dm_plus > dm_minus, 0)
    dm_minus = dm_minus.where(dm_minus > dm_plus, 0)
    atr    = tr.ewm(span=period, adjust=False).mean()
    di_pos = 100 * dm_plus.ewm(span=period, adjust=False).mean()  / atr.replace(0, 1e-10)
    di_neg = 100 * dm_minus.ewm(span=period, adjust=False).mean() / atr.replace(0, 1e-10)
    dx     = 100 * (di_pos - di_neg).abs() / (di_pos + di_neg).replace(0, 1e-10)
    adx    = dx.ewm(span=period, adjust=False).mean()
    return float(adx.iloc[-1])


def _atr_pct(df: pd.DataFrame, period: int = 14) -> float:
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(span=period, adjust=False).mean().iloc[-1]
    return float(atr / close.iloc[-1]) if close.iloc[-1] > 0 else 0.0


def compute_features(df: pd.DataFrame, nifty_df: pd.DataFrame = None) -> dict | None:
    """
    Compute all features using data available up to the signal date.
    Returns a flat dict of floats, or None if insufficient data.

    df  — OHLCV DataFrame ending on the signal date (warmup rows included)
    """
    if len(df) < 60:
        return None

    close  = df["close"]
    high   = df["high"]
    low    = df["low"]
    volume = df.get("volume", pd.Series(dtype=float))

    price = float(close.iloc[-1])
    if price <= 0:
        return None

    # ── Trend features ────────────────────────────────────────────────────────
    ema9  = float(_ema(close, 9).iloc[-1])
    ema21 = float(_ema(close, 21).iloc[-1])
    ema50 = float(_ema(close, 50).iloc[-1])
    ema200_series = _ema(close, 200)
    ema200 = float(ema200_series.iloc[-1])

    ema_ratio        = ema9 / ema21 if ema21 > 0 else 1.0          # > 1 = fast above slow
    price_vs_ema50   = price / ema50  - 1 if ema50  > 0 else 0.0   # % above/below EMA50
    price_vs_ema200  = price / ema200 - 1 if ema200 > 0 else 0.0   # long-term trend context
    adx_value        = _adx(df)

    # ── Momentum features ─────────────────────────────────────────────────────
    rsi_value = _rsi(close)

    ema_fast   = _ema(close, 12)
    ema_slow   = _ema(close, 26)
    macd_line  = ema_fast - ema_slow
    signal_line= macd_line.ewm(span=9, adjust=False).mean()
    macd_hist  = float((macd_line - signal_line).iloc[-1])
    macd_hist_prev = float((macd_line - signal_line).iloc[-2]) if len(df) > 2 else 0.0
    macd_hist_slope = macd_hist - macd_hist_prev                    # rising/falling histogram

    ret_5d  = float(close.iloc[-1] / close.iloc[-6]  - 1) if len(close) > 6  else 0.0
    ret_10d = float(close.iloc[-1] / close.iloc[-11] - 1) if len(close) > 11 else 0.0
    ret_20d = float(close.iloc[-1] / close.iloc[-21] - 1) if len(close) > 21 else 0.0

    # ── Mean-reversion / range features ──────────────────────────────────────
    sma20 = float(close.rolling(20).mean().iloc[-1])
    std20 = float(close.rolling(20).std().iloc[-1])
    bb_zscore = (price - sma20) / std20 if std20 > 0 else 0.0      # <-2 = oversold, >+2 = overbought
    bb_width  = (2 * std20) / sma20     if sma20 > 0 else 0.0      # normalised band width

    # Distance from 52-week high (ladder-buy insight from strategy notes)
    hi52 = float(high.iloc[-252:].max()) if len(high) >= 252 else float(high.max())
    dist_from_52wk_high = (price - hi52) / hi52 if hi52 > 0 else 0.0  # 0 = at high, -0.2 = 20% below

    # ── Volatility ────────────────────────────────────────────────────────────
    atr_pct = _atr_pct(df)

    # ── Volume ────────────────────────────────────────────────────────────────
    if volume is not None and len(volume) >= 21 and float(volume.iloc[-1]) > 0:
        avg_vol = float(volume.iloc[-21:-1].mean())
        vol_ratio = float(volume.iloc[-1]) / avg_vol if avg_vol > 0 else 1.0
    else:
        vol_ratio = 1.0

    # ── Market / breadth proxy ────────────────────────────────────────────────
    # % of last 20 bars where close > EMA21 (trend consistency)
    ema21_series = _ema(close, 21)
    trend_consistency = float((close.iloc[-20:] > ema21_series.iloc[-20:]).mean())

    # ── Nifty regime features ─────────────────────────────────────────────────────
    nifty_above_ema200  = 1.0   # default: neutral (assume uptrend)
    nifty_pct_vs_ema200 = 0.0   # default: neutral
    if nifty_df is not None and not nifty_df.empty:
        # Align to signal date: use Nifty data up to and including signal date
        nifty_window = nifty_df[nifty_df.index <= df.index[-1]]
        if len(nifty_window) >= 200:
            nifty_close  = nifty_window["close"]
            nifty_ema200 = float(_ema(nifty_close, 200).iloc[-1])
            nifty_last   = float(nifty_close.iloc[-1])
            nifty_above_ema200  = 1.0 if nifty_last > nifty_ema200 else 0.0
            nifty_pct_vs_ema200 = round((nifty_last - nifty_ema200) / nifty_ema200, 5)

    # ── Earnings momentum (fundamental proxy) ────────────────────────────────
    earn_score = 0.0   # default: neutral
    if nifty_df is not None and not nifty_df.empty:
        earn_score = _earnings_score(df, nifty_df, signal_date=df.index[-1])

    return {
        # Trend
        "ema_ratio":           round(ema_ratio, 5),
        "price_vs_ema50":      round(price_vs_ema50, 5),
        "price_vs_ema200":     round(price_vs_ema200, 5),
        "adx":                 round(adx_value, 3),
        # Momentum
        "rsi":                 round(rsi_value, 3),
        "macd_hist":           round(macd_hist, 5),
        "macd_hist_slope":     round(macd_hist_slope, 5),
        "ret_5d":              round(ret_5d, 5),
        "ret_10d":             round(ret_10d, 5),
        "ret_20d":             round(ret_20d, 5),
        # Mean-reversion
        "bb_zscore":           round(bb_zscore, 4),
        "bb_width":            round(bb_width, 5),
        "dist_from_52wk_high": round(dist_from_52wk_high, 5),
        # Volatility
        "atr_pct":             round(atr_pct, 5),
        # Volume
        "vol_ratio":           round(vol_ratio, 4),
        # Market structure
        "trend_consistency":   round(trend_consistency, 4),
        # Nifty regime
        "nifty_above_ema200":  nifty_above_ema200,
        "nifty_pct_vs_ema200": nifty_pct_vs_ema200,
        # Fundamental proxy
        "earnings_momentum":   round(earn_score, 5),
        # Context (not used as feature, useful for debugging)
        "_price":              round(price, 2),
    }


FEATURE_COLS = [
    "ema_ratio", "price_vs_ema50", "price_vs_ema200", "adx",
    "rsi", "macd_hist", "macd_hist_slope",
    "ret_5d", "ret_10d", "ret_20d",
    "bb_zscore", "bb_width", "dist_from_52wk_high",
    "atr_pct", "vol_ratio", "trend_consistency",
    "nifty_above_ema200", "nifty_pct_vs_ema200", "earnings_momentum",
]
