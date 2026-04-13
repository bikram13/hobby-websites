"""
NSE sector index data and sector-momentum feature for NEXUS ML gate.

SECTOR_INDICES: maps sector name → yfinance ticker for NSE sector indices.
SYMBOL_SECTOR_MAP: maps NSE stock symbol → sector name.
compute_sector_feature(): returns pct by which sector is above/below its 20d EMA.
"""
import pandas as pd

# NSE sector index tickers on yfinance
SECTOR_INDICES = {
    "bank":    "^NSEBANK",
    "it":      "^CNXIT",
    "pharma":  "^CNXPHARMA",
    "energy":  "^CNXENERGY",
    "fmcg":    "^CNXFMCG",
    "auto":    "^CNXAUTO",
    "metal":   "^CNXMETAL",
}

# Symbol → sector mapping (covers all 89 symbols in config.WATCHLIST)
SYMBOL_SECTOR_MAP = {
    # Banks & Financials
    "HDFCBANK.NS": "bank", "ICICIBANK.NS": "bank", "SBIN.NS": "bank",
    "AXISBANK.NS": "bank", "KOTAKBANK.NS": "bank", "INDUSINDBK.NS": "bank",
    "BANDHANBNK.NS": "bank", "RBLBANK.NS": "bank", "YESBANK.NS": "bank",
    "IDFCFIRSTB.NS": "bank", "BAJFINANCE.NS": "bank", "BAJAJFINSV.NS": "bank",
    "SBILIFE.NS": "bank", "HDFCLIFE.NS": "bank", "CHOLAFIN.NS": "bank",
    "MUTHOOTFIN.NS": "bank", "MANAPPURAM.NS": "bank", "LICHSGFIN.NS": "bank",
    "ABCAPITAL.NS": "bank",
    # IT
    "TCS.NS": "it", "INFY.NS": "it", "HCLTECH.NS": "it", "WIPRO.NS": "it",
    "TECHM.NS": "it", "LTIM.NS": "it", "MPHASIS.NS": "it", "COFORGE.NS": "it",
    "PERSISTENT.NS": "it", "LTTS.NS": "it",
    # Pharma
    "SUNPHARMA.NS": "pharma", "DRREDDY.NS": "pharma", "CIPLA.NS": "pharma",
    "DIVISLAB.NS": "pharma", "APOLLOHOSP.NS": "pharma", "MAXHEALTH.NS": "pharma",
    "FORTIS.NS": "pharma",
    # Energy
    "RELIANCE.NS": "energy", "ONGC.NS": "energy", "COALINDIA.NS": "energy",
    "BPCL.NS": "energy", "GAIL.NS": "energy", "NHPC.NS": "energy",
    "IOC.NS": "energy", "HINDPETRO.NS": "energy", "PETRONET.NS": "energy",
    "NTPC.NS": "energy", "POWERGRID.NS": "energy", "ADANIPORTS.NS": "energy",
    "ADANIENT.NS": "energy",
    # FMCG
    "NESTLEIND.NS": "fmcg", "TATACONSUM.NS": "fmcg", "DABUR.NS": "fmcg",
    "MARICO.NS": "fmcg", "GODREJCP.NS": "fmcg", "PIDILITIND.NS": "fmcg",
    # Auto
    "MARUTI.NS": "auto", "M&M.NS": "auto", "HEROMOTOCO.NS": "auto",
    "EICHERMOT.NS": "auto", "BAJAJ-AUTO.NS": "auto",
    # Metal / Industrials
    "JSWSTEEL.NS": "metal", "TATASTEEL.NS": "metal", "HINDALCO.NS": "metal",
    "SAIL.NS": "metal", "NMDC.NS": "metal",
    "SIEMENS.NS": "metal", "ABB.NS": "metal", "HAVELLS.NS": "metal",
    "VOLTAS.NS": "metal", "POLYCAB.NS": "metal", "CUMMINSIND.NS": "metal",
    "BHEL.NS": "metal", "RVNL.NS": "metal", "IRB.NS": "metal",
    "GRASIM.NS": "metal", "ULTRACEMCO.NS": "metal",
    # Other / Specialty
    "ASIANPAINT.NS": "fmcg", "TITAN.NS": "fmcg",
    "PAYTM.NS": "it", "NYKAA.NS": "fmcg", "POLICYBZR.NS": "bank",
    "IRCTC.NS": "metal", "DELHIVERY.NS": "metal", "INDUSTOWER.NS": "energy",
    "ETERNAL.NS": "it", "PIIND.NS": "pharma", "AARTIIND.NS": "pharma",
    "IDEA.NS": "it",
}


def get_sector_for_symbol(symbol: str) -> str | None:
    """Return the sector name for a given NSE symbol, or None if unmapped."""
    return SYMBOL_SECTOR_MAP.get(symbol)


def compute_sector_feature(
    sector_df: pd.DataFrame | None,
    signal_date,
    ema_period: int = 20,
) -> float:
    """
    Compute sector momentum: (sector_price - sector_EMA20) / sector_EMA20.

    Filters sector_df to only rows <= signal_date (no look-ahead bias).
    Returns 0.0 if sector data unavailable or insufficient rows.

    Range: roughly -0.15 to +0.15 (normalised %)
    """
    if sector_df is None or sector_df.empty or "close" not in sector_df.columns:
        return 0.0

    window = sector_df[sector_df.index <= signal_date]
    if len(window) < ema_period + 5:
        return 0.0

    close   = window["close"]
    ema20   = float(close.ewm(span=ema_period, adjust=False).mean().iloc[-1])
    last    = float(close.iloc[-1])
    if ema20 <= 0:
        return 0.0
    return round((last - ema20) / ema20, 5)
