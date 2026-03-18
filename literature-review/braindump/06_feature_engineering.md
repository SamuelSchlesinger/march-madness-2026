# Feature Engineering for March Madness Prediction

## Summary

The literature on predicting NCAA March Madness outcomes converges on several key themes regarding which statistics and derived features matter most:

1. **Adjusted efficiency margin is the single most predictive statistic.** All 24 national champions over a recent 24-year span ranked in the top 25 of KenPom's adjusted efficiency margin (AEM). This metric combines adjusted offensive efficiency (points scored per 100 possessions) and adjusted defensive efficiency (points allowed per 100 possessions), both corrected for opponent strength and game location.

2. **Dean Oliver's "Four Factors" explain ~98% of offensive efficiency variance:** effective field goal percentage (most important), offensive rebounding rate, turnover rate, and free throw rate (least important). However, team-level matchups in the four factors do *not* add predictive value beyond overall adjusted efficiency ratings.

3. **Difference-based features outperform raw statistics.** Multiple successful models compute the difference between two teams' statistics rather than using absolute values. This reduces dimensionality, prevents bias toward specific schools, and creates natural symmetry (P(A wins) = 1 - P(B wins)).

4. **Tournament play favors "repeatable traits."** Defense, rebounding, and turnover control are more reliable in tournament settings than shooting-dependent metrics, because travel, unfamiliar venues, and quick turnarounds disrupt shooting rhythm more than they disrupt defensive effort.

5. **Feature selection consistently reduces large feature sets to a core of 4-26 features** without meaningful accuracy loss. Methods include coefficient magnitude thresholding, recursive feature elimination with cross-validation (RFECV), and random forest feature importance.

6. **Ranks of variables can be more predictive than their raw rating values,** an insight from combinatorial fusion analysis research.

---

## Source 1: Adit Deshpande — "Applying Machine Learning to March Madness"

- **URL:** https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness
- **Model:** Gradient Boosted Trees
- **Accuracy:** 76.37%

### Features Used (16-dimensional team vector)

| Category | Features |
|----------|----------|
| Box score stats | Points per game scored, points per game allowed, 3PM per game, turnovers per game, assists per game, rebounds per game, steals per game |
| Advanced metrics | Simple Rating System (SRS), Strength of Schedule (SOS) |
| Conference indicators | Power 6 membership (binary), regular season conf. champion (binary), conf. tournament champion (binary) |
| Historical | Tournament appearances since 1985, national championships since 1985 |
| Contextual | Location advantage (-1, 0, or 1) |

### Feature Importance Rankings (Gradient Boosted Trees)

1. **Regular season wins** — most predictive
2. **Strength of Schedule (SOS)** — second
3. **Location** — third

### Key Insights

- Regular season wins serve as a proxy for overall team quality
- SOS adjusts for schedule difficulty, differentiating teams from weak vs. strong conferences
- Location captures home-court-like advantage in tournament games
- The author noted diminishing returns beyond ~76% accuracy, suggesting a ceiling for models using only season-level aggregates

---

## Source 2: The Power Rank — "The Ultimate Guide to Predictive College Basketball Analytics"

- **URL:** https://thepowerrank.com/cbb-analytics/
- **Framework:** Dean Oliver's Four Factors + KenPom efficiency system

### The Four Factors (in order of importance)

1. **Effective Field Goal Percentage (eFG%)** — most important; gives 50% bonus credit for three-pointers
2. **Offensive Rebounding Rate** — calculated as a rate, not raw totals
3. **Turnover Rate** — expressed per possession
4. **Free Throw Rate** — FTA / FGA (least important of the four)

### Critical Finding: Matchups Don't Add Value

Jordan Sperber's research showed that "team level matchups in the four factors do not help in predicting the outcome of a college basketball game." Even when one team excels dramatically in a specific factor while the opponent is weak in the corresponding defensive category, adjusted efficiency ratings remain equally predictive across all matchup types. This means you should use overall efficiency ratings rather than trying to model factor-by-factor matchups.

### KenPom Methodology

- Uses least squares regression to simultaneously solve 706 variables (offensive and defensive ratings for all ~353 teams)
- Weighs recent games more heavily
- Minimizes prediction error better than simple power ratings
- Combining multiple independent rating systems (ensemble approach) outperforms any single metric — demonstrated by FiveThirtyEight's methodology, which includes preseason AP poll rankings

---

