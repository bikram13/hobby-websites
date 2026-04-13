#!/usr/bin/env python3
# NEXUS BRAIN — ML Gate Training Script
# Trains the GBM signal gate on historical NSE data.
#
# Process:
#   1. Download N years of data (or use cached)
#   2. Run ADX + BB strategies in parallel to collect all BUY signals
#   3. Compute 19 features at each signal date
#   4. Label each signal: 1=win if 10d forward return >= +2%
#   5. Train/val split (80/20 by time — NO future leakage)
#   6. Train GBM, find optimal threshold on validation set
#   7. Run backtest WITH parallel gated strategy vs baseline
#   8. Save model to data/ml/
#
# --backtest-only  : skip training, load saved model, run backtest only
#                    (use this to test threshold changes without retraining)

import sys
import os
import json
import logging
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from backtester import Backtester
import config
from strategies import ADXTrendStrategy, BollingerBandStrategy, MACDStrategy, SupertrendStrategy
from ml.label_generator import build_training_dataset
from ml.signal_gate import SignalGate

logging.basicConfig(level=logging.ERROR)


# Best configs found in Layer 1 training
GATE_STRATEGIES = [
    ADXTrendStrategy(ema_fast=9,  ema_slow=18, adx_threshold=25),   # best Sharpe
    ADXTrendStrategy(ema_fast=7,  ema_slow=21, adx_threshold=25),
    BollingerBandStrategy(period=15, std_dev=1.5, rsi_oversold=30),  # best trades
    BollingerBandStrategy(period=20, std_dev=1.5, rsi_oversold=30),
    BollingerBandStrategy(period=25, std_dev=1.5, rsi_oversold=30),
    MACDStrategy(fast=12, slow=26, signal=9),
    SupertrendStrategy(atr_period=10, multiplier=3.0),
]


def download_data(start_date: str, end_date: str) -> tuple:
    """Returns (stock_data_dict, nifty_df, sector_data). nifty_df may be empty on failure."""
    print(f"  Downloading {len(config.WATCHLIST)} symbols ({start_date} → {end_date})...")
    loader = Backtester(start_date=start_date, end_date=end_date,
                        strategy_name="combined",
                        initial_capital=config.INITIAL_CAPITAL)
    data = loader._download(config.WATCHLIST)
    print(f"  {len(data)} symbols cached.")

    # Download Nifty 50 index for regime + earnings features
    print("  Downloading ^NSEI (Nifty 50 index)...")
    nifty_raw = loader._download(["^NSEI"])
    nifty_df  = nifty_raw.get("^NSEI", pd.DataFrame())
    if nifty_df.empty:
        print("  WARNING: Nifty data unavailable — regime features will use neutral defaults")
    else:
        print(f"  Nifty cached: {len(nifty_df)} rows")

    # Download NSE sector indices for sector momentum feature
    print("  Downloading sector indices...")
    from ml.sector_fetcher import SECTOR_INDICES
    sector_raw  = loader._download(list(SECTOR_INDICES.values()))
    sector_data = {}
    for sector_name, ticker in SECTOR_INDICES.items():
        df_sec = sector_raw.get(ticker, pd.DataFrame())
        if not df_sec.empty:
            sector_data[sector_name] = df_sec
    print(f"  Sector data: {len(sector_data)}/{len(SECTOR_INDICES)} indices downloaded")

    # Download India VIX for live inference threshold adjustment
    print("  Downloading ^INDIAVIX (India Volatility Index)...")
    vix_raw = loader._download(["^INDIAVIX"])
    vix_df  = vix_raw.get("^INDIAVIX", pd.DataFrame())
    if vix_df.empty:
        print("  WARNING: India VIX data unavailable — VIX gate will use 0.0 (no adjustment)")
    else:
        print(f"  India VIX cached: {len(vix_df)} rows")

    return data, nifty_df, sector_data, vix_df


def collect_signals(data: dict, strategies: list,
                    hold_days: int, win_threshold: float,
                    nifty_df: pd.DataFrame = None,
                    sector_data: dict = None) -> pd.DataFrame:
    """Collect labelled BUY signals from all strategies."""
    all_frames = []
    for strat in strategies:
        print(f"    Collecting signals: {strat.name}")
        df = build_training_dataset(data, strat,
                                    hold_days=hold_days,
                                    win_threshold=win_threshold,
                                    nifty_df=nifty_df,
                                    sector_data=sector_data)
        if not df.empty:
            all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["symbol", "date"]).sort_values("date")
    return combined.reset_index(drop=True)


