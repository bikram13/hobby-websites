# NEXUS Trading Agent — Sub-Project Context

**Status:** Active (paper trading, Phase 1)
**Capital:** ₹1,00,000 virtual | **Strategy:** ParallelGatedStrategy → ML Gate → RiskManager

## Architecture (3 Layers)

```
Layer 1 — Signal: ParallelGatedStrategy (ADX breakout + Bollinger Bands, parallel)
Layer 2 — Gate:   SignalGate (GradientBoostingClassifier, 19 features, sklearn)
Layer 3 — Risk:   RiskManager (stop-loss 2.5%, target 7%, trailing stop 2%)
```

## Key Files

| File | Purpose |
|------|---------|
| `run.py` | Entry point — starts paper trading loop |
| `agent.py` | Old agent (single strategy, not ML-gated — DO NOT USE for results) |
| `config.py` | All risk params, watchlist (89 NSE symbols), transaction costs |
| `backtester.py` | 10yr backtest engine with NSE transaction costs baked in |
| `strategies/parallel_gated.py` | Active strategy: ADX + BB parallel signals |
| `ml/signal_gate.py` | ML gate — loads `../data/ml/signal_gate.pkl` |
| `ml/feature_engineer.py` | 19-feature extraction (incl. Nifty regime + earnings momentum) |
| `ml/label_generator.py` | Builds training dataset from historical signals |
| `ml/earnings_detector.py` | Earnings proximity and post-earnings momentum scoring |
| `ml/train_gate.py` | Full retrain + backtest pipeline (see commands below) |
| `data/ml/signal_gate_meta.json` | Current model metadata (win rate, threshold, feature list) |

## Current ML Model Results (19 features, 10yr training)

| Metric | Value |
|--------|-------|
| Gated Win Rate | 62.6% |
| Threshold | 0.55 |
| Features | 19 (incl. nifty_above_ema200, nifty_pct_vs_ema200, earnings_momentum) |
| Bear market override | threshold → 0.75 when Nifty < EMA200 |

## ML Features (19)

Core 16: `adx`, `adx_slope`, `bb_pct_b`, `bb_width`, `rsi`, `rsi_slope`, `macd_hist`, `vol_ratio`, `atr_pct`, `price_vs_ema20`, `price_vs_ema50`, `trend_strength`, `momentum_5`, `momentum_10`, `candle_body_pct`, `volume_trend`

New 3: `nifty_above_ema200` (binary), `nifty_pct_vs_ema200` (float), `earnings_momentum` (post-earnings outperformance vs Nifty)

## Commands

```bash
# Run full retrain + backtest
python ml/train_gate.py --years 10

# Fast threshold test (no retrain ~5 min)
python ml/train_gate.py --backtest-only --threshold 0.60

# Run paper trading
python run.py

# Generate report
python reporter.py
```

## Transaction Costs (NSE, Zerodha)

```
Buy:  STT 0.1% + NSE 0.00335% + stamp 0.015% = 0.119%
Sell: STT 0.1% + NSE 0.00335% = 0.104%
DP:   ₹13.5 flat per sell (CDSL demat debit)
```
Configured in `config.py`: `BUY_TRANSACTION_PCT`, `SELL_TRANSACTION_PCT`, `DP_CHARGE_PER_SELL`

## Risk Config (config.py)

```
MAX_POSITION_SIZE_PCT = 0.15  (15% per position)
MAX_OPEN_POSITIONS    = 7
STOP_LOSS_PCT         = 0.025 (2.5%)
TARGET_PCT            = 0.07  (7%)
TRAIL_STOP_PCT        = 0.02  (2% trailing)
LADDER_BUY_ENABLED    = True  (60% entry + 40% add on -3% dip)
```

## Do Not

- Do not edit `agent.py` — it uses old strategy without ML gate
- Do not commit `data/portfolio.json`, `data/trade_log.csv`, `data/*.log` (gitignored)
- Do not commit `signal_gate.pkl` (gitignored, 716KB binary)
- Do not set `PAPER_TRADING = False` without Angel One credentials filled in config.py

## Phase Roadmap

- Phase 1 (current): Paper trading, ML gate tuning, win rate target 70%
- Phase 2: Angel One SmartAPI live integration (fill API keys in config.py)
- Phase 3: Auto-reporting, Telegram alerts, live deployment
