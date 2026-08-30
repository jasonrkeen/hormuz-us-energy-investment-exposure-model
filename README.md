# Hormuz U.S. Energy Investment Exposure Model

A reproducible investment-intelligence model evaluating how the 2026 Strait of Hormuz disruption affected U.S. refiners and integrated oil majors — and whether the strongest beneficiaries still offer attractive prospective exposure after a large market rally.

**Current model version:** 0.5.0  
**Validated live run:** August 29, 2026  
**Universe:** VLO, MPC, PSX, XOM, CVX

> Research project only. This repository does not provide investment advice or price targets.

## Executive finding

The model finds a clear 2026 transmission chain:

**Hormuz disruption → higher refined-product scarcity → wider U.S. crack spreads → stronger refiner economics → refiner equity outperformance.**

The approximate 3-2-1 crack spread rose from an average of **$24.15/bbl in January–February** to **$65.55/bbl in July–August**, a roughly **171% increase**.

![Crack-spread regime shift](charts/crack_spread_regimes.png)

Refining-heavy equities also materially outperformed XLE and the integrated majors during the live 2026 sample.

![2026 equity performance](charts/equity_performance_2026.png)

## Current model result

| Rank | Company | Exposure score | Valuation score | Prospective score |
|---:|---|---:|---:|---:|
| 1 | **Valero Energy (VLO)** | 72.48 | 80.43 | **76.06** |
| 2 | Marathon Petroleum (MPC) | 58.00 | 71.59 | **64.12** |
| 3 | Chevron (CVX) | 55.64 | 49.47 | 52.86 |
| 4 | Phillips 66 (PSX) | 54.49 | 30.10 | 43.52 |
| 5 | Exxon Mobil (XOM) | 46.32 | 27.43 | 37.82 |

![Prospective investment scores](charts/prospective_investment_scores.png)

### Cycle-normalization test

The project does **not** assume Q2 2026 refining margins persist indefinitely. VLO, MPC and PSX are stressed toward issuer-specific mid-cycle margins.

| Refiner | Prospective score | Mid-cycle earnings retained | Soft-cycle earnings retained | Cycle-adjusted score |
|---|---:|---:|---:|---:|
| **VLO** | 76.06 | 26.61% | 12.75% | **77.66** |
| **MPC** | 64.12 | **29.81%** | **15.04%** | **74.88** |
| PSX | 43.52 | 13.24% | 1.21% | 30.46 |

![Cycle-adjusted refiner scores](charts/cycle_adjusted_refiner_scores.png)

**Interpretation:** Valero ranks first on the combined framework, while Marathon is the strongest normalization hedge and closes the gap materially when refining margins revert toward historical levels.

## Why the result is interesting

This is not a generic “higher oil prices are good for energy stocks” model. It separates several competing effects:

- U.S. refiners can benefit from scarce global refining/product supply and wider crack spreads.
- Integrated majors benefit from higher upstream prices but may also carry direct Middle East production, logistics, or asset exposure.
- A strong operating beneficiary may still be a poor prospective investment if the market has already fully rerated the stock.
- Refining businesses can look optically cheap near the top of the cycle, so mid-cycle normalization must be tested explicitly.

## Model architecture

The pipeline is:

```text
Primary-source evidence
        ↓
Hormuz-flow shock benchmark
        ↓
Operational exposure factors
        ↓
Live market confirmation
        ↓
Valuation and balance-sheet layer
        ↓
Scenario scoring
        ↓
10,000-run Monte Carlo sensitivity
        ↓
Refining-cycle normalization
        ↓
Prospective / cycle-adjusted ranking
```

### Operational factors

- Peer operating uplift
- Refining-shock capture
- Middle East resilience
- Upstream price hedge
- Scale resilience
- Live equity-market confirmation

### Valuation factors

- Forward P/E
- EV/EBITDA
- Free-cash-flow yield
- Dividend yield
- Net debt / EBITDA
- Multiple rerating versus FY2025

### Scenarios

1. **Normalization**
2. **Persistent disruption**
3. **Severe disruption**

The persistent-disruption scenario is also subjected to a **10,000-run Monte Carlo sensitivity test**.

## Live market evidence

The validated 2026 live run produced the following period returns:

