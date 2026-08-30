from __future__ import annotations
import pandas as pd

def minmax(s, invert=False):
    s = pd.to_numeric(s, errors="coerce").astype(float)
    if s.max() == s.min():
        out = pd.Series(50.0, index=s.index)
    else:
        out = (s-s.min())/(s.max()-s.min())*100
    return 100-out if invert else out

def valuation_score(df):
    d = df.copy()
    # Cheapness / cash generation
    d["forward_pe_score"] = minmax(d["forward_pe"], invert=True)
    d["ev_ebitda_score"] = minmax(d["ev_ebitda"], invert=True)
    d["fcf_yield_score"] = minmax(d["fcf_yield_pct"])
    d["dividend_score"] = minmax(d["dividend_yield_pct"])
    # Balance-sheet resilience: lower net debt/EBITDA is better.
    d["balance_sheet_score"] = minmax(d["net_debt_ebitda"], invert=True)
    # Rerating restraint: less multiple expansion vs FY2025 is better.
    d["rerating_score"] = minmax(d["ev_ebitda_rerating_pct_vs_2025"], invert=True)

    # Valuation is intentionally multi-dimensional.
    d["valuation_score"] = (
        0.25*d["forward_pe_score"] +
        0.20*d["ev_ebitda_score"] +
        0.25*d["fcf_yield_score"] +
        0.10*d["dividend_score"] +
        0.15*d["balance_sheet_score"] +
        0.05*d["rerating_score"]
    )
    return d
