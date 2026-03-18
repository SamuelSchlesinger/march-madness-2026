# Data Quality, Preprocessing, and Feature Normalization for College Basketball Analytics

## Summary

Data quality is the foundation upon which every March Madness prediction model stands or falls. This review covers practical challenges encountered when building college basketball analytics pipelines: handling missing data, normalizing statistics across eras and tempo, dealing with COVID-disrupted seasons, reconciling multiple data sources, managing conference realignment, addressing mid-season coaching changes, and properly treating First Four / play-in games. The key takeaway across all sources is that **principled imputation, tempo-free normalization, strict temporal separation to prevent data leakage, and awareness of structural breaks in the data (COVID, conference moves, coaching changes) are non-negotiable for trustworthy models.**

---

## Source 1: Forecasting NCAA Basketball Outcomes with Deep Learning (LSTM and Transformer Models)

- **Title:** Forecasting NCAA Basketball Outcomes with Deep Learning: A Comparative Study of LSTM and Transformer Models
- **URL:** https://arxiv.org/html/2508.02725v1
- **Type:** Academic paper (arXiv preprint)

### Data Quality Issues Addressed

1. **Missing values in team-specific features:** Elo ratings, tournament seeds, and GLM-derived quality metrics were incomplete for certain seasons and teams. This is a pervasive problem -- not every team has a long tournament history, and newer metrics (like NET ratings) simply do not exist before their introduction year.

2. **Data leakage prevention:** The authors explicitly flag the risk of tournament outcome information bleeding into predictive features. This is a subtle but critical issue -- e.g., using "tournament wins" as a feature when predicting tournament outcomes.

3. **Overtime inflation of statistics:** Raw box score stats from overtime games are inflated relative to regulation games, creating unfair comparisons if not corrected.

4. **Asymmetric data availability across gender divisions:** Women's tournament data lacked coaching history available for men's teams, illustrating how data quality gaps can be division-specific.

### Preprocessing Techniques

- **Targeted imputation strategies:**
  - Median seed values for missing seeds
  - Baseline Elo of 1000 for teams lacking historical data
  - Neutral quality scores (zero) for teams with insufficient match participation
