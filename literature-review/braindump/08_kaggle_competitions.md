# Kaggle March Machine Learning Mania: Winning Solutions, Top Approaches, and Lessons Learned

## Summary

Kaggle's "March Machine Learning Mania" competition has run annually since 2014 (with a gap in 2020), challenging competitors to predict NCAA tournament game outcomes as probabilities. The competition originally used **log loss** as its evaluation metric but switched to **Brier score** in 2023, which changed strategic dynamics significantly. Key findings from studying multiple years of solutions:

1. **Simple models often win.** Logistic regression and single XGBoost models frequently outperform complex ensembles and deep learning approaches. The most consistent winners use well-calibrated probabilistic models rather than chasing accuracy.

2. **Feature engineering matters more than model complexity.** Top performers rely on established rating systems (Sagarin, Pomeroy/KenPom, Moore, Whitlock), Elo ratings, and efficiency metrics rather than raw box scores. Computing *differences* between teams rather than using absolute stats is standard practice.

3. **Luck is a dominant factor.** Multiple first-place winners have explicitly stated that luck plays an enormous role. Some winners have optimized their *submissions* strategically (e.g., hedging on the championship game) rather than just their models.

4. **Overconfidence is catastrophic under log loss.** Assigning 0.95+ probability to a game and being wrong can destroy an entire submission's score. Under Brier score, extreme predictions are penalized less severely, but the risk remains.

5. **Winning log loss scores** historically range from roughly 0.41 to 0.55, depending heavily on the year's upsets. Gradient boosting models typically achieve around 0.41 log loss, while simpler logistic regression models land around 0.54-0.57.

---

## Source 1: Andrew Landgraf -- 1st Place Winner Interview (2017)

- **Source:** Kaggle Blog, Medium
- **URL:** https://medium.com/kaggle-blog/march-machine-learning-mania-1st-place-winners-interview-andrew-landgraf-f18214efc659
- **Year:** 2017

### Methodology
- Created custom team efficiency ratings using a regression model
- Used those efficiency ratings as covariates in a **Bayesian logistic regression** model to predict game outcomes
- Kept models intentionally simple and probabilistic
- Critically: modeled not just game probabilities but also *competitors' likely submissions*, then searched for the submission with the highest chance of finishing in the top prizes

### Strategic Innovation
- Recognized that in a competition with thousands of entries, you are competing against other submissions, not just the games
- Used the same predictions in both allowed submissions except for the championship game, where each submission gave a different team a 100% win probability -- guaranteeing one submission would perfectly predict the final game
- This meta-game optimization was a key differentiator

### Key Insights
- "Luck is a major component of winning this competition, just like all brackets"
- Goal was to "systematically optimize submissions against the competition"
- Simple, well-calibrated probabilities plus strategic submission management beat complex models

---

## Source 2: Zach Bradshaw -- 1st Place Winner Interview (2015)

- **Source:** Kaggle Blog, Medium
- **URL:** https://medium.com/kaggle-blog/predicting-march-madness-1st-place-winner-zach-bradshaw-89741aea9fda
- **Year:** 2015

### Methodology
- Background in sports analytics was helpful but provided only marginal gains
- Used a **Bayesian framework** to incorporate prior knowledge about team strengths
- In hindsight, the Bayesian priors "hurt his predictions slightly more than it helped"

### Key Insights
- "All models are wrong but some are useful"
- Taking time to understand the problem structure is "an important and oft overlooked step"
- Luck was a necessary component of success
- Simpler approaches (like logistic regression) proved surprisingly competitive, "accurately predicting early-round upsets"

---

## Source 3: maze508 -- Top 1% Gold Solution (2023)

- **Source:** Medium
- **URL:** https://medium.com/@maze508/top-1-gold-kaggle-march-machine-learning-mania-2023-solution-writeup-2c0273a62a78
- **Year:** 2023 (first year using Brier Score instead of Log Loss)

### Methodology
- Selected external rating systems based on historical predictive accuracy
- Chose top 10 rating systems including **Pomeroy (KenPom), Moore, and Sagarin**
- Built features from: win rates, point differentials, away/home splits, team box scores
- Applied **Recursive Feature Elimination (RFE)** to remove features that degraded expanding-window cross-validation scores
- Final model: **XGBoost**

### Evaluation Metric
- Brier Score (new for 2023, replacing Log Loss)
- The metric change had strategic implications: Brier score penalizes extreme wrong predictions less than log loss, which changed how aggressively competitors should predict upsets

### Key Technique
- Expanding window cross-validation across all evaluation years (not just a single train/test split)
- Feature selection was empirically driven rather than domain-assumption driven

### What Didn't Work
- Predictions clustered around 0.5 were not ideal
- Post-processing scaling of predictions did not improve scores as expected

---

## Source 4: Conor Dewey -- Machine Learning Madness (2018)

