"""
Data loading and preprocessing for March Madness prediction.

Loads Kaggle competition data, computes team-season statistics
with opponent-quality adjustments, and builds matchup feature vectors.
"""

import pandas as pd
import numpy as np
from pathlib import Path

KAGGLE_DIR = Path(__file__).parent.parent / "data" / "raw" / "kaggle"

# Pre-tournament day cutoff. Conference tournaments end around day 132;
# NCAA tournament begins around day 134-136. Use 132 to avoid leakage.
PRE_TOURNEY_DAY = 132

# Key Massey ordinal systems (historically most predictive)
MASSEY_KEY_SYSTEMS = ["POM", "SAG", "MOR", "DOL", "COL", "RTH", "WOL", "AP"]

# Required files that the pipeline cannot function without
REQUIRED_FILES = {"teams", "seeds", "reg_detail", "tourney_compact", "ordinals"}


def load_raw_data(data_dir=None):
    """Load all key Kaggle CSV files into a dictionary of DataFrames."""
    kaggle_dir = Path(data_dir) if data_dir else KAGGLE_DIR

    files = {
        "teams": "MTeams.csv",
        "seasons": "MSeasons.csv",
        "seeds": "MNCAATourneySeeds.csv",
        "reg_detail": "MRegularSeasonDetailedResults.csv",
        "tourney_detail": "MNCAATourneyDetailedResults.csv",
        "tourney_compact": "MNCAATourneyCompactResults.csv",
        "ordinals": "MMasseyOrdinals.csv",
        "conferences": "MTeamConferences.csv",
        "coaches": "MTeamCoaches.csv",
        "game_cities": "MGameCities.csv",
        "cities": "Cities.csv",
        "team_spellings": "MTeamSpellings.csv",
        "tourney_slots": "MNCAATourneySlots.csv",
    }
    data = {}
    missing = []
    for key, filename in files.items():
        path = kaggle_dir / filename
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            missing.append(key)
            if key in REQUIRED_FILES:
                raise FileNotFoundError(
                    f"Required file {filename} not found in {kaggle_dir}"
                )
            print(f"Warning: optional file {filename} not found")
    return data


def parse_seed(seed_str):
    """Parse seed string like 'W01' or 'X16a' into integer seed number."""
    return int(seed_str[1:3])


def build_game_stats(df):
    """
    Transform winner/loser game rows into team-perspective rows with stats.
    Vectorized implementation for performance on 100K+ rows.

    Each game produces two rows: one from each team's perspective.
    """
    # Estimate possessions for each team
    w_poss = df["WFGA"] - df["WOR"] + df["WTO"] + 0.475 * df["WFTA"]
    l_poss = df["LFGA"] - df["LOR"] + df["LTO"] + 0.475 * df["LFTA"]
    poss = ((w_poss + l_poss) / 2).clip(lower=1)

    # Overtime normalization factor
    num_ot = df.get("NumOT", pd.Series(0, index=df.index))
    minutes = 40 + 5 * num_ot
    ot_factor = 40 / minutes

    # Per-100-possession efficiency (not OT-normalized; ratio cancels)
    w_off_eff = df["WScore"] / poss * 100
    l_off_eff = df["LScore"] / poss * 100

    # Four Factors — all ratio-based, OT-invariant
    w_efg = (df["WFGM"] + 0.5 * df["WFGM3"]) / df["WFGA"].clip(lower=1)
    l_efg = (df["LFGM"] + 0.5 * df["LFGM3"]) / df["LFGA"].clip(lower=1)

    w_tov_denom = (df["WFGA"] + 0.475 * df["WFTA"] + df["WTO"]).clip(lower=1)
    l_tov_denom = (df["LFGA"] + 0.475 * df["LFTA"] + df["LTO"]).clip(lower=1)
    w_tov = df["WTO"] / w_tov_denom
    l_tov = df["LTO"] / l_tov_denom

    w_orb = df["WOR"] / (df["WOR"] + df["LDR"]).clip(lower=1)
    l_orb = df["LOR"] / (df["LOR"] + df["WDR"]).clip(lower=1)

    w_ftr = df["WFTA"] / df["WFGA"].clip(lower=1)
    l_ftr = df["LFTA"] / df["LFGA"].clip(lower=1)

    # Location mapping for loser perspective
    loc_map = {"H": "A", "A": "H", "N": "N"}
    w_loc = df.get("WLoc", pd.Series("N", index=df.index))

    # Build winner-perspective rows
    winners = pd.DataFrame({
        "Season": df["Season"],
        "DayNum": df["DayNum"],
        "TeamID": df["WTeamID"],
        "OppID": df["LTeamID"],
        "Score": df["WScore"] * ot_factor,
        "OppScore": df["LScore"] * ot_factor,
        "Win": 1,
        "Loc": w_loc,
        "Poss": poss * ot_factor,
        "OffEff": w_off_eff,
        "DefEff": l_off_eff,
        "eFGPct": w_efg,
        "TOVPct": w_tov,
        "ORBPct": w_orb,
        "FTRate": w_ftr,
        "OppeFGPct": l_efg,
        "OppTOVPct": l_tov,
        "OppORBPct": l_orb,
        "OppFTRate": l_ftr,
    })

    # Build loser-perspective rows
    losers = pd.DataFrame({
        "Season": df["Season"],
        "DayNum": df["DayNum"],
        "TeamID": df["LTeamID"],
        "OppID": df["WTeamID"],
        "Score": df["LScore"] * ot_factor,
        "OppScore": df["WScore"] * ot_factor,
        "Win": 0,
        "Loc": w_loc.map(loc_map).fillna("N"),
        "Poss": poss * ot_factor,
        "OffEff": l_off_eff,
        "DefEff": w_off_eff,
        "eFGPct": l_efg,
        "TOVPct": l_tov,
        "ORBPct": l_orb,
        "FTRate": l_ftr,
        "OppeFGPct": w_efg,
        "OppTOVPct": w_tov,
        "OppORBPct": w_orb,
        "OppFTRate": w_ftr,
    })

    return pd.concat([winners, losers], ignore_index=True)


