# NEXUS BRAIN — Label Generator
# For each BUY signal, computes whether the trade was actually profitable.
# Labels are forward-looking — uses data *after* the signal date.
#
# Label = 1 (WIN)  if max forward return within hold_days >= win_threshold
# Label = 0 (LOSS) otherwise
#
# Also generates the full training dataset (features + label) by:
#   1. Running compute_all_signals() per strategy on full historical data
#   2. At each BUY signal date, computing features on the look-back window
#   3. Looking forward hold_days to determine outcome

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ml.feature_engineer import compute_features, FEATURE_COLS


def label_signal(df: pd.DataFrame, signal_idx: int,
                 hold_days: int = 10, win_threshold: float = 0.02) -> int | None:
    """
    Determine if a BUY signal at df.index[signal_idx] was a winner.

    Win = max close in the next hold_days bars rises >= win_threshold above entry.
    Returns 1 (win), 0 (loss), or None if insufficient forward data.
    """
    entry_price = float(df["close"].iloc[signal_idx])
    if entry_price <= 0:
        return None

    forward = df["close"].iloc[signal_idx + 1: signal_idx + 1 + hold_days]
    if len(forward) < hold_days // 2:   # need at least half the window
        return None

    max_return = float((forward.max() - entry_price) / entry_price)
    return 1 if max_return >= win_threshold else 0


def build_training_dataset(data: dict, strategy,
                            hold_days: int = 10,
                            win_threshold: float = 0.02,
                            nifty_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Build a labelled feature dataset from cached OHLCV data + a strategy instance.

    Parameters
    ----------
    data          : {symbol: OHLCV DataFrame} — same dict used by backtester
    strategy      : any strategy with compute_all_signals(df) method
    hold_days     : how many trading days forward to measure outcome
    win_threshold : minimum forward return to count as a win

    Returns
    -------
    DataFrame with columns = FEATURE_COLS + ['label', 'symbol', 'date']
    """
    rows = []

    for sym, df in data.items():
        if len(df) < 60:
            continue

        # Get all buy signals for this symbol
        signals = strategy.compute_all_signals(df)
        if not signals:
            continue

        # Build index lookup for fast positional access
        idx_map = {date: i for i, date in enumerate(df.index)}

        for date, sig in signals.items():
            if sig["signal"] != 1:
                continue

            pos = idx_map.get(date)
            if pos is None or pos < 30:   # need enough look-back for features
                continue

            # Features: window up to and including signal date
            window = df.iloc[: pos + 1]
            features = compute_features(window, nifty_df=nifty_df)
            if features is None:
                continue

            # Label: forward return after signal date
            label = label_signal(df, pos, hold_days=hold_days, win_threshold=win_threshold)
            if label is None:
                continue

            row = {col: features[col] for col in FEATURE_COLS}
            row["label"]  = label
            row["symbol"] = sym
            row["date"]   = date
            row["strategy"] = strategy.name
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df_out = pd.DataFrame(rows)
    df_out["date"] = pd.to_datetime(df_out["date"])
    return df_out.sort_values("date").reset_index(drop=True)
