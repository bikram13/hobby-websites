# trading_agent/ml/earnings_detector.py
# Detects earnings announcement dates from price behaviour (proxy method).
# Uses largest single-day absolute return per calendar quarter as earnings date.
# Threshold: gap must be >= 3% to be meaningful.

import pandas as pd


def find_earnings_dates(df: pd.DataFrame, min_gap_pct: float = 0.03) -> list[pd.Timestamp]:
    """
    Detect earnings announcement dates from OHLCV data.
    Returns list of dates where the largest absolute daily return per
    calendar quarter exceeds min_gap_pct.

    df            — OHLCV DataFrame with DatetimeIndex
    min_gap_pct   — minimum absolute daily return to qualify (default 3%)
    """
    if len(df) < 20:
        return []

    close = df["close"]
    daily_ret = close.pct_change().abs()

    # Group by calendar quarter
    quarters = daily_ret.groupby([daily_ret.index.year, daily_ret.index.quarter])
    dates = []
    for _, group in quarters:
        if group.empty:
            continue
        max_ret = group.max()
        if pd.isna(max_ret) or max_ret < min_gap_pct:
            continue
        dates.append(group.idxmax())

    return sorted(dates)


def earnings_momentum_score(
    df: pd.DataFrame,
    nifty_df: pd.DataFrame,
    signal_date: pd.Timestamp,
    lookback_days: int = 90,
    forward_days: int = 20,
) -> float:
    """
    Compute stock's post-earnings outperformance vs Nifty.

    Finds the most recent earnings date within lookback_days before signal_date.
    Returns: stock 20d return after earnings date - Nifty 20d return after same date.
    Returns 0.0 if no earnings date found or insufficient forward data.

    df            — OHLCV DataFrame for the stock (full history)
    nifty_df      — OHLCV DataFrame for ^NSEI (full history)
    signal_date   — the date of the BUY signal
    lookback_days — how far back to search for the most recent earnings date
    forward_days  — days forward to measure post-earnings return
    """
    if df is None or df.empty:
        return 0.0
    if nifty_df is None or nifty_df.empty:
        return 0.0

    earnings_dates = find_earnings_dates(df)
    if not earnings_dates:
        return 0.0

    # Most recent earnings date before signal_date within lookback window
    cutoff = signal_date - pd.Timedelta(days=lookback_days)
    recent = [d for d in earnings_dates if cutoff <= d < signal_date]
    if not recent:
        return 0.0

    earnings_date = recent[-1]

    # Stock return: forward_days after earnings date
    stock_close = df["close"]
    stock_after = stock_close[stock_close.index > earnings_date].iloc[:forward_days]
    if len(stock_after) < forward_days // 2:
        return 0.0
    stock_base = stock_close[stock_close.index <= earnings_date]
    if stock_base.empty or stock_base.iloc[-1] == 0:
        return 0.0
    stock_ret = float(stock_after.iloc[-1] / stock_base.iloc[-1] - 1)

    # Nifty return: same window
    nifty_close = nifty_df["close"]
    nifty_after = nifty_close[nifty_close.index > earnings_date].iloc[:forward_days]
    if len(nifty_after) < forward_days // 2:
        return 0.0
    nifty_base = nifty_close[nifty_close.index <= earnings_date]
    if nifty_base.empty:
        return 0.0
    nifty_ret = float(nifty_after.iloc[-1] / nifty_base.iloc[-1] - 1)

    return round(stock_ret - nifty_ret, 5)
