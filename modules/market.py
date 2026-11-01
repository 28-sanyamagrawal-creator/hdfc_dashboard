"""
market.py
---------
Live share price for HDFC Bank from Yahoo Finance.

Order of attempts:
  1. yfinance library            (easiest, works on most home / college Wi-Fi)
  2. Yahoo Finance chart API     (plain HTTP request, used if yfinance breaks)
  3. Offline fallback            (31-Mar-2026 closing price from the annual report)

investing.com has no public API and blocks automated requests, so Yahoo is used.
Prices on Yahoo can be delayed by up to ~15 minutes during market hours.
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
import requests

TICKER_NSE = "HDFCBANK.NS"
TICKER_BSE = "HDFCBANK.BO"
BENCHMARK = "^NSEBANK"           # Nifty Bank index
FALLBACK_PRICE = 731.55           # NSE close on 31-Mar-2026 (FY26 annual report)
FALLBACK_DATE = "31-Mar-2026"

_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

PERIODS = {  # label -> (yahoo range, interval)
    "1D": ("1d", "5m"), "5D": ("5d", "15m"), "1M": ("1mo", "1d"), "6M": ("6mo", "1d"),
    "YTD": ("ytd", "1d"), "1Y": ("1y", "1d"), "3Y": ("3y", "1d"), "5Y": ("5y", "1wk"), "MAX": ("max", "1mo"),
}


# ----------------------------------------------------------------------------
def _history_yfinance(ticker: str, rng: str, interval: str) -> pd.DataFrame:
    import yfinance as yf  # imported here so the app still opens if yfinance is missing
    df = yf.Ticker(ticker).history(period=rng, interval=interval, auto_adjust=False)
    if df is None or df.empty:
        raise ValueError("empty history")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    return df


def _history_http(ticker: str, rng: str, interval: str) -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    r = requests.get(url, params={"range": rng, "interval": interval}, headers=_HEADERS, timeout=10)
    r.raise_for_status()
    res = r.json()["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    tz = res.get("meta", {}).get("exchangeTimezoneName", "Asia/Kolkata")
    idx = pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(tz)
    df = pd.DataFrame({"Open": q["open"], "High": q["high"], "Low": q["low"],
                       "Close": q["close"], "Volume": q["volume"]}, index=idx).dropna(subset=["Close"])
    if df.empty:
        raise ValueError("empty history")
    return df


def get_history(ticker: str = TICKER_NSE, period: str = "1Y") -> tuple[pd.DataFrame, str]:
    """Returns (history DataFrame, source label). Empty frame if everything fails."""
    rng, interval = PERIODS.get(period, ("1y", "1d"))
    for fn, label in ((_history_yfinance, "Yahoo Finance (yfinance)"), (_history_http, "Yahoo Finance (API)")):
        try:
            return fn(ticker, rng, interval), label
        except Exception:
            continue
    return pd.DataFrame(), "offline"


def get_quote(ticker: str = TICKER_NSE) -> dict:
    """Latest price snapshot. Always returns a dict; 'live' tells you if it is real-time."""
    # 1) yfinance fast_info + 1-year daily history (for 52-week range)
    try:
        import yfinance as yf
        fi = yf.Ticker(ticker).fast_info
        num = lambda name: float(getattr(fi, name))  # noqa: E731
        q = dict(price=num("last_price"), prev_close=num("previous_close"), open=num("open"),
                 day_high=num("day_high"), day_low=num("day_low"), volume=num("last_volume"),
                 high_52w=num("year_high"), low_52w=num("year_low"),
                 source="Yahoo Finance (yfinance)", live=True)
        if not q["price"] or q["price"] != q["price"]:  # empty or NaN
            raise ValueError("no price")
        return _finish(q)
    except Exception:
        pass
    # 2) Plain HTTP call to the Yahoo chart endpoint
    try:
        d1 = _history_http(ticker, "5d", "5m")
        y1 = _history_http(ticker, "1y", "1d")
        today = d1[d1.index.date == d1.index[-1].date()]
        prev_days = y1[y1.index.date < d1.index[-1].date()]
        q = dict(price=float(d1["Close"].iloc[-1]),
                 prev_close=float(prev_days["Close"].iloc[-1]) if len(prev_days) else float(y1["Close"].iloc[-2]),
                 open=float(today["Open"].iloc[0]), day_high=float(today["High"].max()),
                 day_low=float(today["Low"].min()), volume=float(today["Volume"].sum()),
                 high_52w=float(y1["High"].max()), low_52w=float(y1["Low"].min()),
                 source="Yahoo Finance (API)", live=True)
        return _finish(q)
    except Exception:
        pass
    # 3) Offline
    q = dict(price=FALLBACK_PRICE, prev_close=FALLBACK_PRICE, open=None, day_high=None, day_low=None,
             volume=None, high_52w=None, low_52w=None,
             source=f"Offline - last price from annual report ({FALLBACK_DATE})", live=False)
    return _finish(q)


def _finish(q: dict) -> dict:
    q["change"] = q["price"] - q["prev_close"]
    q["change_pct"] = 100 * q["change"] / q["prev_close"] if q["prev_close"] else 0.0
    q["fetched_at"] = dt.datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
    return q


def period_returns(hist: pd.DataFrame) -> dict:
    """Simple price returns over standard windows from a long daily history."""
    if hist is None or hist.empty:
        return {}
    close = hist["Close"].dropna()
    last_date, last = close.index[-1], close.iloc[-1]
    out = {}
    for label, days in (("1 Week", 7), ("1 Month", 30), ("3 Months", 91), ("6 Months", 182),
                        ("1 Year", 365), ("3 Years", 1095), ("5 Years", 1825)):
        past = close[close.index <= last_date - pd.Timedelta(days=days)]
        if len(past):
            r = 100 * (last / past.iloc[-1] - 1)
            if days > 365:
                yrs = days / 365
                r_ann = 100 * ((last / past.iloc[-1]) ** (1 / yrs) - 1)
                out[label] = (r, r_ann)
            else:
                out[label] = (r, None)
    return out