- **Source:** Personal blog
- **URL:** https://www.conordewey.com/blog/machine-learning-madness-predicting-every-ncaa-tournament-matchup
- **Year:** 2018

### Methodology
- Four-step process: collect high-performing rankings, compile into composite score, compute score differences between matchups, train logistic regression
- Combined multiple rating systems into a **Mean Select Ranking Score** from Sagarin, Pomeroy, Moore, and Whitlock
- Implemented a **normalized Elo rating** adapted from FiveThirtyEight's approach and Liam Kirwin's Kaggle implementation

### Model
- **Logistic regression** -- chosen for its "probabilistic nature and effective, yet simple implementation"

### Scores Achieved
- Mean ranking model alone: **0.543 log loss**
- Elo-based model alone: **0.543 log loss**
- Combined composite model: **0.540 log loss** (slight improvement via cross-validation)

### Key Insights
- Established rating systems already encode enormous predictive power; the model's job is largely to calibrate their probabilities
- Tournament simulations (1,000 iterations) can provide useful uncertainty estimates
- Log loss "provides extreme punishments for being both confident and wrong"

---

## Source 5: Nick C. -- Kaggle March Machine Learning Madness (2016)

- **Source:** Personal blog (nickc1.github.io)
- **URL:** https://nickc1.github.io/machine/learning/2016/03/19/March-Machine-Learning-Madness.html
- **Year:** 2016

### Methodology
- Transformed game-by-game data into season-level statistics
- Used historical data from 2003-2015
- Primary model: **Logistic regression** (scikit-learn)
- 80/20 train-test split across 10,000 iterations for stability

### Features Used (11 statistics, two categories)
**Basic:** Points scored, field goals made/attempted, rebounds, assists, turnovers, steals, blocks, fouls
**Advanced:** Offensive efficiency, defensive efficiency, effective field goal percentage, turnover percentage, offensive rebound percentage, free throw rate, winning percentage, opponent winning percentage, RPI

### Scores
- Historical tournaments (2012-2015): **0.5619 log loss**
- 2016 tournament: **0.573 log loss**

### Key Insights
- RPI showed moderate separability between winners and losers but "the boundary between teams with similar RPI is quite fuzzy"
- Adjusted predicted probabilities by reducing values below 0.35 and increasing those above 0.65 -- manual confidence calibration improved performance
- Future direction: player-based models using neural networks rather than team aggregates

---

## Source 6: Machine Learning Madness (Kumar et al.) -- Multi-Model Comparison

- **Source:** Academic project (mehakumar.github.io)
- **URL:** https://mehakumar.github.io/machine-learning-madness/
- **Year:** 2016 (using 2000-2016 data)

### Methodology
- Tested six different classifiers on the same feature set
- Computed statistical *differences* between opposing teams (not absolute values) to prevent models from memorizing team identities

### Features Used (25 basic statistics)
Wins, Losses, Simple Ranking, Schedule Difficulty, Conference Wins/Losses, Home/Away Wins/Losses, Points, Points Against, Field Goals, FG Attempts, 3-Pointers, 3PT Attempts, Free Throws, FT Attempts, Offensive Rebounds, Total Rebounds, Assists, Steals, Blocks, Turnover %, Personal Fouls, Seed

### Model Comparison (Log Loss / Accuracy)
| Model | Log Loss | Accuracy |
|---|---|---|
| Linear Regression | 0.632 | -- |
| Ridge Regression | 0.632 | -- |
| K-Nearest Neighbors | 0.583 | 71.4% |
| Neural Networks | 0.612 | 76.2% |
| Random Forest | 0.418 | 82.5% |
| **Gradient Boosting** | **0.409** | **84.1%** |

### Key Insights
- Ensemble tree methods (Random Forest, Gradient Boosting) massively outperformed linear models and neural networks
- Feature differencing is essential to prevent team-identity bias
- Gradient Boosting was the clear best performer across both metrics

---

## Source 7: LinkedIn Rank 107 Approach (2025)

- **Source:** LinkedIn Pulse
- **URL:** https://www.linkedin.com/pulse/march-machine-learning-mania-2025-rank-107-approach-g13jf
- **Year:** 2025

### Methodology
- Used a well-regarded public baseline code that has been used since 2018 with minimal modifications
- Single **XGBoost** model with Leave-1-Season-Out cross-validation (20 folds, 2003-2024 excluding 2020)
- 23 features emphasizing attacking metrics, defensive statistics, seed differences, team quality, historical point differentials
- Permutation importance for feature selection
- **Cubic-spline calibration** applied in-fold rather than post-hoc

### Performance
- CV score: 9.258 MAE
- Final ranking: 107th place
- Time investment: only 2 hours

### What Worked
- "Simple single models like XGB are sufficient for this challenge"
- XGBoost outperformed LightGBM, CatBoost, and MLP alternatives
- Optuna hyperparameter tuning with manual stabilization

