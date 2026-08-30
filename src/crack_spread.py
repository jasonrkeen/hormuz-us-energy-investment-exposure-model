from __future__ import annotations
import pandas as pd

def approximate_321_crack(px: pd.DataFrame):
    needed = {"RB=F","HO=F","CL=F"}
    if not needed.issubset(px.columns):
        return pd.DataFrame()
    d = px[list(needed)].dropna().copy()
    # RB and HO are approximately dollars per gallon; convert to $/bbl.
    gas = d["RB=F"] * 42.0
    diesel = d["HO=F"] * 42.0
    crude = d["CL=F"]
    d["crack_321_usd_per_bbl"] = ((2*gas) + diesel - (3*crude)) / 3.0
    return d[["crack_321_usd_per_bbl"]]
