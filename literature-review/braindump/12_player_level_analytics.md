# Player-Level Analytics and Their Impact on Team-Level Predictions for March Madness

## Summary

Most mainstream March Madness prediction models (KenPom, COOPER, the academic papers on Kaggle competitions) operate at the **team level**, using aggregate efficiency metrics. However, a growing body of work—particularly from EvanMiya's Bayesian Performance Rating (BPR) system—demonstrates that player-level modeling can produce more accurate and adaptive predictions, especially in a college basketball landscape increasingly shaped by the transfer portal and one-and-done freshmen. The key tension is this: team-level models are simpler and have strong track records, but they struggle with **roster discontinuity** (transfers, injuries, freshmen) because the team from last year is often not the team playing this year. Player-level models address this directly but require more data and more complex modeling.

Key takeaways:
- **Player-level models are most valuable at the start of seasons and during roster upheaval** (transfer portal era), where team-level models have stale data.
- **Bayesian Performance Rating (BPR)** is the most developed player-level system for college basketball, combining box score stats with play-by-play adjusted plus-minus.
- **Roster continuity / returning minutes** is a meaningful predictor of tournament success (correlation of ~0.36 with offensive efficiency improvement).
- **Player experience in the NCAA tournament** is a statistically significant predictor of future tournament success.
- **Injury adjustments** at the player level meaningfully improve tournament-round predictions (used by COOPER, EvanMiya).
- **Most academic ML papers still use only team-level features** and acknowledge the omission of player-level data as a limitation.

---

## Source 1: EvanMiya — Bayesian Performance Rating (BPR)

- **URL:** https://blog.evanmiya.com/p/bayesian-performance-rating
- **Related:** https://blog.evanmiya.com/p/preseason-player-projections-with
- **Related:** https://blog.evanmiya.com/p/which-schools-get-the-most-out-of

### How Player-Level Data Is Incorporated

BPR is a three-model architecture that is explicitly player-level:

1. **Regularized Adjusted Plus-Minus (RAPM):** Uses play-by-play data to estimate each player's offensive and defensive contribution per 100 possessions, adjusting for the strength of all other players on the court. Critically, BPR uses **Bayesian linear regression** with player-specific priors rather than uniform ridge regression, allowing smarter starting estimates.

2. **College-Specific Box Plus-Minus (Box BPR):** A box-score model trained on Division I data (not NBA data) to determine which box-score skills are most valuable at the college level. Regresses per-100-possession stats (assists, turnovers, rebounds, shooting efficiency) against RAPM coefficients.

3. **Preseason Projection Model:** Separate models for returning players vs. transfers. Uses prior-season BPR, high school recruiting ratings, player class, and developmental trajectory.

### Key Player Metrics

- Offensive and Defensive BPR (points per 100 possessions above D1 average)
- Box score stats weighted approximately 50% for offense, 30% for defense
- Play-by-play adjusted plus-minus for the remainder
- Preseason projections carry ~15% weight by season's end
- Usage rate, assist rate, rebounding rates, shooting efficiency

### Handling Transfers and Freshmen

- **Transfers:** De-emphasize on-off splits (which lose relevance in new systems) and increase reliance on box score stats and recruiting data.
- **Freshmen:** Use recruiting rankings as primary ability indicator, compared to historical cohorts with similar rankings. Freshmen carry substantially larger uncertainty (wider prior standard deviation), so in-season adjustments happen more rapidly.

### Transfer Portal Analysis

EvanMiya published analysis showing which schools get the most out of transfers. The methodology compares end-of-season BPR against preseason projections, controlling for the quality difference between a player's old and new school. Key finding: some programs (Arizona, UConn) consistently improve transfers beyond expectations, while others systematically underperform.

### Data Availability

- Play-by-play data for all D1 games
- Box scores for all D1 games
- Recruiting rankings from major services
- EvanMiya.com provides the aggregated metrics publicly (some features behind paywall)

### Player-Level vs. Team-Level

BPR is explicitly designed to be a player-level metric that aggregates up to team projections. The preseason projection system is where this is most valuable: rather than regressing last year's team rating toward a mean (as KenPom and COOPER do), EvanMiya projects each individual player and then assembles the roster. This should be more accurate when rosters change significantly.

