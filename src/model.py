from __future__ import annotations
import pandas as pd

SCENARIOS = {
    "normalization": {
        "peer_operating_uplift": 0.15,
        "refining_shock_capture": 0.15,
        "middle_east_resilience": 0.15,
        "upstream_hedge": 0.25,
        "scale_resilience": 0.15,
        "market_confirmation": 0.15,
    },
    "persistent_disruption": {
        "peer_operating_uplift": 0.20,
        "refining_shock_capture": 0.30,
        "middle_east_resilience": 0.20,
        "upstream_hedge": 0.10,
        "scale_resilience": 0.10,
        "market_confirmation": 0.10,
    },
    "severe_disruption": {
        "peer_operating_uplift": 0.10,
        "refining_shock_capture": 0.15,
        "middle_east_resilience": 0.30,
        "upstream_hedge": 0.25,
        "scale_resilience": 0.15,
        "market_confirmation": 0.05,
    },
}

def minmax(series):
    s = pd.to_numeric(series, errors="coerce").astype(float)
    if s.max() == s.min():
        return pd.Series(50.0, index=s.index)
    return (s - s.min()) / (s.max() - s.min()) * 100

def prepare_factors(company_df, market_perf=None):
    d = company_df.copy()

    # Normalize operating uplift only inside comparable business groups.
    # This avoids comparing refining-margin growth directly with integrated-major net-income growth.
    d["peer_operating_uplift"] = 50.0
    for group, idx in d.groupby("business_type").groups.items():
        vals = d.loc[idx, "metric_yoy_pct"]
        d.loc[idx, "peer_operating_uplift"] = minmax(vals)

    d["refining_shock_capture"] = d["refining_shock_capture_parameter"].clip(0,100)
    d["middle_east_resilience"] = 100 - d["direct_middle_east_exposure_parameter"].clip(0,100)
    d["upstream_hedge"] = d["upstream_price_hedge_parameter"].clip(0,100)
    d["scale_resilience"] = minmax(d["throughput_or_production_mbd"])
    d["market_confirmation"] = 50.0

    if market_perf is not None and not market_perf.empty:
        perf = market_perf[market_perf["ticker"].isin(d["ticker"])][["ticker","period_return_pct"]]
        d = d.merge(perf, on="ticker", how="left")
        mask = d["period_return_pct"].notna()
        if mask.sum() >= 2:
            d.loc[mask, "market_confirmation"] = minmax(d.loc[mask, "period_return_pct"])

    return d

def score_scenario(factors, scenario):
    d = factors.copy()
    w = SCENARIOS[scenario]
    d["score"] = sum(d[k] * wt for k, wt in w.items())
    d["scenario"] = scenario
    return d.sort_values("score", ascending=False)

def run_all(company_df, market_perf=None):
    factors = prepare_factors(company_df, market_perf)
    scores = pd.concat([score_scenario(factors, s) for s in SCENARIOS], ignore_index=True)
    return factors, scores
