# NEXUS SESSION HANDOFF
**Last updated:** 2026-04-12 | **Resume from here in every new session**

---

## WHERE WE ARE

PROJECT NEXUS has pivoted from digital product sales to **autonomous algorithmic trading**.
A complete paper trading agent is built, packaged, and ready to run on Bikram's Mac.

---

## WHAT'S BUILT (don't rebuild)

| Component | Location | Status |
|-----------|----------|--------|
| Trading agent | `trading_agent/` | ✅ Complete |
| 4 strategies (MA, RSI, Momentum, Combined) | `trading_agent/strategies/` | ✅ Complete |
| Risk manager | `trading_agent/risk_manager.py` | ✅ Complete |
| Portfolio tracker | `trading_agent/portfolio.py` | ✅ Complete |
| Daily reporter | `trading_agent/reporter.py` | ✅ Complete |
| Python packages on Mac | yfinance, pandas, smartapi-python | ✅ Installed |
| Cowork scheduled task | `nexus-trading-agent` (3:45 PM IST) | ✅ Active |
| macOS launchd plist | `trading_agent/com.nexus.tradingagent.plist` | ⚠️ Needs 1 user action |
| Double-click launchers | `🚀 Run NEXUS Agent.command` etc. | ✅ Created |

---

## PENDING — RESUME HERE

### ① User action: Activate daily automation
In Finder, navigate to this folder. Right-click → Open:
**`⚙️ Setup Automation (run once).command`**
This loads the launchd plist so the agent runs every weekday 3:45 PM automatically.
*Ask Bikram if he's done this yet. If not, remind him it's one double-click.*

### ② User action: First test run
Right-click → Open: **`🚀 Run NEXUS Agent.command`**
Should output: signal scan for ~30 stocks, paper trades executed, report saved.
*After first run, read `trading_agent/data/reports/` and show Bikram the P&L.*

### ③ NEXUS action: Phase 2 — Angel One SmartAPI
Once 2–4 weeks of paper trading results look good:
1. Ask Bikram to go to **smartapi.angelbroking.com** → Apps → Create App → get API key
2. Get: API_KEY, CLIENT_ID (Angel One login), 4-digit MPIN, TOTP secret
3. Fill in `trading_agent/config.py` (ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_ID, etc.)
4. Rewrite `trading_agent/data_fetcher.py` to use SmartAPI for live NSE feed
5. Paper trade continues but with real-time data

### ④ NEXUS action: Phase 3 — Go live
Gate: Sharpe ratio > 1.5, win rate > 55%, 20+ completed trades
Requires explicit Overseer command: **"go live"**
Action: Set `PAPER_TRADING = False` in config.py, implement live Angel One order placement

---

## CRITICAL CONFIG

```
Mac workspace: /Users/bikram/Documents/Claude/Projects/PROJECT NEXUS: Autonomous Operations/
Trading agent: .../trading_agent/
Strategy mode: Aggressive (30 stocks, 15% position, 2.5% SL, 7% target, 7 positions max)
Capital: ₹1,00,000 virtual
Schedule: Mon–Fri 3:45 PM IST
```

---

## DO NOT

- Suggest Gumroad, Reddit, Twitter promotion — tried, failed, dropped
- Suggest Fiverr / Upwork / freelance — user explicitly rejected
- Present manual steps as the solution — always find the autonomous path
- Run internet-dependent code in the sandbox — it's network-isolated
- Delete `portfolio.json` or `trade_log.csv`

---

## TOOLS CONNECTED
Gmail MCP ✅ | Google Drive MCP ✅ | Canva MCP ✅ | Razorpay MCP ✅ (session errors) | Claude in Chrome ✅ (blocks Reddit/Twitter/X)