- **Overtime normalization:** All game statistics scaled to equivalent 40-minute regulation periods
- **Dataset symmetry:** Each matchup represented twice (from each team's perspective) to prevent winner/loser ordering bias
- **Feature scaling:** StandardScaler applied to Elo ratings and GLM quality scores

### Practical Recommendations

- Implement principled imputation rather than discarding incomplete samples
- Maintain strict temporal boundaries between training and validation partitions
- Normalize game-level statistics for duration variations
- Document missing data patterns systematically -- certain seasons or divisions have higher incompleteness rates
- Establish feature audit trails to verify no outcome information corrupts pre-game indicators

---

## Source 2: COVID-19 Pause Impact on College Basketball (TeamRankings / PoolGenius)

- **Title:** Measuring the Impact of College Basketball Covid Pauses in 2021
- **URL:** https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/covid-impact-basketball-college/
- **Type:** Applied analytics article

### Data Quality Issues Addressed

1. **COVID pauses as a structural break in team performance data:** The 2020-21 season introduced a completely novel confound -- teams going 10+ days without playing or practicing, then returning to competition. This is not garden-variety missing data; it represents a fundamental change in what the statistics mean.

2. **Distinguishing COVID pauses from normal schedule gaps:** Not all long gaps between games were COVID-related. The authors cross-referenced news reports and Jon Rothstein's documentation to confirm which gaps were actual program shutdowns vs. normal scheduling.

3. **Asymmetric impact by team quality:** Elite teams (Game Score 6.0+) suffered -6.1 point differentials in their first game back; below-average teams showed minimal measurable impact. This means COVID's effect on the data is not uniform and cannot be corrected with a single adjustment factor.

4. **Cumulative pause effects:** Teams experiencing multiple pauses averaged 10.1 points worse than their season average in games after their second or subsequent pause.

### Preprocessing Techniques

- Analyzed 386 games with confirmed COVID pauses identified through manual cross-referencing
- Measured "adjusted Game Score" relative to each team's season average to isolate pause effects
- Segmented analysis by team quality tier to reveal non-uniform impacts

### Practical Recommendations for Handling COVID Seasons

- **Discount or down-weight games immediately following confirmed COVID pauses**, especially for elite teams
- **Account for cumulative effects** when teams endured multiple pauses
- **Do not treat the 2020-21 season as interchangeable with normal seasons** in training data -- it requires special handling or explicit indicators
- **The 2020 tournament (cancelled) creates a complete gap** in tournament-specific training data that must be acknowledged
- **Home court advantage was diminished** in 2020-21 due to empty or limited-capacity arenas, affecting location-based features

### NCAA Statistical Policy Changes (2020-21)

The NCAA issued formal COVID-19 Media Coordination and Statistics Policy Adjustments for the 2020-21 season (documented at http://fs.ncaa.org/Docs/stats/ForSIDs/COVID-19_Policies.pdf), modifying eligibility rules and statistical record-keeping. Any pipeline using official NCAA statistics from this period should verify whether the underlying counting rules changed.

---

## Source 3: ncaahoopR Package -- Play-by-Play Data Quality

- **Title:** ncaahoopR: An R Package for Working with NCAA Basketball Play-by-Play Data
- **URL:** https://github.com/lbenz730/ncaahoopR
- **Type:** Open-source R package documentation

### Data Quality Issues Addressed

1. **Incorrect timestamps in play-by-play data:** The package flags plays tagged at wrong timestamps with a `wrong_time` variable. These erroneous records are filtered out of graphical and statistical helper functions but retained in raw data for analyses where precise timing is less critical.

2. **Inconsistent shot location data:** Shot location information is only available for certain games, determined by ESPN's coverage decisions. This creates systematic missingness -- major conference games are more likely to have shot data than mid-major or low-major games.

3. **Missing point spread data:** Pre-game spreads are unavailable for games involving non-Division 1 teams or contests before the 2016-17 season. When Vegas spreads are missing, the package attempts imputation from derived team strengths, introducing estimation error.

4. **Smaller conference coverage gaps:** The documentation does not extensively discuss this, but the reliance on ESPN as the upstream data source means coverage depth varies by conference prestige. This is a **critical issue for March Madness prediction** since Cinderella teams often come from conferences with the thinnest data coverage.

### Preprocessing Techniques

- Selective filtering rather than deletion: problematic records remain in raw datasets but are excluded from visualizations and summary statistics
- Imputation of missing spreads from derived team strength metrics

### Practical Recommendations

- Independently verify data completeness for non-major conferences and historical seasons
- Be aware that play-by-play data quality degrades for less prominent teams and older seasons
- Treat imputed values (like derived spreads) differently from observed values in downstream models

---

## Source 4: Odds Gods -- Predicting College Basketball: A Complete Technical Methodology

- **Title:** Predicting College Basketball: A Complete Technical Methodology
- **URL:** https://blog.oddsgods.net/predicting-college-basketball-methodology
- **Type:** Technical methodology blog post

### Data Quality Issues Addressed

1. **Missing values in newer metrics:** NET ratings (introduced 2019) have 39% missing values across the full 2003-2026 dataset. Rather than imputing, the author chose LightGBM, which handles missing values natively. This is a pragmatic approach but shifts the burden of missing data handling to the algorithm.

2. **Data leakage risk:** All variables represent a team's state *entering* the game, not after it -- a strict temporal discipline that prevents information leakage.

3. **Inability to capture non-statistical information:** Injuries, suspensions, and other contextual factors are absent from the statistical pipeline, representing a fundamental data quality gap.

### Preprocessing Techniques

- Constructed a single wide table where each row represents one game
- Used Kaggle's March Machine Learning Mania competition data (2003-2026)
- Incorporated weekly ranking snapshots from dozens of rating systems via Massey Rankings
- Relied on LightGBM's native missing value handling rather than explicit imputation

### Practical Recommendations

- Consider algorithm selection as a preprocessing decision -- tree-based models handle missing data more gracefully than neural networks
- Maintain strict temporal ordering of features to prevent leakage
- Supplement statistical pipelines with injury/roster tracking systems

---

## Source 5: Tempo-Free Statistics and KenPom Normalization Methodology

- **Title:** National Efficiency (KenPom Blog) and related KenPom documentation
- **URLs:**
  - https://kenpom.com/blog/national-efficiency/
  - https://kenpom.com/blog/ratings-glossary/
  - https://www.oddsshark.com/ncaab/what-are-kenpom-ratings (OddsShark explainer)
- **Type:** Methodology documentation and explainers

### Data Quality Issues Addressed

1. **Raw statistics are incomparable across different tempos:** A team that plays 80 possessions per game will accumulate more raw stats than one playing 60, regardless of quality. This is the single most important normalization issue in college basketball analytics.

2. **Cross-era comparability:** The pace of college basketball has changed dramatically over decades. Comparing raw PPG from the 1990s to the 2020s is meaningless without tempo adjustment. KenPom's per-100-possessions normalization addresses this.

3. **Opponent quality confounds raw statistics:** Playing in a weak conference inflates raw stats. KenPom adjusts efficiency metrics for opponent quality, game location, and timing.

### Preprocessing Techniques -- Tempo-Free Normalization

- **Possession estimation formula:** `Possessions = FGA - OR + TO + 0.475 * FTA` (KenPom uses 0.475 as the FT multiplier; some older sources use 0.42)
- **Per-100-possessions scaling:** All offensive and defensive statistics converted to rates per 100 possessions
- **Adjusted efficiency:** Iterative adjustment for opponent quality, location, and recency:
  - Each team's per-game efficiency is adjusted based on opponent strength
  - Computations are repeated until convergence
- **Adjusted tempo:** Each team's pace is similarly adjusted for opponent effects

### Differences Between KenPom and BartTorvik

This is relevant for data source reconciliation:
- **BartTorvik adds recency bias:** Games older than 40 days are progressively down-weighted
- **BartTorvik incorporates "GameScript":** Adjusts for garbage time, capturing game narrative beyond raw numbers
- **Rankings are similar but not identical:** Both had the same top-6 teams in one comparison but in different order
- **Accuracy is comparable:** NET at 95.8%, KenPom/BPI/BartTorvik all at 92.5% in one tracking study

### Practical Recommendations

- **Always use tempo-free (per-possession) statistics** rather than raw per-game totals
- **Choose a possession formula and stick with it** -- small differences in the FTA multiplier (0.42 vs 0.475) propagate through all downstream calculations
- When combining data from multiple rating systems, be aware that methodological differences (recency weighting, garbage time handling) mean the same underlying game data produces different ratings
- If building your own ratings, iterative adjustment for opponent quality is essential

---

## Source 6: Kaggle March Madness ML Pipelines (Multiple Practitioners)

- **Titles and URLs:**
  - "Applying Machine Learning to March Madness" -- https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness
  - "March Machine Learning Madness" -- https://nickc1.github.io/machine/learning/2016/03/19/March-Machine-Learning-Madness.html
  - March Madness 2025 Data Card -- https://github.com/alexhalcazar/March_Madness_2025/blob/main/data_card.md
- **Type:** Blog posts and project documentation

### Data Quality Issues Addressed

1. **Merging data from multiple CSV sources:** Kaggle competition data comes as separate files for team IDs, tournament seeds, game results, box scores, geographic data, and weekly rankings from various systems. Reconciling these requires careful joins on team IDs and season identifiers.

2. **Team name inconsistencies across sources:** When combining Kaggle data with Sports Reference or other sources, team naming conventions differ (e.g., "UConn" vs "Connecticut" vs "University of Connecticut").

3. **Sparse early-season data:** Teams may not have played games at the start of a tracked period, producing NaN values that resolve naturally through running average calculations.

4. **Training data selection bias:** Conscious decisions about which seasons and features to include create inherent model bias. One author explicitly cautions that feature selection choices require careful scrutiny.

### Preprocessing Techniques

- **Replace empty strings/spaces with NaN** before any analysis
- **Remove duplicates** across merged datasets
- **Data augmentation through permutation:** Include both orderings of each matchup (Team A vs Team B and Team B vs Team A) to double training samples and prevent ordering bias
- **Feature differencing:** Rather than concatenating team feature vectors, use the *difference* between team vectors to emphasize relative strengths
- **Running averages for temporal smoothing:** Transform game-by-game data into season-level summaries using rolling computations
- **Derived efficiency metrics:** Calculate possessions, offensive/defensive efficiency, effective FG%, turnover rate, rebound rate, and free throw rate from raw box scores
- **Remove team identifiers from features** to prevent the model from memorizing school-specific patterns rather than learning generalizable team quality signals

### Practical Recommendations

- Download fresh Kaggle data each year as new seasons are appended
- Verify column name consistency across years
- Aggregate beyond raw stats into efficiency metrics
- Preserve temporal context using running averages
- Handle sparsity naturally (through rolling calculations) rather than aggressive imputation
- Consider dimensionality reduction (PCA/SVD) for high-dimensional feature sets
- Gradient boosted trees handle heterogeneous/multi-scale data well, partially alleviating normalization needs

---

## Cross-Cutting Themes and Recommendations

### 1. Missing Data Strategy

| Situation | Recommended Approach |
|-----------|---------------------|
| Newer metrics not available in older seasons (e.g., NET pre-2019) | Use algorithms with native missing handling (LightGBM) or impute with reasonable defaults |
| Teams with no tournament history | Assign baseline values (Elo = 1000, median seed) |
| Play-by-play gaps for small conferences | Acknowledge coverage bias; do not treat absence of data as absence of quality |
| COVID-cancelled 2020 tournament | Treat as structural gap; do not interpolate tournament performance |
| Overtime games inflating stats | Normalize all statistics to 40-minute equivalent |

### 2. Normalization Priorities

1. **Tempo-free conversion is mandatory** -- per-possession stats, not per-game
2. **Opponent-quality adjustment** -- iterative methods (KenPom-style) or Elo-based
3. **Recency weighting** -- more recent games are more predictive (BartTorvik uses 40-day window)
4. **Location adjustment** -- home/away/neutral impacts, especially disrupted during COVID
5. **Overtime normalization** -- scale to 40-minute equivalents

### 3. Structural Breaks to Watch For

- **COVID 2020-21 season:** Empty arenas (home court advantage diminished), team pauses (performance drops of 6-10+ points for elite teams), cancelled 2020 tournament, altered eligibility rules, changed statistical policies
- **Conference realignment:** Teams changing conferences alter the meaning of conference-level features; strength of schedule calculations must use the conference membership that was active *during that season*, not current membership
- **Mid-season coaching changes:** Research shows teams typically decline before a coaching change and then recover at a rate similar to teams that did not change coaches -- the coaching change itself does not reliably improve short-term performance. Only ~12% of new coaches significantly outperform predecessors in the near term. For data purposes, season statistics should arguably be split into pre- and post-change segments rather than averaged
- **First Four / play-in games:** These games are structurally different from the main tournament bracket. The teams involved are either the last four at-large selections or the lowest-seeded automatic qualifiers. For bracket prediction models, these games can often be handled separately or excluded, since the "real" 64-team bracket begins after them. However, First Four winners carry additional fatigue and a shorter preparation window into their next game

### 4. Data Source Reconciliation

When combining data from KenPom, BartTorvik, Sports Reference, ESPN, and Kaggle:
- **Team ID mapping is essential** -- create a master lookup table across sources
- **Methodology differences produce different numbers from the same underlying games** -- do not mix raw metrics from different rating systems without understanding their assumptions
- **Update frequency varies** -- some sources update daily, others weekly; ensure temporal alignment
- **Open-source accessibility varies:** KenPom and Synergy are paid; BartTorvik/toRvik and hoopR are free. The toRvik R package (https://www.torvik.dev/) addresses "one distinct problem facing men's college basketball: a lack of accessible open-source data"
- **Historical coverage depth varies:** toRvik has data back to 2007-08 for most stats, game predictions back to 2015, tournament results back to 2000

### 5. Data Leakage Checklist

Before training any model, verify:
- [ ] All features represent pre-game state, not post-game outcomes
- [ ] No tournament outcome information in training features
- [ ] Temporal train/test splits respect chronological ordering (no future data in training)
- [ ] Point differentials and margin of victory are excluded from pre-game features
- [ ] Team identifiers (names/IDs) are excluded from model features to prevent memorization

---

## Tools and Packages for Data Quality

| Tool | Language | Purpose | Coverage |
|------|----------|---------|----------|
| [ncaahoopR](https://github.com/lbenz730/ncaahoopR) | R | Play-by-play data with quality flags | ESPN-sourced, quality varies by conference |
| [hoopR](https://hoopr.sportsdataverse.org/) | R | Clean play-by-play data access | Part of SportsDataverse ecosystem |
| [toRvik](https://www.torvik.dev/) | R | Free access to BartTorvik data | 2007-08 onward, free alternative to KenPom |
| [bigballR](https://github.com/jflancer/bigballR) | R | NCAA basketball data manipulation | Play-by-play focus |
| Kaggle March Mania | CSV | Structured competition datasets | 2003-present, updated annually |

---

## Key Takeaways for This Project

1. **Build a robust team ID mapping table** across all data sources before doing anything else
2. **Normalize everything to per-100-possessions** using a consistent possession formula
3. **Flag or segment COVID-affected data** (2020-21 season) rather than treating it as normal
4. **Handle the 2020 tournament gap explicitly** -- do not let models silently interpolate
5. **Use algorithms that handle missing data natively** (LightGBM, XGBoost) or implement principled imputation with documentation of what was imputed and why
6. **Track conference membership by season** to correctly compute conference-level features
7. **Consider splitting seasons at coaching changes** for teams where mid-season transitions occurred
8. **Treat First Four games as a separate prediction task** or at minimum flag First Four winners with additional contextual features (fatigue, preparation time)
9. **Maintain a data quality log** documenting known issues, imputation decisions, and structural breaks for reproducibility