## Source 3: FOX Sports — "KenPom Trends to Know Before Filling Out Your March Madness Bracket"

- **URL:** https://www.foxsports.com/stories/college-basketball/kenpom-trends-march-madness-bracket
- **Analysis type:** Historical pattern analysis of 24 years of KenPom data

### National Champion Average Pre-Tournament Rankings

| Metric | Average Ranking | Key Threshold |
|--------|----------------|---------------|
| Adjusted Efficiency Margin | 5.17 | **All 24 champions ranked top 25** |
| Adjusted Offensive Efficiency | 8.25 | 23 of 24 ranked top 21 |
| Adjusted Defensive Efficiency | 16.33 | 21 of 24 ranked top 31 |
| Adjusted Tempo | 133.79 | Highly variable — not predictive |

### Key Insights

- **Efficiency margin is the most reliable single predictor** — no champion in 24 years fell outside the top 25
- **Offense matters slightly more than defense** for champions (average rank 8.25 vs 16.33)
- **Tempo is essentially irrelevant** — 14 of 24 champions ranked in the top 100 for tempo, but 6 ranked 200th or worse. Fast or slow pace does not predict championship success.
- **Non-conference strength of schedule is not important** — only 3 of 24 champions ranked in the top 60
- **Luck rating** — 11 of 24 champions ranked in the top 100, suggesting some variance is inherent
- **Final Four teams** averaged slightly lower rankings (18.47 offensive, 22.96 defensive) than champions, establishing a softer threshold for deep runs

---

## Source 4: arXiv Paper — "March Madness Tournament Predictions Model: A Mathematical Modeling Approach" (2025)

- **URL:** https://arxiv.org/html/2503.21790v1
- **Feature selection method:** Coefficient magnitude thresholding (threshold = 0.45)

### Features Selected (4 from original 16)

1. **Adjusted Offensive Efficiency (ADJOE)** — points scored per 100 possessions
2. **Adjusted Defensive Efficiency (ADJDE)** — points allowed per 100 possessions
3. **Power Rating (BARTHAG)** — overall team strength metric (Barttorvik)
4. **Two-Point Shooting Percentage Allowed (2PD)** — defensive interior performance

### Feature Engineering Approach

- Used **difference between teams' feature values** rather than raw values
- This reduced dimensionality while preserving predictive information
- Created mathematical symmetry: P(A wins) = 1 - P(B wins)

### Accuracy Results

| Model | Training Accuracy | Testing Accuracy |
|-------|------------------|-----------------|
| Full (16 features) | 72.76% | 75.39% |
| Reduced (4 features) | 71.35% | 74.60% |

Dropping 12 features cost less than 1 percentage point of accuracy, demonstrating that offensive and defensive efficiency dominate prediction.

---

## Source 5: arXiv Paper — "NCAA Bracket Prediction Using Machine Learning and Combinatorial Fusion Analysis" (2026)

- **URL:** https://arxiv.org/html/2603.10916v1
- **Feature selection method:** Recursive Feature Elimination with Cross-Validation (RFECV), 5-fold CV, log loss metric
- **Feature importance method:** Random Forest feature importance

### Feature Selection Results

- **26 features selected from 44 original features**
- Features organized into four categories:
  1. **Offensive Efficiency** — effectiveness in converting possessions into points
  2. **Defensive Efficiency** — preventing opponents from scoring (points allowed per possession, defensive rebounds, forced turnovers)
  3. **Strength of Schedule** — difficulty of opponents faced
  4. **Luck** — unmeasured chance factors

### Feature Engineering Approach

- Computed **difference variables** between opposing teams for each game (Team 1 stats minus Team 2 stats)
- Found that **ranks of variables are more predictive than their raw rating values** — an important insight for feature transformation

---

## Source 6: Machine Learning Madness (Kumar et al.)

- **URL:** https://mehakumar.github.io/machine-learning-madness/
- **Model:** Gradient Boosting (best performer)
- **Accuracy:** 84.13% (log loss 0.409, beating Kaggle competition winners)

### Features Used (25 basic statistics)

Wins, losses, Simple Ranking, schedule difficulty, conference wins/losses, home wins/losses, away wins/losses, points scored, points against, field goals, field goal attempts, three-pointers, three-point attempts, free throws, free throw attempts, offensive rebounds, total rebounds, assists, steals, blocks, turnover percentage, personal fouls.

### Key Design Decisions

