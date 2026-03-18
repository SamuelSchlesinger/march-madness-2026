# Data Sources and Quality

## 1. The Data Landscape for NCAA Basketball

College basketball analytics sits in an unusual position: the data ecosystem is rich and growing, but fragmented across dozens of sources with varying cost, depth, update frequency, and access restrictions. Unlike professional leagues with centralized statistical infrastructure, NCAA Division I basketball data is scattered across proprietary analytics platforms, community-maintained R packages, official NCAA portals, annual Kaggle competitions, and commercial APIs.

The landscape breaks along a few important axes:

- **Derived metrics vs. raw statistics.** Sources like KenPom and Bart Torvik provide opponent-adjusted, tempo-free efficiency ratings---model outputs, not raw measurements. Sports Reference and Kaggle provide box-score-level data that can be transformed into custom metrics. Understanding which level you are working at matters for [feature engineering](features-and-metrics.md) and for avoiding hidden correlations when stacking features from multiple rating systems.
- **Granularity.** Box scores capture game totals. Play-by-play data captures individual events (shots, rebounds, turnovers) with timestamps. Tracking data captures player positions at frame-level resolution. Each level adds predictive information the previous level cannot provide, but at increasing cost in data volume and preprocessing complexity.
- **Historical depth.** Some sources reach back decades (Sports Reference to 1947); others cover only recent seasons (gamezoneR from 2017-18, NET rankings from 2019). Any model spanning multiple seasons must reconcile these coverage gaps.
- **Accessibility.** Cost ranges from free (Bart Torvik, Kaggle, Massey Ratings) to modest (KenPom at $25/year) to enterprise-level (SportsDataIO, Stats Perform tracking data). Scraping restrictions further constrain access: Sports Reference rate-limits to 20 requests per minute and explicitly prohibits AI training use.

The practical implication is that no single source is sufficient. A working prediction pipeline needs to combine multiple sources, which in turn requires careful attention to team ID mapping, methodology differences, and temporal alignment---themes that recur throughout this chapter.

## 2. Primary Data Sources

### KenPom (kenpom.com)

KenPom is the gold standard for tempo-free college basketball analytics. It provides adjusted offensive and defensive efficiency (points per 100 possessions, adjusted for opponent strength and game location), adjusted tempo, strength of schedule, a luck rating, and player-level advanced stats (usage rate, rebound rate, block rate, steal rate). The four-factors decomposition (effective FG%, turnover rate, offensive rebounding rate, free throw rate) is available for every team.

- **Historical depth:** Back to approximately 2002. The `kenpompy` Python scraper can access data back to 2010.
- **Cost:** $24.95/year for the web subscription; a separate API subscription is available at additional cost. The free tier shows only the main rankings table with no drill-down.
- **Access:** No official CSV export. Programmatic access via `kenpompy` (Python), `cbbdata` (R, requires matching subscription email), or the official API.
- **Update frequency:** After every game during the season.
- **Limitations:** Data is proprietary and represents one analyst's methodology. The free tier is essentially useless for research. Methodology may evolve over time, so comparing KenPom 2005 values to KenPom 2025 values requires caution.

Adjusted efficiency margin is one of the strongest single-feature predictors of tournament outcomes. All 24 of the last national champions ranked in the top 25 of adjusted efficiency margin, and 23 of 24 ranked in the top 21 of adjusted offensive efficiency. Nate Silver's current COOPER model weights KenPom at 3/8ths alongside his proprietary ratings at 5/8ths, suggesting KenPom is a strong but not sufficient signal. See [Modeling Approaches](modeling-approaches.md) for how KenPom features are used across different model architectures.

### Bart Torvik / T-Rank (barttorvik.com)

Bart Torvik provides T-Rank ratings (adjusted offensive/defensive efficiency, adjusted tempo), BARTHAG (a win probability metric), and the PRPG! player metric (Points Over Replacement Per Adjusted Game At That Usage). A distinctive feature is custom date-range filtering, which enables analysis of team performance in specific windows---useful for assessing "hot" vs. "cold" stretches heading into March.

- **Historical depth:** Player game-level data back to 2008 (~70,000 D1 games). Team-level data extends further.
- **Cost:** Completely free. No paywall.
- **Access:** Web tables with some CSV export. Programmatic access via the `toRvik` R package (20+ functions) and the `cbbdata` R package.
- **Update frequency:** Daily during the season.
- **Limitations:** Maintained by a single person (a lawyer by profession). Cloudflare protection can block automated scraping of the website directly.

