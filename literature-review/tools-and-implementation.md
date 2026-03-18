# Tools and Implementation

This chapter synthesizes the practical tooling landscape for building a March Madness bracket prediction system. It covers the Python ecosystem for data acquisition, modeling, and simulation, drawing on patterns observed across dozens of open-source projects, Kaggle competition solutions, and applied analytics blog posts. For the statistical and strategic foundations that inform tool selection, see [Modeling Approaches](modeling-approaches.md), [Data Sources & Quality](data-sources-and-quality.md), [Feature Engineering & Metrics](features-and-metrics.md), and [Recommended Approach](recommended-approach.md).

---

## 1. Python Ecosystem Overview

The Python ecosystem for March Madness prediction is mature. Across the projects surveyed, a remarkably consistent core stack emerges:

- **pandas** and **NumPy** for data wrangling and numerical computation (universal across every project reviewed)
- **scikit-learn** for classical ML models, preprocessing, cross-validation, and evaluation metrics
- **XGBoost** (and increasingly **LightGBM**) for gradient-boosted trees, which consistently rank as the top-performing model family
- **Matplotlib** and **Seaborn** for visualization and exploratory analysis
- **Jupyter Notebook** as the primary development environment for iterative exploration

This stack handles the full pipeline from data ingestion to prediction output. More specialized tools layer on top for specific needs: **PyMC** for Bayesian modeling, **PyTorch** or **TensorFlow** for deep learning, and various scraping libraries for data acquisition.

The key insight from the literature is that the Python tooling is not the bottleneck. Feature engineering and data quality decisions dominate model performance far more than framework choice. A practitioner who invests time in computing opponent-adjusted efficiency metrics using pandas will outperform one who reaches for a deep learning framework but feeds it raw box scores.

---

## 2. Data Acquisition Libraries

Data acquisition is where the tooling landscape is most fragmented. Multiple libraries exist, each wrapping a different upstream source, and choosing the right combination matters for both data quality and pipeline reliability.

### Kaggle Datasets

The Kaggle March Machine Learning Mania competition ships approximately 35 CSV files covering team identifiers, tournament seeds, regular-season and tournament game results, detailed box scores, conference affiliations, geographic data, coaching records, and Massey ordinals (composite rankings from 100+ systems). This dataset is the de facto starting point for nearly every project reviewed. It is clean, well-documented, and updated annually.

For pipeline purposes, Kaggle data requires only `pandas.read_csv()` -- no API keys, no authentication, no rate limits. The main operational consideration is downloading fresh data each season and verifying column-name consistency across years.

### CBBpy

