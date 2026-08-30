from __future__ import annotations
import numpy as np
import pandas as pd

def simulate_scores(factors: pd.DataFrame, scenario_weights: dict, n=10000, seed=20260829):
    """
    Sensitivity simulation around factor inputs and scenario weights.
    This is not a stock-price forecast. It estimates rank robustness.
    """
    rng = np.random.default_rng(seed)
    tickers = factors["ticker"].tolist()
    factor_names = list(scenario_weights.keys())
    base_w = np.array([scenario_weights[k] for k in factor_names], dtype=float)
    base_w = base_w/base_w.sum()

    sims = []
    wins = {t:0 for t in tickers}
    score_store = {t:[] for t in tickers}

    mat = factors[factor_names].to_numpy(dtype=float)

    for _ in range(n):
        # perturb weights using lognormal noise, then renormalize
        w = base_w * rng.lognormal(mean=0.0, sigma=0.20, size=len(base_w))
        w = w/w.sum()
        # perturb factor values with 5-point standard deviation and clamp.
        f = np.clip(mat + rng.normal(0,5,size=mat.shape), 0,100)
        scores = f @ w
        winner = tickers[int(np.argmax(scores))]
        wins[winner] += 1
        for t,s in zip(tickers,scores):
            score_store[t].append(float(s))

    rows = []
    for t in tickers:
        arr = np.array(score_store[t])
        rows.append({
            "ticker": t,
            "win_probability_pct": wins[t]/n*100,
            "score_p05": np.percentile(arr,5),
            "score_p50": np.percentile(arr,50),
            "score_p95": np.percentile(arr,95),
        })
    return pd.DataFrame(rows).sort_values("win_probability_pct", ascending=False)
