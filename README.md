# March Madness Bracket Prediction

A statistical inference system for predicting the NCAA Men's Basketball Tournament, combining Bayesian hierarchical modeling with gradient-boosted ensembles and Monte Carlo simulation.

## Results

Backtested on 669 tournament games across 10 seasons (2015–2025, excluding 2020):

| Model | Brier Score | Log Loss | Accuracy | ECE |
|-------|-----------|---------|----------|-----|
| Seed Baseline | 0.2135 | 0.648 | 70.4% | 0.117 |
| Feature Ensemble (LR + XGB) | 0.1917 | 0.564 | 71.0% | 0.034 |
| Bayesian Only | 0.1901 | 0.559 | 70.9% | 0.045 |
| **Full Ensemble (production)** | **0.1886** | **0.556** | **70.6%** | **0.024** |

A Brier score of 0.189 is competitive with top Kaggle March Machine Learning Mania entries (winners typically score 0.18–0.22). The ECE of 0.024 indicates excellent probability calibration — when the model says 70%, it's right about 70% of the time.

## Architecture

The system uses a five-layer architecture:

```
Layer 1: Bayesian Hierarchical Model (PyMC)
         └─ Estimates team offense/defense strength with uncertainty
         └─ ~350 teams, ~5500 games per season
         └─ NUTS sampling, 4 chains, 2000 draws

Layer 2: Feature-Based Ensemble (scikit-learn + XGBoost)
         ├─ Logistic Regression on standardized features
         └─ Calibrated XGBoost (Platt scaling)

Layer 3: Ensemble Fusion
         └─ 50/50 blend of Bayesian and feature-based models
         └─ Bayesian weight scaled by posterior uncertainty

Layer 4: Monte Carlo Tournament Simulation
         └─ 50,000 bracket simulations
         └─ Propagates game-level uncertainty through bracket structure

Layer 5: Bracket Generation
         └─ Round-by-round advancement probabilities
         └─ Championship odds for all 68 teams
```

## How It Works

### The Bayesian Model

The core innovation is a hierarchical Bayesian model that decomposes each team into offensive and defensive strength parameters. For every game in the regular season:

```
score_home ~ Normal(intercept + home_adv + offense[home] + defense[away], σ)
score_away ~ Normal(intercept + offense[away] + defense[home], σ)
```

This simultaneously estimates all 350+ teams' strengths from ~5,500 games, with automatic opponent-quality adjustment (playing a strong defense reduces your expected offense) and full uncertainty quantification. A team with 30 games has tighter posterior intervals than a team with 15 games — this uncertainty propagates naturally into tournament predictions.

### Feature Engineering

The feature-based models use team-stat differentials (Team A minus Team B):

- **Tier 1**: Opponent-adjusted offensive/defensive efficiency, seed
- **Tier 2**: Four Factors (eFG%, turnover rate, offensive rebound rate, free throw rate)
- **Tier 3**: Massey ordinal rankings from 8 systems (POM, SAG, MOR, DOL, COL, RTH, WOL, AP) plus composite
- **Additional**: Win percentage, scoring margin, consistency (efficiency std dev)

All features use pre-tournament data only (day ≤ 132) to prevent data leakage.

### Why an Ensemble?

A weight sweep over historical data found that a 50/50 blend of the Bayesian and feature-based models outperforms either alone:

- The **Bayesian model** excels at opponent-quality adjustment and uncertainty quantification, but uses only game scores (no box-score details).
- The **feature models** capture nuances like shooting efficiency, turnover rate, and composite ratings from 100+ external systems, but lack principled uncertainty.
- **Together**, they achieve the best Brier score (0.1886) and calibration (ECE 0.024) of any configuration tested.

## Quick Start

### Prerequisites

