from __future__ import annotations
import pandas as pd

TICKERS = ["VLO","MPC","PSX","XOM","CVX"]
BENCHMARKS = ["XLE","BZ=F","CL=F","RB=F","HO=F"]


def fetch_market_data(start="2026-01-01", end=None):
    """Optional live/historical market pull using yfinance adjusted prices."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install yfinance: pip install -r requirements.txt") from exc

    symbols = TICKERS + BENCHMARKS
    raw = yf.download(symbols, start=start, end=end, auto_adjust=True, progress=False)
    if raw.empty:
        raise RuntimeError("No market data returned.")
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw["Close"].copy()
    else:
        px = raw[["Close"]].rename(columns={"Close": symbols[0]})
    return px.dropna(how="all")


def performance_table(px: pd.DataFrame):
    rows = []
    for col in px.columns:
        s = px[col].dropna()
        if len(s) < 2:
            continue
        ret = (s.iloc[-1] / s.iloc[0] - 1) * 100
        vol = s.pct_change().dropna().std() * (252 ** 0.5) * 100
        dd = (s / s.cummax() - 1).min() * 100
        rows.append({
            "ticker": col,
            "sample_start": pd.Timestamp(s.index[0]).date().isoformat(),
            "sample_end": pd.Timestamp(s.index[-1]).date().isoformat(),
            "period_return_pct": ret,
            "annualized_vol_pct": vol,
            "max_drawdown_pct": dd,
        })
    return pd.DataFrame(rows)
