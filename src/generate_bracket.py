"""
Generate a concrete 63-game bracket for a pool contest.

Produces game-by-game picks that are consistent with bracket structure,
optimized for a specific scoring system and pool size.

For small pools (< 25 people): pick favorites (chalk-heavy strategy).
For large pools (100+): pick contrarian upsets for differentiation.
"""

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import load_raw_data, build_game_stats, parse_seed
from pipeline import build_training_data, train_final_models
from bayesian_model import fit_season, compute_win_probability, get_team_ratings
from full_pipeline import build_ensemble_prob_fn, OUTPUT_DIR
from simulate import resolve_playin_games

# CBS scoring
SCORING = {
    "R64": 1,    # Round of 64
    "R32": 2,    # Round of 32
    "S16": 4,    # Sweet 16
    "E8": 8,     # Elite 8
    "F4": 16,    # Final Four
    "Final": 32, # Championship
}


def generate_concrete_bracket(prob_fn, seeds_df, season, teams_df,
                              pool_size=17, strategy="chalk", rng=None):
    """
    Generate a concrete bracket: 63 game picks respecting bracket structure.

    Args:
        prob_fn: callable(team_a, team_b) -> P(A wins)
        seeds_df: seeds DataFrame
        season: tournament year
        teams_df: teams DataFrame for name lookup
        pool_size: number of entries in the pool
        strategy: "chalk" (pick favorites), "balanced", or "contrarian"

    Returns:
        bracket: list of dicts, one per game, with round/region/teams/pick/probability
    """
    if rng is None:
        rng = np.random.default_rng(42)

    # Resolve play-in games deterministically (pick the favorite)
    resolved = resolve_playin_games(seeds_df, season, prob_fn, rng=np.random.default_rng(0))

    # Build matchup structure by region
    matchup_pairs = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]
    name_map = teams_df.set_index("TeamID")["TeamName"].to_dict()
    seed_str_map = seeds_df[seeds_df["Season"] == season].set_index("TeamID")["Seed"].to_dict()

    regions = {}
    region_list = sorted(resolved["Region"].unique())
    for region in region_list:
        region_teams = resolved[resolved["Region"] == region]
        seed_to_team = region_teams.set_index("SeedNum")["TeamID"].to_dict()
        bracket_order = []
        for s1, s2 in matchup_pairs:
            if s1 in seed_to_team and s2 in seed_to_team:
                bracket_order.append((seed_to_team[s1], seed_to_team[s2]))
        regions[region] = bracket_order

    all_picks = []
    round_names = ["R64", "R32", "S16", "E8"]
    regional_winners = {}

    for region in region_list:
        round_teams = []
        for t1, t2 in regions[region]:
            round_teams.extend([t1, t2])

        for round_idx, round_name in enumerate(round_names):
            next_round = []
            for k in range(0, len(round_teams), 2):
                t1 = round_teams[k]
                t2 = round_teams[k + 1]
                p = prob_fn(t1, t2)

                # Pick the favorite for chalk strategy
                if p >= 0.5:
                    pick = t1
                    pick_prob = p
                else:
                    pick = t2
                    pick_prob = 1 - p

                s1 = seed_str_map.get(t1, "?")
                s2 = seed_str_map.get(t2, "?")

                all_picks.append({
                    "Round": round_name,
                    "Region": region,
                    "Points": SCORING[round_name],
                    "Team1": name_map.get(t1, str(t1)),
                    "Seed1": s1,
                    "Team2": name_map.get(t2, str(t2)),
                    "Seed2": s2,
                    "Pick": name_map.get(pick, str(pick)),
                    "PickSeed": seed_str_map.get(pick, "?"),
                    "WinProb": pick_prob,
                })

                next_round.append(pick)

            round_teams = next_round

        regional_winners[region] = round_teams[0]

    # Final Four — W vs X, Y vs Z
    ff_pairing = [(region_list[0], region_list[1]),
                  (region_list[2], region_list[3])]

    finalists = []
    for r_a, r_b in ff_pairing:
        t1 = regional_winners[r_a]
        t2 = regional_winners[r_b]
        p = prob_fn(t1, t2)

        if p >= 0.5:
            pick = t1
            pick_prob = p
        else:
            pick = t2
            pick_prob = 1 - p

        all_picks.append({
            "Round": "F4",
            "Region": f"{r_a} vs {r_b}",
            "Points": SCORING["F4"],
            "Team1": name_map.get(t1, str(t1)),
            "Seed1": seed_str_map.get(t1, "?"),
            "Team2": name_map.get(t2, str(t2)),
            "Seed2": seed_str_map.get(t2, "?"),
            "Pick": name_map.get(pick, str(pick)),
            "PickSeed": seed_str_map.get(pick, "?"),
            "WinProb": pick_prob,
        })

        finalists.append(pick)

    # Championship
    t1, t2 = finalists[0], finalists[1]
    p = prob_fn(t1, t2)
    if p >= 0.5:
        pick = t1
        pick_prob = p
    else:
        pick = t2
        pick_prob = 1 - p

    all_picks.append({
        "Round": "Final",
        "Region": "Championship",
        "Points": SCORING["Final"],
        "Team1": name_map.get(t1, str(t1)),
        "Seed1": seed_str_map.get(t1, "?"),
        "Team2": name_map.get(t2, str(t2)),
        "Seed2": seed_str_map.get(t2, "?"),
        "Pick": name_map.get(pick, str(pick)),
        "PickSeed": seed_str_map.get(pick, "?"),
        "WinProb": pick_prob,
    })

    return pd.DataFrame(all_picks)