- Python 3.12+
- A [Kaggle account](https://www.kaggle.com/) with API credentials

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure Kaggle API

1. Go to https://www.kaggle.com/settings → API → Generate New Token
2. Save your token:
```bash
echo 'YOUR_TOKEN_HERE' > kaggle-token.txt
mkdir -p ~/.kaggle
key=$(cat kaggle-token.txt | tr -d '[:space:]')
echo "{\"username\":\"YOUR_USERNAME\",\"key\":\"$key\"}" > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Download Data

Accept the competition rules at https://www.kaggle.com/competitions/march-machine-learning-mania-2026/rules, then:

```bash
export KAGGLE_API_TOKEN=$(cat kaggle-token.txt | tr -d '[:space:]')
cd src && python data_acquisition.py
```

### Run the Full Pipeline

```bash
cd src && python full_pipeline.py
```

This will:
1. Train feature-based models on historical tournament data (2003–2025)
2. Fit the Bayesian hierarchical model for the target season (~30 seconds)
3. Build the ensemble probability function
4. Run 50,000 Monte Carlo tournament simulations
5. Output advancement probabilities and bracket recommendations

### Run the Backtest

```bash
cd src && python backtest.py
```

Evaluates the full pipeline on every tournament from 2015–2025 with proper temporal cross-validation (each year trained only on prior years). Takes ~7 minutes.

## Project Structure

```
march-madness/
├── src/
│   ├── data_loader.py        # Data loading, feature engineering, team stats
│   ├── pipeline.py            # Feature-based model training and evaluation
│   ├── bayesian_model.py      # PyMC hierarchical model
│   ├── simulate.py            # Monte Carlo tournament simulator
│   ├── full_pipeline.py       # Integrated 5-layer pipeline
│   ├── backtest.py            # Historical evaluation across 10 seasons
│   ├── weight_sweep.py        # Ensemble weight optimization
│   └── data_acquisition.py    # Kaggle data download
├── literature-review/
│   ├── index.md               # Literature review overview and bibliography
│   ├── modeling-approaches.md  # Survey of prediction methods
│   ├── data-sources-and-quality.md
│   ├── features-and-metrics.md
│   ├── tournament-dynamics.md
│   ├── evaluation-and-calibration.md
│   ├── bracket-strategy.md
│   ├── tools-and-implementation.md
│   ├── recommended-approach.md
│   └── braindump/             # 25 raw research files
├── data/                      # Downloaded data (gitignored)
├── requirements.txt
├── METHODOLOGY.md             # Detailed methodology documentation
└── README.md
```

## Process: How This Was Built

This project was built collaboratively between a human and Claude (Anthropic's AI), using Claude Code as the development environment. The process was:

### Phase 1: Literature Review (25 parallel research agents)

We started by dispatching 25 AI research agents in parallel, each investigating a different angle of March Madness prediction: logistic regression, ensemble methods, deep learning, Bayesian approaches, Elo ratings, feature engineering, data sources, Kaggle competition winners, FiveThirtyEight's methodology, upset prediction, Monte Carlo simulation, player analytics, tempo analysis, conference strength, historical seed performance, betting markets, play-by-play data, transfer portal effects, bracket optimization, coaching intangibles, advanced metrics systems, Python tooling, model evaluation, recent innovations, and data quality. Each agent searched the web, read sources, and produced a detailed markdown file.

A second wave of 9 synthesis agents then read all 25 research files and produced an interlinked literature review with a recommended approach document — covering 160+ unique sources.

**Key finding**: The literature converges on a ~74–75% accuracy ceiling regardless of method. The frontier is in calibration (making probabilities accurate), ensemble diversity (combining different model families), and feature engineering (opponent-adjusted efficiency metrics dominate).

### Phase 2: Implementation

We built the system iteratively:
1. Data pipeline with Kaggle integration
2. Feature engineering with opponent-quality adjustment and Four Factors
3. XGBoost + Logistic Regression ensemble with temporal cross-validation
4. Bayesian hierarchical model in PyMC
5. Monte Carlo tournament simulator
6. Full pipeline integration

### Phase 3: Review and Refinement

We dispatched multiple rounds of review agents examining:
- Code quality and Python best practices
- Data science methodology correctness
- Edge cases and potential bugs
- Alignment with literature review findings

This uncovered several critical issues:
- The Bayesian model had a scaling bug (`* sigma` outside `pm.Deterministic`) that made all posterior estimates incorrect
- Play-in games were silently dropped from the simulator
- Data leakage in the training pipeline when backtesting
- Final Four regional pairings used alphabetical sort instead of NCAA bracket structure

All were fixed, and the ensemble weight was tuned via a sweep over historical data (optimal: 50% Bayesian, 50% feature-based).

## Key Insights from the Literature

1. **The ~74–75% accuracy ceiling is real.** Every method — from logistic regression to transformers — converges on roughly the same game-level accuracy. About one quarter of tournament games are genuinely unpredictable.

2. **Calibration > accuracy.** A model that says "70%" and is right 70% of the time is more valuable than one that picks more winners but with poorly calibrated probabilities. Our ECE of 0.024 reflects this focus.

3. **Feature engineering > model complexity.** Adjusted efficiency margin (the #1 predictor) matters more than whether you use logistic regression or deep learning. All 24 national champions from 2001–2024 ranked in the top 25 of adjusted efficiency margin.

4. **Ensemble diversity matters.** Combining fundamentally different model families (generative Bayesian + discriminative gradient boosting + linear regression) outperforms ensembles of similar models (XGBoost + LightGBM + CatBoost).

5. **The betting market is the benchmark.** Closing lines are the single most accurate publicly available predictor. Our model adds value primarily through Bayesian uncertainty quantification and the diversity of its ensemble.

## Future Improvements

Based on the literature review, the highest-impact improvements for next season would be:

- **Training on regular season data** with sample weights (currently only tournament games)
- **Feeding Bayesian posteriors as XGBoost features** (BayesEM, BayesOff, BayesDef, BayesEM_std)
- **Adding late-season momentum features** (last-5, last-10 game performance)
- **Travel distance features** (teams traveling 150+ miles see 33.6% drop in winning odds)
- **Bracket optimization** for specific pool sizes and scoring systems (contrarian picks for large pools)
- **Iterative opponent adjustment** (KenPom-style convergence instead of our single-iteration approximation)

## License

This project is for educational and personal use.

## Data Sources

- [Kaggle March Machine Learning Mania](https://www.kaggle.com/competitions/march-machine-learning-mania-2026)
- [Massey Ratings](https://masseyratings.com/) (via Kaggle ordinals)
- Literature review covers 160+ sources — see `literature-review/index.md`
