# NEXUS TRADING AGENT — Configuration
# Edit this file to change risk parameters and universe

# ── PAPER TRADING SETTINGS ──────────────────────────────────────────────────
PAPER_TRADING = True          # Set False only when going live (Phase 3)
INITIAL_CAPITAL = 100000      # Virtual ₹1,00,000 for paper trading

# ── UNIVERSE — Nifty 100 + High-Beta Mid Caps (expanded for more signals) ────
WATCHLIST = [
    # Nifty 50 large caps
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "SBIN.NS", "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "M&M.NS",
    "HCLTECH.NS", "WIPRO.NS", "BHARTIARTL.NS", "ADANIENT.NS", "JSWSTEEL.NS",
    "LTIM.NS", "TECHM.NS", "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS",
    "DIVISLAB.NS", "NESTLEIND.NS", "TITAN.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS",
    "GRASIM.NS", "HINDALCO.NS", "TATASTEEL.NS", "TATACONSUM.NS", "BAJAJFINSV.NS",
    "NTPC.NS", "POWERGRID.NS", "ADANIPORTS.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "KOTAKBANK.NS", "INDUSINDBK.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS",
    # High-beta mid caps (volatile = more opportunity)
    "ETERNAL.NS", "PAYTM.NS", "NYKAA.NS", "POLICYBZR.NS", "IRCTC.NS",
    "DELHIVERY.NS", "INDUSTOWER.NS", "ABCAPITAL.NS", "IDFCFIRSTB.NS",
    "BANDHANBNK.NS", "RBLBANK.NS", "IDEA.NS", "YESBANK.NS",
    # Energy & commodities
    "ONGC.NS", "COALINDIA.NS", "BPCL.NS", "GAIL.NS", "NHPC.NS",
    "IOC.NS", "HINDPETRO.NS", "PETRONET.NS",
    # IT mid caps
    "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
    # Financials
    "CHOLAFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS", "LICHSGFIN.NS",
    # Industrials & infra
    "SIEMENS.NS", "ABB.NS", "HAVELLS.NS", "VOLTAS.NS", "POLYCAB.NS",
    "CUMMINSIND.NS", "BHEL.NS", "RVNL.NS", "IRB.NS",
    # Consumer & FMCG
    "DABUR.NS", "MARICO.NS", "GODREJCP.NS", "PIDILITIND.NS",
    # Healthcare
    "APOLLOHOSP.NS", "MAXHEALTH.NS", "FORTIS.NS",
    # Specialty chemicals & metals
    "PIIND.NS", "AARTIIND.NS", "SAIL.NS", "NMDC.NS",
]

# ── RISK MANAGEMENT (AGGRESSIVE) ─────────────────────────────────────────────
MAX_POSITION_SIZE_PCT = 0.15  # Max 15% of portfolio per position
STOP_LOSS_PCT = 0.025         # 2.5% stop loss — optimizer winner (Sprint 9)
TARGET_PCT = 0.08             # 8% target — exit optimizer winner (Sprint 9, was 0.10)
MAX_OPEN_POSITIONS = 7        # More concurrent positions
MAX_DAILY_LOSS_PCT = 0.04     # Tolerate up to 4% daily drawdown
TRAIL_STOP_PCT = 0.04         # Trailing stop 4% below peak — exit optimizer winner (Sprint 9, was 0.03)

# Ladder Buy — enter with 60%, add 40% if price dips 3-5% before recovery
LADDER_BUY_ENABLED   = True
LADDER_INITIAL_PCT   = 0.60   # First entry uses 60% of planned position size
LADDER_ADD_PCT       = 0.40   # Second entry uses remaining 40%
LADDER_TRIGGER_DROP  = 0.03   # Add to position if price drops ≥3% from entry

# ── TRANSACTION COSTS (NSE equity delivery, Zerodha zero-brokerage) ──────────
# These are applied on every buy and sell in the backtester.
# Buy-side:  STT 0.1% + NSE charges 0.00335% + stamp duty 0.015% ≈ 0.119%
# Sell-side: STT 0.1% + NSE charges 0.00335% ≈ 0.104%
# DP charge: ₹13.5 flat per sell transaction (CDSL demat debit)
BUY_TRANSACTION_PCT  = 0.00119   # % of buy value deducted on every buy
SELL_TRANSACTION_PCT = 0.00104   # % of sell value deducted on every sell
DP_CHARGE_PER_SELL   = 13.5      # flat ₹13.5 per sell (CDSL DP charge)

# ── STRATEGY SETTINGS ────────────────────────────────────────────────────────
ACTIVE_STRATEGY = "combined"  # Options: "ma_crossover", "rsi", "momentum", "combined"

# Moving Average Crossover — faster periods for aggressive mode
MA_FAST = 5
MA_SLOW = 13

# RSI — wider thresholds catch more trades
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Momentum — lower threshold = more signals
MOMENTUM_PERIOD = 10
MOMENTUM_THRESHOLD = 0.015    # 1.5% move triggers signal (was 2%)

# ── ANGEL ONE API (Phase 2 — fill when ready) ────────────────────────────────
ANGEL_ONE_API_KEY = ""        # From Angel One SmartAPI dashboard
ANGEL_ONE_CLIENT_ID = ""      # Your Angel One client ID
ANGEL_ONE_PIN = ""            # 4-digit MPIN
ANGEL_ONE_TOTP_SECRET = ""    # TOTP secret for 2FA

# ── REPORTING ────────────────────────────────────────────────────────────────
REPORT_DIR = "data/reports"
PORTFOLIO_FILE = "data/portfolio.json"
TRADE_LOG_FILE = "data/trade_log.csv"
