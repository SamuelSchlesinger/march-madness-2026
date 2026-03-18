# Play-by-Play Data, Possession-Level Modeling, and Advanced Event-Based Analytics

## Summary

Play-by-play (PBP) data offers a richer view of basketball games than traditional box scores, enabling possession-level efficiency modeling, lineup analysis, transition/clutch breakdowns, and shot-quality estimation. The key insight across all sources is that granular event data captures *how* teams score and defend, not just *how much*---and this distinction matters for prediction.

**Core findings:**

- **Possession-level efficiency** (points per possession, adjusted for opponent strength) is the foundational metric in modern college basketball analytics. KenPom, Bart Torvik, and EvanMiya all build from this base, and PBP data improves the accuracy of possession counting over box-score formulas.
- **Shot-quality models** (ShotQuality) use computer vision to track all 10 players' positions at the moment of each shot, incorporating ~100 variables. Their shot-probability-based PPP metric outperforms traditional stats even after a single game.
- **Player-level impact from PBP** (EvanMiya's Bayesian Performance Rating) combines Regularized Adjusted Plus-Minus (RAPM) from possession-level lineup data with box-score priors in a Bayesian framework, capturing intangible contributions invisible in box scores.
- **Tracking data from broadcast video** (Stats Perform / Sloan 2020) generated features from 650,000+ college basketball possessions and showed tracking-based models substantially outperform PBP-only models (log-loss 0.30 vs. 0.40), which in turn outperform box-score models.
- **Win probability models** built on PBP data (ncaahoopR) enable game-flow analysis, excitement indices, and identification of clutch moments, providing features useful for tournament prediction.
- **Transition offense** produces roughly 1.11 points per shot vs. 0.994 in half-court sets---about an 8-point-per-game difference in Division I---highlighting the value of play-type decomposition only possible with PBP data.

**Data sources for PBP:** ESPN play-by-play logs (scraped via ncaahoopR), NCAA's official PBP feeds (available since 2010), Stats Perform tracking data (proprietary, generated via computer vision from broadcast video), ShotQuality proprietary data, and BigDataBall game log datasets.

---

## Source 1: ShotQuality -- Shot-Level Probability Modeling with Computer Vision

- **URL:** https://shotqualitybets.com/stats-explained
- **Also:** https://shotquality.com
- **Data granularity:** Individual shot level, with player positions for all 10 players at the moment of each shot
- **Data source:** Proprietary computer vision system that extracts player location and identity from broadcast video for NCAA, NBA, and WNBA games

### Features Derived from Play-by-Play

The ShotQuality shot probability model uses up to **100 variables** organized into five categories:

1. **Defensive Distance:** Closest defender distance, number of defenders within 5 feet, team defensive ability, "crowding effects" (defensive presence affecting shot quality even without direct contest)
2. **Shooter Ability & Performance:** Career shooting history by shot type, weighted toward recent performance. Free throw ability informs jump shot predictions. Transfers to elite shooting programs trigger contextual adjustments.
3. **Play Type Descriptors:** Transition (+4.8% increase over non-transition), pick-and-roll, cuts, drives, post-ups. Identifies "rushed" late-shot-clock situations.
4. **Shot Type Descriptors:** Catch-and-shoot vs. off-the-dribble, hand dominance, shot distance, dunks
5. **Key Inferences:** Handles missing data via position/height correlations, team-level shooting quality, shot volume patterns

### Modeling Approach

Produces a shot probability for every shot attempt, then aggregates to ShotQuality Points Per Possession (SQ PPP). This metric acts as a "luck-adjusted" efficiency measure.

### Improvement Over Box Score

After just **one game**, ShotQuality's predictions are a "consistently better predictor" of future performance compared to traditional box-score metrics. The advantage grows throughout the season because shot quality stabilizes faster than shooting percentage.

---

## Source 2: EvanMiya -- Bayesian Performance Rating (BPR)

- **URL:** https://blog.evanmiya.com/p/bayesian-performance-rating
- **Also:** https://evanmiya.com
- **Data granularity:** Possession-level, with lineup tracking (which 10 players are on the court for each possession)
- **Data source:** NCAA Division I play-by-play data, all games

### Features Derived from Play-by-Play

- **Possession outcomes:** Points scored per possession, with all 10 players on the court identified
- **Lineup-specific performance:** How each combination of players performs offensively and defensively
- **On-court impact:** Player's effect on team scoring rate when on vs. off the court

### Modeling Approach

BPR uses **Bayesian linear regression** combining three components:

1. **RAPM (Regularized Adjusted Plus-Minus):** A regression on possession-level data where each player has an offensive and defensive coefficient. The model solves: `E[Points] = intercept + sum(offensive_coefficients) - sum(defensive_coefficients)` for all 10 players on the court.

2. **Box BPR (Box Plus-Minus):** A college-specific box-score model trained on D1 data to determine which box-score statistics best predict overall impact at the college level. This differs from NBA-derived formulas.

3. **Bayesian Priors:** Each player's Box BPR serves as the prior mean for their RAPM coefficient. This is the key innovation---it stabilizes RAPM estimates (which are noisy with small samples) using box-score information as a starting point.

The final BPR is interpreted as "the number of offensive [or defensive] points per 100 possessions above D1 average expected by the player's team if the player were on the court with 9 other average players."

### Improvement Over Box Score

BPR captures contributions invisible in box scores: defensive positioning, screen-setting, spacing, leadership effects. The Bayesian framework makes it more stable than pure RAPM early in the season while still converging to true on-court impact as data accumulates. Preseason priors incorporate recruiting profiles, previous seasons, and transfer status.

---

## Source 3: Stats Perform -- Tracking Data from Broadcast Video (Sloan 2020)

- **URL:** https://www.sloansportsconference.com/research-papers/predicting-nba-talent-from-enormous-amounts-of-college-basketball-tracking-data
- **Paper:** Patton, Scott, Walker, Ottenwess, Power, Cherukumudi, Lucey (Stats Perform)
- **Data granularity:** Frame-level tracking data (player positions every frame) aggregated to possession-level features
- **Data source:** Computer vision applied to broadcast video of college basketball games; 650,000+ possessions, 300+ million broadcast frames

### Features Derived from Tracking Data

- **Play type detection:** Neural network classifiers for postups, drives, isolations, ball-screens, handoffs, off-ball-screens (recall: 0.8, precision: 0.7)
- **Spatial features:** Player positioning, movement patterns, court coverage
- **Possession-level outcomes:** Points per possession by play type, by player involvement

### Modeling Approach

- Used machine learning models (details in full paper) with **Shapley values** for interpretability
- Task: Predict probability of a college player making the NBA
- Compared tracking-derived features vs. play-by-play features vs. box-score features

### Improvement Over Box Score / Play-by-Play

This is the clearest quantitative evidence of the data hierarchy:

| Data Source | Log-Loss |
|-------------|----------|
| Tracking data | **0.30** |
| Play-by-play data | 0.40 |

Tracking data reduces prediction error by 25% compared to play-by-play alone. The implication for March Madness prediction: even if full tracking data is not available, PBP data still represents a meaningful upgrade over box scores, and any tracking-derived features (like ShotQuality's) add further value.

---

## Source 4: ncaahoopR -- Play-by-Play Infrastructure and Win Probability Modeling

- **URL:** https://github.com/lbenz730/ncaahoopR
- **Blog:** https://lukebenz.com/post/ncaahoopr_win_prob/
- **Data granularity:** Event-level play-by-play (every action in a game: shots, rebounds, turnovers, fouls, substitutions)
- **Data source:** ESPN play-by-play logs, scraped and returned in tidy format

### Features Derivable from Play-by-Play

- **Shot location data:** x/y coordinates normalized to half-court
- **Assist networks:** Graph-based ball movement analysis with edge weights reflecting assist frequency
- **Win probability trajectories:** Real-time probability of winning at each game event
- **Lineup analysis:** Filter PBP data to specific player combinations for lineup-specific efficiency
- **Game flow metrics:** Score differential trends, excitement indices, momentum indicators
- **Possession efficiency:** Points per possession by lineup, by game segment

### Win Probability Model

Luke Benz's model uses **logistic regression** with time-varying coefficients:

- **Inputs:** Score differential and pre-game point spread
- **Key innovation:** Fits separate logistic regressions over overlapping time windows with 90% overlap, using shrinking intervals near game end (100 seconds early, 1 second late)
- **Smoothing:** LOESS smoothing on coefficient estimates across time
- **Training data:** ~10,949 games from 2016-18 seasons
- **Finding:** Pre-game spreads diminish in predictive importance as the game progresses; score differential becomes increasingly influential

### Application to Prediction

Win probability models derived from PBP enable:
- Identification of **clutch performance** (player usage in high-leverage moments)
- **Close game analysis** (how teams perform in tight situations, relevant for March Madness)
- **Excitement index** as a proxy for game competitiveness/volatility
- Pre-scraped historical data available in companion repository (ncaahoopR_data)

---

## Source 5: The Power Rank / Data Action Lab -- Possession-Based Efficiency Framework

- **URL (Power Rank):** https://thepowerrank.com/cbb-analytics/
- **URL (Data Action Lab):** https://www.data-action-lab.com/2021/11/21/predictive-analytics-in-college-basketball/
- **Data granularity:** Possession-level (aggregated from box scores and PBP)
- **Data sources:** Sports Reference, Team Rankings, KenPom, Bart Torvik

### Possession Estimation and PBP

The standard box-score formula for possessions is:

```
POSS = FGA - OREB + TO + (0.475 * FTA)
```

The free throw multiplier (0.475) was **derived using play-by-play data** by KenPom, improving on earlier estimates of 0.4 (Oliver) and 0.44 (Hollinger). PBP data enables more precise possession counts by directly observing when possessions start and end, and by filtering out end-of-game garbage-time possessions with intentional fouls.

### Four Factors Framework

Dean Oliver's Four Factors decompose offensive efficiency into components, explaining **98% of the variance** in offensive efficiency:

1. **Effective Field Goal %** (eFG%): `(FG + 0.5 * 3P) / FGA` (~50% average)
2. **Offensive Rebounding Rate:** `OREB / (OREB + opponent DREB)` (~28%)
3. **Turnover Rate:** `TO / POSS` (~19%)
4. **Free Throw Rate:** `FTA / FGA` (~32%)

### Modeling Approach

- **KenPom's least squares method:** Solves for 706 variables simultaneously (offensive and defensive ratings for 353 D1 teams), minimizing prediction error in points per possession. Recent games weighted more heavily.
- **Binomial distribution approach** (Data Action Lab): Treats each possession as a Bernoulli trial (score or don't score), calculates expected tempo for matchups, adjusts efficiencies for opponent strength, and derives variance via `sigma^2 = np(1-p)`.
- **Predictions:** If Team A's offense is +15 above average and Team B's defense is +10 above average (per 100 possessions), the prediction is +5 for Team A's offense in that matchup.

### Improvement Over Box Score

PBP data specifically improves:
- Possession count accuracy (the 0.475 multiplier vs. cruder estimates)
- Removal of non-representative possessions (garbage time, intentional fouls)
- More accurate tempo estimation between teams

---

## Source 6: Transition Offense/Defense and Play-Type Analytics

- **Sources:** Hoop-Math (hoop-math.com), CBB Analytics (cbbanalytics.com), various coaching analytics
- **Data granularity:** Play-type level (transition vs. half-court, broken down by shot type)

### Key Findings

- **Transition offense** in Division I averages **1.11 points per shot** vs. **0.994 in half-court** sets
- This difference accounts for approximately **8 points per game** in an average D1 game
- Teams that can generate more transition opportunities (via turnovers forced, defensive rebounding) gain a significant efficiency edge
- Play-type decomposition is **only possible with PBP data**---box scores cannot distinguish transition from half-court possessions

### Relevance to March Madness Prediction

- Tournament games often feature unfamiliar matchups where tempo mismatches create prediction value
- Teams that derive disproportionate value from transition may be more or less effective depending on opponent pace
- Clutch performance (usage rate in close-game, late-clock situations) can only be measured through PBP event data

---

## Cross-Cutting Themes

### Data Hierarchy for Prediction Quality

```
Box Scores < Play-by-Play < Tracking/Spatial Data
```

Each level adds information the previous level cannot capture. The Stats Perform paper provides the clearest quantitative evidence (log-loss improvement from 0.40 to 0.30 going from PBP to tracking).

### What PBP Adds Beyond Box Scores

| Capability | Box Score | Play-by-Play | Tracking |
|---|---|---|---|
| Points, rebounds, assists | Yes | Yes | Yes |
| Possession count (accurate) | Approximate | Yes | Yes |
| Lineup-specific performance | No | Yes | Yes |
| Play type breakdown (transition, PnR) | No | Partial | Yes |
| Shot context (contested, open) | No | No | Yes |
| Player positioning/spacing | No | No | Yes |
| Win probability / clutch moments | No | Yes | Yes |
| Tempo-free efficiency | Approximate | Accurate | Accurate |

### Practical Data Sources for NCAA PBP

| Source | Access | Coverage | Notes |
|---|---|---|---|
| ESPN PBP (via ncaahoopR) | Free / scraping | All D1 games | Event-level, includes shot locations |
| NCAA official PBP | Limited | All D1 since 2010 | Used by KenPom for possession calibration |
| BigDataBall | Paid | D1 game logs | Includes odds data |
| ShotQuality | Paid/API | NCAA + NBA | Shot-level with spatial data |
| Stats Perform tracking | Proprietary | Varies | Generated from broadcast CV |
| EvanMiya | Subscription | All D1 | Player/lineup ratings derived from PBP |
| KenPom | Subscription | All D1 | Team-level efficiency from PBP-calibrated formulas |
| Bart Torvik (T-Rank) | Free | All D1 | Similar to KenPom, open access |

### Key Takeaways for March Madness Modeling

1. **Possession efficiency is the foundation.** Any model should use tempo-free, opponent-adjusted efficiency metrics rather than raw per-game stats.
2. **PBP-derived features add real value:** lineup data, play-type breakdowns, clutch performance, and accurate possession counts all improve predictions beyond what box scores offer.
3. **Shot quality models (ShotQuality) stabilize faster** than raw shooting stats, which matters when projecting teams into March Madness matchups they haven't seen before.
4. **Player-level PBP impact (BPR/RAPM)** captures contributions invisible in box scores---critical for evaluating teams that may rely on players whose value comes from defense, spacing, or screen-setting.
5. **Tracking data is the frontier** but remains largely proprietary. The best publicly available approach combines PBP-derived features (ncaahoopR, KenPom, EvanMiya) with shot-quality metrics where available.
6. **Transition efficiency and play-type data** are underutilized in most public bracket models and represent a potential edge.