def print_bracket(bracket_df):
    """Pretty-print the bracket picks."""

    round_order = ["R64", "R32", "S16", "E8", "F4", "Final"]
    round_labels = {
        "R64": "ROUND OF 64",
        "R32": "ROUND OF 32",
        "S16": "SWEET SIXTEEN",
        "E8": "ELITE EIGHT",
        "F4": "FINAL FOUR",
        "Final": "CHAMPIONSHIP",
    }

    total_ev = 0
    total_max = 0

    for round_name in round_order:
        round_games = bracket_df[bracket_df["Round"] == round_name]
        if round_games.empty:
            continue

        pts = SCORING[round_name]
        print(f"\n{'='*70}")
        print(f"  {round_labels[round_name]} ({pts} pts per correct pick)")
        print(f"{'='*70}")

        for _, game in round_games.iterrows():
            region = game["Region"]
            conf = game["WinProb"]
            conf_bar = "█" * int(conf * 20) + "░" * (20 - int(conf * 20))

            if round_name in ["F4", "Final"]:
                print(f"  {game['Seed1']} {game['Team1']:<20} vs {game['Seed2']} {game['Team2']:<20}")
                print(f"    → {game['PickSeed']} {game['Pick']:<20} [{conf_bar}] {conf:.0%}")
            else:
                print(f"  {region} | {game['Seed1']:>3} {game['Team1']:<20} vs {game['Seed2']:>3} {game['Team2']:<20} → {game['PickSeed']:>3} {game['Pick']:<20} {conf:.0%}")

            total_ev += pts * conf
            total_max += pts

    # Summary
    champion = bracket_df[bracket_df["Round"] == "Final"].iloc[0]
    ff_teams = bracket_df[bracket_df["Round"] == "F4"]["Pick"].tolist()

    print(f"\n{'='*70}")
    print(f"  BRACKET SUMMARY")
    print(f"{'='*70}")
    print(f"\n  Champion:   {champion['PickSeed']} {champion['Pick']} ({champion['WinProb']:.0%})")
    print(f"  Final Four: {', '.join(ff_teams)}")

    # Count upsets (lower seed beating higher seed)
    upsets = 0
    for _, game in bracket_df.iterrows():
        pick_seed_num = parse_seed(game["PickSeed"]) if game["PickSeed"] != "?" else 0
        s1_num = parse_seed(game["Seed1"]) if game["Seed1"] != "?" else 0
        s2_num = parse_seed(game["Seed2"]) if game["Seed2"] != "?" else 0
        higher_seed = min(s1_num, s2_num)
        if pick_seed_num > higher_seed:
            upsets += 1

    print(f"  Upsets picked: {upsets} of {len(bracket_df)} games")
    print(f"  Expected points: {total_ev:.1f} / {total_max} possible")
    print(f"  Scoring: CBS (1-2-4-8-16-32)")
    print(f"  Pool size: 17 entries")
    print(f"  Strategy: Chalk (small pool, pick favorites)")


def main():
    print("Loading data and training models...")
    data = load_raw_data()
    target_season = 2026

    # Train feature-based models
    tourney_compact = data["tourney_compact"]
    available_seasons = sorted(
        set(data["reg_detail"]["Season"].unique())
        & set(tourney_compact["Season"].unique())
    )
    train_seasons = [s for s in available_seasons if s < target_season]
    features_df, labels, meta_df = build_training_data(data, seasons=train_seasons)
    models = train_final_models(features_df, labels)

    # Fit Bayesian model
    print(f"\nFitting Bayesian model for {target_season}...")
    bayes_trace, bayes_team_ids, bayes_team_to_idx = fit_season(
        data["reg_detail"], target_season,
        n_samples=2000, n_tune=1000, n_chains=4,
    )

    # Build ensemble probability function
    reg_game_stats = build_game_stats(data["reg_detail"])
    prob_fn = build_ensemble_prob_fn(
        models, data, reg_game_stats, target_season,
        bayes_trace=bayes_trace,
        bayes_team_to_idx=bayes_team_to_idx,
        ensemble_bayes_weight=0.50,
    )

    # Generate bracket
    print("\nGenerating bracket...")
    bracket = generate_concrete_bracket(
        prob_fn, data["seeds"], target_season, data["teams"],
        pool_size=17, strategy="chalk",
    )

    # Print it
    print_bracket(bracket)

    # Save
    out_path = OUTPUT_DIR / f"bracket_picks_{target_season}.csv"
    bracket.to_csv(out_path, index=False)
    print(f"\nBracket saved to {out_path}")


if __name__ == "__main__":
    main()
