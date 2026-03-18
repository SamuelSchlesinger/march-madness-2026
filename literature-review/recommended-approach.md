# Recommended Approach: Ambitious, Evidence-Based March Madness Prediction

## Overview

This document synthesizes findings from 25 literature review braindumps covering logistic regression baselines, ensemble methods, deep learning, Bayesian methods, Elo/rating systems, feature engineering, data sources, Kaggle competitions, FiveThirtyEight's methodology, upset prediction, Monte Carlo simulation, player-level analytics, tempo/pace analysis, conference strength/SOS, historical seed performance, betting markets, play-by-play data, transfer portal dynamics, bracket optimization, coaching intangibles, advanced metrics systems, Python tooling, model evaluation, recent innovations, and data quality preprocessing.

The approach that follows is grounded in what the literature actually shows works, while taking full advantage of available GPU/CPU resources for Bayesian inference and simulation at scale.

Cross-references: [Modeling Approaches](modeling-approaches.md) | [Data Sources & Quality](data-sources-and-quality.md) | [Feature Engineering & Metrics](features-and-metrics.md) | [Tournament Dynamics](tournament-dynamics.md) | [Evaluation & Calibration](evaluation-and-calibration.md) | [Bracket Strategy & Optimization](bracket-strategy.md) | [Tools & Implementation](tools-and-implementation.md)

---

## 1. Philosophy: Where to Invest Effort

The literature converges on several uncomfortable truths and actionable principles. Understanding these before writing a single line of code will save enormous time and prevent common mistakes.

### The ~74-75% Accuracy Ceiling Is Real

Multiple independent approaches -- LRMC (74%), logistic regression on efficiency metrics (74.6%), Sagarin (75%), Boulier-Stekler probit (73.5%), Odds Gods LightGBM (77.6% on tournament) -- all converge on roughly the same game-level accuracy. This ceiling has held from 1999 through 2026 across logistic regression, gradient boosting, LSTMs, and Transformers. Roughly one-quarter of tournament games are genuinely unpredictable from pre-game information due to injuries, shooting variance, referee effects, and other stochastic factors.

**Implication**: Do not chase accuracy. A model at 73% with excellent calibration is more valuable than one at 76% with poor calibration.

### Calibration > Raw Accuracy

The peer-reviewed paper "Machine Learning for Sports Betting: Should Model Selection Be Based on Accuracy or Calibration?" (2024) demonstrates that accuracy-driven models are systematically overconfident and produce worse real-world decisions than calibration-driven models. Kaggle's switch from log loss to Brier score in 2023 reflects this same insight. The LSTM vs. Transformer study shows that loss function choice (Brier vs. BCE) affects calibration more than architecture choice -- Brier-trained models achieve ECE of ~3% vs. ~6% for BCE-trained models regardless of architecture.

**Implication**: Optimize for calibration. Use Brier score as the primary training loss where possible. Always produce and inspect calibration plots.

### Ensemble > Single Model (But Diversity Matters)

FiveThirtyEight's composite of 6+ rating systems, the Massey composite of 100+ systems, and the CFA paper's rank-based fusion all demonstrate that combining diverse models outperforms any individual model. Critically, the CFA paper found that the best ensemble (logistic regression + SVM + CNN) did NOT include the individually strongest models (XGBoost, Random Forest) -- cognitive diversity matters more than individual model strength.

However, there is a countervailing finding: multiple Kaggle competitors report that ensembles of XGBoost + LightGBM + CatBoost + neural networks performed *worse* than a single tuned XGBoost. The difference is that diverse model *families* (linear + kernel + neural) help, while ensembles of similar tree-based models hurt.

**Implication**: Ensemble across fundamentally different model types (Bayesian hierarchical + gradient boosting + logistic regression), not within the same family.

### Features > Architecture

Across every study reviewed, feature engineering provided more predictive lift than model architecture. The LSTM paper showed 0.045-0.049 AUC improvement from better features (Elo, GLM quality metrics), likely exceeding the gain from any architecture switch. The Deshpande study found that "adding better features would yield more improvement than optimizing model parameters." The CFA paper achieved competitive accuracy using just 26 features selected via RFECV from an initial 44.