def compute_team_season_stats(game_stats, max_day=None):
    """
    Aggregate game-level stats into team-season summary statistics,
    with simple opponent-quality adjustment for efficiency metrics.

    Args:
        game_stats: DataFrame from build_game_stats()
        max_day: Only include games up to this DayNum (for leakage prevention).
                 Defaults to PRE_TOURNEY_DAY.
    """
    if max_day is None:
        max_day = PRE_TOURNEY_DAY

    df = game_stats[game_stats["DayNum"] <= max_day].copy()

    # Step 1: Compute raw team averages
    agg = df.groupby(["Season", "TeamID"]).agg(
        Games=("Win", "count"),
        Wins=("Win", "sum"),
        OffEff_mean=("OffEff", "mean"),
        OffEff_std=("OffEff", "std"),
        DefEff_mean=("DefEff", "mean"),
        DefEff_std=("DefEff", "std"),
        eFGPct_mean=("eFGPct", "mean"),
        TOVPct_mean=("TOVPct", "mean"),
        ORBPct_mean=("ORBPct", "mean"),
        FTRate_mean=("FTRate", "mean"),
        OppeFGPct_mean=("OppeFGPct", "mean"),
        OppTOVPct_mean=("OppTOVPct", "mean"),
        OppORBPct_mean=("OppORBPct", "mean"),
        OppFTRate_mean=("OppFTRate", "mean"),
        Score_mean=("Score", "mean"),
        OppScore_mean=("OppScore", "mean"),
        Score_std=("Score", "std"),
        Poss_mean=("Poss", "mean"),
    ).reset_index()

    # Step 2: Opponent-quality adjustment (1 iteration)
    # For each team, compute the average quality of their opponents,
    # then adjust their efficiency by how much their opponents deviate
    # from the league average.
    raw_eff = agg.set_index("TeamID")[["OffEff_mean", "DefEff_mean"]].to_dict("index")
    league_avg_off = agg["OffEff_mean"].mean()
    league_avg_def = agg["DefEff_mean"].mean()

    adj_off = {}
    adj_def = {}

    for season in df["Season"].unique():
        season_df = df[df["Season"] == season]
        season_teams = agg[agg["Season"] == season]

        for _, team_row in season_teams.iterrows():
            team_id = team_row["TeamID"]
            team_games = season_df[season_df["TeamID"] == team_id]

            # Average opponent raw defensive efficiency
            # (opponent's defense = how many points opponents typically allow)
            opp_ids = team_games["OppID"].values
            opp_def_ratings = []
            opp_off_ratings = []
            for opp_id in opp_ids:
                opp_stats = raw_eff.get(opp_id)
                if opp_stats:
                    opp_def_ratings.append(opp_stats["DefEff_mean"])
                    opp_off_ratings.append(opp_stats["OffEff_mean"])

            if opp_def_ratings:
                # If opponents allow more than average, our offense looks inflated
                avg_opp_def = np.mean(opp_def_ratings)
                adj_off[team_id] = team_row["OffEff_mean"] + (league_avg_def - avg_opp_def)

                # If opponents score more than average, our defense looks deflated
                avg_opp_off = np.mean(opp_off_ratings)
                adj_def[team_id] = team_row["DefEff_mean"] + (league_avg_off - avg_opp_off)
            else:
                adj_off[team_id] = team_row["OffEff_mean"]
                adj_def[team_id] = team_row["DefEff_mean"]

    agg["AdjOE"] = agg["TeamID"].map(adj_off)
    agg["AdjDE"] = agg["TeamID"].map(adj_def)

    # Derived features
    agg["WinPct"] = agg["Wins"] / agg["Games"]
    agg["AdjEM"] = agg["AdjOE"] - agg["AdjDE"]
    agg["RawEM"] = agg["OffEff_mean"] - agg["DefEff_mean"]
    agg["ScoreMargin_mean"] = agg["Score_mean"] - agg["OppScore_mean"]
    agg["Consistency"] = agg["OffEff_std"].fillna(agg["OffEff_std"].median())

    return agg


