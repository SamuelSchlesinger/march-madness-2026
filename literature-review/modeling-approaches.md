# Modeling Approaches for March Madness Prediction

## 1. Overview of the Modeling Landscape

Predicting NCAA tournament outcomes has attracted researchers and practitioners from statistics, machine learning, sports analytics, and betting markets for decades. The modeling landscape spans a wide methodological spectrum — from single-variable probit regressions on seed difference to Transformer-based deep learning architectures — yet a striking finding recurs across virtually all published work: **game-level prediction accuracy clusters around 73–75%, regardless of model complexity**. This ceiling appears to reflect irreducible randomness in single-elimination tournament play rather than a failure of methodology.

The approaches can be organized into six broad families:

1. **Classical statistical models** — logistic and probit regression on team-level features
2. **Rating systems** — Elo variants, efficiency-based systems (KenPom, T-Rank, BPI), and least-squares methods (Sagarin, Massey)
3. **Machine learning** — gradient boosting, random forests, and SVMs applied to feature-engineered team statistics
4. **Deep learning** — feedforward networks, LSTMs, Transformers, CNNs, and residual networks
5. **Bayesian methods** — hierarchical models, Bradley-Terry, and state-space formulations with full posterior inference
6. **Ensemble and composite approaches** — multi-system blends (FiveThirtyEight, COOPER, Combinatorial Fusion Analysis) that combine outputs from diverse models

Two principles cut across all families. First, **feature engineering matters more than model choice**: adjusted offensive and defensive efficiency per 100 possessions, computed as team-stat differences between opponents, emerge as the most predictive inputs in study after study (see [Feature Engineering & Metrics](features-and-metrics.md)). Second, **ensemble methods outperform individual models**, with the gains coming from diversity of model type rather than from combining many instances of the same approach.

The sections that follow synthesize findings from the primary literature on each family, identify where methods agree and diverge, and conclude with a comparative summary.

---

## 2. Classical Statistical Approaches

### Logistic Regression

Logistic regression is the workhorse of tournament prediction. A generalized linear model maps team-stat differences through the logit link function to produce win probabilities:

```
P(Team A wins) = 1 / (1 + exp(-(β₀ + Σ βᵢ · Xᵢ)))
```

where each Xᵢ is the difference between Team A and Team B on some statistic (efficiency, rebounding, shooting percentage, etc.).

A 2025 arXiv paper (arXiv:2503.21790) demonstrated that a logistic regression with just four predictors — Adjusted Offensive Efficiency, Adjusted Defensive Efficiency, Power Rating (BARTHAG), and Two-Point Shooting Percentage Allowed — achieves **74.6% test accuracy** on individual NCAA tournament games. This parsimonious model is competitive with far more complex alternatives, and its coefficients are directly interpretable as changes in log-odds per unit of feature difference.

Key design choices that improve logistic regression performance include:

- **Feature differencing**: Using stat differences (Team A minus Team B) rather than concatenated raw stats halves dimensionality while preserving the model's symmetry property — if input x gives probability p, then input −x gives 1−p.
- **L2 regularization**: Prevents overfitting on the relatively small tournament dataset (typically a few hundred games per year).
- **Feature selection**: Most published models converge on 4–6 features from KenPom-derived efficiency metrics as optimal; adding more features provides diminishing returns.

### LRMC: Logistic Regression / Markov Chain

The LRMC model, developed by Sokol and Kvam at Georgia Tech, is a distinctive two-stage classical approach. Stage 1 fits logistic regression on observed margins of victory to estimate pairwise neutral-court win probabilities. Stage 2 assembles these probabilities into a Markov chain transition matrix and iterates to a steady-state ranking vector. Teams that beat strong opponents rise; teams that beat weak opponents are penalized.

LRMC uses minimal data — only matchup, location, and final score — yet has historically picked the winner of more than **74% of tournament games** and outperforms RPI (less than 70%). The Markov chain component implicitly handles strength of schedule without requiring explicit adjustment, which makes the model resistant to overfitting. Three variants exist: Bayesian LRMC (empirical Bayes), Classic LRMC (standard logistic), and LRMC(0) (win/loss only, less accurate).