**Implication**: Spend 60% of effort on feature engineering and data quality, 25% on modeling, 15% on evaluation and calibration.

### The Market Is the Benchmark

Betting markets are remarkably efficient. The closing line is the single most accurate publicly available predictor of game outcomes. FiveThirtyEight found edges only in early rounds when their model strongly disagreed with Vegas (3+ point implied spread difference), going 5-2 in those spots but 6-15 in later rounds. Any serious prediction effort must benchmark against the closing line.

**Implication**: Include market-derived features (Vegas lines, prediction market prices) as inputs, and evaluate model performance against the closing line, not just against baseline models.

---

## 2. Data Stack

### Primary Sources

| Source | Role | Cost | Access Method |
|--------|------|------|---------------|
| **Kaggle March ML Mania** | Foundation: clean game results, seeds, detailed box scores, Massey ordinals (100+ rating systems), geographic data, coach data (2003-present) | Free | CSV download |
| **Bart Torvik / T-Rank** | Advanced metrics: AdjOE, AdjDE, Barthag, tempo, GameScript, recency-weighted ratings, player stats (2008+) | Free | `toRvik` R package or `cbbdata` R package |
| **KenPom** | Gold-standard adjusted efficiency, Pythagorean ratings, luck metric, minutes continuity | $24.95/yr | `kenpompy` Python package or `cbbdata` R package |
| **Massey Ordinals** | Composite rankings from 100+ systems -- acts as a pre-built ensemble of rating systems | Free | Included in Kaggle data; also masseyratings.com CSV |
| **hoopR / CBBpy** | Play-by-play data from ESPN: possession-level events, shot locations, lineup data | Free | R (`hoopR`) or Python (`CBBpy`) |

### Supplementary Sources

| Source | Role | Notes |
|--------|------|-------|
| **Prediction market prices** (Kalshi, Polymarket) | Real-money-weighted crowd probabilities; $2.27B monthly volume suggests high information content | Emerging source; lower vig than traditional sportsbooks |
| **Vegas closing lines** | The benchmark to beat; incorporate as a feature and as an evaluation target | Available via BigDataBall (paid) or historical Kaggle datasets |
| **EvanMiya BPR** | Player-level Bayesian ratings -- most valuable for preseason projections and injury adjustments | Blog free; full data behind paywall |
| **gamezoneR** | Shot location data (170K+ charted shots/season, 2017-18 onward) | Free R package |

### Data Quality Pipeline

The literature is emphatic that data quality is non-negotiable. Build these safeguards before any modeling:

1. **Master team ID mapping table** across Kaggle, KenPom, Torvik, ESPN, and Sports Reference. Team names are inconsistent across sources ("UConn" vs. "Connecticut" vs. "University of Connecticut").

