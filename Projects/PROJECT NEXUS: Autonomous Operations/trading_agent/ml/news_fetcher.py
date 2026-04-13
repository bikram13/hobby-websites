"""
Fetch financial news headlines for an NSE symbol via Google News RSS.
No API key required. Returns recent articles only (not historical).

Used at live inference time only — not during GBM gate training.
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


def _build_rss_url(symbol: str) -> str:
    """Build Google News RSS URL for a symbol."""
    clean = symbol.replace(".NS", "").replace(".BO", "")
    query = f"{clean} NSE stock India"
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"


def _parse_rss(content: bytes, max_articles: int) -> list[tuple[str, str]]:
    """Parse RSS XML bytes into list of (headline, pub_date) tuples."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []
    channel = root.find("channel")
    if channel is None:
        return []
    results = []
    for item in channel.findall("item")[:max_articles]:
        title = (item.findtext("title") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if title:
            results.append((title, pub_date))
    return results


def fetch_headlines(symbol: str, max_articles: int = 20) -> list[tuple[str, str]]:
    """
    Fetch news headlines for an NSE symbol from Google News RSS.

    Parameters
    ----------
    symbol       : NSE ticker e.g. "RELIANCE.NS" (exchange suffix is stripped)
    max_articles : maximum number of headlines to return

    Returns
    -------
    List of (headline_str, pub_date_str) tuples. Empty list on any failure.
    """
    if not symbol:
        return []
    url = _build_rss_url(symbol)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
        return _parse_rss(content, max_articles)
    except Exception:
        return []
