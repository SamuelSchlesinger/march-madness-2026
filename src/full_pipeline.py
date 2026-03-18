"""
Full integrated pipeline for March Madness prediction.

Combines:
  Layer 1: Bayesian hierarchical model (team strength with uncertainty)
  Layer 2: XGBoost + Logistic Regression (game outcome prediction)
  Layer 3: Calibrated ensemble (diverse model families)
  Layer 4: Monte Carlo tournament simulation
  Layer 5: Bracket generation (advancement probabilities)
"""

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import (
    load_raw_data,
    build_game_stats,
    build_seed_features,
    build_matchup_features,
    parse_seed,
)
from pipeline import (
    build_training_data,
    train_final_models,
    _precompute_season,
    _build_matchup_row,
    _impute_features,
    PROB_CLIP_LOW,
    PROB_CLIP_HIGH,
    ENSEMBLE_WEIGHTS,
)
from bayesian_model import (
    fit_season,
    compute_win_probability,
    get_team_ratings,
)
from simulate import (
    simulate_tournament,
    format_results,
)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_ensemble_prob_fn(models, data, reg_game_stats, season,
                           bayes_trace=None, bayes_team_to_idx=None,
                           ensemble_bayes_weight=0.25):
    """
    Build a function that returns P(team_a wins over team_b) using
    the full ensemble of models.

    The ensemble combines:
    - Logistic Regression (feature-based)
    - Calibrated XGBoost (feature-based)
    - Bayesian model (if available, weighted by posterior certainty)
    """
    season_data = _precompute_season(data, reg_game_stats, season)
    feature_cols = models["feature_columns"]

    def prob_fn(team_a, team_b):
        features, has_data = _build_matchup_row(team_a, team_b, season_data)

        if not has_data:
            # Fall back to Bayesian model or 0.5
            if bayes_trace is not None and bayes_team_to_idx is not None:
                bp, _ = compute_win_probability(
                    bayes_trace, bayes_team_to_idx, team_a, team_b
                )
                return np.clip(bp, PROB_CLIP_LOW, PROB_CLIP_HIGH)
            return 0.5

        # Build feature vector
        feat_df = pd.DataFrame([features])
        for col in feature_cols:
            if col not in feat_df.columns:
                feat_df[col] = np.nan
        feat_df = feat_df[feature_cols]
        feat_df = _impute_features(feat_df, feature_cols)

        # Feature-based model probabilities
        lr_p = models["lr"].predict_proba(
            models["scaler"].transform(feat_df)
        )[0, 1]
        cal_xgb_p = models["cal_xgb"].predict_proba(feat_df)[0, 1]

        # Feature-based ensemble
        feat_p = (
            ENSEMBLE_WEIGHTS["lr"] * lr_p
            + ENSEMBLE_WEIGHTS["cal_xgb"] * cal_xgb_p
        )

        # Blend with Bayesian model if available
        if bayes_trace is not None and bayes_team_to_idx is not None:
            bayes_p, bayes_std = compute_win_probability(
                bayes_trace, bayes_team_to_idx, team_a, team_b,
                n_posterior_samples=500,
            )
            # Downweight Bayesian contribution when posterior is uncertain
            # bayes_std near 0 = confident, near 0.25 = very uncertain
            confidence = 1.0 - np.clip(bayes_std / 0.25, 0, 0.8)
            bw = ensemble_bayes_weight * confidence
            final_p = (1 - bw) * feat_p + bw * bayes_p
        else:
            final_p = feat_p

        return np.clip(final_p, PROB_CLIP_LOW, PROB_CLIP_HIGH)

    return prob_fn


def generate_bracket(advancement_probs, round_names, teams_df, seeds_df, season):
    """
    Format advancement probabilities with seed and team info.
    """
    results = format_results(advancement_probs, {}, round_names, teams_df)

    # Add seed info
    season_seeds = seeds_df[seeds_df["Season"] == season].copy()
    season_seeds["SeedNum"] = season_seeds["Seed"].apply(parse_seed)
    seed_map = season_seeds.set_index("TeamID")["SeedNum"].to_dict()
    seed_str_map = season_seeds.set_index("TeamID")["Seed"].to_dict()
    results["Seed"] = results["TeamID"].map(seed_map)
    results["SeedStr"] = results["TeamID"].map(seed_str_map)

    return results