2. **Tempo-free normalization**: All statistics converted to per-100-possessions using `POSS = FGA - OREB + TO + 0.475 * FTA`. Use 0.475 consistently (KenPom's college-specific coefficient).

3. **COVID-19 flag**: The 2020-21 season requires special handling. Elite teams showed -6.1 point differentials in first games back from COVID pauses. The 2020 tournament was cancelled entirely. Down-weight or flag these observations.

4. **Conference membership by season**: Conference realignment means a team's conference affiliation in 2015 may differ from 2025. Track membership per season.

5. **Temporal leakage audit**: All features must represent pre-game state. No tournament outcome information in training features. No future season data in training folds.

6. **Overtime normalization**: Scale all game statistics to 40-minute regulation equivalents.

7. **Missing data strategy**: Use LightGBM's native missing value handling for tree-based models. For Bayesian models, use principled imputation -- baseline Elo of 1000 for teams lacking history, median seed for missing seeds, neutral quality scores for insufficient data.

---

## 3. Feature Engineering

The literature provides a clear hierarchy of feature importance. Build features in this order of priority.

### Tier 1: Core Predictive Features (Non-Negotiable)

These appear in virtually every successful model and explain the majority of predictive variance.

- **Adjusted Efficiency Margin** (AdjEM = AdjOE - AdjDE): All 24 national champions from 2001-2024 ranked in the top 25. The single most reliable predictor.
- **Adjusted Offensive Efficiency** (AdjOE): Points scored per 100 possessions, adjusted for opponent defensive quality and game location. 23 of 24 champions ranked top 21.
- **Adjusted Defensive Efficiency** (AdjDE): Points allowed per 100 possessions, adjusted for opponent offensive quality and game location. 21 of 24 champions ranked top 31.
- **Power Rating / Barthag**: Pythagorean win expectancy (win probability vs. average team on neutral court). KenPom uses exponent 10.25; Torvik uses 11.5.
- **Tournament Seed**: The dominant predictor in regression models (p = 0.00000000045 in one study). The chalk bracket alone scores ~30% better than the average bracket.

All matchup features should be computed as **differences** (Team A stat minus Team B stat), not raw values. This reduces dimensionality, creates mathematical symmetry (P(A wins) = 1 - P(B wins) with logistic function), and prevents models from memorizing team identities.

### Tier 2: Four Factors Differentials

Dean Oliver's Four Factors explain ~99.8% of the variance in offensive efficiency (correlation 0.998 with actual offensive rating). Normalized sensitivity weights:

| Factor | Importance | Average |
|--------|-----------|---------|
| Effective FG% (eFG%) | 47% | ~50% |
| Offensive Rebounding Rate (ORB%) | 26% | ~28% |
| Turnover Rate (TOV%) | 21% | ~19% |
| Free Throw Rate (FTr = FTA/FGA) | 7% | ~32% |

Include both offensive and defensive versions for each team. Note the finding that team-level Four Factor *matchups* (e.g., elite ORB% offense vs. poor DRB% defense) do NOT add predictive value beyond overall efficiency ratings -- use the factors as general team quality indicators, not for matchup-specific analysis.

### Tier 3: Rating System Inputs (Ensemble Signal)

The Massey ordinals provide rankings from 100+ independent rating systems. Using multiple rating systems as features gives the model access to a pre-built ensemble. Key systems to extract:

- **KenPom** overall ranking and component metrics
- **Bart Torvik / T-Rank** (with recency weighting -- captures late-season form better than KenPom)
- **Massey composite ranking** (meta-ranking of all systems)
- **LRMC** (Logistic Regression / Markov Chain -- minimal-data approach captures different signal)
- **ESPN BPI** (incorporates travel distance, rest, altitude, crowd proximity)

The CFA paper found that **ranks of variables can be more predictive than raw rating values**. Consider including both the raw rating and the ordinal rank as separate features.

### Tier 4: Travel Distance and Geography

Travel distance has the strongest empirical support among "intangible" factors:

- Teams traveling 150+ miles see winning odds drop ~33.6% (Clay et al., 26-year study).
- Favorites traveling 1,000+ miles win only 59% vs. 76% when within 500 miles.
- Teams from the West crossing 2+ time zones eastward: winning percentage drops below 38%.

**Feature construction**:
- Distance from each team's campus to the game venue (available in Kaggle geographic data).
- Differential in travel distance between the two teams.
- COOPER's formula for travel effect: `5 * distance_miles^(1/3)` (cube root transformation with diminishing marginal impact).
- Time zone direction indicator (eastward travel is worse than westward).

### Tier 5: Roster Continuity and Experience

The transfer portal era (post-2021) has reduced average roster continuity to historic lows (34% in 2024-25). The literature is mixed on continuity's value:

- Returning minutes correlates with offensive efficiency improvement at r = 0.36.
- But 17 of 23 national champions had a junior or senior as top contributor -- experience matters even if acquired via transfer.
- Harvard found experience R-squared = 0.0002 once seed is controlled for.

**Recommended approach**: Include roster continuity as a **time-decaying feature** -- weight it heavily in November/December, discount it by March as teams gel. Separate total roster experience (juniors/seniors as % of minutes) from returning continuity (players who were on the same team last year).

### Tier 6: Variance and Consistency Features

The Kansas model (Professor Templin) found that consistency -- low variance in game-to-game performance -- is as important as mean performance. Inconsistent high-seeds are upset-prone; consistent low-seeds are dangerous.

- Standard deviation of scoring margin across the season.
- Standard deviation of offensive/defensive efficiency.
- Scoring margin differential over last 5 and last 10 games vs. season average (momentum proxy).
- Elo trend: OLS slope of Elo over time.

### Features to Avoid or Handle Carefully

- **Adjusted Tempo**: Champions averaged rank ~134 in tempo; 6 of 24 ranked 200th or worse. Tempo tells you about style, not quality. Include it for score prediction (total points) but not for win prediction.
- **Three-point shooting percentage**: High game-to-game variance makes it unreliable for tournament prediction. Three-point *rate* (how much a team depends on threes) is more stable and useful for identifying high-variance teams.
- **Non-conference SOS**: Only 3 of 24 champions ranked in the top 60. Not predictive of championship success.
- **Raw per-game statistics**: Always use per-possession, opponent-adjusted metrics.

---

## 4. Modeling Strategy: A Five-Layer Architecture

### Layer 1: Bayesian Hierarchical Model for Team Strength Estimation

**Purpose**: Estimate latent team offensive and defensive strength with full uncertainty quantification. This provides the foundation for all downstream predictions.

**Implementation**: PyMC (v5+) with NUTS sampler, GPU-accelerated via JAX backend.

**Model specification**:

```
# Hierarchical structure
sigma_offense ~ HalfStudentT(nu=3, sigma=2.5)
sigma_defense ~ HalfStudentT(nu=3, sigma=2.5)
home_advantage ~ Normal(3.5, sigma=1.5)
intercept ~ Normal(70, sigma=5)

# Team-level parameters (sum-to-zero constraint for identifiability)
offense[team] ~ Normal(0, sigma_offense)  # for all 353+ teams
defense[team] ~ Normal(0, sigma_defense)

# Game-level likelihood (Normal, not Poisson -- basketball scores are better modeled continuously)
mu_home = intercept + home_advantage + offense[home_team] + defense[away_team]
mu_away = intercept + offense[away_team] + defense[home_team]
sigma_game ~ HalfNormal(10)
score_home ~ Normal(mu_home, sigma_game)
score_away ~ Normal(mu_away, sigma_game)
```

**Key design decisions grounded in literature**:
- **Normal likelihood, not Poisson**: Hollander's work shows Normal is more appropriate for basketball (mean score ~70, continuous distribution captures variance better than Poisson). The Barnes Analytics Poisson model is a reasonable starting point but imperfect.
- **Sum-to-zero constraint on team parameters**: Ensures identifiability (Hollander's key insight).
- **Offense/defense decomposition**: Two parameters per team rather than one -- captures the difference between a team that wins 80-75 vs. 55-50. Also enables richer matchup predictions.
- **Weakly informative priors**: The data dominates with hundreds of games per season. HalfStudentT for variance parameters provides regularization without being overly restrictive.

**Extensions to explore**:
- **Time-varying strength** via state-space component (Lopez et al.): `strength[t] = strength[t-1] + noise`. Captures late-season improvement/decline. This is the most promising Bayesian extension identified in the literature.
- **Conference hierarchical structure**: Add a conference-level grouping parameter to handle the unbalanced schedule problem (Wieland showed conference structure inflates rating error by 54%).
- **Informative priors from Massey ordinals**: Use the composite ranking to set informative priors on team strength, following FiveThirtyEight's approach of incorporating preseason polls as Bayesian priors.

**Computational considerations**: With ~353 teams and ~5,000+ games per season, the parameter space is large. PyMC with JAX backend on GPU should handle this comfortably. Target 4 chains, 2,000 samples each with 1,000 tuning steps. Expect 15-30 minutes on modern GPU hardware.

**Output**: Full posterior distributions over offensive and defensive strength for every team. These posteriors -- not just point estimates -- feed directly into the Monte Carlo simulation layer.

### Layer 2: Gradient Boosting for Game Outcome Prediction

**Purpose**: Capture nonlinear feature interactions that the Bayesian model cannot. The literature consistently shows gradient boosting as the strongest single model family for this task.

**Implementation**: XGBoost (preferred over LightGBM based on recent Kaggle findings -- the 2025 rank-107 solution found XGBoost outperformed LightGBM, CatBoost, and MLP).

**Feature set**: All features from Section 3 (efficiency differentials, Four Factors differentials, rating system inputs, travel distance, continuity, variance metrics), computed as team-A-minus-team-B differences.

**Training protocol**:
- **Leave-one-season-out cross-validation**: Train on all tournaments except year N, test on year N. Repeat for 2015-2025 (excluding 2020). This is the gold-standard temporal CV approach from top Kaggle solutions.
- **Sample weighting**: Regular season = 1x, late regular season / conference tournaments = 2x, NCAA tournament = 6x (following the Odds Gods approach). This deliberately prioritizes tournament accuracy.
- **Feature selection via RFECV**: Start with all features, recursively eliminate those that do not improve expanding-window CV score (following the maze508 gold solution approach).
- **Hyperparameter tuning**: Optuna with manual stabilization. Based on the literature, expect diminishing returns -- feature engineering matters more than hyperparameters.

**Calibration**: Apply **isotonic regression** on out-of-fold predictions to correct overconfident probability extremes (Odds Gods approach). Alternatively, train with Brier loss directly if XGBoost supports it via custom objective, since the LSTM/Transformer paper showed that loss function choice affects calibration more than architecture.

**Output**: Calibrated game-level win probabilities for any matchup.

### Layer 3: Calibrated Ensemble

**Purpose**: Combine the Bayesian posteriors, gradient boosting probabilities, and a logistic regression baseline into a final calibrated probability estimate.

**Implementation**: Following the CFA paper's key insight, use **rank-based fusion** rather than simple probability averaging. Rank-based fusion normalizes for different models having different probability scales and confidence patterns.

**Components**:

1. **Bayesian posterior win probabilities**: Derived from sampling the posterior predictive distribution of the Layer 1 model. For each potential matchup, draw from the posterior distributions of both teams' offensive and defensive strengths, compute expected scores, and determine win probability across thousands of posterior samples.

2. **XGBoost calibrated probabilities**: From Layer 2.

3. **Logistic regression on rating differentials**: A deliberately simple model using only KenPom AdjEM difference and seed difference. This serves as a "cognitive diversity" component -- its errors will be in different places than the tree-based or Bayesian models.

**Fusion method**:
- Convert each model's probabilities to rankings across all possible matchups.
- Compute cognitive diversity between model pairs using the CFA rank-score characteristic function.
- Weight models by a combination of historical performance and diversity contribution.
- Convert fused ranks back to probabilities via isotonic calibration against historical tournament outcomes.

**Why this matters**: The CFA paper showed 1.58% accuracy improvement over the best individual model. With only ~67 games per tournament, every percentage point matters. The diversity of model types (generative Bayesian, discriminative tree-based, linear) maximizes the "cognitive diversity" that CFA leverages.

### Layer 4: GPU-Accelerated Monte Carlo Tournament Simulation

**Purpose**: Propagate uncertainty from individual game probabilities through the bracket structure to compute round-by-round advancement probabilities.

**Implementation**: CUDA-accelerated via NumPy/CuPy or JAX, targeting **100,000+ simulations** (Silver's current standard; academic papers using 100 simulations are grossly insufficient).

**Simulation protocol**:

For each simulation:
1. For every first-round matchup, draw a game outcome using the ensemble win probability from Layer 3 as the Bernoulli parameter.
2. Advance winners and repeat for subsequent rounds.
3. **Dynamic rating update** (following the Unabated approach): After each simulated round, update team ratings based on performance relative to expectation. A team that dramatically outperforms expectations in Round 1 should have increased probability in Round 2. The update formula: `rating_diff = B1 * (actual_margin - expected_margin) + B2 * (actual_margin - expected_margin) * ln(game_number)`, sampled from a normal distribution centered on the regression estimate.
4. Track which teams advance to each round across all simulations.

**Score modeling**: Rather than simple Bernoulli win/loss draws, sample actual score differentials from a **t-distribution** (heavier tails than Normal, better capturing extreme outcomes). Use the Bayesian posterior's uncertainty to parameterize the spread. COOPER's insight about pace-adjusted variance applies here: an 85-75 expected game has different upset probability than a 65-55 expected game at the same margin.

**Parallelization**: Tournament simulations are embarrassingly parallel -- each simulation is independent. On a modern GPU, 100,000 simulations should complete in seconds.

**Output**: For every team, probability of advancing to each round (Round of 32, Sweet 16, Elite 8, Final Four, Championship, Winner). These are the core deliverables for bracket construction.

### Layer 5: Bracket Optimization Given Pool Parameters

**Purpose**: Translate advancement probabilities into an optimal bracket that maximizes expected pool-winning probability, not just expected score.

**Implementation**: Custom optimizer that processes five variables simultaneously (following PoolGenius methodology):

1. **Pool size**: The primary strategic variable.
   - Small pools (<10): Go chalk. Let opponents self-destruct.
   - Mid-size pools (25-100): Balance risk and value. Concentrate risk in one area.
   - Large pools (100+): Maximize leverage against public pick distribution.

2. **Scoring system**: Standard doubling (1-2-4-8-16-32) makes champion selection worth 32 first-round picks. Flat or upset-bonus scoring changes the calculus entirely.

3. **Public pick distribution**: Scrape or estimate ownership percentages from ESPN, Yahoo, CBS bracket platforms. The "leverage" concept is central: `value = advancement_probability - public_pick_rate`. Positive leverage = underowned team.

4. **Team advancement probabilities**: From Layer 4.

5. **Risk allocation**: The optimizer distributes risk across all 67 picks, concentrating contrarian bets where leverage is greatest.

**Key insight from the literature**: #1 seeds are "massively overselected" as champions relative to their actual title probability. This is the single most exploitable inefficiency in typical bracket pools. Strong 2- or 3-seeds with lower public selection rates often provide better expected value.

---

## 5. Evaluation Strategy

### Primary Metrics

| Metric | Purpose | Target |
|--------|---------|--------|
| **Brier Score** | Primary calibration-aware metric; Kaggle standard since 2023 | < 0.185 (competitive with Odds Gods); < 0.170 (top Kaggle tier) |
| **Log Loss** | Secondary; more sensitive to confident errors | < 0.50 (strong); < 0.43 (Kaggle winning range) |
| **Accuracy** | Sanity check only (not a primary optimization target) | > 74% on tournament games |
| **Calibration Plot** | Visual diagnostic -- always produce and inspect | Points should follow the diagonal |
| **ECE (Expected Calibration Error)** | Quantifies calibration quality | < 5% (good); < 3% (excellent, per LSTM paper) |

### Temporal Cross-Validation Protocol

**Expanding-window CV** is the gold standard, as confirmed by Kaggle gold solutions and the systematic review of sports ML literature:

```
Fold 1: Train on 2003-2014, Test on 2015 tournament
Fold 2: Train on 2003-2015, Test on 2016 tournament
Fold 3: Train on 2003-2016, Test on 2017 tournament
...
Fold 9: Train on 2003-2023, Test on 2024 tournament
Fold 10: Train on 2003-2024, Test on 2025 tournament
```

- Skip 2020 (cancelled tournament).
- Flag 2021 as a structural break (COVID bubble tournament, no travel effects, empty/limited arenas).
- Feature selection must occur *inside* each CV fold to prevent selection bias.

### Benchmarks

Every model evaluation should compare against:

1. **Chalk baseline**: Always pick the higher seed. ~72-75% accuracy. If your model cannot beat this, it is not adding value.
2. **Seed-based probability baseline**: Assign win probabilities from historical seed matchup frequencies. Log loss ~0.55-0.58.
3. **KenPom AdjEM logistic regression**: Single-feature baseline. ~73-74% accuracy.
4. **Vegas closing line implied probabilities**: The hardest benchmark. If you cannot beat the closing line, your model has no betting edge (though it may still be useful for bracket pools).

### Backtest Protocol

Run the full pipeline (Bayesian model fitting, XGBoost training, ensemble calibration, tournament simulation, bracket optimization) on every tournament from 2015 through 2025. Track:

- Game-level Brier score and log loss per year.
- Bracket scoring under standard 1-2-4-8-16-32 format.
- Calibration plots per year and aggregated.
- Whether optimized brackets would have won various pool sizes (simulate against public pick distributions).

### Brier Score Decomposition

Decompose the Brier score into three components to diagnose where the model fails:
- **Reliability** (calibration): How well do predicted probabilities match observed frequencies?
- **Resolution** (discrimination): How much do predictions differ from the base rate?
- **Uncertainty** (inherent): How unpredictable are the outcomes themselves?

This decomposition, recommended by the sports ML systematic review, is more informative than the raw score alone.

---

## 6. What NOT to Do: Lessons from the Literature

### Do Not Chase Accuracy Over Calibration

The single most important lesson. Accuracy-driven models are systematically overconfident, and overconfidence is catastrophic under both log loss (unbounded penalty) and Brier score. A model that says 0.95 and is wrong destroys an entire submission. The 2014 Kaggle winners estimated that even an optimal model had at best a 50-50 chance of finishing in the top 10 due to randomness.

### Do Not Build Homogeneous Ensembles

Combining XGBoost + LightGBM + CatBoost -- three flavors of the same gradient boosting idea -- performed *worse* than a single tuned XGBoost in the 2025 Kaggle rank-107 solution. Diversity across model families (Bayesian + trees + linear) is what creates value.

### Do Not Overfit to Historical Tournaments

With only ~63-67 games per tournament and high variance, it is trivially easy to overfit. A model that "learns" to predict Virginia's 2018 loss to UMBC is learning noise, not signal. Regularize aggressively, keep feature sets parsimonious (the literature shows 4-26 features suffice), and always evaluate across multiple tournament years.

### Do Not Ignore the Role of Luck

The 2014 Kaggle winners, the 2015 winner, and the 2017 winner all explicitly stated that luck was a dominant factor. UConn winning as a 7-seed in 2014, UMBC beating Virginia in 2018, Saint Peter's reaching the Elite Eight in 2022 -- these events are not predictable and will tank even well-calibrated models. Accept this. Design the system to be robust to bad luck, not to avoid it.

### Do Not Use Standard K-Fold Cross-Validation

Standard k-fold CV mixes data from different years, allowing future information to leak into training. This produces inflated performance estimates that do not generalize. Always use temporal CV (expanding window or leave-one-season-out).

### Do Not Neglect the Women's Tournament

Since 2023, the Kaggle competition combines men's and women's brackets. The women's tournament has significantly fewer upsets (FiveThirtyEight's best women's Brier score was 0.107 vs. ~0.18-0.21 for men's), requiring different calibration. Build separate models or at minimum include a gender indicator feature.

### Do Not Model Four Factor Matchups

Jordan Sperber's research showed that team-level Four Factor matchups "do not help in predicting the outcome of a college basketball game." Even when one team excels in a specific factor while the opponent is weak in the corresponding defensive category, overall adjusted efficiency ratings remain equally predictive. Use the Four Factors as general quality indicators, not for matchup-specific analysis.

### Do Not Treat Tempo as Predictive of Success

Champions averaged rank ~134 in adjusted tempo; 6 of 24 champions ranked 200th or worse. The "slow tempo aids upsets" theory is empirically refuted -- the Harvard study found faster-paced games were associated with MORE upsets, and Gasaway found essentially zero correlation (+0.09) between pace and tournament performance. Use tempo for score prediction, not win prediction.

### Do Not Ignore Data Quality

Team name inconsistencies across sources, conference realignment, COVID season effects, overtime stat inflation, play-by-play tracker errors, and missing data for newer metrics (NET pre-2019) can all silently corrupt models. The data quality pipeline described in Section 2 is not optional.

---

## 7. Timeline and Milestones

This phasing assumes work starts approximately 4-6 weeks before the tournament. Adjust based on actual start date.

### Phase 1: Data Foundation (Week 1-2)

**Deliverables**:
- Download and ingest all Kaggle March ML Mania data.
- Pull Bart Torvik data via `toRvik` R package (or scrape); pull KenPom data via `kenpompy` or `cbbdata`.
- Build master team ID mapping table across all sources.
- Implement tempo-free normalization pipeline.
- Flag COVID-affected observations and handle structural breaks.
- Construct feature matrix with all Tier 1-4 features from Section 3.
- Verify no data leakage via the checklist in Section 2.

**Milestone**: Clean, unified feature matrix covering 2003-present with all features computed as team-A-minus-team-B differences, ready for modeling.

### Phase 2: Bayesian Model (Week 2-3)

**Deliverables**:
- Implement hierarchical Bayesian model in PyMC v5 with JAX backend.
- Validate on synthetic data (known true parameters; verify recovery).
- Fit on historical seasons; inspect forest plots of posterior distributions.
- Extend with time-varying strength component if time permits.
- Generate posterior predictive win probabilities for historical tournament matchups.

**Milestone**: Bayesian model producing posterior distributions over team strength with Brier score competitive with seed-based baseline on held-out tournaments.

### Phase 3: Gradient Boosting + Ensemble (Week 3-4)

**Deliverables**:
- Train XGBoost with leave-one-season-out CV on the full feature matrix.
- Perform RFECV-based feature selection inside CV folds.
- Calibrate via isotonic regression on out-of-fold predictions.
- Implement logistic regression baseline on KenPom AdjEM + seed.
- Build CFA-style rank-based fusion ensemble combining all three models.
- Evaluate ensemble Brier score against individual models and benchmarks.

**Milestone**: Calibrated ensemble producing per-matchup win probabilities that beat seed-based and KenPom-only baselines on expanding-window CV.

### Phase 4: Simulation + Optimization (Week 4-5)

**Deliverables**:
- Implement GPU-accelerated Monte Carlo tournament simulator.
- Run 100,000+ simulations using ensemble probabilities.
- Implement dynamic rating updates between simulated rounds.
- Generate round-by-round advancement probabilities for all 68 teams.
- Build bracket optimizer that accepts pool size, scoring system, and public pick distribution.
- Backtest on 2015-2025 tournaments.

**Milestone**: Full pipeline from data ingestion through optimized bracket output. Backtest shows improvement over chalk baseline and seed-based simulation.

### Phase 5: Tournament Deployment (Tournament Week)

**Deliverables**:
- Run final model with current-year data once the bracket is announced.
- Generate advancement probabilities and optimized brackets for different pool configurations.
- Optionally: update predictions between rounds using actual tournament results (Silver's "hot" model approach).

**Milestone**: Brackets submitted; data logged for post-tournament analysis.

### Phase 6: Post-Tournament Analysis (After Tournament)

**Deliverables**:
- Evaluate actual performance vs. predictions.
- Calibration analysis: did 70% predictions win 70% of the time?
- Compare against Vegas closing lines and public models.
- Document what worked, what did not, and what to change for next year.
- Add 2026 tournament data to the training set.

**Milestone**: Written retrospective with specific, actionable improvements for the next season.

---

## Appendix: Key Quantitative Benchmarks from the Literature

| Metric | Baseline | Competitive | Elite |
|--------|----------|-------------|-------|
| Game-level accuracy | 72-73% (seed/chalk) | 74-75% | 77%+ (tournament-specific) |
| Brier score | 0.25 (coin flip) | 0.185-0.195 | < 0.170 |
| Log loss | 0.693 (coin flip) | 0.50-0.55 | < 0.43 |
| Calibration (ECE) | -- | < 5% | < 3% |
| Bracket points (1-2-4-8-16-32) | ~100 (average public) | ~120 (chalk) | ~130+ (optimized) |

| Reference Model | Accuracy | Notes |
|----------------|----------|-------|
| Always pick higher seed | ~72-75% | The benchmark to beat |
| KenPom logistic regression | ~73-74% | Strong single-feature baseline |
| FiveThirtyEight composite | ~70% | With calibration and adjustments |
| Odds Gods LightGBM | 77.6% tournament | Multi-system ensemble |
| Kaggle winning entries | -- | Brier 0.18-0.22; log loss 0.41-0.43 |
| CFA rank fusion ensemble | 74.6% | Diverse model types |
| LSTM (Brier loss) | 72.8% | Best calibration (ECE 3.2%) |
| Transformer (BCE loss) | 73.6% | Best discrimination (AUC 0.847) |
| Vegas closing line | ~73-74% | The hardest benchmark |
