# PROJECT NEXUS — Claude Code Context

## What This Is
Autonomous NSE algorithmic trading system. Paper trading ₹1,00,000 virtual capital.
Goal: push win rate to 70%+, generate ₹4,500–5,000/month net at ₹5L capital.

## Active Architecture (Layer 1 → 2 → 3)

```
Layer 1: ParallelGatedStrategy (ADX ema=9/18 + BB p=20/std=1.5, run in parallel)
              ↓ every BUY signal
Layer 2: SignalGate (GBM, 19 features, threshold=0.55)
         - Nifty regime: nifty_above_ema200, nifty_pct_vs_ema200 (#1 feature)
         - Earnings proxy: earnings_momentum (post-earnings outperformance vs Nifty)
         - Bear market soft gate: threshold rises 0.55 → 0.75 when Nifty < EMA200
              ↓ approved signals only
Layer 3: RiskManager (trailing stop 2%, ladder buy 60%/40%, SL -2.5%, target +7%)
```

**IMPORTANT:** `agent.py` uses OLD `CombinedStrategy` — not the ML gate. Do NOT update it yet.
The good backtest numbers come from `ml/train_gate.py` + `ParallelGatedStrategy`.

## Current Results (10-year backtest, threshold=0.55, with transaction costs)
| Capital | Monthly net | Win rate | Sharpe | Max drawdown |
|---------|------------|---------|--------|--------------|
| ₹1,00,000 | ~₹900 | 57.8% | 1.917 | -₹4,000 |
| ₹5,00,000 | ~₹5,000 | 58.8% | 2.052 | -₹22,000 |

Gap to 70% target: ~11pp. Transaction costs fully modeled (STT + NSE + DP ₹13.5/sell).

## Key Files

### Trading Core
| File | Purpose |
|------|---------|
| `trading_agent/config.py` | All risk params, watchlist (89 symbols), transaction costs |
| `trading_agent/backtester.py` | Historical replay engine — transaction costs wired in |
| `trading_agent/risk_manager.py` | Trailing stops, ladder buys, position sizing |

### ML Gate (Layer 2)
| File | Purpose |
|------|---------|
| `trading_agent/ml/train_gate.py` | **Main training script** — also has `--backtest-only --threshold` |
| `trading_agent/ml/signal_gate.py` | GBM gate, `approve()`, soft Nifty threshold |
| `trading_agent/ml/feature_engineer.py` | 19 features, `compute_features(df, nifty_df=None)` |
| `trading_agent/ml/label_generator.py` | Training labels, `build_training_dataset(..., nifty_df=None)` |
| `trading_agent/ml/earnings_detector.py` | Earnings date proxy from price gaps |
| `data/ml/signal_gate.pkl` | Trained model (threshold=0.55, do not delete) |
| `data/ml/signal_gate_meta.json` | Model metadata + feature importances |

### Strategies (Layer 1)
| File | Purpose |
|------|---------|
| `trading_agent/strategies/adx_trend.py` | Best strategy — EMA cross + ADX filter |
| `trading_agent/strategies/bollinger_bands.py` | BB mean reversion + RSI |
| `trading_agent/ml/train_gate.py` | `ParallelGatedStrategy` class lives here |

## Key Commands

```bash
# Backtest with current saved model (fast — no retraining)
cd trading_agent
python3 ml/train_gate.py --backtest-only --threshold 0.55 --years 10

# Full retrain (10yr, ~10min)
python3 ml/train_gate.py --years 10 --hold-days 10 --win-threshold 0.02 --target-win-rate 0.70

# Quick 2yr retrain
python3 ml/train_gate.py --years 2 --hold-days 10 --win-threshold 0.02

# Run live paper trading agent (uses OLD CombinedStrategy — not ML gate yet)
python3 run.py
```

## Phases
| Phase | Status |
|-------|--------|
| Phase 1: Foundation + Paper Trading agent | ✅ Done |
| Phase 2: ML Gate + 19 features + Nifty regime | ✅ Done |
| Phase 3: Angel One SmartAPI live data | ⬜ Pending (gate: 2–4 weeks paper trading results) |
| Phase 4: Live trading | ⬜ Pending (gate: Sharpe > 1.5, win rate > 55%, 20+ trades) |

## DO NOT
- Update `agent.py` yet — it's the live runner, will be updated when going live
- Delete `data/ml/signal_gate.pkl` or `data/ml/signal_gate_meta.json`
- Delete `trading_agent/data/portfolio.json` or `trading_agent/data/trade_log.csv`
- Suggest Gumroad/Reddit/Fiverr — tried and dropped
- Run retraining without `--years 10` unless doing a quick test

## Config Quick Reference
```python
# trading_agent/config.py
INITIAL_CAPITAL = 100_000       # change to 500_000 for ₹5L simulation
MAX_POSITION_SIZE_PCT = 0.15    # 15% per position
STOP_LOSS_PCT = 0.025           # 2.5% SL
TARGET_PCT = 0.07               # 7% target
MAX_OPEN_POSITIONS = 7
TRAIL_STOP_PCT = 0.02           # 2% trailing stop
LADDER_BUY_ENABLED = True       # 60% entry, 40% add on 3% dip
BUY_TRANSACTION_PCT = 0.00119   # STT + NSE + stamp duty
SELL_TRANSACTION_PCT = 0.00104  # STT + NSE
DP_CHARGE_PER_SELL = 13.5       # CDSL flat charge per sell
```
