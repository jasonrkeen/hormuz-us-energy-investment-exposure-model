from __future__ import annotations
import pandas as pd

def build_refiner_final_rank(v04_ranking: pd.DataFrame, resilience: pd.DataFrame):
    d = v04_ranking[v04_ranking["ticker"].isin(["VLO","MPC","PSX"])].copy()
    d = d.merge(resilience[[
        "ticker","midcycle_retention_pct","softcycle_retention_pct",
        "midcycle_annualized_proxy_bn","softcycle_annualized_proxy_bn",
        "cycle_resilience_score"
    ]], on="ticker", how="left")

    # v0.5 is deliberately focused on "what remains after normalization":
    # 70% v0.4 prospective attractiveness + 30% cycle resilience.
    d["cycle_adjusted_prospective_score"] = (
        0.70*d["prospective_score"] + 0.30*d["cycle_resilience_score"]
    )
    return d.sort_values("cycle_adjusted_prospective_score", ascending=False)
