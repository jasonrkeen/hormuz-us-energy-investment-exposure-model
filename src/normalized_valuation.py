from __future__ import annotations
import pandas as pd


def build_q2_replacement_bridge(
    valuation: pd.DataFrame,
    resilience: pd.DataFrame,
    cycle_inputs: pd.DataFrame,
    fundamentals: pd.DataFrame,
) -> pd.DataFrame:
    """Build a transparent TTM EV/EBITDA normalization bridge.

    Replaces observed Q2 2026 segment earnings proxy with a modeled mid-cycle
    or soft-cycle quarterly proxy while holding all other TTM components fixed.
    This is a sensitivity diagnostic, not an EPS forecast or price target.
    """
    base = cycle_inputs[[
        "ticker", "company", "q2_2026_earnings_proxy_bn",
        "earnings_proxy_definition"
    ]].copy()
    base = base.merge(resilience[[
        "ticker", "midcycle_annualized_proxy_bn", "softcycle_annualized_proxy_bn"
    ]], on="ticker", how="left")
    base = base.merge(fundamentals[[
        "ticker", "enterprise_value_bn", "ttm_ebitda_bn"
    ]], on="ticker", how="left")
    base = base.merge(valuation[["ticker", "ev_ebitda"]], on="ticker", how="left")

    rows = []
    for _, r in base.iterrows():
        for scenario, annualized_col in [
            ("mid_cycle", "midcycle_annualized_proxy_bn"),
            ("soft_cycle_20pct_below_normal", "softcycle_annualized_proxy_bn"),
        ]:
            scenario_q = float(r[annualized_col]) / 4.0
            current_q = float(r["q2_2026_earnings_proxy_bn"])
            excess_removed = current_q - scenario_q
            adjusted_ttm = float(r["ttm_ebitda_bn"]) - excess_removed
            implied_multiple = (
                float(r["enterprise_value_bn"]) / adjusted_ttm
                if adjusted_ttm > 0 else float("nan")
            )
            rows.append({
                "ticker": r["ticker"],
                "company": r["company"],
                "scenario": scenario,
                "earnings_proxy_definition": r["earnings_proxy_definition"],
                "q2_current_segment_proxy_bn": current_q,
                "q2_scenario_segment_proxy_bn": scenario_q,
                "q2_excess_removed_bn": excess_removed,
                "current_ttm_ebitda_bn": float(r["ttm_ebitda_bn"]),
                "adjusted_ttm_ebitda_bn": adjusted_ttm,
                "enterprise_value_bn": float(r["enterprise_value_bn"]),
                "current_ev_ebitda": float(r["ev_ebitda"]),
                "implied_ev_ebitda_after_q2_replacement": implied_multiple,
            })
    return pd.DataFrame(rows)


def build_pass_through_sensitivity(
    valuation: pd.DataFrame,
    resilience: pd.DataFrame,
    pass_through_levels=(0.50, 0.75, 1.00),
) -> pd.DataFrame:
    """Stress valuation ratios using segment earnings-retention assumptions."""
    d = resilience.merge(valuation[[
        "ticker", "forward_pe", "ev_ebitda", "fcf_yield_pct"
    ]], on="ticker", how="left")

    rows = []
    for _, r in d.iterrows():
        for scenario, retention_col in [
            ("mid_cycle", "midcycle_retention_pct"),
            ("soft_cycle_20pct_below_normal", "softcycle_retention_pct"),
        ]:
            segment_retention = float(r[retention_col]) / 100.0
            for pass_through in pass_through_levels:
                consolidated_retention = 1.0 - pass_through * (1.0 - segment_retention)
                rows.append({
                    "ticker": r["ticker"],
                    "scenario": scenario,
                    "segment_retention_pct": segment_retention * 100.0,
                    "pass_through_pct": pass_through * 100.0,
                    "implied_consolidated_earnings_retention_pct": consolidated_retention * 100.0,
                    "current_forward_pe": float(r["forward_pe"]),
                    "stressed_forward_pe": float(r["forward_pe"]) / consolidated_retention,
                    "current_ev_ebitda": float(r["ev_ebitda"]),
                    "stressed_ev_ebitda": float(r["ev_ebitda"]) / consolidated_retention,
                    "current_fcf_yield_pct": float(r["fcf_yield_pct"]),
                    "stressed_fcf_yield_pct": float(r["fcf_yield_pct"]) * consolidated_retention,
                })
    return pd.DataFrame(rows)
