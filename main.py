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

ROOT = Path(__file__).resolve().parent
DATA = ROOT/"data"
OUT = ROOT/"outputs"

def main():
    print("="*80)
    print("Hormuz U.S. Energy Investment Exposure Model v0.5")
    print("="*80)

    company = pd.read_csv(DATA/"company_metrics.csv")
    valuation = pd.read_csv(DATA/"valuation_current.csv")
    events = pd.read_csv(DATA/"event_dates.csv")
    cycle_inputs = pd.read_csv(DATA/"cycle_normalization_inputs.csv")

    print("[1/11] Loading SEC/EIA operating and cycle-normalization evidence...")
    print("[2/11] Current valuation layer...")
    val = valuation_score(valuation)
    val.to_csv(OUT/"valuation_scores_current.csv",index=False)

    print("[3/11] Attempting live market-data pull...")
    px=None
    market_perf=None
    crack=None
    try:
        px=fetch_market_data(start="2026-01-01")
        px.to_csv(OUT/"market_prices.csv")
        market_perf=performance_table(px)
        market_perf.to_csv(OUT/"market_performance.csv",index=False)
        print("       Market data pull successful")
    except Exception as exc:
        print("       Market data unavailable:", exc)

    print("[4/11] Operational exposure scenarios...")
    factors,scores=run_all(company,market_perf)
    factors.to_csv(OUT/"factor_table.csv",index=False)
    scores.to_csv(OUT/"scenario_scores.csv",index=False)

    print("[5/11] Event-window backtest...")
    if px is not None:
        stocks=[c for c in ["VLO","MPC","PSX","XOM","CVX","XLE"] if c in px.columns]
        event_window_returns(px[stocks],events).to_csv(OUT/"event_window_returns.csv",index=False)

    print("[6/11] Crack-spread regimes...")
    if px is not None:
        crack=approximate_321_crack(px)
        crack.to_csv(OUT/"crack_321_proxy.csv")
        summarize_crack_regimes(crack).to_csv(OUT/"crack_regime_summary.csv",index=False)

    print("[7/11] Persistent-disruption Monte Carlo...")
    simulate_scores(factors,SCENARIOS["persistent_disruption"],n=10000).to_csv(
        OUT/"monte_carlo_persistent.csv",index=False
    )

    print("[8/11] v0.4 prospective ranking...")
    ranking=integrate(scores,val)
    ranking.to_csv(OUT/"prospective_investment_ranking.csv",index=False)

    print("[9/11] Refining-cycle normalization scenarios...")
    cycle_scen=build_cycle_scenarios(cycle_inputs)
    cycle_scen.to_csv(OUT/"cycle_normalization_scenarios.csv",index=False)
    resilience=cycle_resilience(cycle_scen)
    resilience.to_csv(OUT/"cycle_resilience.csv",index=False)

    print("[10/11] Cycle-adjusted refiner ranking...")
    final=build_refiner_final_rank(ranking,resilience)
    final.to_csv(OUT/"cycle_adjusted_refiner_ranking.csv",index=False)

    print("[11/11] Results")
    show=["ticker","company","prospective_score","midcycle_retention_pct",
          "softcycle_retention_pct","cycle_resilience_score",
          "cycle_adjusted_prospective_score"]
    print(final[show].round(2).to_string(index=False))

    print("\nMid-cycle annualized segment earnings proxies:")
    print(final[["ticker","midcycle_annualized_proxy_bn",
                 "softcycle_annualized_proxy_bn"]].round(2).to_string(index=False))

    print("\nIMPORTANT: earnings proxies are segment-specific and not directly comparable")
    print("to consolidated EPS. The exercise tests cycle dependence, not price targets.")
    print("Research only; not investment advice.")

if __name__=="__main__":
    main()