def run_walk_forward_validation(df_signals: pd.DataFrame, n_folds: int = 3) -> dict:
    """
    Walk-forward validation: train on past, predict on future, rolling window.
    Reports average win rate across folds.
    """
    n = len(df_signals)
    fold_size = n // (n_folds + 1)
    results = []

    print("\n  Walk-forward validation:")
    print(f"  {'Fold':<6} {'Train size':>12} {'Val size':>10} {'Val win rate':>14}")
    print(f"  {'─'*6} {'─'*12} {'─'*10} {'─'*14}")

    for fold in range(n_folds):
        val_start   = fold_size * (fold + 1)
        val_end     = val_start + fold_size
        df_train_wf = df_signals.iloc[:val_start].copy()
        df_val_wf   = df_signals.iloc[val_start:val_end].copy()

        if len(df_train_wf) < 100 or len(df_val_wf) < 20:
            continue

        gate_wf = SignalGate(threshold=0.55)
        gate_wf.train(df_train_wf)
        probs_wf = gate_wf.predict_proba_batch(df_val_wf)
        mask_wf  = probs_wf >= 0.55
        wr_wf    = float(df_val_wf["label"].values[mask_wf].mean()) * 100 if mask_wf.sum() > 0 else 0
        results.append(wr_wf)
        print(f"  {fold+1:<6} {len(df_train_wf):>12} {len(df_val_wf):>10} {wr_wf:>13.1f}%")

    avg_wr = sum(results) / len(results) if results else 0
    print(f"  {'Avg':>6} {'':>12} {'':>10} {avg_wr:>13.1f}%")
    return {"walk_forward_folds": results, "walk_forward_avg_win_rate": avg_wr}


class ParallelGatedStrategy:
    """
    Runs ADX + BB in parallel. Either can fire a BUY signal.
    All BUY signals are then filtered by the ML gate.
    SELL from either strategy on an open position triggers an exit.
    ADX SELL takes priority over BB SELL.
    """
    def __init__(self, adx_strat, bb_strat, gate_model):
        self.adx  = adx_strat
        self.bb   = bb_strat
        self.gate = gate_model
        self.name = f"Parallel+Gate({adx_strat.name}|{bb_strat.name})"

    def compute_all_signals(self, df) -> dict:
        adx_sigs = self.adx.compute_all_signals(df)
        bb_sigs  = self.bb.compute_all_signals(df)
        idx_map  = {date: i for i, date in enumerate(df.index)}
        all_dates = sorted(set(adx_sigs) | set(bb_sigs))
        _no_sig   = {"signal": 0, "strength": 0, "reason": "No signal"}
        merged = {}
        for date in all_dates:
            a = adx_sigs.get(date, _no_sig)
            b = bb_sigs.get(date, _no_sig)
            # Merge: BUY if either fires, SELL if either fires, ADX priority
            if a["signal"] == 1 or b["signal"] == 1:
                # Take the stronger buy signal; apply gate
                raw = a if a["signal"] == 1 and a.get("strength", 0) >= b.get("strength", 0) else b
                if raw["signal"] != 1:
                    raw = a if a["signal"] == 1 else b
                pos    = idx_map.get(date)
                window = df.iloc[:pos + 1] if pos is not None else df
                merged[date] = self.gate.approve(window, raw)
            elif a["signal"] == -1:
                merged[date] = a
            elif b["signal"] == -1:
                merged[date] = b
            else:
                merged[date] = _no_sig
        return merged

    def get_latest_signal(self, df) -> dict:
        a = self.adx.get_latest_signal(df)
        b = self.bb.get_latest_signal(df)
        if a["signal"] == 1 or b["signal"] == 1:
            raw = a if a["signal"] == 1 and a.get("strength", 0) >= b.get("strength", 0) else b
            if raw["signal"] != 1:
                raw = a if a["signal"] == 1 else b
            return self.gate.approve(df, raw)
        if a["signal"] == -1:
            return a
        if b["signal"] == -1:
            return b
        return {"signal": 0, "strength": 0, "reason": "No signal"}


