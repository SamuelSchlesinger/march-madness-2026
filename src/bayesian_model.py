"""
Bayesian hierarchical model for team strength estimation.

Estimates latent offensive and defensive strength for every team
with full uncertainty quantification via PyMC/NUTS sampling.

Model:
    sigma_off ~ HalfStudentT(3, 2.5)
    sigma_def ~ HalfStudentT(3, 2.5)
    home_adv ~ Normal(3.5, 1.5)
    intercept ~ Normal(70, 5)
    sigma_game ~ HalfNormal(10)

    offense[team] ~ Normal(0, sigma_off)   (sum-to-zero for identifiability)
    defense[team] ~ Normal(0, sigma_def)   (sum-to-zero for identifiability)

    mu_home = intercept + home_adv + offense[home] + defense[away]
    mu_away = intercept + offense[away] + defense[home]

    score_home ~ Normal(mu_home, sigma_game)
    score_away ~ Normal(mu_away, sigma_game)
"""

import numpy as np
import pandas as pd
import pymc as pm
import pytensor.tensor as pt
from scipy.stats import norm
from data_loader import build_game_stats, PRE_TOURNEY_DAY


def prepare_model_data(reg_detail, season, max_day=None):
    """
    Prepare game data for the Bayesian model for a single season.

    Returns:
        game_df: DataFrame with home_id, away_id, home_score, away_score, is_neutral
        team_ids: sorted array of unique team IDs
        team_to_idx: dict mapping TeamID -> index
    """
    if max_day is None:
        max_day = PRE_TOURNEY_DAY

    season_games = reg_detail[
        (reg_detail["Season"] == season) & (reg_detail["DayNum"] <= max_day)
    ].copy()

    # Get all teams
    all_teams = sorted(
        set(season_games["WTeamID"].unique()) | set(season_games["LTeamID"].unique())
    )
    team_to_idx = {t: i for i, t in enumerate(all_teams)}

    # Build game data
    # WLoc: H = winner was home, A = winner was away, N = neutral
    rows = []
    for _, g in season_games.iterrows():
        w_loc = g.get("WLoc", "N")

        # Normalize overtime scores to 40-minute equivalents
        num_ot = g.get("NumOT", 0)
        ot_factor = 40 / (40 + 5 * num_ot)

        if w_loc == "H":
            # Winner was home
            rows.append({
                "home_idx": team_to_idx[g["WTeamID"]],
                "away_idx": team_to_idx[g["LTeamID"]],
                "home_score": g["WScore"] * ot_factor,
                "away_score": g["LScore"] * ot_factor,
                "is_neutral": 0,
            })
        elif w_loc == "A":
            # Winner was away, so loser was home
            rows.append({
                "home_idx": team_to_idx[g["LTeamID"]],
                "away_idx": team_to_idx[g["WTeamID"]],
                "home_score": g["LScore"] * ot_factor,
                "away_score": g["WScore"] * ot_factor,
                "is_neutral": 0,
            })
        else:
            # Neutral site — pick arbitrary "home" (winner) but flag neutral
            rows.append({
                "home_idx": team_to_idx[g["WTeamID"]],
                "away_idx": team_to_idx[g["LTeamID"]],
                "home_score": g["WScore"] * ot_factor,
                "away_score": g["LScore"] * ot_factor,
                "is_neutral": 1,
            })

    game_df = pd.DataFrame(rows)
    return game_df, np.array(all_teams), team_to_idx


def build_pymc_model(game_df, n_teams):
    """
    Build the PyMC hierarchical model.

    Uses ZeroSumNormal for offense/defense parameters to ensure identifiability.
    """
    home_idx = game_df["home_idx"].values.astype(int)
    away_idx = game_df["away_idx"].values.astype(int)
    home_score = game_df["home_score"].values.astype(float)
    away_score = game_df["away_score"].values.astype(float)
    is_neutral = game_df["is_neutral"].values.astype(float)

    with pm.Model() as model:
        # Hyperpriors
        sigma_off = pm.HalfStudentT("sigma_off", nu=3, sigma=2.5)
        sigma_def = pm.HalfStudentT("sigma_def", nu=3, sigma=2.5)

        # Game-level noise
        sigma_game = pm.HalfNormal("sigma_game", sigma=10)

        # Global parameters
        intercept = pm.Normal("intercept", mu=70, sigma=5)
        home_adv = pm.Normal("home_adv", mu=3.5, sigma=1.5)

        # Team-level parameters with sum-to-zero constraint
        # Scaling by sigma must be INSIDE Deterministic so trace stores scaled values
        offense_raw = pm.Normal("offense_raw", mu=0, sigma=1, shape=n_teams - 1)
        offense = pm.Deterministic(
            "offense",
            pt.concatenate([offense_raw, -offense_raw.sum(keepdims=True)]) * sigma_off
        )

        defense_raw = pm.Normal("defense_raw", mu=0, sigma=1, shape=n_teams - 1)
        defense = pm.Deterministic(
            "defense",
            pt.concatenate([defense_raw, -defense_raw.sum(keepdims=True)]) * sigma_def
        )

        # Expected scores
        # Home advantage only applies for non-neutral games
        ha = home_adv * (1 - is_neutral)

        mu_home = intercept + ha + offense[home_idx] + defense[away_idx]
        mu_away = intercept + offense[away_idx] + defense[home_idx]

        # Likelihood
        pm.Normal("home_score_obs", mu=mu_home, sigma=sigma_game, observed=home_score)
        pm.Normal("away_score_obs", mu=mu_away, sigma=sigma_game, observed=away_score)

    return model