| Ticker | Return |
|---|---:|
| MPC | 125.94% |
| VLO | 116.31% |
| PSX | 90.79% |
| XLE | 39.20% |
| CVX | 33.10% |
| XOM | 30.33% |

Following the initial major Hormuz disruption event, 20-trading-day returns were:

| Ticker | 20-day return |
|---|---:|
| MPC | 16.84% |
| VLO | 16.45% |
| PSX | 15.38% |
| XOM | 11.19% |
| CVX | 11.13% |
| XLE | 9.34% |

The event-window results are descriptive rather than causal proof, but they provide useful market confirmation alongside the operating data.

## Data and source discipline

The project uses primary-source or market-observable inputs wherever practical.

### Primary sources

- U.S. Energy Information Administration — Hormuz flows and energy-market disruption
- SEC filings — VLO, MPC, PSX, XOM and CVX operating/financial disclosures
- Issuer historical filings — refining-margin normalization anchors

See [`research/source_register.csv`](research/source_register.csv) for the detailed source register.

### Market data

When internet access is available, `yfinance` is used to retrieve:

- VLO, MPC, PSX, XOM, CVX
- XLE
- Brent (`BZ=F`)
- WTI (`CL=F`)
- RBOB gasoline (`RB=F`)
- distillate / heating oil (`HO=F`)

## Project structure

```text
.
├── charts/
│   ├── crack_spread_regimes.png
│   ├── equity_performance_2026.png
│   ├── prospective_investment_scores.png
│   └── cycle_adjusted_refiner_scores.png
├── data/
│   ├── company_metrics.csv
│   ├── cycle_normalization_inputs.csv
│   ├── event_dates.csv
│   ├── hormuz_flows_eia.csv
│   └── valuation_current.csv
├── outputs/
│   ├── crack_321_proxy.csv
│   ├── crack_regime_summary.csv
│   ├── cycle_adjusted_refiner_ranking.csv
│   ├── cycle_normalization_scenarios.csv
│   ├── event_window_returns.csv
│   ├── market_performance.csv
│   ├── monte_carlo_persistent.csv
│   └── prospective_investment_ranking.csv
├── research/
│   ├── article_research_outline.md
│   ├── crack_spread_methodology.md
│   ├── cycle_normalization_methodology.md
│   ├── findings_snapshot.md
│   ├── source_register.csv
│   ├── validation_notes.md
│   └── valuation_source_register.csv
├── src/
│   └── model modules
├── tests/
│   └── test_smoke.py
├── main.py
└── requirements.txt
```

## Run locally

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

If the market-data pull succeeds, the model refreshes the market-confirmation, event-window, and crack-spread outputs.

## Run validation checks

```powershell
python -m unittest discover -s tests -v
```

## Key limitations

- This is a comparative research model, not an expected-return estimator.
- Forward valuation metrics can change quickly and should be refreshed before publication.
- Crack spreads are market proxies and differ from issuer-specific realized margins.
- Cycle-normalization uses transparent segment-level sensitivity bridges, not consolidated EPS forecasts.
- Event-window returns do not establish causality.
- Some geographic exposure and business-model factors remain explicit analyst parameters because issuer disclosures are not standardized across the universe.
- Refining margins can revert sharply; apparent low valuation multiples can therefore be cyclical rather than structural bargains.

## Research conclusion

The validated live run supports **Valero Energy as the strongest overall prospective exposure in the five-company universe**, based on the combination of operational exposure, current valuation, cash-flow characteristics, balance-sheet resilience and market confirmation.

**Marathon Petroleum is the strongest competing thesis.** It delivered the highest 2026 equity return in the sample and retains slightly more modeled segment earnings than VLO when margins normalize.

Phillips 66 participated strongly in the initial trade, but the cycle-normalization analysis suggests materially greater sensitivity to a reversal in elevated refining economics.

The central risk to the VLO thesis is therefore not whether the Hormuz disruption improved U.S. refining economics — the model finds substantial evidence that it did — but whether the market is now capitalizing an unusually favorable refining regime for too long.

## Related research note

See [`research/article_research_outline.md`](research/article_research_outline.md) for a publication-oriented research structure. Any submission should follow the target publisher's current authorship and AI-use rules.
