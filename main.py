from pathlib import Path
import pandas as pd

from src.model import run_all, SCENARIOS
from src.market_data import fetch_market_data, performance_table
from src.valuation import valuation_score
from src.backtest import event_window_returns
from src.crack_spread import approximate_321_crack
from src.crack_regimes import summarize_crack_regimes
from src.monte_carlo import simulate_scores
from src.investment_rank import integrate
from src.cycle_normalization import build_cycle_scenarios, cycle_resilience
from src.final_rank import build_refiner_final_rank
from src.normalized_valuation import build_q2_replacement_bridge, build_pass_through_sensitivity

ROOT = Path(__file__).resolve().parent
DATA = ROOT/"data"
OUT = ROOT/"outputs"


def main():
    print("="*80)
    print("Hormuz U.S. Energy Investment Exposure Model v0.5.1")
    print("="*80)

    company = pd.read_csv(DATA/"company_metrics.csv")
    valuation = pd.read_csv(DATA/"valuation_current.csv")
    events = pd.read_csv(DATA/"event_dates.csv")
    cycle_inputs = pd.read_csv(DATA/"cycle_normalization_inputs.csv")
    normalized_fundamentals = pd.read_csv(DATA/"normalized_valuation_fundamentals.csv")

    print("[1/12] Loading SEC/EIA operating and cycle-normalization evidence...")
    print("[2/12] Current valuation layer...")
    val = valuation_score(valuation)
    val.to_csv(OUT/"valuation_scores_current.csv",index=False)

    print("[3/12] Attempting live market-data pull...")
    px=None
    market_perf=None
    crack=None
    try:
        px=fetch_market_data(start="2026-01-01")
        px.to_csv(OUT/"market_prices.csv")
        market_perf=performance_table(px)
        market_perf.to_csv(OUT/"market_performance.csv",index=False)
        print("       Market data pull successful")
        if not market_perf.empty:
            start = market_perf["sample_start"].min()
            end = market_perf["sample_end"].max()
            print(f"       Observed market sample: {start} through {end}")
    except Exception as exc:
        print("       Market data unavailable:", exc)

    print("[4/12] Operational exposure scenarios...")
    factors,scores=run_all(company,market_perf)
    factors.to_csv(OUT/"factor_table.csv",index=False)
    scores.to_csv(OUT/"scenario_scores.csv",index=False)

    print("[5/12] Event-window backtest...")
    if px is not None:
        stocks=[c for c in ["VLO","MPC","PSX","XOM","CVX","XLE"] if c in px.columns]
        event_window_returns(px[stocks],events).to_csv(OUT/"event_window_returns.csv",index=False)

    print("[6/12] Crack-spread regimes...")
    if px is not None:
        crack=approximate_321_crack(px)
        crack.to_csv(OUT/"crack_321_proxy.csv")
        crack_regimes=summarize_crack_regimes(crack)
        crack_regimes.to_csv(OUT/"crack_regime_summary.csv",index=False)
        if not crack_regimes.empty:
            latest=crack_regimes.iloc[-1]
            print(
                f"       Latest regime observed through {latest['observed_through']} "
                f"(defined window end {latest['defined_window_end']})"
            )

    print("[7/12] Persistent-disruption Monte Carlo...")
    simulate_scores(factors,SCENARIOS["persistent_disruption"],n=10000).to_csv(
        OUT/"monte_carlo_persistent.csv",index=False
    )

    print("[8/12] Prospective ranking...")
    ranking=integrate(scores,val)
    ranking.to_csv(OUT/"prospective_investment_ranking.csv",index=False)

    print("[9/12] Refining-cycle normalization scenarios...")
    cycle_scen=build_cycle_scenarios(cycle_inputs)
    cycle_scen.to_csv(OUT/"cycle_normalization_scenarios.csv",index=False)
    resilience=cycle_resilience(cycle_scen)
    resilience.to_csv(OUT/"cycle_resilience.csv",index=False)

    print("[10/12] Cycle-adjusted refiner ranking...")
    final=build_refiner_final_rank(ranking,resilience)
    final.to_csv(OUT/"cycle_adjusted_refiner_ranking.csv",index=False)

    print("[11/12] Normalized valuation stress tests...")
    bridge=build_q2_replacement_bridge(
        valuation=valuation,
        resilience=resilience,
        cycle_inputs=cycle_inputs,
        fundamentals=normalized_fundamentals,
    )
    bridge.to_csv(OUT/"normalized_q2_replacement_ev_ebitda_bridge.csv",index=False)
    sensitivity=build_pass_through_sensitivity(valuation,resilience)
    sensitivity.to_csv(OUT/"normalized_valuation_pass_through_sensitivity.csv",index=False)

    print("[12/12] Results")
    show=["ticker","company","prospective_score","midcycle_retention_pct",
          "softcycle_retention_pct","cycle_resilience_score",
          "cycle_adjusted_prospective_score"]
    print(final[show].round(2).to_string(index=False))

    print("\nMid-cycle annualized segment earnings proxies:")
    print(final[["ticker","midcycle_annualized_proxy_bn",
                 "softcycle_annualized_proxy_bn"]].round(2).to_string(index=False))

    print("\nQ2-replacement EV/EBITDA bridge (mid-cycle):")
    bridge_mid=bridge[bridge["scenario"]=="mid_cycle"][[
        "ticker","current_ev_ebitda","implied_ev_ebitda_after_q2_replacement"
    ]]
    print(bridge_mid.round(2).to_string(index=False))

    print("\nIMPORTANT: segment earnings proxies are not directly comparable to consolidated EPS.")
    print("Normalized valuation outputs are sensitivity diagnostics, not price targets.")
    print("Research only; not investment advice.")


if __name__=="__main__":
    main()