Torvik differs from KenPom in two notable ways: it applies recency bias (games older than 40 days are progressively down-weighted) and incorporates a "GameScript" adjustment for garbage time. Rankings are similar but not identical to KenPom's. In one tracking study, NET achieved 95.8% accuracy while KenPom, BPI, and Torvik all came in at 92.5%.

Torvik also provides transfer portal data (histories for 5,000+ players back to 2011-12), recruiting rankings (6,000+ players back to 2007-08), returning minutes percentages, and the RosterCast tool for projecting team rating changes based on roster composition. The `toRvik` R package includes a `transfer_portal()` function that returns transfer histories with matchable player IDs.

### Kaggle March Machine Learning Mania

The annual Kaggle competition ships approximately 35 CSV files covering team identifiers, tournament seeds, regular season and tournament game results (both compact and detailed box scores), conference affiliations, geographic data (game cities, distances), coaching records, and Massey ordinals (composite rankings from 100+ computer systems). Both men's (TeamIDs 1000-1999) and women's (TeamIDs 3000-3999) data are included.

- **Historical depth:** Detailed stats back to approximately 2003; basic results go further.
- **Cost:** Free. Requires a Kaggle account.
- **Format:** Clean CSV files, well-documented, ready for pandas or R ingestion.
- **Update frequency:** Released annually, typically in February/March, with cumulative historical data.
- **Limitations:** Some early years have less complete detailed stats. The dataset is curated and generally clean, but merging with external sources introduces team name inconsistencies.

Kaggle is the single most popular entry point for March Madness prediction projects. Thousands of public notebooks demonstrate approaches from logistic regression to deep learning. The competition's log-loss scoring metric encourages well-calibrated probability estimates rather than just picking winners---a valuable alignment with good modeling practice. See [Evaluation & Calibration](evaluation-and-calibration.md) for more on scoring metrics.

### Sports Reference (sports-reference.com/cbb)

Sports Reference provides comprehensive box scores, team and player stats, schedules, results, conference standings, and coaching records (3,000+ coaches) for men's basketball back to 1947-48 (basic stats) and 1998-99 (detailed player stats).

- **Cost:** Free for browsing. Stathead subscription required for advanced queries.
- **Access friction:** Rate-limited to 20 requests per minute. Terms of service explicitly prohibit automated scraping, bots, and AI training use. The `sportsipy` Python package exists but must be used carefully to avoid IP bans.
- **Best use:** Manual spot-checking, historical context, and long-run trend analysis. Not suitable as an automated pipeline data source.

### Massey Ratings (masseyratings.com)

Massey Ratings aggregates 100+ computer ranking systems into a composite ranking. This composite includes KenPom, Sagarin, BPI, T-Rank, RPI, and dozens of others. CSV exports are available from the website, and the Massey ordinals are included as a standard feature set in the Kaggle competition data.

The composite rankings are one of the strongest feature sets in top-performing Kaggle entries. Using ordinal ranks from multiple systems as input features effectively ensembles the wisdom of many different rating algorithms. The tradeoff is that some constituent systems use similar methodologies, creating hidden correlations that must be handled during [feature engineering](features-and-metrics.md).

### Other Notable Sources

- **NCAA Official Stats Portal (stats.ncaa.org):** Free official statistics and play-by-play data, but the site uses dynamic content loading that defeats standard scrapers, and play-by-play data suffers from human tracker errors (events attributed to wrong players, unclean substitution records). The `bigballR` R package wraps this source.
- **ESPN BPI:** Free team power rankings, game predictions, and tournament projections. Undocumented JSON API endpoints exist (community-documented at github.com/pseudo-r/Public-ESPN-API). ESPN's play-by-play data, accessible through `hoopR` and `CBBpy`, is more commonly used than BPI ratings themselves.
- **cbbdata (R package):** A unified API wrapping Bart Torvik, KenPom (with subscription), and NET data. Updates every 15 minutes during the season. The single best entry point for R users wanting clean programmatic access to multiple sources.
- **SportsDataIO:** Real-time scores, stats, odds, and projections via a RESTful JSON API. Commercial pricing makes it impractical for non-commercial use.
- **EvanMiya (evanmiya.com):** Bayesian Performance Rating (BPR) player ratings, transfer portal rankings, and player projections. Subscription-based.

## 3. Play-by-Play and Tracking Data

### The Data Hierarchy