[CBBpy](https://pypi.org/project/CBBpy/) scrapes ESPN for NCAA Division I basketball data, including play-by-play records, boxscores, game metadata, and player information. It supports both men's and women's basketball and uses ESPN game IDs as the primary identifier. CBBpy is the closest Python equivalent to the R package `ncaahoopR`, which powers much of the R-based play-by-play analytics ecosystem.

CBBpy is the best option when you need event-level data (individual plays, shot locations, assist networks) that Kaggle's aggregated CSVs do not provide. Its main limitation is that it inherits ESPN's coverage patterns -- major-conference games have richer data than mid-major or low-major games, which creates systematic missingness that matters for March Madness prediction since Cinderella teams often come from thinly covered conferences.

### sportsipy

[sportsipy](https://sportsreference.readthedocs.io/en/stable/) (formerly `sportsreference`) wraps Sports Reference's website, providing programmatic access to boxscores, schedules, rankings, team statistics, and conference data. Its NCAAB module allows calls like `Schedule('purdue')` to iterate through a team's games.

The critical caveat is that Sports Reference enforces aggressive anti-scraping policies: a 20-requests-per-minute rate limit, with IP bans lasting up to a day for violations. Their terms of service explicitly prohibit automated scraping and use of data for AI model training. sportsipy should be used sparingly for spot-checks and historical research rather than as a primary pipeline data source.

### cbbd (CollegeBasketballData.com API)

The `cbbd` Python package wraps the CollegeBasketballData.com REST API, providing a clean interface for team statistics, game results, and advanced metrics. It was featured in the CollegeFootballData blog's XGBoost tutorial, which pulled 686 NCAA tournament games (2013--2024) with 25 features per team including offensive/defensive ratings, pace, and the four factors.

The cbbd API's key advantage is that it handles regular-season vs. postseason filtering natively, which directly addresses the data leakage problem described in [Data Sources & Quality](data-sources-and-quality.md). It returns many more features than most projects use, leaving room for feature expansion.

### basketball-reference-scraper

An alternative to sportsipy for scraping Basketball Reference directly. Subject to the same rate limits and terms-of-service constraints.

### R Ecosystem (for Reference)

The richest play-by-play and advanced metrics ecosystem lives in R, not Python. The key packages are:

- **hoopR**: ESPN play-by-play and box scores with 36+ functions; part of the SportsDataverse
- **gamezoneR**: STATS LLC shot location data (170,000+ charted shots per season, back to 2017--18)
- **ncaahoopR**: ESPN play-by-play with win probability models and game-flow visualizations
- **bigballR**: NCAA official play-by-play with lineup analysis capabilities
- **cbbdata / toRvik**: Unified access to Bart Torvik, KenPom, and NET data, updating every 15 minutes during the season

For a Python-first project, the practical approach is to use R packages for one-time data extraction (writing to CSV or Parquet), then bring that data into the Python pipeline for modeling. Alternatively, CBBpy covers the ESPN play-by-play niche in Python, and the cbbd API handles team-level advanced metrics.

### Recommended Acquisition Strategy

| Data Need | Primary Source | Backup Source |
|-----------|---------------|---------------|
| Historical game results and seeds | Kaggle March ML Mania | cbbd API |
| Advanced team metrics (efficiency, tempo) | cbbd API / Bart Torvik (via R) | KenPom (paid, $25/yr) |
| Composite rankings | Massey ordinals (in Kaggle data) | Direct from masseyratings.com |
| Play-by-play events | CBBpy (Python) or hoopR (R) | ncaahoopR (R) |
| Shot location data | gamezoneR (R) | ShotQuality (paid) |

---

## 3. Modeling Libraries

### scikit-learn

scikit-learn is the workhorse for classical ML in every project reviewed. Commonly used components include:

- **Models**: `LogisticRegression`, `RandomForestClassifier`, `GradientBoostingClassifier`, `KNeighborsClassifier`, `BaggingClassifier`
- **Preprocessing**: `StandardScaler`, `train_test_split`, feature selection via `RFE` (recursive feature elimination)
- **Evaluation**: `log_loss`, `brier_score_loss`, `accuracy_score`, `roc_auc_score`, classification reports
- **Tuning**: `RandomizedSearchCV`, `GridSearchCV`, cross-validation utilities

A finding that recurs across projects is that logistic regression -- the simplest scikit-learn classifier -- is surprisingly competitive. Paul Lindquist's comparison of six models found logistic regression yielded the most consistent accuracy with the lowest standard deviation. Multiple Kaggle winners used logistic regression as their primary or only model. This is not because logistic regression is the best possible model; it is because the problem's noise floor is high enough that the variance reduction from a simpler model often outweighs the bias reduction from a more complex one.

### XGBoost

XGBoost is the single most common model in top-performing projects. Adit Deshpande's project achieved 76.37% accuracy with gradient-boosted trees across 100 train/test splits. The Kumar et al. multi-model comparison found gradient boosting at 84.1% accuracy and 0.409 log loss, substantially outperforming all other approaches. The 2025 Kaggle rank-107 approach used a single XGBoost model with Optuna hyperparameter tuning, explicitly reporting that it outperformed LightGBM, CatBoost, and MLP alternatives.

XGBoost is typically used in one of two modes:
- **`XGBClassifier`** for binary win/loss prediction
- **`XGBRegressor`** for point-margin prediction (which provides richer output and can be converted to win probabilities)

The cbbd/XGBoost tutorial used the regression approach, predicting point margin with a validation MAE of ~7.97 points and 64.3% tournament accuracy. The regression framing is worth considering because point-margin predictions naturally encode confidence -- a predicted margin of +15 implies higher certainty than +2.

### LightGBM

LightGBM appears in fewer projects than XGBoost but has a notable advantage: it handles missing values natively. The Odds Gods methodology blog explicitly chose LightGBM because NET ratings (introduced 2019) have 39% missing values across the full 2003--2026 dataset. Rather than imputing, they let LightGBM's built-in missing-value handling manage the problem, shifting the burden from preprocessing to the algorithm.

LightGBM is also faster to train than XGBoost on larger datasets, though for the dataset sizes typical of March Madness prediction (hundreds to low thousands of games), training speed is rarely the bottleneck.

### PyMC (Bayesian Modeling)

PyMC offers a fundamentally different approach from the discriminative models above. The Barnes Analytics project demonstrated a hierarchical Bayesian model where:

- Each team has offensive and defensive strength parameters drawn from hierarchical Normal priors
- Game scores are modeled as Poisson-distributed with intensity depending on the matchup
- Posterior sampling (1,000 iterations with 1,000 tuning steps) produces full probability distributions over outcomes

The Bayesian approach's advantages for bracket prediction are substantial and distinct from what gradient boosting provides:

1. **Full uncertainty quantification**: Instead of a point estimate of "Team A wins with probability 0.72," you get a distribution over that probability, which matters for bracket optimization under different scoring systems.
2. **Hierarchical regularization**: Partial pooling means small-sample teams (mid-majors with fewer high-quality opponents) borrow strength from the population, reducing overfitting without ad hoc regularization.
3. **Counterfactual simulation**: The generative model can simulate any hypothetical matchup, including venue effects, which is exactly what bracket prediction requires.
4. **Principled probability calibration**: The model outputs are inherently probabilistic, avoiding the post-hoc calibration step that discriminative models require.

PyMC (now at v5+, using PyTensor instead of the older Theano backend) supports discrete variables and non-gradient-based samplers, unlike Stan. For a project that values uncertainty quantification and bracket-optimization (as opposed to raw game-level accuracy), PyMC is the most natural fit. See [Modeling Approaches](modeling-approaches.md) for a deeper comparison of Bayesian vs. frequentist frameworks.

### Stan (via PyStan or CmdStanPy)

Stan is an alternative to PyMC for Bayesian modeling, using Hamiltonian Monte Carlo (HMC) sampling. It is generally faster than PyMC for large hierarchical models and has a more mature diagnostic ecosystem. The tradeoff is that Stan uses its own modeling language rather than Python-native syntax, and it does not support discrete latent variables (requiring marginalization instead).

For this project, PyMC is likely the better choice unless performance on large hierarchical models becomes a bottleneck, because the Python-native interface reduces development friction.

---

## 4. Deep Learning Frameworks

### When Deep Learning Is and Is Not Worth the Complexity

The literature is clear on this point: **deep learning is generally overkill for March Madness prediction at the team level.** The dataset sizes involved (hundreds to low thousands of tournament games, a few thousand regular-season games per year) are far too small for deep architectures to learn meaningful representations that simpler models cannot capture.

The Kumar et al. comparison found neural networks achieved 76.2% accuracy with 0.612 log loss -- substantially worse than gradient boosting (84.1% accuracy, 0.409 log loss) on the same features. The 2025 Kaggle rank-107 approach explicitly reported that an ensemble including neural networks performed worse than a single XGBoost model. Multiple Kaggle winners have noted that simpler models win.

An arXiv preprint on LSTM and Transformer models for NCAA prediction represents the deep learning frontier, using sequence models to capture temporal dynamics across a season. This is a legitimate use case -- modeling momentum and form changes over time is something that static feature vectors cannot capture -- but it requires careful handling of missing data, overtime normalization, and temporal train/test splits that add significant implementation complexity.

### Where Deep Learning May Add Value

There are specific niches where deep learning's representational capacity is justified:

1. **Player embeddings**: Learning dense vector representations of individual players from play-by-play data, capturing intangible contributions (spacing, screen-setting, defensive positioning) that box scores miss. This requires player-level event data (from CBBpy or hoopR) and a model architecture that aggregates player embeddings into team-level predictions.

2. **Shot-quality models**: ShotQuality uses neural networks with ~100 input variables (player positions, defender distances, play type) to predict individual shot probabilities. This is a domain where the input dimensionality and nonlinear interactions genuinely benefit from deep architectures.

3. **Play-type classification**: Stats Perform's Sloan 2020 paper used neural network classifiers to detect postups, drives, isolations, ball-screens, and other play types from tracking data (achieving 0.8 recall, 0.7 precision). Play-type decomposition enables features that static models cannot derive.

4. **Temporal sequence modeling**: LSTM or Transformer architectures modeling a team's game-by-game trajectory through a season, capturing momentum and form changes. The value here is encoding *when* stats occurred, not just their averages.

### Framework Choice: PyTorch vs. TensorFlow

If deep learning is pursued, **PyTorch** is the more natural choice for a research-oriented project. Its imperative execution model makes debugging straightforward, the research community has largely converged on it, and it integrates well with the rest of the Python scientific stack. TensorFlow/Keras remains viable and has a gentler learning curve for standard architectures, but offers less flexibility for custom model components.

---

## 5. Data Pipeline Architecture

The projects reviewed converge on a five-stage pipeline. The architecture below synthesizes best practices from across the literature.

### Stage 1: Data Acquisition (Scraping / API Calls / Downloads)

**Input**: Raw data from multiple sources (Kaggle CSVs, API responses, scraped pages).

**Key operations**:
- Download Kaggle competition data (annual refresh)
- Pull advanced metrics via cbbd API or R-based cbbdata/toRvik
- Optionally extract play-by-play data via CBBpy or hoopR
- Build a **master team ID mapping table** across all sources before any joins -- team naming conventions differ between sources ("UConn" vs. "Connecticut" vs. "University of Connecticut")

**Output**: Raw data files in a standardized directory structure.

### Stage 2: Cleaning and Quality Assurance

**Input**: Raw data files.

**Key operations**:
- Replace empty strings/spaces with NaN
- Remove duplicates across merged datasets
- Normalize overtime game statistics to 40-minute equivalents
- Flag or segment COVID-affected data (2020--21 season) rather than treating it as normal -- elite teams showed performance drops of 6--10+ points after COVID pauses
- Handle the 2020 tournament gap explicitly (cancelled tournament creates a structural break)
- Track conference membership by season to correctly compute conference-level features despite realignment
- Verify no tournament outcome information has leaked into pre-game features (see the data leakage checklist in [Data Sources & Quality](data-sources-and-quality.md))

**Output**: Cleaned, temporally consistent datasets with documented quality flags.

### Stage 3: Feature Engineering

**Input**: Cleaned datasets.

**Key operations**:
- Compute per-100-possessions efficiency metrics using a consistent possession formula: `POSS = FGA - OREB + TO + 0.475 * FTA`
- Calculate the four factors: eFG%, turnover rate, offensive rebound rate, free throw rate
- Derive opponent-adjusted metrics (iterative adjustment for opponent quality, a la KenPom)
- Weight recent games more heavily (Bart Torvik uses a 40-day decay window)
- Construct matchup feature vectors as the **difference** between two team feature vectors -- this is the universally adopted representation
- Apply data augmentation through perspective flipping (each game generates two training examples, one from each team's viewpoint)
- Remove team identifiers from features to prevent memorization of school-specific patterns
- Optionally: extract play-by-play features (lineup efficiency, transition rate, clutch performance, shot quality)

See [Feature Engineering & Metrics](features-and-metrics.md) for the detailed feature taxonomy.

**Output**: Feature matrices ready for modeling.

### Stage 4: Modeling

**Input**: Feature matrices with temporal train/test splits.

**Key operations**:
- Split data using leave-one-season-out cross-validation or expanding-window validation -- never random k-fold on shuffled data, which leaks future information
- Train candidate models (logistic regression as baseline, XGBoost as primary, optionally PyMC for Bayesian inference)
- Tune hyperparameters via `RandomizedSearchCV` or Optuna
- Calibrate predicted probabilities -- this is critical for bracket optimization. Options include Platt scaling, isotonic regression, or cubic-spline calibration (used by the rank-107 Kaggle entry)
- Evaluate on held-out tournament years using the competition's metric (Brier score since 2023, log loss before that)

**Output**: Trained models producing calibrated win probabilities for any hypothetical matchup.

### Stage 5: Simulation and Bracket Generation

**Input**: Calibrated win probabilities for all possible matchups; the actual tournament bracket.

**Key operations**:
- Simulate the tournament thousands of times (Monte Carlo), sampling game outcomes from the predicted probability distributions
- For Bayesian models, sample from the posterior to incorporate parameter uncertainty into simulations
- Optimize the bracket for the target scoring system (e.g., ESPN standard scoring, which rewards correct picks in later rounds exponentially)
- Optionally implement strategic adjustments (picking a less-likely champion if the expected value under the scoring system justifies the risk)

**Output**: One or more bracket submissions optimized for expected score.

---

## 6. Key GitHub Repositories and Open-Source Projects

The following repositories represent the most instructive open-source implementations, ordered by pedagogical value:

| Repository | Author | Approach | Key Value |
|-----------|--------|----------|-----------|
| [March-Madness-ML](https://github.com/adeshpande3/March-Madness-ML) | Adit Deshpande | XGBoost, feature differencing, 76% accuracy | Well-documented end-to-end pipeline with blog walkthrough |
| [machine-learning-vs-march-madness](https://github.com/paul-lindquist/machine-learning-vs-march-madness) | Paul Lindquist | 6-model comparison, KenPom features | Clear demonstration that logistic regression matches complex models |
| [predicting-march-madness](https://github.com/sfirke/predicting-march-madness) | Sam Firke | R/tidyverse pipeline | Reproducible pipeline that achieved top-10% Kaggle finish |
| [ncaahoopR](https://github.com/lbenz730/ncaahoopR) | Luke Benz | Play-by-play infrastructure, win probability | Foundation for event-level feature engineering |
| [ncaa-predict](https://github.com/brendanlong/ncaa-predict) | Brendan Long | TensorFlow neural network | Reference implementation for deep learning approach |
| [Public-ESPN-API](https://github.com/pseudo-r/Public-ESPN-API) | Community | Undocumented ESPN API endpoints | Useful for programmatic ESPN data access |
| [ncaa-api](https://github.com/henrygd/ncaa-api) | henrygd | Free API wrapping ncaa.com | Scores, stats, standings, schedules |

The Kaggle competition itself hosts thousands of public notebooks, many of which demonstrate complete pipelines. The maze508 gold solution (2023) and the rank-107 approach (2025) are particularly instructive for understanding what works in practice.

---

## 7. GPU Utilization Opportunities

For most March Madness prediction work, GPU compute is unnecessary. Gradient-boosted trees (the dominant model family) train on CPU, and the dataset sizes are small enough that training completes in seconds to minutes. However, there are three specific areas where GPU acceleration provides meaningful benefit:

### Monte Carlo Bracket Simulation

Simulating tens of thousands of tournament brackets -- each requiring 63 game-outcome samples -- is embarrassingly parallel. On CPU, this is typically fast enough (seconds for 10,000 simulations with NumPy), but GPU-accelerated random number generation and parallel evaluation can scale to millions of simulations. This becomes valuable when:

- Optimizing bracket selections under complex scoring systems that require exhaustive search
- Running sensitivity analyses across many model parameterizations
- Sampling from Bayesian posterior distributions for each simulation

Libraries like **CuPy** (GPU-accelerated NumPy) or **JAX** (which PyMC can use as a backend) enable this without rewriting the core logic.

### Deep Learning (If Pursued)

Player embedding models, shot-quality models, and temporal sequence models (LSTM/Transformer) all benefit from GPU training. PyTorch's CUDA integration is straightforward. The practical question is whether the dataset size justifies the architectural complexity -- see section 4 above.

### Large-Scale Hyperparameter Search

Optuna or similar frameworks can run hundreds of XGBoost training runs in parallel across GPU-enabled workers. XGBoost itself supports GPU-accelerated tree construction via the `gpu_hist` tree method, which provides 2--10x speedups on moderately sized datasets. This is most useful during intensive hyperparameter tuning phases.

### Bayesian Posterior Sampling

PyMC can use JAX as its computation backend (via `numpyro`), enabling GPU-accelerated MCMC sampling. For hierarchical models with hundreds of team-level parameters (offensive and defensive strength for each of ~350 Division I teams), GPU sampling can reduce posterior computation from minutes to seconds. This is one of the more compelling GPU use cases for this specific project, since the Bayesian approach requires extensive sampling.

---

## 8. Recommended Tech Stack for This Project

Based on the literature review, the following stack balances capability, simplicity, and alignment with proven approaches.

### Core Stack

| Layer | Tool | Rationale |
|-------|------|-----------|
| **Data storage** | CSV/Parquet files | Simple, portable; no database needed for this data volume |
| **Data wrangling** | pandas, NumPy | Universal across all reviewed projects |
| **Visualization** | Matplotlib, Seaborn | Adequate for exploration and diagnostics |
| **Environment** | Jupyter Notebook + Python scripts | Notebooks for exploration, scripts for reproducible pipeline steps |
| **Package management** | pip + virtual environment (or conda) | Keep dependencies isolated |

### Data Acquisition

| Need | Tool |
|------|------|
| **Baseline data** | Kaggle March ML Mania CSVs |
| **Advanced metrics** | cbbd Python API (CollegeBasketballData.com) |
| **Play-by-play** (if needed) | CBBpy for Python-native access; hoopR via R for richer coverage |
| **Composite rankings** | Massey ordinals (included in Kaggle data) |

### Modeling (Tiered Approach)

The literature consistently shows that model complexity should be increased incrementally, with each tier justified by measured improvement over the previous one.

**Tier 1 -- Baseline (start here)**:
- Logistic regression (scikit-learn) using Massey ordinal rankings and seed differences as features
- This alone gets you to ~70% accuracy and competitive Kaggle scores (~0.54 log loss)

**Tier 2 -- Primary model**:
- XGBoost with efficiency metrics, four factors, and strength-of-schedule features
- Leave-one-season-out cross-validation
- Optuna for hyperparameter tuning
- Expected improvement to ~75% accuracy, ~0.41 log loss

**Tier 3 -- Bayesian inference (the distinctive capability)**:
- PyMC hierarchical model with team-level offensive/defensive strength parameters
- Full posterior distributions for uncertainty quantification
- Monte Carlo bracket simulation with posterior-sampled probabilities
- This tier does not necessarily improve single-game accuracy but enables bracket-level optimization that point-estimate models cannot

**Tier 4 -- Deep learning (only if justified)**:
- PyTorch for player embeddings or temporal sequence modeling
- Pursue only after Tiers 1--3 are established and measured

### What to Avoid

- **Building custom scrapers for Sports Reference**: The rate limits and terms of service make this fragile and legally questionable. Use Kaggle data, cbbd, or CBBpy instead.
- **Complex model ensembles as a first step**: Multiple Kaggle competitors report that XGBoost + LightGBM + CatBoost + neural network ensembles performed worse than a single tuned XGBoost. Start simple.
- **Investing in infrastructure before feature engineering**: Offensive/defensive efficiency difference is consistently the single strongest predictor. Computing it well matters more than any modeling decision.
- **Treating the 2020--21 season as normal training data**: COVID pauses caused performance drops of 6--10+ points for elite teams. This season requires special handling -- either down-weighting, segmenting, or explicit indicator variables. See [Data Sources & Quality](data-sources-and-quality.md) for details.

---

## Sources

- [March-Madness-ML (Adit Deshpande) -- GitHub](https://github.com/adeshpande3/March-Madness-ML)
- [Applying Machine Learning to March Madness (Adit Deshpande) -- Blog](https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness)
- [Talking Tech: March Madness with XGBoost -- CollegeFootballData Blog](https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/)
- [Predicting March Madness Winners with Bayesian Statistics in PyMC3 -- Barnes Analytics](https://barnesanalytics.com/predicting-march-madness-winners-with-bayesian-statistics-in-pymc3/)
- [March Madness 2025 Prediction -- Jonathan Marcu](https://jtmarcu.github.io/projects/march-madness.html)
- [Machine Learning vs. March Madness (Paul Lindquist) -- GitHub](https://github.com/paul-lindquist/machine-learning-vs-march-madness)
- [Top 1% Gold Kaggle March Mania 2023 Solution -- maze508](https://medium.com/@maze508/top-1-gold-kaggle-march-machine-learning-mania-2023-solution-writeup-2c0273a62a78)
- [March Machine Learning Mania Rank 107 Approach (2025) -- LinkedIn](https://www.linkedin.com/pulse/march-machine-learning-mania-2025-rank-107-approach-g13jf)
- [Predicting College Basketball: A Complete Technical Methodology -- Odds Gods](https://blog.oddsgods.net/predicting-college-basketball-methodology)
- [ncaahoopR (Luke Benz) -- GitHub](https://github.com/lbenz730/ncaahoopR)
- [ShotQuality Stats Explained](https://shotqualitybets.com/stats-explained)
- [EvanMiya Bayesian Performance Rating](https://blog.evanmiya.com/p/bayesian-performance-rating)
- [Predicting NBA Talent from College Basketball Tracking Data -- Sloan 2020](https://www.sloansportsconference.com/research-papers/predicting-nba-talent-from-enormous-amounts-of-college-basketball-tracking-data)
- [Kaggle March Machine Learning Mania 2025](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/data)
- [sportsipy Documentation](https://sportsreference.readthedocs.io/en/stable/)
- [CBBpy -- PyPI](https://pypi.org/project/CBBpy/)
- [cbbd API / CollegeBasketballData.com](https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/)
- [hoopR](https://hoopr.sportsdataverse.org)
- [gamezoneR](https://jacklich10.github.io/gamezoneR/)
- [cbbdata](https://cbbdata.aweatherman.com)
- [KenPom National Efficiency](https://kenpom.com/blog/national-efficiency/)
- [Forecasting NCAA Basketball Outcomes with Deep Learning -- arXiv](https://arxiv.org/html/2508.02725v1)
- [COVID Impact on College Basketball -- TeamRankings/PoolGenius](https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/covid-impact-basketball-college/)
