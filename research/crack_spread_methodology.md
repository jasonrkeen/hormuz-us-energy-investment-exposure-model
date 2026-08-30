# Crack Spread Methodology

v0.3 uses two possible paths:

1. **Live market proxy** when available:
   - RBOB gasoline futures (`RB=F`)
   - ULSD/heating-oil futures (`HO=F`)
   - WTI crude (`CL=F`)
   - Approximate 3-2-1 crack:
     `((2 * gasoline_usd_per_bbl) + diesel_usd_per_bbl - (3 * crude_usd_per_bbl)) / 3`
   - Futures quoted in $/gallon are converted to $/barrel using 42 gallons/barrel.

2. **Company-filed realized refining margin** as a primary-source operating confirmation.

The futures proxy is a market indicator, not the same as any issuer's realized margin.