The literature documents a clear hierarchy of predictive value:

| Data Level | Log-Loss (from Stats Perform study) | What It Adds |
|---|---|---|
| Box scores | (baseline) | Points, rebounds, assists, shooting percentages |
| Play-by-play | 0.40 | Accurate possession counts, lineup-specific performance, play-type breakdowns, win probability, clutch moments |
| Tracking/spatial data | 0.30 | Player positioning, defensive contest data, shot quality, movement patterns |

The Stats Perform paper (Sloan 2020) provides the clearest quantitative evidence: models using tracking features from 650,000+ possessions achieved a log-loss of 0.30, compared to 0.40 for play-by-play-only models---a 25% reduction in prediction error. Even without full tracking data, play-by-play represents a meaningful upgrade over box scores.

### What Play-by-Play Data Enables

**Accurate possession counting.** The standard box-score formula (`POSS = FGA - OREB + TO + 0.475 * FTA`) uses a free throw multiplier that KenPom himself derived from play-by-play data. PBP enables direct observation of when possessions start and end, and filtering of non-representative possessions (garbage time, intentional fouls at the end of games).

**Lineup analysis.** PBP data identifies which five players are on the court for each possession, enabling lineup-specific efficiency metrics. EvanMiya's Bayesian Performance Rating (BPR) uses this to compute Regularized Adjusted Plus-Minus (RAPM), capturing intangible contributions (defense, spacing, screen-setting) invisible in box scores. BPR combines RAPM with box-score priors in a Bayesian framework, producing player-level impact estimates interpretable as "points per 100 possessions above D1 average."

**Play-type decomposition.** Transition offense in Division I averages 1.11 points per shot versus 0.994 in half-court sets---roughly an 8-point-per-game difference. This distinction is only possible with PBP data. Teams that derive disproportionate value from transition may perform differently depending on opponent pace, a matchup-specific feature that box scores cannot provide.

**Win probability and clutch analysis.** The `ncaahoopR` package builds logistic regression-based win probability models from PBP data, enabling identification of clutch performance, close-game behavior, and game-flow patterns. These features are relevant for tournament prediction, where single-elimination pressure magnifies clutch performance differences.

### Shot Quality Models

ShotQuality uses computer vision to extract all 10 players' positions from broadcast video at the moment of each shot, incorporating approximately 100 variables across five categories: defensive distance, shooter ability, play type, shot type, and contextual inferences. The resulting shot probability metric acts as a "luck-adjusted" efficiency measure that stabilizes faster than raw shooting percentage---after just one game, ShotQuality predictions are already a better predictor of future performance than traditional box-score metrics. This fast stabilization is particularly valuable for projecting teams into unfamiliar March Madness matchups.

### PBP Data Sources

| Source | Package | Language | Coverage | Notes |
|---|---|---|---|---|
| ESPN play-by-play | `ncaahoopR`, `hoopR`, `CBBpy` | R, R, Python | All D1 games | Event-level, includes some shot locations |
| STATS LLC GameZone | `gamezoneR` | R | 2017-18 onward | 170,000+ charted shots/season (vs. ~70,000 from ESPN) |
| NCAA official PBP | `bigballR` | R | 2010 onward | Human tracker errors; requires headless browser scraping |
| ShotQuality | API | Various | NCAA + NBA | Proprietary; shot-level with spatial data |
| Stats Perform tracking | Proprietary | N/A | Varies | Generated from broadcast computer vision |

Coverage varies systematically by conference prestige: major conference games are more likely to have complete shot location data from ESPN. This is a critical issue for March Madness prediction, since Cinderella teams often come from conferences with the thinnest data coverage.

## 4. Betting Market Data

### Market Efficiency

Academic research spanning decades finds that NCAA tournament betting markets are broadly efficient. The closing line is widely considered the single most accurate predictor of game outcomes. Key findings from the literature:

- A study of tournament betting data from 1996 to 2019 (Hickman, *Journal of Economics and Finance*, 2020) found very little detectable bias based on seeding and no profitable systematic betting strategy based on seeds alone.
- Examination of point spread data across multiple sports found that NCAA basketball betting markets are generally efficient, with no odds-based strategy yielding statistically significant long-term profits.
- FiveThirtyEight's model, when converted to implied spreads and compared against Vegas closing lines, went 26-31 overall in hypothetical bets. It performed well in the Round of 64 (17-13) but poorly in later rounds (6-15), suggesting that market efficiency increases as the tournament progresses.