### Probit Regression on Seeds

The Boulier-Stekler probit model represents the simplest possible approach: it predicts outcomes using only the seed difference between teams, with a probit (normal CDF) link function. This baseline achieves **73.5% accuracy** across the first four rounds — a number that is surprisingly close to the ceiling achieved by complex models. However, accuracy degrades sharply by the Elite Eight, where seed differences shrink and the model performs no better than chance.

The probit and logit link functions produce nearly identical predictions in practice, with the logistic function's slightly heavier tails marginally better at capturing extreme upsets. Most practitioners prefer logistic regression because of the interpretability of odds ratios.

### Implications

Classical regression models establish that the core predictive signal in tournament outcomes is captured by a small number of efficiency-based features. They provide baselines that more complex methods must beat — and often don't by much. Their transparency and reproducibility make them natural starting points for any prediction pipeline (see [Recommended Approach](recommended-approach.md)).

---

## 3. Rating Systems

Rating systems assign a single number (or a small set of numbers) to each team, summarizing overall quality. They are the dominant paradigm in college basketball analytics and serve as both standalone predictors and input features for downstream models. For details on the underlying metrics, see [Feature Engineering & Metrics](features-and-metrics.md).

### Elo Rating Systems

**FiveThirtyEight Elo.** FiveThirtyEight maintained Elo ratings for college basketball dating back to the 1950s. Each team's rating updates after every game based on the surprise in the outcome: upsets produce larger updates than expected wins. Season-to-season, ratings revert toward the team's *conference* mean (not the global mean), capturing the idea that elite programs tend to stay elite. The win probability formula is:

```
P(win) = 1 / (1 + 10^(-rating_diff × 30.464 / 400))
```

Notably, FiveThirtyEight found that there are **fewer upsets in the tournament than expected from regular-season Elo differentials**, possibly due to neutral sites, higher-stakes preparation, and better officiating. This tournament-specific calibration improved their forecasts.

**COOPER (Nate Silver / Silver Bulletin).** COOPER, introduced in 2025–2026, extends Elo with several innovations:

- **Separate offensive/defensive ratings** (PPPG and PPAG), allowing matchup-level reasoning about scoring dynamics.
- **Bayesian updating that allows rating drops after wins**: if Duke barely beats a weak opponent, COOPER can lower Duke's rating, unlike traditional Elo where any win must increase the rating. This alone improves accuracy by approximately 1%.
- **Pace-adjusted variance modeling**: a team favored 90–80 in an uptempo game has different upset probability than a team favored 65–55 at the same margin, because more possessions introduce more variance.
- **Individualized home-court advantages** per venue and a travel distance effect following a cube-root formula.
- **Dynamic K-factor**: K=55 at baseline, escalating to K=110 for early-season games where results are more informative.

For tournament forecasting, Silver blends COOPER (5/8 weight) with KenPom (3/8 weight) and runs 100,000 bracket simulations.

**Custom Elo (Odds Gods).** A well-documented open implementation uses 15% season-to-season regression toward the mean, a three-phase K-factor (50 for first 5 games, 40 for games 5–19, 15 thereafter), and a 1.75× multiplier for cross-conference games. This Elo feeds into a LightGBM model alongside other features, achieving 72.56% overall accuracy and 77.61% on tournament games specifically.

### Efficiency-Based Systems

**KenPom.** Ken Pomeroy's system is the gold standard for college basketball analytics. Core metrics are Adjusted Offensive Efficiency (AdjOE), Adjusted Defensive Efficiency (AdjDE), and Adjusted Efficiency Margin (AdjEM = AdjOE − AdjDE), all measured per 100 possessions to remove the influence of tempo. Opponent adjustment is iterative: a team's efficiency is adjusted for opponent quality, which itself depends on adjusted ratings, creating a system of simultaneous equations solved by least squares across all 353+ D-I teams.

