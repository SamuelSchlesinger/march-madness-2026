"""
Main pipeline for March Madness prediction.

Builds training data from historical tournaments, trains models,
evaluates via temporal cross-validation, and generates predictions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

from data_loader import (
    load_raw_data,
    build_game_stats,
    compute_team_season_stats,
    get_massey_ordinals,
    build_seed_features,
    build_matchup_features,
    parse_seed,
    MASSEY_KEY_SYSTEMS,
)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Probability clipping bounds — conservative to avoid catastrophic log-loss
# from overconfident wrong predictions (UMBC over Virginia, FDU over Purdue)
PROB_CLIP_LOW = 0.05
PROB_CLIP_HIGH = 0.95

# Default median rank for missing Massey ordinal imputation
MISSING_RANK_VALUE = 175

# XGBoost hyperparameters (single source of truth)
XGB_PARAMS = dict(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    eval_metric="logloss",
)

# Ensemble weights
ENSEMBLE_WEIGHTS = {"lr": 0.5, "cal_xgb": 0.5}


def _precompute_season(data, reg_game_stats, season):
    """Precompute team stats, seeds, and Massey ordinals for a season."""
    season_gs = reg_game_stats[reg_game_stats["Season"] == season]
    team_stats = compute_team_season_stats(season_gs)
    team_stats_dict = team_stats.set_index("TeamID").to_dict("index")

    seeds_df = build_seed_features(data)
    season_seeds = seeds_df[seeds_df["Season"] == season].set_index("TeamID")

    massey = get_massey_ordinals(data, season)
    massey_dict = massey.set_index("TeamID").to_dict("index") if not massey.empty else {}

    return team_stats_dict, season_seeds, massey_dict


def _build_matchup_row(team_a, team_b, season_data):
    """Build a single matchup feature dict from precomputed season data."""
    team_stats_dict, season_seeds, massey_dict = season_data

    a_stats = team_stats_dict.get(team_a)
    b_stats = team_stats_dict.get(team_b)
    if a_stats is None or b_stats is None:
        return None, False

    a_seed = season_seeds.loc[team_a, "SeedNum"] if team_a in season_seeds.index else None
    b_seed = season_seeds.loc[team_b, "SeedNum"] if team_b in season_seeds.index else None

    a_massey = massey_dict.get(team_a, {})
    b_massey = massey_dict.get(team_b, {})

    features = build_matchup_features(
        a_stats, b_stats,
        team_a_seed=a_seed, team_b_seed=b_seed,
        a_massey=a_massey, b_massey=b_massey,
    )
    return features, True


def _impute_features(features_df, feature_columns):
    """
    Handle missing values in feature DataFrame.
    Massey rank columns get median-rank imputation; other columns get 0.
    """
    df = features_df.copy()
    for col in df.columns:
        if "_rank" in col:
            df[col] = df[col].fillna(MISSING_RANK_VALUE)
        else:
            df[col] = df[col].fillna(0)
    return df


def build_training_data(data, seasons=None):
    """
    Build the full training dataset from historical tournament games.

    For each tournament game, compute feature differences between the two teams
    using only regular season data available before the tournament started.
    """
    reg_detail = data["reg_detail"]
    tourney_compact = data["tourney_compact"]

    print("Building game-level stats from regular season data...")
    reg_game_stats = build_game_stats(reg_detail)

    if seasons is None:
        available_seasons = set(reg_detail["Season"].unique()) & set(tourney_compact["Season"].unique())
        seasons = sorted(available_seasons)

    all_features = []
    all_labels = []
    all_meta = []
    all_has_data = []

    for season in seasons:
        print(f"  Processing season {season}...")
        season_data = _precompute_season(data, reg_game_stats, season)
        season_tourney = tourney_compact[tourney_compact["Season"] == season]

        for _, game in season_tourney.iterrows():
            w_id = game["WTeamID"]
            l_id = game["LTeamID"]

            # Convention: TeamA is the lower ID (matches submission format)
            if w_id < l_id:
                team_a, team_b = w_id, l_id
                label = 1
            else:
                team_a, team_b = l_id, w_id
                label = 0

            features, has_data = _build_matchup_row(team_a, team_b, season_data)
            if not has_data:
                continue

            all_features.append(features)
            all_labels.append(label)
            all_meta.append({"Season": season, "TeamA": team_a, "TeamB": team_b})

    features_df = pd.DataFrame(all_features)
    labels = pd.Series(all_labels, name="Win")
    meta_df = pd.DataFrame(all_meta)

    print(f"Built {len(features_df)} training examples across {len(seasons)} seasons")
    return features_df, labels, meta_df


def temporal_cv(features_df, labels, meta_df, test_seasons=None):
    """
    Expanding-window temporal cross-validation.
    Train on all prior seasons, evaluate on each test season.
    """
    if test_seasons is None:
        all_seasons = sorted(meta_df["Season"].unique())
        test_seasons = [s for s in all_seasons if s >= 2015 and s != 2020]

    results = []
    feature_cols = list(features_df.columns)

    for test_season in test_seasons:
        train_mask = meta_df["Season"] < test_season
        test_mask = meta_df["Season"] == test_season

        if train_mask.sum() < 50 or test_mask.sum() == 0:
            continue

        X_train = _impute_features(features_df[train_mask], feature_cols)
        y_train = labels[train_mask]
        X_test = _impute_features(features_df[test_mask], feature_cols)
        y_test = labels[test_mask]

        # --- Logistic Regression ---
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        lr.fit(X_train_scaled, y_train)
        lr_probs = lr.predict_proba(X_test_scaled)[:, 1]

        # --- XGBoost ---
        xgb_model = xgb.XGBClassifier(**XGB_PARAMS)
        xgb_model.fit(X_train, y_train)
        xgb_probs = xgb_model.predict_proba(X_test)[:, 1]

        # --- Calibrated XGBoost (Platt scaling — sigmoid, safer on small samples) ---
        cal_xgb = CalibratedClassifierCV(
            xgb.XGBClassifier(**XGB_PARAMS), cv=3, method="sigmoid"
        )
        cal_xgb.fit(X_train, y_train)
        cal_xgb_probs = cal_xgb.predict_proba(X_test)[:, 1]

        # --- Ensemble ---
        ensemble_probs = (
            ENSEMBLE_WEIGHTS["lr"] * lr_probs
            + ENSEMBLE_WEIGHTS["cal_xgb"] * cal_xgb_probs
        )

        for name, probs in [
            ("LogReg", lr_probs),
            ("XGBoost", xgb_probs),
            ("CalXGB", cal_xgb_probs),
            ("Ensemble", ensemble_probs),
        ]:
            probs_clipped = np.clip(probs, PROB_CLIP_LOW, PROB_CLIP_HIGH)
            brier = brier_score_loss(y_test, probs_clipped)
            ll = log_loss(y_test, probs_clipped)
            acc = ((probs_clipped > 0.5) == y_test).mean()
            results.append({
                "Season": test_season,
                "Model": name,
                "Brier": brier,
                "LogLoss": ll,
                "Accuracy": acc,
                "N_games": len(y_test),
            })

    return pd.DataFrame(results)


def train_final_models(features_df, labels):
    """Train final models on all available data for generating predictions."""
    feature_cols = list(features_df.columns)
    X = _impute_features(features_df, feature_cols)
    y = labels

    # Logistic Regression
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    lr.fit(X_scaled, y)

    # Calibrated XGBoost (Platt scaling)
    cal_xgb = CalibratedClassifierCV(
        xgb.XGBClassifier(**XGB_PARAMS), cv=5, method="sigmoid"
    )
    cal_xgb.fit(X, y)

    # Also train a raw XGBoost for feature importance analysis
    xgb_model = xgb.XGBClassifier(**XGB_PARAMS)
    xgb_model.fit(X, y)

    return {
        "lr": lr,
        "xgb": xgb_model,
        "cal_xgb": cal_xgb,
        "scaler": scaler,
        "feature_columns": feature_cols,
    }


def generate_submission(data, models, submission_path):
    """
    Generate submission file for the Kaggle competition.
    """
    sample = pd.read_csv(
        Path(__file__).parent.parent / "data" / "raw" / "kaggle" / "SampleSubmissionStage1.csv"
    )

    reg_detail = data["reg_detail"]
    reg_game_stats = build_game_stats(reg_detail)

    # Parse submission IDs
    parts = sample["ID"].str.split("_", expand=True)
    parts.columns = ["Season", "TeamA", "TeamB"]
    parts["Season"] = parts["Season"].astype(int)
    parts["TeamA"] = parts["TeamA"].astype(int)
    parts["TeamB"] = parts["TeamB"].astype(int)

    predict_seasons = sorted(parts["Season"].unique())
    print(f"Generating predictions for seasons: {predict_seasons}")

    # Precompute per-season data
    season_cache = {}
    for season in predict_seasons:
        season_cache[season] = _precompute_season(data, reg_game_stats, season)

    # Generate features for each matchup, tracking which have data
    all_features = []
    has_data_flags = []

    for _, row in parts.iterrows():
        season = row["Season"]
        team_a = row["TeamA"]
        team_b = row["TeamB"]

        features, has_data = _build_matchup_row(team_a, team_b, season_cache[season])
        if not has_data:
            all_features.append({})
        else:
            all_features.append(features)
        has_data_flags.append(has_data)

    features_df = pd.DataFrame(all_features)
    has_data_mask = pd.Series(has_data_flags)

    # Align columns with training features
    for col in models["feature_columns"]:
        if col not in features_df.columns:
            features_df[col] = np.nan
    features_df = features_df[models["feature_columns"]]

    # Impute
    features_df = _impute_features(features_df, models["feature_columns"])

    # Predict with ensemble
    lr_probs = models["lr"].predict_proba(
        models["scaler"].transform(features_df)
    )[:, 1]
    cal_xgb_probs = models["cal_xgb"].predict_proba(features_df)[:, 1]

    ensemble_probs = (
        ENSEMBLE_WEIGHTS["lr"] * lr_probs
        + ENSEMBLE_WEIGHTS["cal_xgb"] * cal_xgb_probs
    )
    ensemble_probs = np.clip(ensemble_probs, PROB_CLIP_LOW, PROB_CLIP_HIGH)

    # Default to 0.5 for matchups where we have no team data
    ensemble_probs[~has_data_mask.values] = 0.5

    sample["Pred"] = ensemble_probs
    sample.to_csv(submission_path, index=False)
    print(f"Submission saved to {submission_path} ({len(sample)} predictions)")

    return sample


if __name__ == "__main__":
    print("=" * 60)
    print("MARCH MADNESS PREDICTION PIPELINE")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/5] Loading data...")
    data = load_raw_data()

    # Step 2: Build training data
    print("\n[2/5] Building training data...")
    features_df, labels, meta_df = build_training_data(data)
    print(f"  Features shape: {features_df.shape}")
    print(f"  Feature columns: {list(features_df.columns)}")
    print(f"  Label distribution: {labels.value_counts().to_dict()}")

    # Step 3: Temporal cross-validation
    print("\n[3/5] Running temporal cross-validation...")
    cv_results = temporal_cv(features_df, labels, meta_df)
    print("\nPer-season results:")
    print(cv_results.to_string(index=False))

    print("\nAggregated results by model:")
    agg = cv_results.groupby("Model").agg(
        Brier_mean=("Brier", "mean"),
        LogLoss_mean=("LogLoss", "mean"),
        Accuracy_mean=("Accuracy", "mean"),
    ).round(4)
    print(agg.to_string())

    # Step 4: Train final models
    print("\n[4/5] Training final models...")
    models = train_final_models(features_df, labels)

    # Show feature importances
    xgb_model = models["xgb"]
    importance = pd.Series(
        xgb_model.feature_importances_,
        index=models["feature_columns"]
    ).sort_values(ascending=False)
    print("\nTop 15 XGBoost features:")
    print(importance.head(15).to_string())

    # Step 5: Generate submission
    print("\n[5/5] Generating submission...")
    sub_path = OUTPUT_DIR / "submission_stage1.csv"
    generate_submission(data, models, sub_path)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
