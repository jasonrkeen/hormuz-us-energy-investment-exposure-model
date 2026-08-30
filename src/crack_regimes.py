from __future__ import annotations
import pandas as pd

def summarize_crack_regimes(crack: pd.DataFrame):
    if crack is None or crack.empty:
        return pd.DataFrame()

    d = crack.copy()
    d.index = pd.to_datetime(d.index)
    col = "crack_321_usd_per_bbl"
    periods = [
        ("pre_shock_jan_feb_2026","2026-01-01","2026-02-28"),
        ("initial_disruption_mar_apr_2026","2026-03-01","2026-04-30"),
        ("elevated_may_jun_2026","2026-05-01","2026-06-30"),
        ("extreme_jul_aug_2026","2026-07-01","2026-08-31"),
    ]
    rows=[]
    for name,start,end in periods:
        s=d.loc[start:end,col].dropna()
        if s.empty:
            continue
        rows.append({
            "regime":name,
            "start":start,
            "end":end,
            "observations":len(s),
            "average_crack_usd_per_bbl":s.mean(),
            "median_crack_usd_per_bbl":s.median(),
            "p10":s.quantile(.10),
            "p90":s.quantile(.90),
        })
    return pd.DataFrame(rows)
