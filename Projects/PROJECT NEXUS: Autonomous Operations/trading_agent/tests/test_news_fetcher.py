"""Tests for news_fetcher.py — headline fetching and parsing."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET
from ml.news_fetcher import fetch_headlines, _build_rss_url, _parse_rss


# ── _build_rss_url ────────────────────────────────────────────────────────────

def test_build_url_strips_ns_suffix():
    url = _build_rss_url("RELIANCE.NS")
    assert "RELIANCE.NS" not in url
    assert "RELIANCE" in url

def test_build_url_strips_bo_suffix():
    url = _build_rss_url("HDFCBANK.BO")
    assert "HDFCBANK.BO" not in url
    assert "HDFCBANK" in url

def test_build_url_is_google_news_rss():
    url = _build_rss_url("TCS.NS")
    assert url.startswith("https://news.google.com/rss/search")
    assert "TCS" in url

def test_build_url_already_clean():
    url = _build_rss_url("INFY")
    assert "INFY" in url


# ── _parse_rss ────────────────────────────────────────────────────────────────

def test_parse_rss_extracts_titles():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title>TCS Q4 profit jumps 12%</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
      <item><title>TCS wins $500M deal</title><pubDate>Sun, 13 Apr 2026 09:00:00 GMT</pubDate></item>
    </channel></rss>"""
    results = _parse_rss(xml_bytes, max_articles=10)
    assert len(results) == 2
    assert results[0][0] == "TCS Q4 profit jumps 12%"
    assert results[1][0] == "TCS wins $500M deal"

def test_parse_rss_respects_max_articles():
    items = "".join(
        f"<item><title>News {i}</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>"
        for i in range(10)
    )
    xml_bytes = f"""<?xml version="1.0"?><rss><channel>{items}</channel></rss>""".encode()
    results = _parse_rss(xml_bytes, max_articles=3)
    assert len(results) == 3

def test_parse_rss_skips_empty_titles():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title></title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
      <item><title>Real headline</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
    </channel></rss>"""
    results = _parse_rss(xml_bytes, max_articles=10)
    assert len(results) == 1
    assert results[0][0] == "Real headline"

def test_parse_rss_returns_empty_on_malformed_xml():
    results = _parse_rss(b"this is not xml", max_articles=10)
    assert results == []


# ── fetch_headlines (network-mocked) ─────────────────────────────────────────

def test_fetch_headlines_returns_list_on_success():
    xml_bytes = b"""<?xml version="1.0"?>
    <rss><channel>
      <item><title>Reliance Industries posts record revenue</title><pubDate>Mon, 14 Apr 2026 10:00:00 GMT</pubDate></item>
    </channel></rss>"""

    with patch("ml.news_fetcher.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = xml_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        results = fetch_headlines("RELIANCE.NS")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0][0] == "Reliance Industries posts record revenue"

def test_fetch_headlines_returns_empty_on_network_error():
    with patch("ml.news_fetcher.urllib.request.urlopen", side_effect=Exception("timeout")):
        results = fetch_headlines("RELIANCE.NS")
        assert results == []

def test_fetch_headlines_returns_empty_for_empty_symbol():
    results = fetch_headlines("")
    assert results == []