### Exploitable Biases

Despite overall efficiency, specific biases have been documented:

- **Big underdogs (20+ point spreads)** cover more often than the efficient market would imply.
- **ACC teams** tend to cover the spread less than expected in opening-round games---a conference-specific bias possibly reflecting inflated public perception of "brand name" conferences.
- **College basketball exhibits the strongest longshot bias** of any major sport: the market systematically overprices large underdogs on the moneyline.
- **Home favorites** cover more often than expected, opposite to the pattern in other sports.

### Using Market Data in Models

The literature suggests three uses for betting market data:

1. **As a benchmark.** Any model should be evaluated against closing-line implied probabilities. Many published models report accuracy and Brier scores without this comparison, making it impossible to assess whether they add value beyond what the market already knows. See [Evaluation & Calibration](evaluation-and-calibration.md) for evaluation methodology.

2. **As a feature.** Pre-game point spreads encode real-time information (injuries, travel, lineup changes, motivation) that season-long efficiency metrics miss. KenPom picks the correct winner 60.5% of the time when spreads are 7 points or fewer, but drops to 52.7% for spreads of 3 or fewer---in tight games, the market's situational awareness provides an edge. Combining KenPom for structural team quality assessment with Vegas lines as a situational reality check should outperform either alone.

3. **As an upset signal.** When a model's implied spread disagrees with the market by 3+ points, FiveThirtyEight found a 5-2 record in early rounds---a concrete threshold for identifying high-confidence deviations.

### Prediction Markets

Prediction market platforms (Kalshi, Polymarket, Robinhood) are emerging as alternatives to traditional sportsbooks. Kalshi generated $2.27 billion in men's college basketball trading volume in February 2026 alone. Their transparent fee structure (vs. baked-in vig at sportsbooks) may produce less distorted implied probabilities, though no rigorous comparison of prediction market accuracy versus sportsbook accuracy has been published for NCAA tournament outcomes.

## 5. Roster and Transfer Portal Data

### The Scale of the Problem

The transfer portal has fundamentally reshaped college basketball roster construction. As of 2025, more than 53% of rotation players in the 68-team tournament field previously played at another D-I school, and roughly one-third of top-8 minute players on each roster played for a different D-I program just last season. The NCAA eliminated sit-out requirements in 2021 and further loosened transfer rules in April 2024.