The ranking metric BARTHAG uses a Pythagorean formula with exponent 10.25 to convert efficiencies into expected win percentage against an average team:

```
BARTHAG = AdjOE^10.25 / (AdjOE^10.25 + AdjDE^10.25)
```

KenPom predicts correct winners approximately **73% of the time** overall, with finer-grained accuracy of 58.2% in games with projected margins of 5 points or fewer. KenPom-derived features appear as top predictors in virtually every published March Madness model, making it arguably the single most important data source in the ecosystem.

**Bart Torvik's T-Rank.** T-Rank uses the same efficiency-per-100-possessions framework as KenPom but diverges in three ways: (1) it maintains the *multiplicative* Pythagorean approach (exponent 11.5) while KenPom switched to additive post-2017; (2) it applies aggressive **recency weighting** — games older than 40 days lose weight at 1% per day, flooring at 60% after 80 days; and (3) it provides a **GameScript** metric derived from play-by-play data that filters garbage time. T-Rank's recency bias can capture late-season surges, making it theoretically appealing for March prediction, though it can also overreact to small recent samples. T-Rank reported **73.5% favorite accuracy** in 2018–19 with a 9.0-point mean absolute error. All data and tools are free.

**ESPN's Basketball Power Index (BPI).** BPI is a predictive power rating expressing how many points above or below average a team is on a neutral court. It differentiates itself through a sophisticated **preseason model** that integrates coaching history, recruiting class quality, returning player minutes, and returning player performance via Bayesian hierarchical modeling. Game predictions incorporate rest differential, travel distance, altitude, and crowd proximity. The BPI favorite has won **75.6% of games** since 2007–08, with strong calibration across probability buckets. BPI is proprietary and opaque.

**Haslametrics.** Erik Haslam's system uses play-by-play logs (available for 90%+ of games) rather than box scores, enabling garbage-time filtering by truncating data when games are mathematically decided. It also provides shot selection analysis (frequency, distance, defensive context). The play-by-play foundation gives it access to signal that box-score-only systems miss, though the interface is less polished.

**EvanMiya / Bayesian Performance Rating.** This system is unique in building from **player-level ratings** up to team ratings, using a Bayesian integration of box-score models and adjusted plus-minus from play-by-play data. A dynamic linear model projects player skills forward, adjusting for opponent strength, usage, and year-over-year development curves. The player-level granularity means EvanMiya can respond to roster changes (transfers, injuries) more naturally than team-level systems. Publicly available accuracy estimates suggest it outperforms team-level ensemble models by approximately 2%.

**ShotQuality.** Represents a frontier approach using computer vision and AI to extract shot-level data from game video — defensive distance, shooter ability, play type — to compute expected value for every shot. This enables "luck adjustment" at the shot level rather than the game level, potentially identifying regression candidates more precisely.

### Evaluation and Selection Tools

**NCAA NET Rankings.** The NET replaced RPI as the NCAA's official tournament selection tool before the 2018–19 season. It combines a Team Value Index (rewarding quality wins, especially on the road) with Adjusted Net Efficiency. Crucially, the NET **does not use margin of victory** — a deliberate design choice to avoid incentivizing running up scores. It defines the Quadrant system (Q1–Q4) that the selection committee uses. The NET is designed for selection, not prediction; models that use it as a predictive input are implicitly treating it as a noisy proxy for team quality.

**Sagarin Ratings (Historical).** Jeff Sagarin published ratings in USA Today from 1985 to 2023, combining a predictor (BLUE least-squares), golden mean, and recency-weighted component. Sagarin reported approximately **75% straight-up accuracy** and **53% against the spread**. However, KenPom outperformed Sagarin in tracked head-to-head comparisons (58.68% of 121 games, 2017–19). The system is now discontinued.

**Massey Ratings.** Kenneth Massey's least-squares system simultaneously solves for ratings that best explain observed margins. Massey's composite ranking — aggregating dozens of other systems — has historically been among the best-performing "systems" precisely because it benefits from ensemble effects.

