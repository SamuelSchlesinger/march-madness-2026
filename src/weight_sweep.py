"""
Quick sweep of Bayesian ensemble weights using saved backtest data.
Re-uses the per-game probabilities from the backtest to avoid re-fitting.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from backtest import backtest


def sweep_weights(df):
    """Test different Bayesian weight configurations."""
    print(f"\n{'='*70}")
    print(f"  ENSEMBLE WEIGHT SWEEP")
    print(f"{'='*70}")
    print(f"\n{'BayesWeight':>12} {'Brier':>8} {'LogLoss':>8} {'Accuracy':>8} {'ECE':>8}")
    print("-" * 55)

    best_brier = 1.0
    best_weight = 0.0

    for bw in [0.0, 0.10, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.0]:
        # Recompute ensemble with this weight
        # Use uncertainty-scaled weight like the production code
        # But since we don't have per-game bayes_std saved, use simple linear blend
        blended = (1 - bw) * df["FeatProb"] + bw * df["BayesProb"]
        blended = np.clip(blended, 0.05, 0.95)

        brier = brier_score_loss(df["Actual"], blended)
        ll = log_loss(df["Actual"], blended)
        acc = ((blended > 0.5) == df["Actual"]).mean()

        # ECE
        bins = np.linspace(0, 1, 11)
        bin_idx = np.digitize(blended, bins) - 1
        ece = 0
        for b in range(10):
            mask = bin_idx == b
            if mask.sum() > 0:
                ece += mask.sum() / len(df) * abs(blended[mask].mean() - df["Actual"][mask].mean())

        marker = " <-- best" if brier < best_brier else ""
        print(f"{bw:>12.2f} {brier:>8.4f} {ll:>8.4f} {acc:>8.1%} {ece:>8.4f}{marker}")

        if brier < best_brier:
            best_brier = brier
            best_weight = bw

    print(f"\nOptimal Bayesian weight: {best_weight:.2f} (Brier: {best_brier:.4f})")
    return best_weight


if __name__ == "__main__":
    df = backtest()
    sweep_weights(df)
