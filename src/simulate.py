"""
Monte Carlo tournament simulator.

Given game-level win probabilities, simulates the NCAA tournament bracket
thousands of times to compute round-by-round advancement probabilities
for every team.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from data_loader import parse_seed


def load_bracket(data, season):
    """
    Load the tournament bracket structure for a given season.

    Returns:
        seeds: dict mapping TeamID -> (region, seed_num)
        slots: DataFrame with bracket slots and matchup structure
    """
    seeds_df = data["seeds"][data["seeds"]["Season"] == season].copy()
    seeds_df["SeedNum"] = seeds_df["Seed"].apply(parse_seed)
    seeds_df["Region"] = seeds_df["Seed"].str[0]

    seeds = {}
    for _, row in seeds_df.iterrows():
        seeds[row["TeamID"]] = (row["Region"], row["SeedNum"], row["Seed"])

    slots = None
    if "tourney_slots" in data:
        slots = data["tourney_slots"][data["tourney_slots"]["Season"] == season]

    return seeds, slots


def resolve_playin_games(seeds_df, season, win_prob_fn=None, rng=None):
    """
    Resolve play-in (First Four) games for seeds with multiple teams.

    For each seed number that has >1 team in a region, simulate the play-in
    game using win_prob_fn or pick randomly if no function is provided.

    Returns a cleaned seeds DataFrame with exactly one team per seed per region.
    """
    season_seeds = seeds_df[seeds_df["Season"] == season].copy()
    season_seeds["SeedNum"] = season_seeds["Seed"].apply(parse_seed)
    season_seeds["Region"] = season_seeds["Seed"].str[0]

    if rng is None:
        rng = np.random.default_rng(42)

    resolved = []
    for (region, seed_num), group in season_seeds.groupby(["Region", "SeedNum"]):
        if len(group) == 1:
            resolved.append(group.iloc[0])
        else:
            # Play-in game: simulate or probabilistically select winner
            teams = group["TeamID"].tolist()
            if win_prob_fn is not None and len(teams) == 2:
                p = win_prob_fn(teams[0], teams[1])
                winner = teams[0] if rng.random() < p else teams[1]
            else:
                winner = rng.choice(teams)
            winner_row = group[group["TeamID"] == winner].iloc[0]
            resolved.append(winner_row)

    return pd.DataFrame(resolved)


def build_first_round_matchups(seeds_df, season, win_prob_fn=None, rng=None):
    """
    Build first-round matchups from seeds.

    Resolves play-in games first, then builds standard bracket matchups:
    1v16, 8v9, 5v12, 4v13, 6v11, 3v14, 7v10, 2v15 within each region.
    """
    resolved_seeds = resolve_playin_games(seeds_df, season, win_prob_fn, rng)

    # Standard matchup order by seed (determines bracket tree topology)
    matchup_pairs = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]

    matchups = []
    for region in resolved_seeds["Region"].unique():
        region_teams = resolved_seeds[resolved_seeds["Region"] == region]
        seed_to_team = region_teams.set_index("SeedNum")["TeamID"].to_dict()

        for s1, s2 in matchup_pairs:
            if s1 in seed_to_team and s2 in seed_to_team:
                matchups.append({
                    "Region": region,
                    "Seed1": s1,
                    "Seed2": s2,
                    "Team1": seed_to_team[s1],
                    "Team2": seed_to_team[s2],
                })

    return matchups


def simulate_tournament(win_prob_fn, seeds_df, season, n_sims=10000, rng=None):
    """
    Simulate the NCAA tournament via Monte Carlo.

    Args:
        win_prob_fn: callable(team_a_id, team_b_id) -> float P(A wins)
        seeds_df: DataFrame with Season, Seed, TeamID
        season: int
        n_sims: number of simulations
        rng: numpy random generator

    Returns:
        advancement: dict mapping TeamID -> array of shape (n_rounds,)
                     with fraction of sims team advanced to each round
        champions: dict mapping TeamID -> fraction of sims team won title
    """
    if rng is None:
        rng = np.random.default_rng(42)

    # Build initial matchups, resolving play-in games via win_prob_fn
    matchups = build_first_round_matchups(seeds_df, season, win_prob_fn, rng)

    if not matchups:
        print(f"  No matchups found for season {season}")
        return {}, {}

    # Group by region
    regions = {}
    for m in matchups:
        r = m["Region"]
        if r not in regions:
            regions[r] = []
        regions[r].append((m["Team1"], m["Team2"]))

    # Determine Final Four pairings from tournament slot data
    # NCAA pairs regions: W vs X, Y vs Z (from R5WX, R5YZ slots)
    # Default to this standard pairing; works for all recent seasons
    region_list = sorted(regions.keys())
    if len(region_list) == 4:
        # Standard pairing: (W,X) and (Y,Z) — or equivalently first two vs last two
        # when sorted alphabetically W<X<Y<Z, this gives W vs X, Y vs Z
        ff_pairing = [(region_list[0], region_list[1]),
                      (region_list[2], region_list[3])]
    else:
        ff_pairing = [(region_list[0], region_list[1])]
    all_team_ids = set()
    for m in matchups:
        all_team_ids.add(m["Team1"])
        all_team_ids.add(m["Team2"])

    # Precompute all pairwise win probabilities for teams in the tournament
    team_list = sorted(all_team_ids)
    n_teams = len(team_list)
    team_idx = {t: i for i, t in enumerate(team_list)}

    print(f"  Precomputing {n_teams * (n_teams - 1) // 2} pairwise probabilities...")
    prob_matrix = np.full((n_teams, n_teams), 0.5)
    for i in range(n_teams):
        for j in range(i + 1, n_teams):
            p = win_prob_fn(team_list[i], team_list[j])
            prob_matrix[i, j] = p
            prob_matrix[j, i] = 1 - p

    # Track advancement counts
    # Rounds: R64, R32, S16, E8, F4, Championship, Winner = 7 rounds
    round_names = ["R64", "R32", "S16", "E8", "F4", "Final", "Champion"]
    advancement_counts = {t: np.zeros(7) for t in team_list}

    print(f"  Running {n_sims} simulations...")
    for sim in range(n_sims):
        # Simulate each region
        regional_winners = {}

        for region in region_list:
            # First round: 8 games
            bracket = [t for pair in regions[region] for t in pair]
            # bracket is ordered: [1-seed, 16-seed, 8-seed, 9-seed, ...]

            round_teams = list(bracket)

            round_idx = 0  # R64
            while len(round_teams) > 1:
                next_round = []
                for k in range(0, len(round_teams), 2):
                    t1 = round_teams[k]
                    t2 = round_teams[k + 1]
                    i1, i2 = team_idx[t1], team_idx[t2]
                    p = prob_matrix[i1, i2]

                    if rng.random() < p:
                        winner = t1
                    else:
                        winner = t2

                    advancement_counts[winner][round_idx + 1] += 1
                    next_round.append(winner)

                round_teams = next_round
                round_idx += 1

            regional_winners[region] = round_teams[0]

        # Final Four: semi-finals using actual regional pairings
        finalists = []
        for r_a, r_b in ff_pairing:
            t1 = regional_winners[r_a]
            t2 = regional_winners[r_b]
            i1, i2 = team_idx[t1], team_idx[t2]
            if rng.random() < prob_matrix[i1, i2]:
                finalists.append(t1)
            else:
                finalists.append(t2)
            finalists[-1]  # the winner
            advancement_counts[finalists[-1]][5] += 1  # Final

        finalist1, finalist2 = finalists[0], finalists[1]

        # Championship
        i1, i2 = team_idx[finalist1], team_idx[finalist2]
        if rng.random() < prob_matrix[i1, i2]:
            champ = finalist1
        else:
            champ = finalist2
        advancement_counts[champ][6] += 1  # Champion

    # All tournament teams made R64
    for t in team_list:
        advancement_counts[t][0] = n_sims  # everyone starts in R64

    # Convert to probabilities
    advancement_probs = {
        t: counts / n_sims for t, counts in advancement_counts.items()
    }

    champions = {t: advancement_probs[t][6] for t in team_list}

    return advancement_probs, champions, round_names


def format_results(advancement_probs, champions, round_names, teams_df):
    """Format simulation results as a readable DataFrame."""
    rows = []
    for team_id, probs in advancement_probs.items():
        row = {"TeamID": team_id}
        for i, rname in enumerate(round_names):
            row[rname] = probs[i]
        rows.append(row)

    df = pd.DataFrame(rows)

    # Add team names
    name_map = teams_df.set_index("TeamID")["TeamName"]
    df["Team"] = df["TeamID"].map(name_map)

    # Sort by championship probability
    df = df.sort_values("Champion", ascending=False)

    return df


if __name__ == "__main__":
    from data_loader import load_raw_data

    # Quick test with a simple seed-based probability model
    data = load_raw_data()
    seeds_df = data["seeds"]

    season = 2025
    season_seeds = seeds_df[seeds_df["Season"] == season].copy()
    season_seeds["SeedNum"] = season_seeds["Seed"].apply(parse_seed)
    seed_lookup = season_seeds.set_index("TeamID")["SeedNum"].to_dict()

    def seed_prob(team_a, team_b):
        """Simple seed-based win probability."""
        s_a = seed_lookup.get(team_a, 8)
        s_b = seed_lookup.get(team_b, 8)
        diff = s_b - s_a  # positive if A is better seed
        return 1 / (1 + 10 ** (-diff * 0.15))

    print("Simulating 2025 tournament with seed-based probabilities...")
    adv_probs, champs, round_names = simulate_tournament(
        seed_prob, seeds_df, season, n_sims=50000
    )

    results = format_results(adv_probs, champs, round_names, data["teams"])
    print("\nTop 20 teams by championship probability:")
    cols = ["Team", "R64", "R32", "S16", "E8", "F4", "Final", "Champion"]
    print(results[cols].head(20).to_string(index=False, float_format=lambda x: f"{x:.3f}"))