### Comparative Accuracy of Rating Systems

| System | Approx. Game Accuracy | Key Differentiator |
|--------|----------------------|---------------------|
| KenPom | ~73% | Tempo-free efficiency; gold standard |
| T-Rank | ~73.5% | Recency weighting; GameScript |
| BPI | ~75.6% (favorite wins) | Preseason priors; travel/altitude |
| Sagarin | ~75% (self-reported) | Historical depth; now discontinued |
| LRMC | ~74% | Minimal data; Markov chain SOS |
| COOPER | ~1% over prior system | Bayesian updates; pace variance |
| EvanMiya | ~2% over team-level ensembles | Player-level Bayesian ratings |
| Vegas lines | ~73–74% | Market efficiency benchmark |

The systems largely agree on strong and weak teams, diverging primarily on: mid-major evaluation (where strength-of-schedule adjustment sensitivity matters most), teams with unusual tempo or style, and teams with recent roster changes. This divergence is exactly what makes them valuable as ensemble components.

---

## 4. Machine Learning Approaches

### Gradient Boosting and XGBoost

Gradient-boosted tree models (XGBoost, LightGBM) are the most consistently top-performing machine learning approach for tournament prediction. They excel at capturing nonlinear feature interactions — for example, the way offensive rebounding percentage interacts with opponent defensive rebounding to affect second-chance point expectations.

Reported accuracies across independent studies:

- **84.1% accuracy, 0.409 log loss** (Kumar et al., gradient boosting on 25 stat differentials, 2000–2019)
- **76.4% accuracy** (Deshpande, gradient boosted trees on 16-feature difference vectors, 1993–2016)
- **77.6% tournament accuracy** (Odds Gods, LightGBM with 1,545 trees using multiple rating systems as inputs, 2025)
- **64.3% accuracy** (CollegeBasketballData.com tutorial, XGBoost on 25 features, 2024 held-out test)

The wide range (64–84%) reflects differences in feature quality, evaluation methodology, and dataset construction more than differences in the algorithm itself. Studies using KenPom efficiency metrics or multiple rating systems as inputs consistently outperform those using raw box-score statistics.

### Random Forests

Random forests appear as a close second to gradient boosting in most comparative studies. Kumar et al. found random forests at 82.5% accuracy vs. gradient boosting at 84.1%; Lindquist found random forests competitive with XGBoost and logistic regression when using KenPom ratings as inputs. The random forest's advantage is stability (lower variance across cross-validation folds), while gradient boosting's advantage is the sequential error-correction mechanism.

### Key Findings from Machine Learning Studies

**Feature engineering dominates hyperparameter tuning.** The CollegeBasketballData.com tutorial found that hyperparameter optimization changed MAE from 7.97 to 7.98 — essentially no improvement. Multiple authors emphasize that adding better features provides far more lift than tweaking model parameters.