---

## Source 2: Nate Silver's COOPER Rating System

- **URL:** https://www.natesilver.net/p/introducing-cooper-silver-bulletins

### How Player-Level Data Is Incorporated

COOPER is **primarily a team-level system** based on margin of victory, opponent strength, and pace. However, it incorporates player-level data in one important way:

- **Tournament injury adjustments:** For NCAA tournament forecasts only, COOPER uses probabilistic injury data (percentage chance of player availability) weighted by the player's importance as measured by **Win Shares from sports-reference.com**, adjusted for strength of schedule.
- Replacement-level player quality varies by team—backup players at elite programs are projected stronger than backups at weaker programs.

### Handling Roster Changes

COOPER handles roster turnover indirectly: teams retain 70% of their prior-year rating with 30% reversion toward conference mean. This is a blunt instrument compared to player-level projection models.

### Key Insight

COOPER demonstrates that even team-centric models benefit from player-level adjustments at critical moments (injuries during the tournament). The fact that Silver added this layer suggests team-level models alone are insufficient when player availability changes.

---

## Source 3: TeamRankings — Returning Minutes and Tournament Experience

- **URL:** https://www.teamrankings.com/blog/ncaa-tournament/does-past-ncaa-tournament-experience-lead-to-march-success-the-data-says

### How Player-Level Data Is Incorporated

This analysis uses **returning minutes percentage** as a player-derived, team-aggregated metric:

- Measures the proportion of a team's playing time from the prior season that carries over.
- For tournament-specific analysis: "the number of games a team played in the NCAA tournament in the previous year multiplied by the percent of minutes that team returns."

### Key Findings

- Returning minutes correlates with offensive efficiency improvement at **r = 0.36**.
- Returning minutes correlates with defensive efficiency improvement at **r = -0.19** (negative = improvement in points allowed).
- NCAA tournament experience is a **statistically significant positive predictor** of future tournament success (95% confidence level).
- **Critical nuance:** "Returning everyone from a mediocre team does not transform it into a world beater." Talent baseline matters—elite teams benefit less from returning minutes than developing squads.

### Data Challenges

- Five years of historical data for efficiency analysis; six years of NCAA tournament data.
- Difficult to disentangle "experience" from "the team was already good."
- Does not account for quality of minutes returned (starter vs. bench).

---

## Source 4: Harvard Sports Analysis Collective — A Method to the Madness

- **URL:** https://harvardsportsanalysis.org/2019/03/a-method-to-the-madness-predicting-ncaa-tournament-success/

### How Player-Level Data Is Incorporated

This study examined whether individual player experience predicts tournament overperformance (actual wins minus expected wins for a given seed). Experience was measured by weighting each team's players by regular-season minutes played.

### Key Findings

- **Player experience was a surprisingly weak predictor:** R-squared = 0.0002.
- Offensive ranking (R² = 0.013), defensive ranking (R² = 0.006), and three-point rate (R² = 0.0009) were also weak.
- The conclusion: "the unpredictability of March Madness is what makes it so entertaining."

### Important Caveat

This study measured **overperformance relative to seed**, not raw win prediction. Seeds already encode a lot of team quality information, so this is testing whether player experience adds **marginal** predictive power beyond what seeding already captures. This is a much harder bar to clear than predicting game outcomes from scratch.

### Data Challenges

- Experience metric doesn't account for redshirting or injury-related minute distribution.
- KenPom and Kaggle data from 2002-2017.

---

## Source 5: Academic ML Papers (Team-Level with Player-Level Gaps)

### Paper A: March Madness Tournament Predictions Model (2025)
- **URL:** https://arxiv.org/html/2503.21790v1
- **Method:** Logistic regression with L2 regularization + Monte Carlo simulation
- **Features:** Adjusted Offensive Efficiency (ADJOE), Adjusted Defensive Efficiency (ADJDE), Power Rating, Two-Point Shooting Percentage Allowed — all team-level
- **Accuracy:** 74.6% on individual matchups
- **Player-level gap:** Authors explicitly note that "team statistics can rapidly change during a season or tournament as players get injured" and that "player injuries, team strategies, and external factors" are variables potentially overlooked.

