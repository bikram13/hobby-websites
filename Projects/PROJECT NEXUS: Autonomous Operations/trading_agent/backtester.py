# NEXUS TRADING AGENT — Historical Backtester
# Replays the live strategy on real historical data, day by day.
# Produces: trade log, equity curve, Sharpe ratio, win rate, max drawdown.

import os
import logging
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

import config
from strategies import CombinedStrategy, MACrossoverStrategy, RSIStrategy, MomentumStrategy
from risk_manager import RiskManager

# Suppress noisy INFO logs from sub-modules during backtest
logging.getLogger().setLevel(logging.WARNING)

STRATEGY_MAP = {
    "ma_crossover": MACrossoverStrategy,
    "rsi": RSIStrategy,
    "momentum": MomentumStrategy,
    "combined": CombinedStrategy,
}


class Backtester:
    def __init__(self, start_date, end_date, strategy_name="combined", initial_capital=100_000,
                 verbose=True, gate=None):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.verbose = verbose
        self.gate = gate          # optional SignalGate instance for Layer 2 filtering
        # Allow external strategy injection (used by training loop)
        self.strategy = None
        self.cash = float(initial_capital)
        self.positions = {}       # {symbol: {qty, entry_price, stop_loss, target, entry_date, cost}}
        self.closed_trades = []
        self.equity_curve = []    # [{date, value}]

        # Only instantiate default strategy if not injected externally
        if self.strategy is None:
            StrategyClass = STRATEGY_MAP.get(strategy_name, CombinedStrategy)
            self.strategy = StrategyClass()
        self.risk = RiskManager(config)
        self.ladder_enabled     = getattr(config, "LADDER_BUY_ENABLED",  True)
        self.ladder_initial_pct = getattr(config, "LADDER_INITIAL_PCT",  0.60)
        self.ladder_add_pct     = getattr(config, "LADDER_ADD_PCT",      0.40)
        self.ladder_trigger     = getattr(config, "LADDER_TRIGGER_DROP", 0.03)
        # Transaction costs (NSE equity delivery)
        self._buy_cost_pct  = getattr(config, "BUY_TRANSACTION_PCT",  0.00119)
        self._sell_cost_pct = getattr(config, "SELL_TRANSACTION_PCT", 0.00104)
        self._dp_charge     = getattr(config, "DP_CHARGE_PER_SELL",   13.5)

    # ── Data download ─────────────────────────────────────────────────────────

    def _download(self, symbols):
        """Download history with 90-day warmup for indicator calculation."""
        warmup_start = (
            datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(days=90)
        ).strftime("%Y-%m-%d")

        data = {}
        failed = []
        for sym in symbols:
            df = yf.download(sym, start=warmup_start, end=self.end_date,
                             progress=False, auto_adjust=True)
            if df.empty:
                failed.append(sym)
                continue
            # yfinance ≥0.2 returns MultiIndex columns — flatten to single level
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0].lower() for c in df.columns]
            else:
                df.columns = [c.lower() for c in df.columns]
            df.index = pd.to_datetime(df.index)
            data[sym] = df

        if failed:
            print(f"  Skipped (no data): {', '.join(failed)}")
        return data

    # ── Portfolio helpers ──────────────────────────────────────────────────────

    def _portfolio_value(self, current_prices):
        positions_value = sum(
            pos["qty"] * current_prices.get(sym, pos["entry_price"])
            for sym, pos in self.positions.items()
        )
        return self.cash + positions_value

    def _close(self, sym, price, date, reason):
        pos = self.positions[sym]
        gross_proceeds = pos["qty"] * price
        sell_charges   = gross_proceeds * self._sell_cost_pct + self._dp_charge
        net_proceeds   = gross_proceeds - sell_charges
        pnl     = net_proceeds - pos["cost"]   # cost already includes buy charges
        pnl_pct = (pnl / pos["cost"]) * 100

        self.closed_trades.append({
            "symbol": sym,
            "qty": pos["qty"],
            "entry_price": round(pos["entry_price"], 2),
            "exit_price": round(price, 2),
            "entry_date": str(pos["entry_date"].date()),
            "exit_date": str(date.date()),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "charges": round(sell_charges + pos.get("buy_charges", 0), 2),
            "reason": reason,
        })
        self.cash += net_proceeds
        del self.positions[sym]

    # ── Main simulation loop ───────────────────────────────────────────────────

    def run(self, symbols):
        """Download data then simulate. Use run_with_data() to skip downloading."""
        print(f"\nDownloading {len(symbols)} symbols ({self.start_date} → {self.end_date})...")
        data = self._download(symbols)
        if not data:
            print("No data downloaded. Aborting.")
            return None
        return self._simulate(data)

    def run_with_data(self, data: dict):
        """Simulate using pre-downloaded data — no network calls. Used by training loop."""
        return self._simulate(data)

    def _reset_state(self):
        """Reset portfolio state for a fresh simulation run."""
        self.cash = float(self.initial_capital)
        self.positions = {}
        self.closed_trades = []
        self.equity_curve = []
        self._ladder_done = set()  # symbols where ladder buy already executed

    def _simulate(self, data: dict):
        """Core simulation loop — shared by run() and run_with_data()."""
        self._reset_state()

        # All trading days within the backtest window
        all_dates = sorted(set(
            d for df in data.values()
            for d in df.index
            if self.start_date <= str(d.date()) <= self.end_date
        ))
        if not all_dates:
            return None

        # Pre-compute all signals once per symbol — O(N) not O(N²)
        _no_signal = {"signal": 0, "strength": 0, "reason": "No signal"}
        if hasattr(self.strategy, "compute_all_signals"):
            raw_cache = {sym: self.strategy.compute_all_signals(df) for sym, df in data.items()}
            # Apply ML gate filter if provided (Layer 2)
            if self.gate is not None and self.gate.trained:
                signal_cache = {}
                for sym, sig_dict in raw_cache.items():
                    df      = data[sym]
                    idx_map = {date: i for i, date in enumerate(df.index)}
                    gated   = {}
                    for date, sig in sig_dict.items():
                        if sig["signal"] == 1:
                            pos    = idx_map.get(date)
                            window = df.iloc[:pos + 1] if pos is not None else df
                            sig    = self.gate.approve(window, sig)
                        gated[date] = sig
                    signal_cache[sym] = gated
            else:
                signal_cache = raw_cache
        else:
            signal_cache = {}

        for day_num, date in enumerate(all_dates, 1):
            current_prices = {
                sym: float(df.loc[df.index <= date].iloc[-1]["close"])
                for sym, df in data.items()
                if not df.loc[df.index <= date].empty
            }

            # --- 1. Check exits (stop loss / target) ---
            for sym in list(self.positions.keys()):
                price = current_prices.get(sym)
                if price is None:
                    continue
                should_exit, reason = self.risk.check_exit_conditions(
                    sym, self.positions[sym], price
                )
                if should_exit:
                    self._close(sym, price, date, reason)

            # --- 2. Signal scan and entries ---
            daily_start_value = self._portfolio_value(current_prices)

            for sym, df in data.items():
                if self.risk.should_stop_trading(
                    self._portfolio_value(current_prices),
                    self.initial_capital,
                    daily_start_value
                ):
                    break

                # Use pre-computed signal if available, else fall back to slice-compute
                if signal_cache:
                    sig = signal_cache.get(sym, {}).get(date, _no_signal)
                else:
                    hist = df[df.index <= date]
                    if len(hist) < 30:
                        continue
                    sig = self.strategy.get_latest_signal(hist)

                if sig["signal"] == 1 and sym not in self.positions:
                    if not self.risk.can_open_position(sym, self.positions):
                        continue
                    price = current_prices.get(sym, 0)
                    if price <= 0:
                        continue
                    pv = self._portfolio_value(current_prices)
                    full_qty = self.risk.calculate_position_size(
                        pv, price,
                        signal_strength=sig.get("strength", 1.0),
                        gate_prob=sig.get("gate_prob"),   # None if not gated → falls back to signal_strength
                    )
                    if full_qty == 0:
                        continue
                    # Ladder: enter with 60% first, reserve 40% for dip add
                    if self.ladder_enabled:
                        qty = max(1, int(full_qty * self.ladder_initial_pct))
                    else:
                        qty = full_qty
                    cost         = qty * price
                    buy_charges  = cost * self._buy_cost_pct
                    total_outlay = cost + buy_charges
                    if total_outlay > self.cash:
                        continue
                    stop_loss, target = self.risk.calculate_stops(price)
                    self.cash -= total_outlay
                    self.positions[sym] = {
                        "qty": qty,
                        "entry_price": price,
                        "entry_date": date,
                        "stop_loss": stop_loss,
                        "target": target,
                        "cost": total_outlay,        # includes buy charges — used for P&L calc
                        "buy_charges": buy_charges,  # tracked for reporting
                        # Ladder tracking
                        "full_qty": full_qty,
                        "ladder_added": False,
                    }

                elif sig["signal"] == -1 and sym in self.positions:
                    price = current_prices.get(sym, 0)
                    if price > 0:
                        self._close(sym, price, date, f"Signal: {sig['reason'][:60]}")

                # --- Ladder Buy: add remaining 40% if price dips 3%+ from entry ---
                elif (self.ladder_enabled
                      and sym in self.positions
                      and not self.positions[sym].get("ladder_added", True)):
                    pos   = self.positions[sym]
                    price = current_prices.get(sym, 0)
                    if price <= 0:
                        continue
                    drop  = (pos["entry_price"] - price) / pos["entry_price"]
                    above_stop = price > pos.get("trailing_stop", pos["stop_loss"])
                    if drop >= self.ladder_trigger and above_stop:
                        add_qty = pos["full_qty"] - pos["qty"]
                        if add_qty > 0:
                            add_cost    = add_qty * price
                            add_charges = add_cost * self._buy_cost_pct
                            add_total   = add_cost + add_charges
                            if add_total <= self.cash:
                                self.cash -= add_total
                                pos["qty"]          += add_qty
                                pos["cost"]         += add_total
                                pos["buy_charges"]   = pos.get("buy_charges", 0) + add_charges
                                pos["entry_price"]   = pos["cost"] / pos["qty"]  # blended avg
                                pos["ladder_added"]  = True
                                # Recalculate stops from new average cost
                                sl, tgt = self.risk.calculate_stops(pos["entry_price"])
                                pos["stop_loss"] = sl
                                pos["target"]    = tgt

            # --- 3. Snapshot equity ---
            self.equity_curve.append({
                "date": date,
                "value": self._portfolio_value(current_prices)
            })

            # Progress every 50 days (only in verbose mode)
            if self.verbose and (day_num % 50 == 0 or day_num == len(all_dates)):
                pv = self.equity_curve[-1]["value"]
                ret = (pv - self.initial_capital) / self.initial_capital * 100
                print(f"  [{day_num:>3}/{len(all_dates)}] {date.date()}  "
                      f"Portfolio: ₹{pv:>10,.0f}  ({ret:+.1f}%)  "
                      f"Trades: {len(self.closed_trades)}")

        # Close any remaining open positions at last price
        final_prices = {
            sym: float(df.iloc[-1]["close"])
            for sym, df in data.items() if not df.empty
        }
        for sym in list(self.positions.keys()):
            price = final_prices.get(sym, self.positions[sym]["entry_price"])
            self._close(sym, price, all_dates[-1], "End of backtest")

        return self._build_report()

    # ── Report generation ──────────────────────────────────────────────────────

    def _build_report(self):
        equity = pd.DataFrame(self.equity_curve).set_index("date")
        final_value = equity["value"].iloc[-1]
        total_pnl = final_value - self.initial_capital
        total_return_pct = (total_pnl / self.initial_capital) * 100

        daily_returns = equity["value"].pct_change().dropna()
        sharpe = (
            (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5)
            if daily_returns.std() > 0 else 0
        )

        rolling_max = equity["value"].cummax()
        drawdown = (equity["value"] - rolling_max) / rolling_max
        max_drawdown_pct = drawdown.min() * 100

        trades = self.closed_trades
        winners = [t for t in trades if t["pnl"] > 0]
        losers  = [t for t in trades if t["pnl"] <= 0]
        win_rate = len(winners) / len(trades) * 100 if trades else 0
        avg_win  = sum(t["pnl"] for t in winners) / len(winners) if winners else 0
        avg_loss = sum(t["pnl"] for t in losers)  / len(losers)  if losers  else 0
        gross_profit = sum(t["pnl"] for t in winners)
        gross_loss   = abs(sum(t["pnl"] for t in losers))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Average holding period
        holding_days = []
        for t in trades:
            try:
                entry = datetime.strptime(t["entry_date"], "%Y-%m-%d")
                exit_ = datetime.strptime(t["exit_date"], "%Y-%m-%d")
                holding_days.append((exit_ - entry).days)
            except Exception:
                pass
        avg_hold = sum(holding_days) / len(holding_days) if holding_days else 0

        return {
            "summary": {
                "period": f"{self.start_date} to {self.end_date}",
                "initial_capital": self.initial_capital,
                "final_value": round(final_value, 2),
                "total_pnl": round(total_pnl, 2),
                "total_return_pct": round(total_return_pct, 2),
                "sharpe_ratio": round(sharpe, 3),
                "max_drawdown_pct": round(max_drawdown_pct, 2),
                "total_trades": len(trades),
                "win_rate": round(win_rate, 1),
                "avg_win_inr": round(avg_win, 2),
                "avg_loss_inr": round(avg_loss, 2),
                "profit_factor": round(profit_factor, 2),
                "avg_hold_days": round(avg_hold, 1),
                "phase3_ready": sharpe >= 1.5 and win_rate >= 55 and len(trades) >= 20,
            },
            "trades": trades,
            "equity_curve": equity,
        }

    # ── Save report to disk ────────────────────────────────────────────────────

    def save_report(self, result, path=None):
        s = result["summary"]
        trades = result["trades"]
        phase3 = "✅ YES — criteria met" if s["phase3_ready"] else "❌ Not yet"

        lines = [
            f"# NEXUS Backtest Report",
            f"*Period: {s['period']} | Strategy: Combined Consensus | Generated: {datetime.now():%Y-%m-%d %H:%M}*",
            "",
            "## Performance Summary",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Initial Capital | ₹{s['initial_capital']:,.0f} |",
            f"| Final Value | ₹{s['final_value']:,.0f} |",
            f"| Total P&L | ₹{s['total_pnl']:+,.0f} ({s['total_return_pct']:+.1f}%) |",
            f"| Sharpe Ratio | {s['sharpe_ratio']:.3f} |",
            f"| Max Drawdown | {s['max_drawdown_pct']:.1f}% |",
            f"| Total Trades | {s['total_trades']} |",
            f"| Win Rate | {s['win_rate']:.1f}% |",
            f"| Avg Win | ₹{s['avg_win_inr']:,.0f} |",
            f"| Avg Loss | ₹{s['avg_loss_inr']:,.0f} |",
            f"| Profit Factor | {s['profit_factor']:.2f} |",
            f"| Avg Hold (days) | {s['avg_hold_days']:.1f} |",
            "",
            f"## Phase 3 Gate",
            f"Sharpe ≥ 1.5: {'✅' if s['sharpe_ratio'] >= 1.5 else '❌'} ({s['sharpe_ratio']:.3f})",
            f"Win rate ≥ 55%: {'✅' if s['win_rate'] >= 55 else '❌'} ({s['win_rate']:.1f}%)",
            f"Trades ≥ 20: {'✅' if s['total_trades'] >= 20 else '❌'} ({s['total_trades']})",
            f"**Overall: {phase3}**",
            "",
            "## Trade Log",
            "| # | Symbol | Entry | Exit | Entry ₹ | Exit ₹ | P&L | % | Reason |",
            "|---|--------|-------|------|---------|--------|-----|---|--------|",
        ]

        for i, t in enumerate(trades, 1):
            pnl_str = f"₹{t['pnl']:+,.0f}"
            lines.append(
                f"| {i} | {t['symbol'].replace('.NS','')} | {t['entry_date']} | {t['exit_date']} "
                f"| ₹{t['entry_price']:,.1f} | ₹{t['exit_price']:,.1f} "
                f"| {pnl_str} | {t['pnl_pct']:+.1f}% | {t['reason'][:50]} |"
            )

        if not path:
            os.makedirs("data/reports", exist_ok=True)
            path = f"data/reports/backtest_{self.start_date}_{self.end_date}.md"

        with open(path, "w") as f:
            f.write("\n".join(lines))

        return path