Average roster continuity (measured by KenPom's Minutes Continuity metric, the percentage of returning minutes from the prior season) has dropped to historic lows: 34.0% in 2024-25, down from 39.1% the prior year. Several prominent coaches (Tony Bennett, Jay Wright, Jim Larranaga) have retired partly due to portal dynamics.

### Continuity: Measurable but Debated

The evidence on continuity's predictive value is mixed:

- **Cases for continuity:** In the COVID-disrupted 2020-21 season, 8 of 10 mid-major teams with the highest returning minutes improved their KenPom rating. Drexel jumped from KenPom 244 to 158; Loyola Chicago reached KenPom 10 with a Sweet 16 run.
- **Cases against:** Kentucky (0.0% continuity in 2024-25) beat Duke, Florida, Mississippi State, Texas A&M, and Tennessee. Gonzaga (72.7% continuity, 4th nationally) lost to low-continuity Kentucky and West Virginia early.
- **Temporal pattern:** Continuity advantages show most during the first month of the season, as newly assembled teams are still gelling. By March, talent and coaching quality dominate.

### Player-Level Projection

The frontier is individual player projection rather than aggregate team continuity:

- **EvanMiya's BPR** measures transfer performance relative to preseason projections, isolating the school's development effect from the player's inherent talent. Key finding: Arizona and UConn systematically outperform with transfers, while North Carolina, Arkansas, and Indiana systematically underperform---suggesting a "transfer development" factor specific to program culture and coaching.
- **Bart Torvik's RosterCast** projects team offensive and defensive efficiency based on roster composition, accounting for returning players, incoming freshmen, and transfers. Available programmatically through the `toRvik` R package.

### Experience Still Predicts Championships

Despite the disruption of the portal era, 17 of 23 national champions since 2002 had a junior or senior as their top contributor. The key insight is that in the portal era, experience can be *acquired* via transfers rather than *developed* internally. Models should track total roster experience (juniors/seniors as percentage of minutes) rather than just "returning" experience.

### Modeling Recommendations for Roster Data

1. Use player-level projected contributions (BPR or similar) rather than a single aggregate continuity number.
2. Treat continuity as a time-decaying feature: weight it heavily in November, discount it by March.
3. Weight continuity by position and minutes share---returning a lead guard matters more than returning a bench player.
4. Build a historical "transfer alpha" for each program based on how consistently transfers over- or under-perform projections.
5. Track experience composition (juniors/seniors as percentage of minutes) separately from continuity.
6. Account for coaching stability: a new coach with a new roster faces compounding uncertainty.

## 6. Data Quality Challenges

### Team Name and ID Inconsistencies

When combining data from multiple sources (Kaggle, KenPom, Torvik, Sports Reference, ESPN), team naming conventions differ: "UConn" versus "Connecticut" versus "University of Connecticut." Building a robust team ID mapping table across all data sources is a prerequisite for any multi-source pipeline.

### COVID-Disrupted Seasons

The 2020-21 season introduced structural breaks that cannot be treated as normal missing data:

- **COVID pauses** caused elite teams (Game Score 6.0+) to perform 6.1 points worse in their first game back. Teams with multiple pauses averaged 10.1 points worse than their season average after their second or subsequent pause. Below-average teams showed minimal measurable impact.
- **Home court advantage was diminished** due to empty or limited-capacity arenas, affecting location-based features.
- **The 2020 tournament was cancelled entirely**, creating a gap in tournament-specific training data that models should not silently interpolate.
- **NCAA statistical policy changes** modified eligibility rules and record-keeping for 2020-21.

The non-uniform impact across team quality tiers means a single correction factor is inadequate. The recommended approach is to flag or segment COVID-affected data (2020-21 season) rather than treating it as normal, and to down-weight games immediately following confirmed COVID pauses, especially for elite teams.

### Conference Realignment

Teams changing conferences alter the meaning of conference-level features. Strength of schedule calculations must use the conference membership that was active *during that season*, not current membership. The Kaggle data includes conference affiliation by season, but external sources may not track this cleanly.

### Strength of Schedule Estimation Error

A simulation study (Wieland, 2024) quantified the fundamental problem: with realistic conference-heavy scheduling, rating system estimation error roughly doubles compared to an ideal random-schedule scenario (mean absolute error of 8.18 vs. 5.30). The ~10 non-conference games each team plays are disproportionately important for calibrating the entire rating landscape, but cross-conference data remains structurally sparse.

This has a specific downstream consequence: rating systems are fundamentally less accurate for teams in weak conferences, not because the systems are poorly designed, but because the data is insufficient. Mid-major teams with strong actual quality may be systematically underrated. Tournament data bears this out: 12-seeds win first-round games at a 34.6% rate and 11-seeds at 37.1%---both above seed-line expectations, consistent with systematic underseeding. See [Modeling Approaches](modeling-approaches.md) for how different models handle this bias.

### Power Conference Circular Amplification

The Quad system (used by the selection committee) structurally favors power conferences: high-major conference games qualify as Quad 1 results approximately 48% of the time, versus approximately 6% for mid/low-major conference games. Power conference teams inflate each other's metrics through internal play---every game produces a "quality win" for the winner and a "good loss" for the loser. Academic research documents that SEC teams have been seeded approximately 2 positions higher than model-predicted performance warrants (Coleman, Lynch, and DuMond, *Economics Bulletin*).

### Tracking and PBP Data Quality

Play-by-play data from the NCAA official portal suffers from human tracker errors: events attributed to players not on the court, unclean substitution records, and occasional scoring discrepancies. Shot location data from ESPN is only available for games ESPN covers, creating systematic missingness that correlates with conference prestige. Any features derived from PBP data inherit these errors and biases.

### Missing Data Patterns

| Situation | Recommended Approach |
|---|---|
| Newer metrics unavailable in older seasons (e.g., NET pre-2019) | Use algorithms with native missing handling (LightGBM) or impute with documented defaults |
| Teams with no tournament history | Assign baseline values (Elo = 1000, median seed) |
| Play-by-play gaps for small conferences | Acknowledge coverage bias; absence of data does not mean absence of quality |
| COVID-cancelled 2020 tournament | Treat as structural gap; do not interpolate tournament performance |
| Overtime games inflating stats | Normalize all statistics to 40-minute equivalents |

## 7. Preprocessing Best Practices

### Tempo-Free Normalization

Converting all statistics to per-100-possessions rates is the single most important normalization step. Raw per-game statistics are incomparable across different tempos and eras. The standard possession formula is:

```
POSS = FGA - OREB + TO + 0.475 * FTA
```

The 0.475 multiplier (derived by KenPom from play-by-play data) is more accurate than older estimates of 0.4 (Oliver) or 0.44 (Hollinger). Choose a formula and stick with it---small differences in the FTA multiplier propagate through all downstream calculations.

### Opponent-Quality Adjustment

KenPom's approach iteratively adjusts each team's per-game efficiency based on opponent strength, game location, and recency until convergence. If building custom ratings, this iterative adjustment is essential. If using pre-computed ratings from KenPom or Torvik, be aware that their methodologies differ (recency weighting, garbage time handling) and mixing raw metrics from different rating systems without understanding their assumptions introduces inconsistencies.

### Leakage Prevention

Data leakage is the most consequential preprocessing failure in tournament prediction. Before training any model, verify:

- All features represent pre-game state, not post-game outcomes.
- No tournament outcome information appears in training features.
- Temporal train/test splits respect chronological ordering (no future data in training).
- Point differentials and margin of victory are excluded from pre-game features.
- Team identifiers (names/IDs) are excluded from model features to prevent memorization of school-specific patterns.
- Tournament seeding is used carefully: seeds incorporate committee judgment that already reflects team quality metrics, creating subtle leakage when combined with those same metrics.

See [Evaluation & Calibration](evaluation-and-calibration.md) for temporal cross-validation strategies.

### Feature Construction

- **Dataset symmetry.** Represent each matchup twice (from each team's perspective) to double training samples and prevent winner/loser ordering bias.
- **Feature differencing.** Use the difference between team feature vectors rather than concatenating them, to emphasize relative strengths.
- **Rolling averages.** Transform game-by-game data into season-level summaries using rolling computations; this handles early-season sparsity naturally.
- **Overtime normalization.** Scale all game-level statistics to 40-minute equivalents.
- **Remove team identifiers** from features to prevent memorization.

### Algorithm-Aware Preprocessing

Algorithm selection is itself a preprocessing decision. Tree-based models (LightGBM, XGBoost) handle missing values, heterogeneous scales, and non-linear relationships natively, reducing the need for explicit imputation and normalization. Neural networks typically require more aggressive preprocessing. See [Tools & Implementation](tools-and-implementation.md) for implementation details.

## 8. Recommended Data Stack for This Project

### Foundation Layer

1. **Kaggle March Machine Learning Mania data** as the structured backbone: clean, historical, free, purpose-built for prediction. Includes Massey ordinals (composite rankings from 100+ systems) which are among the strongest feature sets in top competition entries.
2. **Bart Torvik via `cbbdata`/`toRvik`** for advanced metrics (adjusted efficiency, tempo, BARTHAG), transfer portal data, and returning minutes data. Free and programmatically accessible.
3. **KenPom** ($25/year) for the gold-standard adjusted efficiency metrics if budget allows. Provides the most widely cited ratings in the literature.

### Advanced Feature Layer

4. **gamezoneR** for shot location data (170,000+ charted shots per season), enabling spatial features and shot distribution analysis.
5. **hoopR / CBBpy** for ESPN play-by-play data, enabling possession-level features, lineup analysis, and win probability modeling.
6. **Betting market closing lines** as both a benchmark for model evaluation and a feature encoding real-time situational information.

### Sources to Avoid for Automated Pipelines

- **Sports Reference:** Excellent data quality but hostile to automated access. Use manually for spot-checking.
- **stats.ncaa.org:** Data quality issues (tracker errors) and difficult scraping requirements (requires headless browser).
- **SportsDataIO:** Cost-prohibitive for non-commercial use.

### Critical Infrastructure

Before ingesting any data: build a **master team ID mapping table** across all sources. This is the single most important piece of infrastructure for a multi-source pipeline, and skipping it will cause cascading errors downstream.

Track **conference membership by season** to correctly compute conference-level features across realignment boundaries. Flag the **2020-21 season** with explicit indicators rather than treating it as normal data. Maintain a **data quality log** documenting known issues, imputation decisions, and structural breaks for reproducibility.

For the full picture of how these data sources feed into modeling, feature engineering, and evaluation, see [Modeling Approaches](modeling-approaches.md), [Feature Engineering & Metrics](features-and-metrics.md), [Evaluation & Calibration](evaluation-and-calibration.md), and [Recommended Approach](recommended-approach.md).