### Paper B: NCAA Bracket Prediction Using ML and Combinatorial Fusion Analysis (2026)
- **URL:** https://arxiv.org/html/2603.10916v1
- **Method:** Combinatorial Fusion Analysis combining logistic regression, SVM, random forest, XGBoost, and CNNs
- **Features:** 26 team-level features (from original 44) selected via Recursive Feature Elimination — offensive/defensive efficiency, strength of schedule, luck factor
- **Player-level gap:** Makes no mention of handling roster changes, injuries, or transfers. All features are team-aggregate.
- **Data:** Kaggle's March Machine Learning Mania competition + KenPom

### Observation

The gap between what academic papers use (team-level aggregates) and what practitioner systems use (EvanMiya's player-level BPR) is notable. Academic papers tend to use readily available Kaggle datasets which provide team-level stats. Player-level data requires more work to collect and integrate, but practitioner models that do so appear to gain meaningful advantages, especially for preseason projections and handling mid-season roster changes.

---

## Source 6: KenPom and Bart Torvik — Bridging Player and Team Data

- **KenPom:** https://kenpom.com/
- **Torvik:** https://barttorvik.com/
- **Guide:** https://www.basketunderreview.com/how-to-use-kenpom-to-analyze-college-basketball-part-1-player-stats/

### Player-Level Data Available

Both KenPom and Bart Torvik provide extensive player-level statistics:
- Usage rate (percentage of possessions used)
- Offensive/defensive rebound percentage
- Assist rate, steal rate, block rate
- Effective field goal percentage
- Per-possession efficiency metrics
- **Torvik:** 40+ variables per player per game, advanced box scores for every D1 game

### How Player Data Feeds Into Team Ratings

Both systems' **core team ratings are team-level** (adjusted offensive/defensive efficiency based on game outcomes). Player data is available as a supplementary analytical layer but is not directly used in the team rating algorithms. KenPom's efficiency margin is the difference between points scored and allowed per 100 possessions, adjusted for opponent strength and game location.

### Minutes Continuity

KenPom tracks **minutes continuity** as a team-level metric derived from player data — measuring how much of last year's playing time returns. This is one of the few places player-level data directly influences team projections in these systems.

### Data Availability

- KenPom: subscription required for full data; widely used in academic research
- Torvik: free access to most data; player stats, game logs, historical comparisons
- Both provide data back to 2002+

---

## Cross-Cutting Themes

### When Player-Level Models Add the Most Value

1. **Preseason projections** — When rosters change significantly (transfer portal era), team-level models that simply regress last year's rating are at a disadvantage vs. models that project individual players and reassemble.
2. **Mid-season injury adjustments** — Losing a star player changes a team's expected efficiency dramatically; only player-level models can quantify this precisely.
3. **Matchup analysis** — Player-level data enables analysis of specific matchup problems (e.g., a team without a rim protector facing a team that attacks the paint).

### When Team-Level Models Are Sufficient

1. **Stable rosters with long track records** — If a team returns most players, team-level efficiency metrics are reliable.
2. **Predicting game outcomes (not margins)** — Simple models based on team efficiency and strength of schedule achieve 70-75% accuracy, which is already strong.

### Data Availability Challenges

- **Play-by-play data** is needed for adjusted plus-minus but is harder to collect and process than box scores.
- **Recruiting rankings** for freshmen are noisy and vary across services.
- **Transfer impact** is hard to predict because players change systems, roles, and competition levels simultaneously.
- **Injury data** is often incomplete, unreliable, or deliberately obscured by coaches.
- **Small sample sizes** per player per season (30-35 games) limit the precision of individual player metrics.

### Do Player-Level Models Outperform Team-Level Models?

No definitive head-to-head comparison exists in the literature. However:
- EvanMiya's player-level system is competitive with KenPom and Torvik for game prediction accuracy.
- The largest advantage appears to be in **preseason and early-season predictions**, where player-level models can incorporate recruiting data, transfer projections, and returning player development curves.
- By late season, team-level models "catch up" because they have enough game data to estimate team strength directly.
- For tournament-specific prediction (conditional on seeding), the marginal value of player-level data appears small (per the Harvard analysis), but this may be because seeding already encodes player-level information indirectly.