**Stat differentials are the correct input representation.** Subtracting Team B's statistics from Team A's (rather than concatenating both teams' raw stats) halves input dimensionality, enforces symmetry, and consistently improves accuracy.

**Log loss is the right evaluation metric.** Kaggle's March Machine Learning Mania competition uses log loss, with winning scores typically 0.41–0.43. Accuracy alone can be misleading because the real challenge is calibrating probabilities, not just picking winners. A model that assigns 51% probability to every favorite can achieve high accuracy while being nearly useless for bracket optimization (see [Evaluation & Calibration](evaluation-and-calibration.md)).

**Beating the seed baseline is the real bar.** Simply picking the higher seed wins approximately 72–76% of tournament games. Machine learning models must clear this bar to demonstrate value, and many do not by large margins.

For details on recommended features, see [Feature Engineering & Metrics](features-and-metrics.md). For implementation guidance, see [Tools & Implementation](tools-and-implementation.md).

---

## 5. Deep Learning Approaches

Deep learning has been applied to March Madness through feedforward networks, CNNs, LSTMs, Transformers, and residual networks. The literature delivers a humbling verdict: **deep learning rarely dominates simpler methods for this task**.

### When Deep Learning Helps

**Temporal modeling.** LSTMs and Transformers show promise for modeling team performance trajectories through a season. Habib (2025) found that Transformers achieve the best discriminative power (AUC 0.8473) through multi-head attention capturing feature interactions, while LSTMs trained with Brier loss produce the best-calibrated probabilities (Brier score 0.1589, ECE 3.2%). The choice of **loss function matters more than architecture** for calibration: Brier loss produces dramatically better-calibrated probabilities than binary cross-entropy, regardless of architecture.

**Ensemble diversity.** The CFA papers (Wu et al., 2026; Alfatemi et al., 2024) demonstrate that including a neural network alongside logistic regression and SVMs creates "cognitive diversity" that improves ensemble performance. The best CFA ensemble (logistic regression + SVM + CNN) achieved 74.60% accuracy — notably, it excluded XGBoost and random forest, suggesting that diversity of model type matters more than individual model strength.

**Upset detection.** A practitioner study (Adithya GV, 2022–2024) showed that statistically enriched neural networks better identify early-round upsets compared to seed-only models, and correctly predicted unlikely runs like Florida Atlantic's 2023 Final Four appearance. Getting a few early upsets right creates cascading scoring improvements in bracket pools.

### When Deep Learning Does Not Help

**Small data.** NCAA tournament history provides only ~60 games per year, with a few hundred games in typical training sets. Deep networks with hundreds of thousands of parameters are prone to overfitting on such small datasets.

**Feature-driven tasks.** When predictions are driven primarily by a handful of efficiency metrics, the representational capacity of deep networks offers no advantage. Kumar et al. found gradient boosting at 84.1% accuracy versus a neural network at 76.2% — and the neural network had *worse* log loss (0.612) than KNN (0.583), indicating poor probability calibration.

**No play-by-play or video data.** No study in the reviewed literature successfully applies deep learning to play-by-play sequences or game video for tournament prediction. This remains a frontier where deep learning's advantages in processing sequential and visual data could potentially unlock genuine gains.

### Summary

The most practical use of deep learning in March Madness prediction is as **one diverse voice in an ensemble**, not as a standalone predictor. For teams pursuing deep learning, LSTM architectures with Brier loss training and carefully engineered features (Elo, GLM quality metrics, efficiency differentials) represent the current best practice.

---

## 6. Bayesian Approaches

Bayesian methods treat team strengths as latent variables with uncertainty, update beliefs as new data arrives, and produce full probability distributions over outcomes rather than point estimates. This framework is naturally suited to tournament prediction, where quantifying uncertainty — not just picking winners — is essential for bracket optimization (see [Bracket Strategy & Optimization](bracket-strategy.md)).

### Bradley-Terry and Hierarchical Models

The **Bradley-Terry model** estimates a latent strength parameter for each team, with win probability given by the logistic function of the strength difference. It is mathematically equivalent to logistic regression on team-strength differences and serves as the canonical model for paired comparisons. In a Bayesian implementation (typically in Stan or PyMC), team strengths receive Normal(0, σ²) priors with σ learned from data via a hierarchical hyperprior.

**Hierarchical extensions** decompose team ability into offensive and defensive components:

```
E[Score_home] = Intercept + Home_Advantage + Offense_home + Defense_away
E[Score_away] = Intercept + Offense_away + Defense_home
```

The likelihood can be Poisson (treating scores as counts) or Normal (more appropriate for basketball, where scores have large means around 70 points). **Sum-to-zero constraints** on team ratings ensure identifiability. Inference proceeds via MCMC, typically NUTS (No-U-Turn Sampler) in PyMC or Stan.

Nelson (2012) demonstrated that Bayesian logistic regression using MCMC for both model selection and coefficient estimation matched KenPom and Sagarin accuracy on the 2012 tournament, with eight of his Bayesian models matching Pomeroy's system and four matching Sagarin's.

### State-Space Models

A **state-space formulation** treats team strength as a time-varying latent variable:

```
strength[t] = strength[t-1] + noise
```

This decomposes variability into between-season, within-season, and game-to-game components. Lopez et al. applied this to college basketball using betting market data (point spreads) as observed outcomes rather than raw scores, leveraging market efficiency to obtain high-signal observations. The framework is important for March Madness because teams that are improving or declining at season's end may be systematically under- or over-rated by static models.

### Practical Advantages of Bayesian Methods

1. **Uncertainty quantification.** Credible intervals on team strengths reveal which rankings are confident and which are uncertain — critical for identifying high-variance matchups. See [Evaluation & Calibration](evaluation-and-calibration.md).
2. **Natural regularization.** The hierarchical structure (team parameters drawn from a population distribution) provides automatic shrinkage, handling the unbalanced college basketball schedule where some teams face far stronger opponents than others.
3. **Counterfactual reasoning.** Posterior samples enable questions like "what if these teams played on a neutral court?" — exactly the scenario in NCAA tournament games.
4. **Propagating uncertainty through brackets.** Posterior predictive simulation generates bracket probabilities that account for parameter uncertainty, not just point-estimate win probabilities. See [Tournament Dynamics](tournament-dynamics.md).

### Practical Limitations

- **Computational cost.** MCMC inference takes minutes to hours, compared to seconds for logistic regression or gradient boosting.
- **Accuracy.** Bayesian methods typically achieve 67–74% game-level accuracy, comparable to but not exceeding frequentist alternatives. The advantage lies in richer output, not higher accuracy.
- **Priors matter less than structure.** With hundreds of games per season, weakly informative priors (Normal(0, large σ)) are sufficient; the data dominates. The real modeling choice is the hierarchical structure and likelihood specification.

---

## 7. Ensemble and Composite Approaches

The single most robust finding across the literature is that **blending diverse models outperforms any individual model**. This principle has been operationalized at multiple levels of sophistication.

### FiveThirtyEight (2011–2023)

FiveThirtyEight's model blended six computer rating systems (KenPom, Sagarin, LRMC, BPI, Sonny Moore, and FiveThirtyEight's own Elo) with two human-derived rankings (NCAA S-curve and preseason polls), weighting 75% computer and 25% human. All systems were normalized to the same mean and standard deviation before blending.

