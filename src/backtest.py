"""
Historical backtest of the full prediction pipeline.

For each tournament year (2015-2025, excluding 2020), trains on prior years
and evaluates predictions against actual outcomes. Tests all model variants:
feature-only ensemble, Bayesian-only, and full ensemble.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, log_loss
from data_loader import (
    load_raw_data, build_game_stats, compute_team_season_stats,
    get_massey_ordinals, build_seed_features, build_matchup_features,
    MASSEY_KEY_SYSTEMS,
)
from pipeline import (
    build_training_data, train_final_models,
    _precompute_season, _build_matchup_row, _impute_features,
    PROB_CLIP_LOW, PROB_CLIP_HIGH, ENSEMBLE_WEIGHTS, XGB_PARAMS,
)
from bayesian_model import fit_season, compute_win_probability


def backtest(test_seasons=None, fit_bayes=True):
    print("Loading data...")
    data = load_raw_data()
    reg_game_stats = build_game_stats(data["reg_detail"])
    tourney_compact = data["tourney_compact"]
    seeds_df = build_seed_features(data)

    if test_seasons is None:
        test_seasons = [s for s in range(2015, 2026) if s != 2020]

    all_results = []

    for test_season in test_seasons:
        print(f"\n{'='*60}")
        print(f"  BACKTESTING SEASON {test_season}")
        print(f"{'='*60}")

        # --- Train feature-based models on prior seasons ---
        available = sorted(
            set(data["reg_detail"]["Season"].unique())
            & set(tourney_compact["Season"].unique())
        )
        train_seasons = [s for s in available if s < test_season]
        features_df, labels, meta_df = build_training_data(data, seasons=train_seasons)
        models = train_final_models(features_df, labels)

        # --- Fit Bayesian model for test season ---
        bayes_trace = None
        bayes_team_to_idx = None
        if fit_bayes:
            try:
                print(f"  Fitting Bayesian model for {test_season}...")
                bayes_trace, _, bayes_team_to_idx = fit_season(
                    data["reg_detail"], test_season,
                    n_samples=2000, n_tune=1000, n_chains=4,
                )
            except Exception as e:
                print(f"  Bayesian model failed: {e}")

        # --- Precompute season data ---
        season_data = _precompute_season(data, reg_game_stats, test_season)
        feature_cols = models["feature_columns"]

        # --- Evaluate on actual tournament games ---
        season_tourney = tourney_compact[tourney_compact["Season"] == test_season]

        for _, game in season_tourney.iterrows():
            w_id = game["WTeamID"]
            l_id = game["LTeamID"]

            # Convention: TeamA = lower ID
            if w_id < l_id:
                team_a, team_b = w_id, l_id
                actual = 1  # team A won
            else:
                team_a, team_b = l_id, w_id
                actual = 0

            # --- Feature-based prediction ---
            features, has_data = _build_matchup_row(team_a, team_b, season_data)
            if not has_data:
                feat_prob = 0.5
            else:
                feat_df = pd.DataFrame([features])
                for col in feature_cols:
                    if col not in feat_df.columns:
                        feat_df[col] = np.nan
                feat_df = feat_df[feature_cols]
                feat_df = _impute_features(feat_df, feature_cols)

                lr_p = models["lr"].predict_proba(
                    models["scaler"].transform(feat_df)
                )[0, 1]
                cal_xgb_p = models["cal_xgb"].predict_proba(feat_df)[0, 1]
                feat_prob = (
                    ENSEMBLE_WEIGHTS["lr"] * lr_p
                    + ENSEMBLE_WEIGHTS["cal_xgb"] * cal_xgb_p
                )

            # --- Bayesian prediction ---
            bayes_prob = 0.5
            if bayes_trace is not None and bayes_team_to_idx is not None:
                bp, bs = compute_win_probability(
                    bayes_trace, bayes_team_to_idx, team_a, team_b,
                    n_posterior_samples=500,
                )
                bayes_prob = bp

            # --- Full ensemble ---
            if bayes_trace is not None:
                confidence = 1.0 - np.clip(bs / 0.25, 0, 0.8)
                bw = 0.25 * confidence
                full_prob = (1 - bw) * feat_prob + bw * bayes_prob
            else:
                full_prob = feat_prob

            # --- Seed baseline ---
            season_seeds = seeds_df[seeds_df["Season"] == test_season].set_index("TeamID")
            a_seed = season_seeds.loc[team_a, "SeedNum"] if team_a in season_seeds.index else 8
            b_seed = season_seeds.loc[team_b, "SeedNum"] if team_b in season_seeds.index else 8
            seed_diff = b_seed - a_seed  # positive = A is better seed
            seed_prob = 1 / (1 + 10 ** (-seed_diff * 0.15))

            all_results.append({
                "Season": test_season,
                "TeamA": team_a,
                "TeamB": team_b,
                "Actual": actual,
                "SeedProb": np.clip(seed_prob, PROB_CLIP_LOW, PROB_CLIP_HIGH),
                "FeatProb": np.clip(feat_prob, PROB_CLIP_LOW, PROB_CLIP_HIGH),
                "BayesProb": np.clip(bayes_prob, PROB_CLIP_LOW, PROB_CLIP_HIGH),
                "FullProb": np.clip(full_prob, PROB_CLIP_LOW, PROB_CLIP_HIGH),
            })

    df = pd.DataFrame(all_results)

    # --- Compute metrics ---
    print(f"\n\n{'='*70}")
    print(f"  BACKTEST RESULTS ({min(test_seasons)}-{max(test_seasons)})")
    print(f"{'='*70}")

    models_to_eval = {
        "Seed Baseline": "SeedProb",
        "Feature Ensemble (LR+XGB)": "FeatProb",
        "Bayesian Only": "BayesProb",
        "Full Ensemble": "FullProb",
    }

    # Per-season results
    print(f"\nPer-season Brier scores:")
    print(f"{'Season':<8}", end="")
    for name in models_to_eval:
        print(f"  {name[:18]:<20}", end="")
    print(f"  {'Games':<6}")
    print("-" * 100)

    for season in test_seasons:
        sdf = df[df["Season"] == season]
        if len(sdf) == 0:
            continue
        print(f"{season:<8}", end="")
        for name, col in models_to_eval.items():
            brier = brier_score_loss(sdf["Actual"], sdf[col])
            print(f"  {brier:<20.4f}", end="")
        print(f"  {len(sdf):<6}")

    # Aggregate metrics
    print(f"\n{'='*70}")
    print(f"  AGGREGATE METRICS ({len(df)} games)")
    print(f"{'='*70}")
    print(f"\n{'Model':<30} {'Brier':>8} {'LogLoss':>8} {'Accuracy':>8} {'ECE':>8}")
    print("-" * 70)

    for name, col in models_to_eval.items():
        brier = brier_score_loss(df["Actual"], df[col])
        ll = log_loss(df["Actual"], df[col])
        acc = ((df[col] > 0.5) == df["Actual"]).mean()

        # Expected Calibration Error (10 bins)
        bins = np.linspace(0, 1, 11)
        bin_indices = np.digitize(df[col], bins) - 1
        ece = 0
        for b in range(10):
            mask = bin_indices == b
            if mask.sum() > 0:
                avg_pred = df[col][mask].mean()
                avg_actual = df["Actual"][mask].mean()
                ece += mask.sum() / len(df) * abs(avg_pred - avg_actual)

        print(f"{name:<30} {brier:>8.4f} {ll:>8.4f} {acc:>8.1%} {ece:>8.4f}")

    # Calibration table
    print(f"\n{'='*70}")
    print(f"  CALIBRATION TABLE (Full Ensemble)")
    print(f"{'='*70}")
    print(f"\n{'Predicted':>12} {'Actual':>8} {'Count':>8} {'Error':>8}")
    print("-" * 45)
    bins = [(0.0, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
            (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1.0)]
    for lo, hi in bins:
        mask = (df["FullProb"] >= lo) & (df["FullProb"] < hi)
        if mask.sum() > 0:
            avg_pred = df["FullProb"][mask].mean()
            avg_actual = df["Actual"][mask].mean()
            print(f"{lo:.1f}-{hi:.1f}      {avg_actual:>8.3f} {mask.sum():>8} {avg_pred - avg_actual:>+8.3f}")

    return df


if __name__ == "__main__":
    df = backtest()