def get_massey_ordinals(data, season, day_num=None):
    """
    Get the latest Massey ordinal rankings for a season up to a given day.

    Returns DataFrame with one row per team, columns for key ranking systems
    plus a composite rank averaged across the key systems only.
    """
    if day_num is None:
        day_num = PRE_TOURNEY_DAY

    ordinals = data["ordinals"]
    season_ord = ordinals[
        (ordinals["Season"] == season) & (ordinals["RankingDayNum"] <= day_num)
    ]

    if season_ord.empty:
        return pd.DataFrame()

    # Get latest ranking day for each system-team pair
    latest = season_ord.sort_values("RankingDayNum").groupby(
        ["SystemName", "TeamID"]
    ).last().reset_index()

    # Pivot to wide format: one row per team, one column per system
    pivot = latest.pivot_table(
        index="TeamID", columns="SystemName", values="OrdinalRank"
    )

    # Select key systems
    available = [s for s in MASSEY_KEY_SYSTEMS if s in pivot.columns]
    result = pivot[available].copy() if available else pivot.iloc[:, :8].copy()

    # Composite: mean rank across selected key systems only (not all 100+)
    result["MasseyComposite"] = result[available].mean(axis=1) if available else pivot.mean(axis=1)

    result = result.reset_index()
    result["Season"] = season

    return result


def build_seed_features(data):
    """Build seed lookup: (Season, TeamID) -> seed number."""
    seeds = data["seeds"].copy()
    seeds["SeedNum"] = seeds["Seed"].apply(parse_seed)
    seeds["Region"] = seeds["Seed"].str[0]
    return seeds[["Season", "TeamID", "SeedNum", "Region"]]


def add_massey_features(features, a_massey, b_massey):
    """
    Add Massey ordinal differential features to a matchup feature dict.
    Negative values mean team A has a better (lower) rank.
    """
    if not a_massey or not b_massey:
        return
    systems = [s for s in MASSEY_KEY_SYSTEMS if s in a_massey and s in b_massey]
    systems.append("MasseyComposite")
    for sys_name in systems:
        a_rank = a_massey.get(sys_name)
        b_rank = b_massey.get(sys_name)
        if a_rank is not None and b_rank is not None:
            features[f"d_{sys_name}_rank"] = a_rank - b_rank


def build_matchup_features(team_a_stats, team_b_stats,
                           team_a_seed=None, team_b_seed=None,
                           a_massey=None, b_massey=None):
    """
    Build a feature vector for a matchup by differencing team stats.
    Positive values mean team A has a higher value for that stat.

    Note: for DefEff/TOVPct/ranks, higher is worse, so the model must
    learn the appropriate sign. This is standard — tree models and
    logistic regression handle mixed polarity fine.
    """
    diff_cols = [
        "AdjEM", "AdjOE", "AdjDE",
        "OffEff_mean", "DefEff_mean",
        "eFGPct_mean", "TOVPct_mean", "ORBPct_mean", "FTRate_mean",
        "OppeFGPct_mean", "OppTOVPct_mean", "OppORBPct_mean", "OppFTRate_mean",
        "WinPct", "ScoreMargin_mean", "Consistency",
    ]

    features = {}
    for col in diff_cols:
        a_val = team_a_stats.get(col, np.nan)
        b_val = team_b_stats.get(col, np.nan)
        if isinstance(a_val, (int, float)) and isinstance(b_val, (int, float)):
            features[f"d_{col}"] = a_val - b_val
        else:
            features[f"d_{col}"] = np.nan

    if team_a_seed is not None and team_b_seed is not None:
        features["d_Seed"] = team_a_seed - team_b_seed

    # Add Massey ordinal features
    add_massey_features(features, a_massey, b_massey)

    return features