The rationale was explicitly ensemble-theoretic: "each system has different features and bugs, and blending them helps to smooth out any rough edges that matter because even small differences can compound over the course of a single-elimination tournament."

Post-aggregation adjustments included injury deductions (via Win Shares), travel distance effects, and in-tournament rating updates. The model achieved approximately 70% game-level accuracy and competitive Brier scores, with strong calibration (teams at 70% predicted probability won approximately 70% of the time).

A simplified replication using only seed and Sonny Moore's ratings achieved R² = 0.94 against the full model output, suggesting that much of the model's power comes from basic team quality, with the ensemble and adjustments providing important but marginal refinement.

### COOPER / Silver Bulletin (2025–2026)

Nate Silver's post-FiveThirtyEight system represents an evolution from broad ensemble (six systems) to narrower, higher-confidence blend: COOPER (5/8 weight) + KenPom (3/8 weight). COOPER's Bayesian updating, pace-adjusted variance, and individualized home-court advantages are described in Section 3 above. The infrastructure upgrade from Excel to proper simulation code (100,000 simulations) enables more sophisticated scenario modeling.

### Combinatorial Fusion Analysis (CFA)

Wu et al. (2026) introduced CFA to sports prediction — a framework that goes beyond simple averaging by measuring "cognitive diversity" between models using rank-score characteristic functions. CFA converts model outputs to ordinal ranks before combining, which normalizes for different models having different probability scales. The optimal ensemble (logistic regression + SVM + CNN) achieved **74.60% accuracy**, outperforming all ten major public ranking systems and all individual base models.

Key insight: **rank-based fusion outperforms score-based fusion** (74.60% vs. 71.43%), and the best ensemble deliberately combines structurally different model families to maximize diversity.

