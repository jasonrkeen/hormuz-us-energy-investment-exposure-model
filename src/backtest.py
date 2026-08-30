from __future__ import annotations
import pandas as pd

def event_window_returns(prices: pd.DataFrame, events: pd.DataFrame, windows=(1,5,20)):
    """
    Computes close-to-close returns around the nearest trading day on/after each event.
    Returns are forward event windows, useful for comparing relative market reaction.
    """
    px = prices.copy().sort_index()
    px.index = pd.to_datetime(px.index)
    rows = []
    for _, ev in events.iterrows():
        d = pd.Timestamp(ev["event_date"])
        eligible = px.index[px.index >= d]
        if len(eligible) == 0:
            continue
        t0 = eligible[0]
        i0 = px.index.get_loc(t0)
        for ticker in px.columns:
            s = px[ticker].dropna()
            if t0 not in s.index:
                continue
            for w in windows:
                idx = i0 + w
                if idx >= len(px.index):
                    continue
                t1 = px.index[idx]
                if pd.isna(px.loc[t0, ticker]) or pd.isna(px.loc[t1, ticker]):
                    continue
                ret = (px.loc[t1, ticker] / px.loc[t0, ticker] - 1) * 100
                rows.append({
                    "event": ev["event"],
                    "event_date": ev["event_date"],
                    "ticker": ticker,
                    "window_trading_days": w,
                    "return_pct": ret
                })
    return pd.DataFrame(rows)