def run_gated_backtest(data: dict, gate: SignalGate,
                       start_date: str, end_date: str,
                       nifty_df: pd.DataFrame = None,
                       sector_data: dict = None,
                       vix_df: pd.DataFrame = None) -> dict:
    """Run a backtest with the parallel ADX+BB gated strategy."""
    gate.nifty_df    = nifty_df
    gate.sector_data = sector_data or {}
    # Set gate VIX to the latest reading in the backtest window
    if vix_df is not None and not vix_df.empty and "close" in vix_df.columns:
        gate.vix_value = float(vix_df["close"].iloc[-1])
    else:
        gate.vix_value = 0.0

    adx_strat = ADXTrendStrategy(ema_fast=9, ema_slow=18, adx_threshold=25)
    bb_strat  = BollingerBandStrategy(period=20, std_dev=1.5, rsi_oversold=30)
    strat     = ParallelGatedStrategy(adx_strat, bb_strat, gate)

    bt = Backtester(start_date=start_date, end_date=end_date,
                    strategy_name="_custom",
                    initial_capital=config.INITIAL_CAPITAL,
                    verbose=False)
    bt.strategy = strat
    result = bt.run_with_data(data)
    return result["summary"] if result else None


def _fmt(v, pct=False):
    """Format a metric value for the results table."""
    if v is None:
        return "N/A"
    return f"{v:+.1f}%" if pct else f"{v:.3f}"