### TeamRankings Multi-Model Approach

TeamRankings runs six distinct models in parallel — predictive power ratings, similar-games matching, possession-based simulation, decision tree ensemble (~100 trees), Vegas-implied model, and seed-difference model — presenting each individually rather than collapsing them into a single number. This transparency allows users to see where models agree and disagree.

### Principles for Effective Ensembling

1. **Diversity of model type trumps number of models.** Combining logistic regression, SVM, and CNN outperformed combining five tree-based models.
2. **Rank combination over score combination.** Converting to ordinal ranks before merging is more robust than averaging probabilities.
3. **Include human/market signals.** FiveThirtyEight's 25% weight on human rankings reflects the finding that selection committees and polls encode injury, momentum, and context information that purely algorithmic models miss.
4. **Calibrate after combining.** Isotonic regression on out-of-fold predictions corrects overconfident probability extremes (the goto_conversion trick that has won multiple Kaggle medals).
5. **Weight toward tournament outcomes.** The Odds Gods model weights tournament games 6× more heavily than early-season games during training, deliberately prioritizing the target distribution.

---

## 8. The ~74–75% Accuracy Ceiling

Multiple independent approaches converge on roughly the same game-level accuracy:

| Method | Accuracy |
|--------|----------|
| LRMC | 74% |
| Logistic regression (4 features) | 74.6% |
| CFA ensemble (LR + SVM + CNN) | 74.6% |
| Sagarin | ~75% |
| BPI (favorite wins) | 75.6% |
| Seed-based probit | 73.5% |
| KenPom | ~73% |

This convergence across fundamentally different methods strongly suggests that **roughly 25% of tournament games are genuinely unpredictable** from pre-game information available to any model. The sources of irreducible noise include:

- **Hot/cold shooting variance.** A team shooting 40% from three versus 30% in the same game distribution can swing outcomes by 10+ points.
- **Referee variability.** Foul calling patterns affect tempo, key player availability, and free-throw opportunities.
- **Injury and illness.** Unreported minor injuries and game-time decisions introduce information asymmetry.
- **Psychological factors.** First-time tournament participants, pressure situations, and team chemistry under stress are not captured by any statistical model.
- **Late-round convergence.** The Boulier-Stekler finding that seed-based predictions degrade to chance level by the Elite Eight is echoed across models. As teams converge in quality, the signal-to-noise ratio drops, and factors not in the data (coaching adjustments, matchup specifics, clutch performance) dominate.

The Harvard Sports Analysis Collective articulated this starkly: "Statistically predicting the NCAA tournament is largely a fool's errand ... the difference between a good bracket and a great bracket is luck." Matthews and Lopez, the 2014 Kaggle competition winners, estimated that even an optimal model had at best a 50-50 chance of finishing in the top 10 due to randomness.

This ceiling has important practical implications. It means that **marginal improvements in accuracy are genuinely valuable** (every percentage point matters in a Kaggle competition or betting context), but that **no amount of additional model complexity will push accuracy to 85% or 90%**. The right response is to focus on probability calibration, uncertainty quantification, and bracket optimization strategies rather than raw accuracy (see [Evaluation & Calibration](evaluation-and-calibration.md) and [Bracket Strategy & Optimization](bracket-strategy.md)).

---

## 9. Comparative Summary

The following table synthesizes accuracy, strengths, and weaknesses across the major modeling approaches. Accuracy ranges reflect variation across studies and feature sets; single values indicate the most frequently reported figure.

