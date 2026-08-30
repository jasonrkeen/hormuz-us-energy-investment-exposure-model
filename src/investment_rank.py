from __future__ import annotations
import pandas as pd

def integrate(exposure_scores: pd.DataFrame, valuation_scores: pd.DataFrame):
    base = exposure_scores.pivot_table(
        index=["ticker","company"], columns="scenario", values="score"
    ).reset_index()
    scen = ["normalization","persistent_disruption","severe_disruption"]
    base["exposure_avg"] = base[scen].mean(axis=1)

    cols = [
        "ticker","forward_pe","ev_ebitda","fcf_yield_pct","dividend_yield_pct",
        "net_debt_ebitda","valuation_score"
    ]
    d = base.merge(valuation_scores[cols], on="ticker", how="left")

    # Exposure remains primary, but real current valuation is now material.
    d["integrated_score"] = 0.65*d["exposure_avg"] + 0.35*d["valuation_score"]

    # A separate prospective score puts somewhat more emphasis on valuation
    # because the historical shock trade has already generated large gains.
    d["prospective_score"] = 0.55*d["exposure_avg"] + 0.45*d["valuation_score"]

    return d.sort_values("prospective_score", ascending=False)
