from __future__ import annotations
import numpy as np
import pandas as pd

SCENARIOS = {
    # share of Q2 2026 margin premium above normalized margin that persists
    "q2_2026_extreme": 1.00,
    "elevated_75pct_premium": 0.75,
    "partial_50pct_premium": 0.50,
    "partial_25pct_premium": 0.25,
    "mid_cycle": 0.00,
    "soft_cycle_20pct_below_normal": -0.20,
}

DAYS_IN_QTR = 91.0

def scenario_margin(normalized, current, premium_share):
    premium = current - normalized
    if premium_share >= 0:
        return normalized + premium_share * premium
    # negative values represent a discount to normalized margin itself
    return normalized * (1.0 + premium_share)

def build_cycle_scenarios(inputs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in inputs.iterrows():
        current_margin = float(r["q2_2026_margin_per_bbl"])
        normal_margin = float(r["normalized_margin_per_bbl"])
        current_q_earn = float(r["q2_2026_earnings_proxy_bn"])
        throughput = float(r["q2_2026_throughput_mbpd"])

        # At Q2 actual, the earnings proxy is observed. For other scenarios,
        # reduce/increase the proxy dollar-for-dollar with modeled margin dollars.
        for name, premium_share in SCENARIOS.items():
            m = scenario_margin(normal_margin, current_margin, premium_share)
            delta_margin = m - current_margin
            delta_bn = delta_margin * throughput * DAYS_IN_QTR / 1000.0
            q_earn = max(current_q_earn + delta_bn, 0.0)
            annualized = q_earn * 4.0
            retention = (q_earn/current_q_earn*100.0) if current_q_earn else np.nan

            rows.append({
                "ticker": r["ticker"],
                "company": r["company"],
                "scenario": name,
                "modeled_margin_per_bbl": m,
                "modeled_quarter_earnings_proxy_bn": q_earn,
                "modeled_annualized_earnings_proxy_bn": annualized,
                "earnings_retention_vs_q2_pct": retention,
                "earnings_proxy_definition": r["earnings_proxy_definition"],
            })
    return pd.DataFrame(rows)

def cycle_resilience(scenarios: pd.DataFrame) -> pd.DataFrame:
    mid = scenarios[scenarios["scenario"]=="mid_cycle"].copy()
    soft = scenarios[scenarios["scenario"]=="soft_cycle_20pct_below_normal"].copy()
    m = mid[["ticker","company","earnings_retention_vs_q2_pct",
             "modeled_annualized_earnings_proxy_bn"]].rename(columns={
        "earnings_retention_vs_q2_pct":"midcycle_retention_pct",
        "modeled_annualized_earnings_proxy_bn":"midcycle_annualized_proxy_bn"
    })
    s = soft[["ticker","earnings_retention_vs_q2_pct",
              "modeled_annualized_earnings_proxy_bn"]].rename(columns={
        "earnings_retention_vs_q2_pct":"softcycle_retention_pct",
        "modeled_annualized_earnings_proxy_bn":"softcycle_annualized_proxy_bn"
    })
    out = m.merge(s,on="ticker",how="left")

    # Score based on a blend of mid-cycle and soft-cycle earnings retention.
    raw = 0.70*out["midcycle_retention_pct"] + 0.30*out["softcycle_retention_pct"]
    if raw.max() == raw.min():
        out["cycle_resilience_score"] = 50.0
    else:
        out["cycle_resilience_score"] = (raw-raw.min())/(raw.max()-raw.min())*100.0
    return out
