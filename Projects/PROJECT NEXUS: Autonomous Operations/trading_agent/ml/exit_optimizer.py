#!/usr/bin/env python3
"""
Exit parameter grid search for NEXUS ML gate.
Tests (target_pct × trail_stop_pct × stop_loss_pct) combinations.
Uses current saved model (no retraining). Ranks by monthly ₹ return.

Usage:
    cd trading_agent
    export DYLD_LIBRARY_PATH="..."
    python3 ml/exit_optimizer.py --years 5
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import json
from datetime import datetime, timedelta
from itertools import product

import pandas as pd
from backtester import Backtester
import config as base_config
from strategies import ADXTrendStrategy, BollingerBandStrategy
from ml.signal_gate import SignalGate
from ml.train_gate import download_data, ParallelGatedStrategy

# Grid
TARGET_OPTIONS     = [0.07, 0.08, 0.10, 0.12, 0.15]
TRAIL_STOP_OPTIONS = [0.02, 0.03, 0.04]
STOP_LOSS_OPTIONS  = [0.02, 0.025, 0.03]


def _run_one(data, gate, start_date, end_date, target, trail, stop, num_months):
    """Single backtest with overridden exit params. Returns metrics dict or None."""

    adx_strat = ADXTrendStrategy(ema_fast=9, ema_slow=18, adx_threshold=25)
    bb_strat  = BollingerBandStrategy(period=20, std_dev=1.5, rsi_oversold=30)
    strat     = ParallelGatedStrategy(adx_strat, bb_strat, gate)

    bt = Backtester(
        start_date=start_date, end_date=end_date,
        strategy_name="_custom",
        initial_capital=base_config.INITIAL_CAPITAL,
        verbose=False,
    )
    # Override risk manager params via bt.risk (RiskManager instance)
    bt.risk.stop_loss_pct = stop
    bt.risk.target_pct    = target
    bt.risk.trail_pct     = trail
    bt.strategy = strat

    result = bt.run_with_data(data)
    if not result or not result.get("summary"):
        return None
    s = result["summary"]
    total_ret = s.get("total_return_pct") or 0
    if total_ret != total_ret:  # NaN check
        total_ret = 0
    monthly_pct = total_ret / max(num_months, 1)
    monthly_inr = monthly_pct / 100 * base_config.INITIAL_CAPITAL
    sharpe = s.get("sharpe_ratio") or 0
    if sharpe != sharpe:
        sharpe = 0
    return {
        "target":           target,
        "trail_stop":       trail,
        "stop_loss":        stop,
        "win_rate":         s.get("win_rate") or 0,
        "sharpe":           round(float(sharpe), 3),
        "total_return_pct": round(float(total_ret), 2),
        "monthly_pct":      round(float(monthly_pct), 4),
        "monthly_inr":      round(float(monthly_inr), 0),
        "total_trades":     s.get("total_trades") or 0,
        "max_drawdown_pct": s.get("max_drawdown_pct") or 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years",     type=int,   default=5)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--output",    type=str,   default="/tmp/exit_optimizer_results.json")
    args = parser.parse_args()

    end_date   = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=args.years * 365)).strftime("%Y-%m-%d")
    num_months = args.years * 12
    n_combos   = len(TARGET_OPTIONS) * len(TRAIL_STOP_OPTIONS) * len(STOP_LOSS_OPTIONS)

    print(f"\n{'='*70}")
    print(f"  NEXUS Exit Parameter Grid Search  ({args.years}yr, threshold={args.threshold})")
    print(f"  Combinations: {n_combos}")
    print(f"{'='*70}\n")

    gate = SignalGate()
    if not gate.load():
        print("ERROR: No saved model.")
        return
    gate.threshold = args.threshold

    print("  Downloading data (shared across all combos)...")
    data, nifty_df, sector_data, vix_df = download_data(start_date, end_date)
    if not data:
        print("ERROR: No data.")
        return

    gate.nifty_df    = nifty_df
    gate.sector_data = sector_data or {}
    if vix_df is not None and not vix_df.empty and "close" in vix_df.columns:
        gate.vix_value = float(vix_df["close"].iloc[-1])

    results = []
    done = 0
    for target, trail, stop in product(TARGET_OPTIONS, TRAIL_STOP_OPTIONS, STOP_LOSS_OPTIONS):
        done += 1
        print(f"  [{done:2d}/{n_combos}] T={target:.0%} trail={trail:.0%} SL={stop:.1%} ...", end="", flush=True)
        r = _run_one(data, gate, start_date, end_date, target, trail, stop, num_months)
        if r:
            results.append(r)
            print(f"  wr={r['win_rate']:.1f}% monthly=INR{r['monthly_inr']:,.0f} sh={r['sharpe']:.2f}")
        else:
            print("  SKIP")

    if not results:
        print("No results.")
        return

    results.sort(key=lambda x: x["monthly_inr"], reverse=True)

    print(f"\n{'='*70}")
    print(f"  TOP 10 (ranked by monthly INR at 1L capital)")
    print(f"{'='*70}")
    print(f"  {'#':<3} {'Target':>7} {'Trail':>7} {'Stop':>6} {'WinRate':>8} {'Monthly':>12} {'Sharpe':>8}")
    print(f"  {'─'*3} {'─'*7} {'─'*7} {'─'*6} {'─'*8} {'─'*12} {'─'*8}")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i:<3} {r['target']:>6.0%} {r['trail_stop']:>6.0%} {r['stop_loss']:>5.1%}  "
              f"{r['win_rate']:>7.1f}% {r['monthly_inr']:>10,.0f}  {r['sharpe']:>7.2f}")

    w = results[0]
    print(f"\n  WINNER: target={w['target']:.0%}  trail={w['trail_stop']:.0%}  SL={w['stop_loss']:.1%}")
    print(f"  Monthly: INR{w['monthly_inr']:,.0f}  |  Win: {w['win_rate']:.1f}%  |  Sharpe: {w['sharpe']:.2f}")
    print(f"\n  config.py update:")
    print(f"    TARGET_PCT     = {w['target']}")
    print(f"    TRAIL_STOP_PCT = {w['trail_stop']}")
    print(f"    STOP_LOSS_PCT  = {w['stop_loss']}")

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Full results: {args.output}")


if __name__ == "__main__":
    main()