def main(target_season=2026):
    print("=" * 70)
    print("FULL MARCH MADNESS PREDICTION PIPELINE")
    print("=" * 70)

    # --- Load data ---
    print("\n[1/6] Loading data...")
    data = load_raw_data()

    # --- Determine target season ---
    seeds_target = data["seeds"][data["seeds"]["Season"] == target_season]
    if len(seeds_target) == 0:
        target_season = max(data["seeds"]["Season"].unique())
        print(f"  No seeds for requested season, falling back to {target_season}")

    # --- Train feature-based models (exclude target season to prevent leakage) ---
    print(f"\n[2/6] Training feature-based models (excluding {target_season})...")
    tourney_compact = data["tourney_compact"]
    available_seasons = sorted(
        set(data["reg_detail"]["Season"].unique())
        & set(tourney_compact["Season"].unique())
    )
    train_seasons = [s for s in available_seasons if s < target_season]

    features_df, labels, meta_df = build_training_data(data, seasons=train_seasons)
    models = train_final_models(features_df, labels)
    print(f"  Trained on {len(features_df)} games from {len(train_seasons)} seasons "
          f"({min(train_seasons)}-{max(train_seasons)})")

    # --- Fit Bayesian model for target season ---
    print(f"\n[3/6] Fitting Bayesian model for {target_season}...")
    bayes_trace = None
    bayes_team_ids = None
    bayes_team_to_idx = None

    try:
        bayes_trace, bayes_team_ids, bayes_team_to_idx = fit_season(
            data["reg_detail"], target_season,
            n_samples=1500, n_tune=1000, n_chains=4,
        )

        # Check for divergences
        if hasattr(bayes_trace, "sample_stats"):
            divergences = bayes_trace.sample_stats["diverging"].values.sum()
            if divergences > 0:
                print(f"  WARNING: {divergences} divergent transitions detected. "
                      f"Results may be unreliable.")

        # Show top Bayesian ratings
        ratings = get_team_ratings(bayes_trace, bayes_team_ids)
        name_map = data["teams"].set_index("TeamID")["TeamName"]
        ratings["Name"] = ratings["TeamID"].map(name_map)
        ratings_sorted = ratings.sort_values("BayesEM_mean", ascending=False)
        print(f"\n  Top 15 teams by Bayesian efficiency margin ({target_season}):")
        print(ratings_sorted[["Name", "BayesEM_mean", "BayesEM_std"]].head(15).to_string(index=False))

    except Exception as e:
        print(f"  WARNING: Bayesian model failed ({e}). Using feature-based models only.")

    # --- Build ensemble probability function ---
    print(f"\n[4/6] Building ensemble probability function...")
    reg_game_stats = build_game_stats(data["reg_detail"])

    prob_fn = build_ensemble_prob_fn(
        models, data, reg_game_stats, target_season,
        bayes_trace=bayes_trace,
        bayes_team_to_idx=bayes_team_to_idx,
        ensemble_bayes_weight=0.50,
    )

    # --- Monte Carlo simulation ---
    print(f"\n[5/6] Running Monte Carlo tournament simulation ({target_season})...")
    adv_probs, champions, round_names = simulate_tournament(
        prob_fn, data["seeds"], target_season,
        n_sims=50000,
    )

    # --- Format and display results ---
    print(f"\n[6/6] Results for {target_season} tournament:")
    bracket = generate_bracket(
        adv_probs, round_names, data["teams"], data["seeds"], target_season
    )

    cols = ["SeedStr", "Team", "R32", "S16", "E8", "F4", "Final", "Champion"]
    available_cols = [c for c in cols if c in bracket.columns]
    print(f"\n{'='*80}")
    print(f"  ADVANCEMENT PROBABILITIES — {target_season} NCAA Tournament")
    print(f"{'='*80}")
    print(bracket[available_cols].head(30).to_string(
        index=False, float_format=lambda x: f"{x:.1%}"
    ))

    # Save results
    bracket.to_csv(OUTPUT_DIR / f"bracket_{target_season}.csv", index=False)
    print(f"\nResults saved to {OUTPUT_DIR / f'bracket_{target_season}.csv'}")

    # --- Print the bracket pick (most likely winner of each round) ---
    print(f"\n{'='*80}")
    print(f"  RECOMMENDED BRACKET PICKS")
    print(f"{'='*80}")

    # Champion
    champ_row = bracket.iloc[0]
    print(f"\n  Champion: {champ_row['Team']} ({champ_row.get('SeedStr', '?')}) — {champ_row['Champion']:.1%}")

    # Final Four
    ff_teams = bracket.nlargest(4, "F4")
    print(f"\n  Final Four:")
    for _, row in ff_teams.iterrows():
        print(f"    {row.get('SeedStr', '?')} {row['Team']} — {row['F4']:.1%}")

    # Elite Eight
    e8_teams = bracket.nlargest(8, "E8")
    print(f"\n  Elite Eight:")
    for _, row in e8_teams.iterrows():
        print(f"    {row.get('SeedStr', '?')} {row['Team']} — {row['E8']:.1%}")

    print(f"\n{'='*70}")
    print("FULL PIPELINE COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