### What Didn't Work
- An ensemble combining XGBoost, LightGBM, CatBoost, and neural networks "performed poorly over the single XGB model"
- Diminishing returns from model complexity

---

## Source 8: Adit Deshpande -- Applying Machine Learning to March Madness

- **Source:** Personal blog
- **URL:** https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness
- **Year:** 2017 (using 1993-2016 data, 115,000+ games)

### Methodology
- Created 16-feature team vectors and computed difference vectors between competing teams
- Trained on regular season games to predict tournament outcomes
- 100 train/test splits for evaluation stability

### Features Used
- Average points per game (scored and allowed)
- Assists, rebounds, steals, turnovers, 3-pointers
- Simple Rating System (SRS, adjusted for strength of schedule)
- Strength of schedule
- Conference power designation (binary)
- Conference/tournament championships (binary)
- Historical tournament appearances and titles since 1985

### Best Model
- **Gradient Boosted Trees** at approximately 76.37% accuracy

### Key Insights
- Feature importance analysis: number of regular season wins was the strongest predictor, followed by strength of schedule and home-court advantage
- Domain knowledge confirmed by data -- wins and schedule difficulty matter most
- Emphasized that practitioners control training data selection and feature engineering, which introduces inherent bias regardless of algorithm sophistication

---

## Source 9: Sam Firke -- Predicting March Madness Tutorial (R-based)

- **Source:** GitHub
- **URL:** https://github.com/sfirke/predicting-march-madness
- **Year:** 2016-2017

### Methodology
- R/tidyverse-based pipeline: parameter selection, data scraping (rvest), cleaning, model training, prediction generation
- Achieved top 10% in 2016, top 25% in 2017

### Key Insights
- "Luck plays a big enough role that you can be a legit contender fairly easily"
- References Gregory Matthews and Michael Lopez (2014 winners) who published academic research on luck's role in the competition
- A well-structured, reproducible pipeline with thoughtful feature selection can be competitive without exotic methods

---

## Cross-Cutting Themes and Common Pitfalls

### What Distinguishes Winners from Average Entries

1. **Probability calibration** -- Winners ensure their predicted probabilities are well-calibrated, not just that their binary predictions are accurate. A model that says 0.70 should win 70% of the time when it says 0.70.

2. **Established rating systems as features** -- KenPom, Sagarin, and similar expert rating systems encode decades of domain knowledge. Using them as inputs (rather than reinventing them from raw box scores) is a consistent trait of top entries.

3. **Strategic submission management** -- Exploiting the two-submission rule, particularly by hedging on the championship game, is a known meta-strategy among top competitors.

4. **Restraint in model complexity** -- Single XGBoost or logistic regression models frequently outperform ensembles and deep learning for this problem. The data is too noisy and the sample size too small for complex models to generalize.

5. **Feature differencing** -- Computing the difference in statistics between two teams in a matchup, rather than feeding absolute team stats, is a universally adopted technique that prevents models from learning team-specific biases.

### Common Pitfalls

1. **Overconfident predictions** -- Under log loss, predicting 0.95 for a team that loses yields a penalty of ~3.0 for that single game, enough to ruin an entire submission. Even under Brier score, extreme wrong predictions are damaging.

2. **Overfitting to historical tournaments** -- With only ~67 games per tournament and high variance in outcomes, models can easily overfit to past upsets that were genuinely random events.

3. **Ignoring the evaluation metric** -- The switch from log loss to Brier score in 2023 changed optimal strategy. Log loss heavily penalizes confident wrong answers; Brier score is more forgiving of extreme predictions but less rewarding for confident correct ones.

4. **Complex ensembles for small, noisy data** -- Multiple competitors report that ensembles of XGBoost + LightGBM + CatBoost + neural networks performed *worse* than a single tuned XGBoost model.

5. **Predictions clustered around 0.5** -- Models that refuse to commit (predicting every game at 0.48-0.52) score poorly because they cannot differentiate between heavy favorites and coin flips.

6. **Neglecting the women's tournament** -- Since 2023, the competition combines men's and women's brackets. The women's tournament has fewer upsets, requiring different calibration.

7. **Not using cross-validation properly** -- Expanding window or leave-one-season-out CV is essential because basketball trends change over time. Standard k-fold CV on shuffled data leaks future information.

### Historical Score Ranges

| Metric | Typical Winning Range | Typical Median Range |
|---|---|---|
| Log Loss (pre-2023) | 0.41 -- 0.50 | 0.55 -- 0.60 |
| Brier Score (2023+) | ~0.18 -- 0.22 | ~0.22 -- 0.28 |

Note: Scores vary dramatically by year depending on how many upsets occur. A year with many chalk results (favorites winning) rewards conservative models; a year full of upsets punishes them.
