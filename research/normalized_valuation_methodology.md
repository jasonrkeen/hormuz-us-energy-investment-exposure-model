# Normalized Valuation Methodology — v0.5.1

Version 0.5.1 adds two valuation diagnostics without changing the v0.5 exposure, valuation-score, prospective-score, or cycle-resilience formulas.

## Q2-replacement EV/EBITDA bridge

The bridge asks what current TTM EV/EBITDA would look like if the extreme Q2 2026 segment earnings proxy were replaced by the model's mid-cycle or soft-cycle quarterly proxy.

`adjusted TTM EBITDA = current TTM EBITDA - (Q2 current segment proxy - Q2 scenario segment proxy)`

`implied EV/EBITDA = current enterprise value / adjusted TTM EBITDA`

The bridge is deliberately transparent. VLO and PSX segment proxies are not reported EBITDA measures, so the modeled change is treated as an EBITDA sensitivity while depreciation/amortization and non-refining items are held constant. This is not a consolidated forecast or price target.

## Consolidated pass-through sensitivity

A second diagnostic applies 50%, 75%, and 100% of the modeled segment earnings decline to current consolidated valuation measures:

`consolidated retention = 1 - pass_through × (1 - segment retention)`

Forward P/E and EV/EBITDA are divided by consolidated retention; FCF yield is multiplied by consolidated retention.

This is intentionally harsher than the Q2-replacement bridge and tests when MPC's superior modeled cycle retention can overcome VLO's lower starting valuation.

## Data refresh discipline

`data/normalized_valuation_fundamentals.csv` should be refreshed whenever `data/valuation_current.csv` is refreshed. The files should share the same valuation date where practical.