| Approach | Representative Accuracy | Log Loss | Key Strengths | Key Weaknesses |
|----------|------------------------|----------|---------------|----------------|
| **Seed-based probit** | 73.5% | — | Simplest possible baseline; no data beyond seeds | Degrades to chance in later rounds; coarse |
| **Logistic regression** (efficiency features) | 74–75% | — | Interpretable; parsimonious; competitive | Cannot capture nonlinear interactions |
| **LRMC** | 74% | — | Minimal data needs; Markov chain handles SOS | No player-level info; early-season noise |
| **KenPom** | ~73% | — | Gold standard features; tempo-free; widely trusted | Proprietary; no injury adjustment |
| **T-Rank** | 73.5% | — | Free; recency weighting; GameScript | Can overreact to recent results |
| **BPI** | 75.6% (fav. wins) | — | Preseason priors; travel/altitude | Opaque; reliant on recruiting data |
| **EvanMiya** | ~2% over team ensembles | — | Player-level; roster-change sensitive | Partial paywall; newer system |
| **Elo (FiveThirtyEight)** | ~70% (standalone) | — | Long history; ensemble component | Slow to react; weak alone |
| **COOPER** | ~1% over prior system | — | Bayesian updates; pace variance | New; limited track record |
| **Random Forest** | 71–83% | 0.42 | Stable; handles nonlinearity | Less accurate than gradient boosting |
| **Gradient Boosting / XGBoost** | 64–84% | 0.41–0.55 | Best ML method for tabular data | Feature-dependent; risk of overfitting |
| **LightGBM** (multi-system input) | 77.6% (tournament) | 0.47 | Strong with ensemble features | Requires external rating systems |
| **Neural Network** (feedforward) | 76% | 0.61 | Simple to implement | Poor calibration; outperformed by trees |
| **LSTM** (Brier loss) | 73% | — | Best calibration (Brier 0.159) | Modest accuracy advantage |
| **Transformer** (BCE loss) | 74% | — | Best AUC (0.847) | Poor calibration with BCE; data-hungry |
| **Bayesian hierarchical** | 67–74% | — | Uncertainty quantification; interpretable | Computationally expensive |
| **FiveThirtyEight composite** | ~70% | Brier ~0.15–0.21 | Diverse ensemble; well-calibrated | Defunct; marginal over simple blend |
| **CFA ensemble** (LR+SVM+CNN) | 74.6% | — | Principled diversity; rank fusion | Complex to implement |
| **LLMs** (ChatGPT, Claude, etc.) | ~70% | — | Zero-effort; captures public consensus | Chalky; no probabilistic calibration |

### Key Takeaways

1. **Efficiency metrics are king.** AdjOE, AdjDE, and derived metrics (BARTHAG, net rating) appear as top predictors across every method family. See [Feature Engineering & Metrics](features-and-metrics.md).

2. **Margin of victory matters, with diminishing returns.** Models incorporating margin of victory consistently outperform win/loss-only models, but blowout margins should be capped or dampened.

3. **Ensembles of diverse models provide the most reliable predictions.** The FiveThirtyEight approach (blending KenPom, Elo, Sagarin, LRMC, BPI, and human rankings) and CFA (combining structurally different classifiers) both demonstrate that diversity, not individual model strength, drives ensemble gains.

4. **Gradient boosting is the machine learning method of choice for tabular sports data**, outperforming neural networks in most head-to-head comparisons on this task.

5. **Deep learning's value is in ensemble diversity and temporal modeling**, not as a standalone approach. LSTMs with Brier loss training produce the best-calibrated probabilities.

6. **Bayesian methods provide richer output** (credible intervals, posterior predictive distributions) without sacrificing accuracy, making them valuable for downstream bracket simulation and strategy optimization.

7. **Calibration matters more than accuracy** for bracket pool scoring. The goto_conversion technique and Brier-loss training represent practical approaches to improving calibration. See [Evaluation & Calibration](evaluation-and-calibration.md).

8. **The ~74–75% ceiling is real and persistent.** Model effort is better spent on calibration, uncertainty quantification, and bracket strategy than on pushing raw accuracy. See [Tournament Dynamics](tournament-dynamics.md) for how this ceiling interacts with single-elimination bracket structure.

9. **Emerging data sources** — prediction markets ($2.27B monthly volume on Kalshi), LLM-based qualitative reasoning, and shot-level computer vision data (ShotQuality) — represent the most likely frontiers for breaking through current performance bounds. See [Data Sources & Quality](data-sources-and-quality.md).