def main():
    parser = argparse.ArgumentParser(description="Train NEXUS signal gate")
    parser.add_argument("--years",           type=int,   default=2,    help="Years of data")
    parser.add_argument("--hold-days",       type=int,   default=10,   help="Forward window for labelling")
    parser.add_argument("--win-threshold",   type=float, default=0.02, help="Min forward return to label as win")
    parser.add_argument("--target-win-rate", type=float, default=0.70, help="Target win rate for threshold tuning")
    parser.add_argument("--threshold",       type=float, default=None, help="Override gate threshold (backtest-only mode)")
    parser.add_argument("--backtest-only",   action="store_true",      help="Skip training; load saved model and backtest only")
    args = parser.parse_args()

    end_date   = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=args.years * 365)).strftime("%Y-%m-%d")

    # ── BACKTEST-ONLY mode ────────────────────────────────────────────────────
    if args.backtest_only:
        print("\n" + "=" * 70)
        print("  NEXUS BRAIN — BACKTEST ONLY (saved model)")
        print(f"  Period   : {start_date} → {end_date}")

        gate = SignalGate()
        if not gate.load():
            print("ERROR: No saved model found. Run without --backtest-only to train first.")
            return

        if args.threshold is not None:
            gate.threshold = args.threshold
            print(f"  Threshold: {gate.threshold} (overridden via --threshold)")
        else:
            print(f"  Threshold: {gate.threshold} (from saved model)")
        print("=" * 70)

        data, nifty_df, sector_data, vix_df = download_data(start_date, end_date)
        if not data:
            print("ERROR: No data. Aborting.")
            return

        print("\n  Running baseline backtest (ADX only, no gate)...")
        base_strat = ADXTrendStrategy(ema_fast=9, ema_slow=18, adx_threshold=25)
        bt_base    = Backtester(start_date=start_date, end_date=end_date,
                                strategy_name="_custom",
                                initial_capital=config.INITIAL_CAPITAL, verbose=False)
        bt_base.strategy = base_strat
        base_result  = bt_base.run_with_data(data)
        base_summary = base_result["summary"] if base_result else {}

        print("  Running gated backtest (ADX + BB parallel, with gate + ladder buy)...")
        gated_summary = run_gated_backtest(data, gate, start_date, end_date,
                                           nifty_df=nifty_df, sector_data=sector_data,
                                           vix_df=vix_df)

        print("\n" + "=" * 70)
        print("  RESULTS: Baseline vs. Gated")
        print(f"  {'Metric':<25} {'Baseline':>12} {'Gated':>12} {'Delta':>10}")
        print(f"  {'─'*25} {'─'*12} {'─'*12} {'─'*10}")

        from datetime import datetime as dt
        d0 = dt.strptime(start_date, "%Y-%m-%d")
        d1 = dt.strptime(end_date,   "%Y-%m-%d")
        num_months = max((d1 - d0).days / 30.44, 1)

        if base_summary and gated_summary:
            base_summary["monthly_profit_pct"]  = base_summary["total_return_pct"]  / num_months
            base_summary["monthly_trades"]       = base_summary["total_trades"]       / num_months
            gated_summary["monthly_profit_pct"] = gated_summary["total_return_pct"] / num_months
            gated_summary["monthly_trades"]      = gated_summary["total_trades"]      / num_months

            metrics = [
                ("Win rate",        "win_rate",          True),
                ("Sharpe ratio",    "sharpe_ratio",       False),
                ("Total return",    "total_return_pct",   True),
                ("Max drawdown",    "max_drawdown_pct",   True),
                ("─── Monthly ───", None,                 False),
                ("Profit / month",  "monthly_profit_pct", True),
                ("Trades / month",  "monthly_trades",     False),
                ("Total trades",    "total_trades",       False),
            ]
            for label, key, is_pct in metrics:
                if key is None:
                    print(f"  {label}")
                    continue
                b = base_summary.get(key)
                g = gated_summary.get(key)
                delta = (g - b) if (b is not None and g is not None) else None
                print(f"  {label:<25} {_fmt(b, is_pct):>12} {_fmt(g, is_pct):>12} {_fmt(delta, is_pct):>10}")

        if gated_summary:
            gwr = gated_summary.get("win_rate", 0)
            if gwr >= args.target_win_rate * 100:
                print(f"\n  ✅ TARGET REACHED: {gwr:.1f}% win rate (target {args.target_win_rate*100:.0f}%)")
            else:
                print(f"\n  Win rate: {gwr:.1f}% (target {args.target_win_rate*100:.0f}%) — gap: {args.target_win_rate*100 - gwr:.1f}pp")
        return

    # ── FULL TRAINING mode ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  NEXUS BRAIN — ML GATE TRAINING (Layer 2)")
    print(f"  Period   : {start_date} → {end_date}")
    print(f"  Labelling: hold={args.hold_days}d, win>={args.win_threshold*100:.0f}%")
    print(f"  Target   : win rate >= {args.target_win_rate*100:.0f}%")
    print("=" * 70)

    # 1. Data
    data, nifty_df, sector_data, vix_df = download_data(start_date, end_date)
    if not data:
        print("ERROR: No data. Aborting.")
        return

    # 2. Collect labelled signals
    print("\n  Collecting BUY signals and computing features...")
    df_signals = collect_signals(data, GATE_STRATEGIES, args.hold_days, args.win_threshold,
                                 nifty_df=nifty_df, sector_data=sector_data)
    if df_signals.empty:
        print("ERROR: No signals collected.")
        return

    n_total = len(df_signals)
    n_wins  = int(df_signals["label"].sum())
    raw_wr  = n_wins / n_total * 100
    print(f"  {n_total} signals collected | {n_wins} wins ({raw_wr:.1f}%) | "
          f"{n_total - n_wins} losses ({100-raw_wr:.1f}%)")

    # 3. Temporal train/val split (80/20, no leakage)
    split_idx = int(len(df_signals) * 0.80)
    df_train  = df_signals.iloc[:split_idx].copy()
    df_val    = df_signals.iloc[split_idx:].copy()

    val_start = str(df_val["date"].iloc[0].date())
    print(f"\n  Train: {len(df_train)} signals | Val: {len(df_val)} signals (from {val_start})")

    # Walk-forward validation diagnostic
    run_walk_forward_validation(df_signals)

    # 4. Train GBM
    print("\n  Training GBM gate...")
    gate = SignalGate(threshold=0.60)
    meta = gate.train(df_train)
    print(f"  In-sample accuracy: {meta['in_sample_acc']*100:.1f}%")

    # 5. Print feature importances
    print("\n  Feature importances (top 8):")
    for feat, imp in list(meta["feature_importances"].items())[:8]:
        bar = "█" * int(imp * 200)
        print(f"    {feat:<25} {imp:.4f}  {bar}")

    # 6. Validation set performance before/after gate
    val_raw_wr = float(df_val["label"].mean()) * 100
    probs_val  = gate.predict_proba_batch(df_val)

    print(f"\n  Validation set baseline win rate: {val_raw_wr:.1f}%")
    print(f"\n  Threshold sweep on validation set:")
    print(f"  {'Threshold':>10} {'Signals kept':>14} {'% kept':>8} {'Win rate':>10}")
    print(f"  {'─'*10} {'─'*14} {'─'*8} {'─'*10}")

    import numpy as np
    for t in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]:
        mask     = probs_val >= t
        kept     = mask.sum()
        pct_kept = kept / len(df_val) * 100
        wr       = float(df_val["label"].values[mask].mean()) * 100 if kept > 0 else 0
        marker   = " ← target" if wr >= args.target_win_rate * 100 and kept >= 10 else ""
        print(f"  {t:>10.2f} {kept:>14} {pct_kept:>7.1f}% {wr:>9.1f}%{marker}")

    # 7. Find optimal threshold
    best_thresh = gate.find_threshold(df_val, target_win_rate=args.target_win_rate)
    print(f"\n  Optimal threshold: {best_thresh}")

    # 8. Run gated backtest vs. ungated baseline
    print("\n  Running baseline backtest (ADX only, no gate)...")
    base_strat = ADXTrendStrategy(ema_fast=9, ema_slow=18, adx_threshold=25)
    bt_base    = Backtester(start_date=start_date, end_date=end_date,
                            strategy_name="_custom",
                            initial_capital=config.INITIAL_CAPITAL, verbose=False)
    bt_base.strategy = base_strat
    base_result = bt_base.run_with_data(data)
    base_summary = base_result["summary"] if base_result else {}

    print("  Running gated backtest (ADX + BB parallel, with gate + ladder buy)...")
    gated_summary = run_gated_backtest(data, gate, start_date, end_date,
                                       nifty_df=nifty_df, sector_data=sector_data,
                                       vix_df=vix_df)

    # 9. Print comparison
    print("\n" + "=" * 70)
    print("  RESULTS: Baseline vs. Gated")
    print(f"  {'Metric':<25} {'Baseline':>12} {'Gated':>12} {'Delta':>10}")
    print(f"  {'─'*25} {'─'*12} {'─'*12} {'─'*10}")

    # Calculate months in backtest window
    from datetime import datetime as dt
    d0 = dt.strptime(start_date, "%Y-%m-%d")
    d1 = dt.strptime(end_date,   "%Y-%m-%d")
    num_months = max((d1 - d0).days / 30.44, 1)

    if base_summary and gated_summary:
        # Derived monthly metrics
        base_summary["monthly_profit_pct"]  = base_summary["total_return_pct"]  / num_months
        base_summary["monthly_trades"]       = base_summary["total_trades"]       / num_months
        gated_summary["monthly_profit_pct"] = gated_summary["total_return_pct"] / num_months
        gated_summary["monthly_trades"]      = gated_summary["total_trades"]      / num_months

        metrics = [
            ("Win rate",           "win_rate",           True),
            ("Sharpe ratio",       "sharpe_ratio",        False),
            ("Total return",       "total_return_pct",    True),
            ("Max drawdown",       "max_drawdown_pct",    True),
            ("─── Monthly ───",    None,                  False),
            ("Profit / month",     "monthly_profit_pct",  True),
            ("Trades / month",     "monthly_trades",      False),
            ("Total trades",       "total_trades",        False),
        ]
        for label, key, is_pct in metrics:
            if key is None:
                print(f"  {label}")
                continue
            b = base_summary.get(key)
            g = gated_summary.get(key)
            delta = (g - b) if (b is not None and g is not None) else None
            print(f"  {label:<25} {_fmt(b, is_pct):>12} {_fmt(g, is_pct):>12} {_fmt(delta, is_pct):>10}")

    # 10. Save model
    os.makedirs("data/ml", exist_ok=True)
    saved_path = gate.save()
    print(f"\n  Model saved: {saved_path}")

    # Save extended meta with backtest comparison
    gate.meta["years_trained"]           = args.years
    gate.meta["baseline_win_rate"]       = base_summary.get("win_rate")
    gate.meta["gated_win_rate"]          = gated_summary.get("win_rate") if gated_summary else None
    gate.meta["baseline_sharpe"]         = base_summary.get("sharpe_ratio")
    gate.meta["gated_sharpe"]            = gated_summary.get("sharpe_ratio") if gated_summary else None
    gate.meta["gated_monthly_profit_pct"]= gated_summary.get("monthly_profit_pct") if gated_summary else None
    gate.meta["gated_monthly_trades"]    = gated_summary.get("monthly_trades") if gated_summary else None
    gate.meta["trained_at"]              = datetime.now().isoformat()
    gate.save()

    print("\n  Layer 2 gate training complete.")
    if gated_summary:
        gwr = gated_summary.get("win_rate", 0)
        if gwr >= args.target_win_rate * 100:
            print(f"  ✅ TARGET REACHED: {gwr:.1f}% win rate (target {args.target_win_rate*100:.0f}%)")
        else:
            print(f"  Win rate: {gwr:.1f}% (target {args.target_win_rate*100:.0f}%) — gap: {args.target_win_rate*100 - gwr:.1f}pp")


if __name__ == "__main__":
    main()
