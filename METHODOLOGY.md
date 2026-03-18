# Methodology

This document provides a detailed technical description of the prediction system — what it does, why it does it that way, and what the evidence says about each design choice.

## Table of Contents

- [Problem Formulation](#problem-formulation)
- [Data Pipeline](#data-pipeline)
- [Feature Engineering](#feature-engineering)
- [Bayesian Hierarchical Model](#bayesian-hierarchical-model)
- [Feature-Based Models](#feature-based-models)
- [Ensemble Construction](#ensemble-construction)
- [Monte Carlo Simulation](#monte-carlo-simulation)
- [Evaluation Methodology](#evaluation-methodology)
- [Known Limitations](#known-limitations)

---

## Problem Formulation

The task is to predict the probability that Team A defeats Team B for every possible matchup in the NCAA Men's Basketball Tournament. These probabilities are then used to:

1. Evaluate model quality via Brier score and log loss on historical tournaments
2. Simulate the tournament thousands of times to compute advancement probabilities
3. Generate bracket recommendations

The key distinction from a pure classification problem: **we care about probability calibration, not just who wins.** A model that predicts every game at 0.55 and gets 55% right is better calibrated (and more useful for bracket optimization) than one that predicts every game at 0.90 and gets 70% right.

## Data Pipeline

### Source Data

All data comes from the Kaggle March Machine Learning Mania competition, which provides:

- **Regular season detailed results** (2003–2026): ~5,500 games/season with full box scores (field goals, rebounds, assists, turnovers, steals, blocks, fouls, overtime periods)
- **Tournament results** (2003–2025): ~67 games/year for training and evaluation
- **Seeds** (1985–2026): Tournament seeding for all 68 teams
- **Massey ordinals** (2003–2026): Rankings from ~197 independent computer rating systems
- **Geographic data**: Game locations for potential travel-distance features

### Preprocessing

**Tempo-free normalization.** All statistics are converted to per-100-possessions using:

```
POSS = FGA - OREB + TO + 0.475 * FTA
```

The 0.475 coefficient is KenPom's college-specific free throw multiplier, derived from play-by-play data. Both teams' possession estimates are averaged for each game.

**Overtime normalization.** Game scores and possessions are scaled to 40-minute equivalents:

```
ot_factor = 40 / (40 + 5 * num_overtime_periods)
```

The Four Factors (eFG%, TOV%, ORB%, FTRate) are ratio-based and therefore overtime-invariant, so they need no adjustment.

**Temporal cutoff.** All features use data from day ≤ 132 of each season (before the NCAA tournament begins, typically day 134–136). This prevents information leakage from conference tournament results that may overlap with early tournament scheduling.

**Vectorized computation.** The game statistics transformation processes ~125,000 regular-season game rows using pandas vectorized operations (no `iterrows`), creating two rows per game — one from each team's perspective.

### Opponent-Quality Adjustment

Raw per-possession efficiency metrics are misleading because teams play different-strength schedules. We apply a single-iteration opponent adjustment:

```
AdjOE[team] = RawOE[team] + (league_avg_DE - mean(RawDE[opponents]))
AdjDE[team] = RawDE[team] + (league_avg_OE - mean(RawOE[opponents]))
```

If a team's opponents allow more points than average (weak defenses), the team's raw offense is inflated. The adjustment corrects for this by adding the difference between the league-average defense and the team's opponents' average defense.

This is a simplified version of KenPom's iterative least-squares approach. A single iteration captures most of the adjustment but does not fully converge. The Massey ordinal features (which come from systems that do iterate to convergence) compensate for this approximation.

## Feature Engineering

All matchup features are computed as **differences** (Team A stat minus Team B stat). This halves the feature space, creates mathematical symmetry (P(A wins) = 1 - P(B wins) under logistic models), and prevents models from memorizing team identities.

### Feature Set (26 features)

**Efficiency metrics (6 features):**
- `d_AdjEM`: Adjusted efficiency margin (AdjOE - AdjDE) — the single strongest predictor
- `d_AdjOE`: Opponent-adjusted offensive efficiency (points scored per 100 possessions)
- `d_AdjDE`: Opponent-adjusted defensive efficiency (points allowed per 100 possessions)
- `d_OffEff_mean`: Raw offensive efficiency (unadjusted, provides complementary signal)
- `d_DefEff_mean`: Raw defensive efficiency
- `d_ScoreMargin_mean`: Average scoring margin

**Four Factors (8 features):**
- `d_eFGPct_mean`: Effective FG% = (FGM + 0.5 × FGM3) / FGA — accounts for 47% of efficiency variance
- `d_TOVPct_mean`: Turnover rate — accounts for 21%
- `d_ORBPct_mean`: Offensive rebound rate — accounts for 26%
- `d_FTRate_mean`: Free throw rate (FTA/FGA) — accounts for 7%
- Plus the opponent-side versions of each (what the team forces defensively)

**Team quality indicators (3 features):**
- `d_WinPct`: Win percentage
- `d_Consistency`: Standard deviation of offensive efficiency (lower = more consistent)
- `d_Seed`: Tournament seed difference

**Massey ordinal rankings (9 features):**
- `d_POM_rank`, `d_SAG_rank`, `d_MOR_rank`, `d_DOL_rank`, `d_COL_rank`, `d_RTH_rank`, `d_WOL_rank`, `d_AP_rank`: Individual ranking system differentials
- `d_MasseyComposite_rank`: Mean rank across the 8 selected key systems

These ranking features are among the most important in the model (POM and MOR are typically the #1 and #2 features by XGBoost importance). They effectively give the model access to a pre-built ensemble of ~8 independent rating algorithms, each of which has done its own opponent adjustment and weighting.

**Missing value handling.** Rank features are imputed with 175 (roughly median D-I rank). Other features are imputed with 0 (neutral difference). This is preferable to dropping rows, as it preserves the matchup structure.

## Bayesian Hierarchical Model

### Model Specification

```
# Hyperpriors
σ_off ~ HalfStudentT(ν=3, σ=2.5)
σ_def ~ HalfStudentT(ν=3, σ=2.5)
σ_game ~ HalfNormal(σ=10)

# Global parameters
intercept ~ Normal(70, 5)        # average score
home_adv ~ Normal(3.5, 1.5)     # home court advantage

# Team-level parameters (sum-to-zero for identifiability)
offense[i] ~ Normal(0, σ_off)    # for i = 1..N_teams, Σ offense = 0
defense[i] ~ Normal(0, σ_def)    # for i = 1..N_teams, Σ defense = 0

# Likelihood
score_home ~ Normal(intercept + home_adv × (1 - neutral) + offense[home] + defense[away], σ_game)
score_away ~ Normal(intercept + offense[away] + defense[home], σ_game)
```

### Design Choices

**Normal likelihood, not Poisson.** Basketball scores have a large mean (~70) and continuous-like variance. The Normal distribution is more appropriate than Poisson and avoids the exponential link function that Poisson requires.

**Sum-to-zero constraint.** Without it, the model is unidentifiable — you can add any constant to all offenses and subtract it from the intercept without changing the likelihood. The constraint is implemented via a non-centered parameterization: sample N-1 unconstrained parameters, set the Nth to the negative sum.

**Offense/defense decomposition.** Two parameters per team (vs. a single strength parameter) captures the difference between a team that wins 80–75 (high-scoring, porous defense) and one that wins 55–50 (defensive grinder). This also enables richer matchup predictions.

**Weakly informative priors.** HalfStudentT(3, 2.5) for scale parameters is the standard recommendation from Gelman and the Stan development team. The data (5,500+ games) dominates the priors in all cases.

**Home court adjustment.** The `home_adv` parameter is multiplied by `(1 - is_neutral)`, zeroing it out for neutral-site games. Tournament games are neutral, so this parameter affects only the regular-season estimation but not tournament predictions.

### Inference

The model is fit using PyMC's NUTS (No-U-Turn Sampler):
- **4 chains**, each with **1,000 tuning steps** and **2,000 sampling draws**
- **8,000 total posterior samples** per team parameter
- Takes **~35 seconds** per season on a modern machine

Zero divergent transitions across all backtest seasons indicates the posterior geometry is well-behaved.

### Win Probability Computation

For a neutral-site matchup between Team A and Team B, the expected score differential is:

```
Δ = (intercept + offense[A] + defense[B]) - (intercept + offense[B] + defense[A])
  = offense[A] - offense[B] + defense[B] - defense[A]
```

The actual score differential follows `Normal(Δ, √2 × σ_game)`, so:

```
P(A wins) = Φ(Δ / (√2 × σ_game))
```

where Φ is the standard normal CDF. This is computed for each posterior sample and averaged, capturing parameter uncertainty in the final probability.

## Feature-Based Models

### Logistic Regression

A regularized logistic regression (C=1.0) on standardized features. Despite its simplicity, it is surprisingly competitive — multiple Kaggle winners have used logistic regression as their primary model. Its value in the ensemble is cognitive diversity: its errors are in systematically different places than the tree-based model.

### Calibrated XGBoost

An XGBoost gradient-boosted tree classifier with:
- 200 estimators, max depth 4, learning rate 0.05
- Subsample 0.8, column subsample 0.8
- L1 regularization (alpha=0.1), L2 regularization (lambda=1.0)
- Platt scaling (sigmoid calibration) via `CalibratedClassifierCV`

Platt scaling was chosen over isotonic calibration because the training set is small (~1,200–1,400 tournament games). Isotonic regression is non-parametric and can overfit on small calibration sets; sigmoid calibration has only 2 parameters.

### Feature-Based Ensemble

The logistic regression and calibrated XGBoost predictions are averaged with equal weights (0.5/0.5). This provides model family diversity (linear vs. tree-based) which the literature identifies as the key driver of ensemble benefit.

## Ensemble Construction

The final ensemble blends the feature-based models and the Bayesian model:

```
P_final = (1 - w_bayes) × P_features + w_bayes × P_bayesian
```

where `w_bayes` is scaled by posterior uncertainty:

```
confidence = 1 - clip(bayes_std / 0.25, 0, 0.8)
w_bayes = 0.50 × confidence
```

When the Bayesian model is confident about a matchup (low posterior standard deviation), it gets its full 50% weight. When uncertain (e.g., for teams with few games), the weight is reduced, leaning more on the feature-based models.

### Weight Selection

A sweep over Bayesian weight from 0.0 to 1.0 on the 10-season backtest found:

- 0.0 (features only): Brier 0.1917
- 0.25: Brier 0.1896
- **0.50: Brier 0.1886** ← optimal
- 0.60: Brier 0.1886
- 1.0 (Bayesian only): Brier 0.1901

The optimum at 0.50 indicates both model families contribute roughly equally valuable — and crucially, different — information.

## Monte Carlo Simulation

### Tournament Structure

The simulator implements the full NCAA tournament bracket:

1. **Play-in resolution.** For seeds with multiple teams (First Four), the play-in game is simulated using the ensemble win probability function.
2. **Regional bracket.** Each of 4 regions is simulated through 4 rounds (R64 → R32 → S16 → E8), following the standard bracket tree: 1v16, 8v9, 5v12, 4v13, 6v11, 3v14, 7v10, 2v15.
3. **Final Four.** Regional winners are paired according to the NCAA bracket structure (W vs X, Y vs Z).
4. **Championship.** Final Four winners play for the title.

### Implementation

All pairwise win probabilities are precomputed into a matrix before simulation begins (~2,016 unique pairs for 64 teams). Each simulation then uses only array lookups and random draws, running 50,000 simulations in ~15 seconds.

Game outcomes are drawn as Bernoulli trials using the precomputed probabilities. The advancement count for each team at each round is tallied across all simulations and divided by the total to produce advancement probabilities.

## Evaluation Methodology

### Temporal Cross-Validation

The gold-standard evaluation protocol from the literature: **expanding-window temporal CV.**

```
Fold 1: Train on 2003-2014, test on 2015 tournament
Fold 2: Train on 2003-2015, test on 2016 tournament
...
Fold 10: Train on 2003-2024, test on 2025 tournament
```

The 2020 tournament (cancelled due to COVID) is skipped. Feature selection, model training, and calibration all occur within each fold — no future information leaks into training.

### Metrics

- **Brier Score** (primary): Mean squared error of probability predictions. Lower is better. Range: 0 (perfect) to 1 (worst). A coin flip scores 0.25.
- **Log Loss**: Logarithmic scoring rule. More sensitive to confident wrong predictions than Brier. A single prediction of 0.95 that's wrong contributes ~3.0 to log loss.
- **Accuracy**: Fraction of games where the predicted winner (P > 0.5) was correct. Useful as a sanity check but not the optimization target.
- **ECE** (Expected Calibration Error): Measures how well predicted probabilities match observed frequencies across probability bins. ECE < 0.03 is excellent.

### Benchmarks

Every evaluation compares against:

1. **Seed baseline**: Win probability from a logistic function of seed difference. ~70% accuracy, Brier ~0.21.
2. **Feature ensemble alone**: LR + calibrated XGBoost without Bayesian component.
3. **Bayesian alone**: Hierarchical model without feature-based models.
4. **Full ensemble**: The production system.

## Known Limitations

### What the Model Doesn't Know

1. **Injuries.** The model uses season-aggregate statistics and has no knowledge of individual player availability for tournament games.
2. **Matchup-specific dynamics.** A zone defense might neutralize a team that relies on driving, but the model sees only aggregate offensive/defensive efficiency.
3. **Motivation and psychology.** Senior-laden teams in their last tournament, coaches in their first, revenge matchups — none of this is captured.
4. **In-season improvement.** The opponent adjustment uses season-long averages. A team that improved dramatically in the last month looks the same as its October version. (The Massey ordinal features partially mitigate this, as some rating systems apply recency weighting.)

### Methodological Limitations

1. **Training only on tournament data.** The feature-based models are trained on ~1,400 historical tournament games. Including regular-season games with sample weights would increase the training set ~100x.
2. **Single-iteration opponent adjustment.** KenPom iterates to convergence; we approximate with one pass. The Massey ordinals compensate, but our own efficiency metrics are less precise than KenPom's.
3. **No travel distance features.** The literature identifies this as the strongest "intangible" predictor (150+ miles → 33.6% drop in winning odds), but we haven't implemented it yet.
4. **Static game probabilities in simulation.** The simulator uses pre-tournament ratings throughout. A team that pulls a dramatic first-round upset doesn't get a rating boost for subsequent rounds.
5. **No bracket optimization.** The system generates advancement probabilities but doesn't optimize bracket picks for specific pool sizes or scoring systems. In large pools, contrarian picks (underowned teams with positive expected value) can significantly outperform probability-maximizing picks.

### The Accuracy Ceiling

The literature documents a persistent ~74–75% accuracy ceiling across all methods, from logistic regression to transformers. Our 70.6% accuracy reflects honest out-of-sample evaluation with proper temporal CV — many published models report higher accuracy using evaluation methods that allow subtle information leakage.

Roughly one quarter of tournament games are genuinely unpredictable from pre-game information. UMBC over Virginia (2018), Fairleigh Dickinson over Purdue (2023), and countless other upsets are not modeling failures — they are the irreducible randomness of single-elimination basketball.