- Used **difference of two teams' basic stats** for each matchup
- Deliberately **excluded advanced/derived statistics** because they are "derived from the others with respect to time or other stats" — avoiding multicollinearity
- This approach prevents bias toward specific schools and focuses on competitive strength

### Baseline Finding

Simply choosing the higher-seeded team achieves **76% accuracy**, establishing the benchmark any model must beat. Their gradient boosting model exceeded this substantially at 84%.

---

## Source 7: Tournament-Specific Statistical Insights

- **Sources:** ESPN, SI, Basket Under Review coverage of 2026 tournament
- **URLs:**
  - https://www.espn.com/mens-college-basketball/story/_/id/48223542/ncaa-tournament-upsets-first-round-giant-killers-march-madness-2026
  - https://www.basketunderreview.com/march-madness-2026-stat-pack-analyzing-statistical-trends-for-each-first-round-matchup/

### Tournament vs. Regular Season: Which Stats Hold Up

**Most reliable in tournament play (repeatable traits):**
- Defense (adjusted defensive efficiency)
- Rebounding (especially offensive rebounding rate)
- Turnover control (both forcing and avoiding turnovers)

**Less reliable in tournament play:**
- Three-point shooting percentage (disrupted by unfamiliar gyms, travel, pressure)
- Tempo-dependent advantages (neutral sites compress tempo differences)
- Non-conference strength of schedule

**Specific examples:**
- Teams in the top 5 nationally in turnover rate at both ends scored 21 points per game off miscues
- TCU went 13-0 when their offensive rebounding rate exceeded 36%, but just 9-11 when it didn't
- Louisville made 11.5 threes per game (41% of scoring), creating high-variance outcomes typical of three-point-dependent teams

### Upset Indicators

- Lower seeds that force turnovers and crash the offensive glass can compensate for talent gaps
- Three-point shooting variance is the primary mechanism for upsets — a hot-shooting day can close large talent gaps, but this is not predictable

---

## Cross-Source Synthesis: Feature Tier List

Based on the convergence across all sources, here is a consolidated ranking of feature importance:

### Tier 1: Core Predictive Features (appear in virtually every successful model)
- **Adjusted Offensive Efficiency** (ADJOE / KenPom OE)
- **Adjusted Defensive Efficiency** (ADJDE / KenPom DE)
- **Adjusted Efficiency Margin** (AEM = ADJOE - ADJDE)
- **Seed / Power Rating** (BARTHAG or equivalent)

### Tier 2: Strong Supporting Features
- **Strength of Schedule** (SOS)
- **Effective Field Goal Percentage** (eFG%)
- **Turnover Rate** (per possession)
- **Offensive Rebounding Rate**
- **Regular Season Wins** (adjusted for SOS)

### Tier 3: Useful but Secondary
- **Free Throw Rate** (FTA/FGA)
- **Two-Point Shooting Percentage Allowed**
- **Steals per game**
- **Assists per game**
- **Simple Rating System (SRS)**

### Tier 4: Contextual / Low Predictive Value
- **Adjusted Tempo** — champions vary wildly (rank 1 to 200+)
- **Non-Conference SOS** — only 3 of 24 champions in top 60
- **Conference tournament results** — small sample, high variance
- **Three-point shooting percentage** — high game-to-game variance makes it unreliable for tournament prediction despite regular-season value
- **Luck rating** — by definition captures randomness

---

## Methodological Takeaways for Feature Engineering

1. **Use difference features** (Team A stat - Team B stat) rather than absolute values for each team. This is the most common and effective approach across sources.

2. **Prefer rate stats over counting stats.** Points per 100 possessions > points per game. Turnover rate > turnovers per game. This removes tempo effects.

3. **Prefer adjusted stats over raw stats.** Adjusting for opponent quality is critical — raw stats conflate team quality with schedule difficulty.

4. **Be aggressive with feature selection.** Multiple sources show that reducing from 16-44 features down to 4-26 features loses minimal accuracy. Efficiency metrics dominate.

5. **Consider using ranks instead of raw values** for some features, as the combinatorial fusion analysis paper found ranks more predictive than ratings.

6. **Avoid multicollinearity.** Either use raw box score stats OR derived advanced stats, not both. Several sources explicitly excluded advanced stats because they are linear combinations of basic stats.

7. **Ensemble diverse rating systems.** Combining KenPom, Sagarin, BPI, and other independent rating systems outperforms any single system, as each captures slightly different signal.