def fit_season(reg_detail, season, max_day=None,
               n_samples=1500, n_tune=1000, n_chains=4, target_accept=0.9):
    """
    Fit the Bayesian model for a single season.

    Returns:
        trace: PyMC InferenceData object with posterior samples
        team_ids: array of team IDs (index matches offense/defense arrays)
        team_to_idx: mapping from TeamID to index
    """
    print(f"  Preparing data for season {season}...")
    game_df, team_ids, team_to_idx = prepare_model_data(reg_detail, season, max_day)
    n_teams = len(team_ids)
    n_games = len(game_df)
    print(f"    {n_teams} teams, {n_games} games")

    print(f"  Building model...")
    model = build_pymc_model(game_df, n_teams)

    print(f"  Sampling ({n_chains} chains, {n_samples} samples, {n_tune} tune)...")
    with model:
        trace = pm.sample(
            draws=n_samples,
            tune=n_tune,
            chains=n_chains,
            target_accept=target_accept,
            random_seed=42,
            progressbar=True,
        )

    return trace, team_ids, team_to_idx


def compute_win_probability(trace, team_to_idx, team_a_id, team_b_id,
                            neutral=True, n_posterior_samples=None):
    """
    Compute win probability for team A vs team B using posterior samples.

    Draws from the posterior distribution of offense/defense parameters
    and simulates game outcomes to estimate P(A wins).

    Returns:
        win_prob: float, estimated P(team_a wins)
        prob_std: float, standard deviation of the estimate
    """
    if team_a_id not in team_to_idx or team_b_id not in team_to_idx:
        return 0.5, 0.25  # uninformative if team not in model

    a_idx = team_to_idx[team_a_id]
    b_idx = team_to_idx[team_b_id]

    # Extract posterior samples
    offense = trace.posterior["offense"].values  # shape: (chains, draws, n_teams)
    defense = trace.posterior["defense"].values
    intercept = trace.posterior["intercept"].values  # shape: (chains, draws)
    sigma_game = trace.posterior["sigma_game"].values
    home_adv = trace.posterior["home_adv"].values

    # Flatten chains
    n_chains, n_draws = offense.shape[:2]
    offense = offense.reshape(-1, offense.shape[-1])
    defense = defense.reshape(-1, defense.shape[-1])
    intercept = intercept.reshape(-1)
    sigma_game = sigma_game.reshape(-1)
    home_adv = home_adv.reshape(-1)

    if n_posterior_samples is not None and n_posterior_samples < len(intercept):
        idx = np.random.choice(len(intercept), n_posterior_samples, replace=False)
        offense = offense[idx]
        defense = defense[idx]
        intercept = intercept[idx]
        sigma_game = sigma_game[idx]
        home_adv = home_adv[idx]

    # Expected scores on neutral court
    ha = 0 if neutral else home_adv
    mu_a = intercept + ha + offense[:, a_idx] + defense[:, b_idx]
    mu_b = intercept + offense[:, b_idx] + defense[:, a_idx]

    # Score differential is Normal(mu_a - mu_b, sqrt(2) * sigma_game)
    score_diff = mu_a - mu_b
    combined_sigma = np.sqrt(2) * sigma_game

    # P(A wins) = P(score_diff + noise > 0) = Phi(score_diff / combined_sigma)
    win_probs = norm.cdf(score_diff / combined_sigma)

    return float(np.mean(win_probs)), float(np.std(win_probs))


def get_team_ratings(trace, team_ids):
    """
    Extract posterior mean and std for each team's offensive and defensive rating.

    Returns DataFrame with TeamID, Off_mean, Off_std, Def_mean, Def_std, EM_mean, EM_std.
    """
    offense = trace.posterior["offense"].values.reshape(-1, len(team_ids))
    defense = trace.posterior["defense"].values.reshape(-1, len(team_ids))

    off_mean = offense.mean(axis=0)
    off_std = offense.std(axis=0)
    def_mean = defense.mean(axis=0)
    def_std = defense.std(axis=0)
    em = offense - defense  # compute EM directly from posterior samples
    em_mean = em.mean(axis=0)
    em_std = em.std(axis=0)

    return pd.DataFrame({
        "TeamID": team_ids,
        "BayesOff_mean": off_mean,
        "BayesOff_std": off_std,
        "BayesDef_mean": def_mean,
        "BayesDef_std": def_std,
        "BayesEM_mean": em_mean,
        "BayesEM_std": em_std,
    })


if __name__ == "__main__":
    from data_loader import load_raw_data

    print("Loading data...")
    data = load_raw_data()

    # Fit 2025 season as a test
    trace, team_ids, team_to_idx = fit_season(data["reg_detail"], 2025)

    # Show team ratings
    ratings = get_team_ratings(trace, team_ids)
    ratings_sorted = ratings.sort_values("BayesEM_mean", ascending=False)
    print("\nTop 20 teams by Bayesian efficiency margin (2025):")
    teams = data["teams"].set_index("TeamID")["TeamName"]
    ratings_sorted["Name"] = ratings_sorted["TeamID"].map(teams)
    print(ratings_sorted[["Name", "BayesEM_mean", "BayesEM_std", "BayesOff_mean", "BayesDef_mean"]].head(20).to_string())
