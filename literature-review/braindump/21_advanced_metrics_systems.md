# Advanced Metrics Systems for NCAA Basketball Prediction

## Summary

The college basketball analytics ecosystem is built around several comprehensive rating systems that measure team quality through **tempo-free, possession-based efficiency metrics**. The foundational idea shared across all major systems is adjusting raw offensive and defensive efficiency (points per 100 possessions) for opponent strength. Where the systems diverge is in their specific adjustment methods (additive vs. multiplicative), weighting schemes (recency bias, blowout discounting), data granularity (box score vs. play-by-play vs. shot-level), and supplementary features.

**Key systems reviewed:**

| System | Creator | Core Approach | Data Access | Unique Angle |
|--------|---------|---------------|-------------|--------------|
| **KenPom** | Ken Pomeroy | Least-squares adjusted efficiency | $24.95/year (basic free) | Gold standard; NCAA committee reference; additive model since 2017 |
| **T-Rank (Bart Torvik)** | Bart Torvik | Adjusted efficiency + Barthag | Free | Recency weighting; GameScript; rich free tooling |
| **Haslametrics** | Erik Haslam | Play-by-play efficiency + shot selection | Free | Garbage-time filtering; play-by-play data for 90%+ of games |
| **TeamRankings** | TeamRankings.com | Ensemble of 6 models | Paid (subscription tiers) | Multi-model approach; includes ML decision trees and simulation |
| **EvanMiya** | Dr. Evan Miyakawa | Bayesian Performance Rating (player-level) | Blog free; site has paid tier | Player-level ratings aggregated to team; Bayesian methods |
| **ShotQuality** | Simon Gerszberg | Shot-level expected value via computer vision | Paid (premium tiers) | Proprietary shot-tracking data; AI/computer vision |

**Predictive accuracy benchmarks:** KenPom picks correct winners ~58% of the time in games with projected margins of 5 points or fewer. T-Rank reported 73.5% favorite accuracy in 2018-19 with a mean absolute error of 9.0 points. A well-tuned LightGBM model using multiple rating systems as inputs achieved 77.6% accuracy on the 2025 NCAA tournament, suggesting that ensembling across systems adds value.

---

## Source 1: KenPom Ratings Explanation and Methodology Update

**URLs:**
- [Ratings Explanation (kenpom.com)](https://kenpom.com/blog/ratings-explanation/)
- [Ratings Methodology Update (kenpom.com)](https://kenpom.com/blog/ratings-methodology-update/)
- [KenPom Rankings Explained (Sports Illustrated)](https://www.si.com/college-basketball/kenpom-rankings-explained-who-is-ken-pomeroy-what-do-rankings-mean)

### Background

Ken Pomeroy is a former meteorologist (National Weather Service, 12 years) who created kenpom.com, now college basketball's premier statistical archive dating back to 2002. His metrics are used by the NCAA tournament selection committee, ESPN broadcasts, and coaching staffs.

### Methodology Details

**Core metric: Adjusted Efficiency Margin (AdjEM)**

AdjEM = Adjusted Offensive Efficiency - Adjusted Defensive Efficiency

This represents how many points a team would outscore an average D-I team per 100 possessions.

**Possession estimation formula:**

```
Possessions = FGA - OREB + TO + (0.475 * FTA)
```

The 0.475 multiplier is specific to the college game (differs from the NBA coefficient).

**Opponent adjustment (current additive approach, post-2017):**

In the updated additive model, the effects of two competing teams are considered additive. If Team A's offense is 10% above average and Team B's defense is 10% above average, the expected outcome is the national average (the effects cancel). This replaced an older multiplicative approach.

**Opponent adjustment (historical multiplicative approach):**

```
Game Adj. OE = Raw OE * (National Avg / Opponent's Adj. DE)
```

Game-level adjusted efficiencies are averaged with recency weighting to produce final ratings.

**Least squares method:** The system simultaneously calculates 706 variables (offensive and defensive ratings for all 353 D-I teams) to minimize error between predicted and actual game results.

**Preseason weighting:** Early in the season, prior-year data is incorporated as a Bayesian prior. This phases out as conference play generates sufficient sample size.

### Key Metrics on the Site

- **AdjOE / AdjDE**: Adjusted offensive/defensive efficiency per 100 possessions
- **AdjEM**: Net rating (the primary ranking metric)
- **AdjTempo**: Adjusted pace of play
- **Luck**: Deviation between actual winning percentage and expected results based on efficiency (identifies teams over/underperforming their metrics)
- **Strength of Schedule**: Composite opponent quality

### Accuracy

- Correct winner in 58.2% of games with projected margin <= 5 points
- NCAA tournament: 54.1% (20-17) in close games (margin <= 5)
- Jordan Sperber's research found KenPom predictions differed by less than 1 point per 100 possessions from actual results in extreme matchup scenarios

### Data Access

- Basic rankings visible for free at kenpom.com
- Advanced stats and historical data require $24.95/year subscription
- Does NOT account for injuries (ratings only change when game results reflect player absence)

---

## Source 2: Bart Torvik T-Rank

**URLs:**
- [T-Rank (barttorvik.com)](https://barttorvik.com/trank.php)
- [Torvik Ratings Guide (OddsShark)](https://www.oddsshark.com/ncaab/what-are-torvik-ratings)
- [T-Rank FAQ (Adam's WI Sports Blog)](http://adamcwisports.blogspot.com/p/every-possession-counts.html)

### Methodology Details

**Core calculation:** Like KenPom, T-Rank measures offensive and defensive efficiency as points per possession (PPP), adjusted for opponent quality and venue.

**Adjustment formula:**

```
Game Adj. OE = PPP_observed / (Opponent's Adj. DE / Average PPP)
```

Home/road adjustments of +/- 1.4% are applied.

**Barthag:** The system's signature metric. Uses Bill James' Pythagorean expectation formula with an exponent of 11.5 to estimate a team's win probability against an average D-I opponent on a neutral court. Produces a value between 0 and 1.

**Key difference from KenPom:** T-Rank maintains the **multiplicative** Pythagorean calculation approach, while KenPom switched to an additive efficiency margin model after 2017.

### Unique Features

1. **Recency weighting scheme:**
   - Games within 40 days: 100% weight
   - 40-80 days old: lose 1 percentage point per day
   - 80+ days old: fixed at 60% weight

2. **GameScript adjustment:** Derived from play-by-play data, measures average lead/deficit while filtering out garbage time. This captures whether a team tends to play from ahead or behind.

3. **Blowout discounting:** Large victories against weak opponents receive reduced weight to prevent schedule inflation.

4. **Preseason component:** Incorporated but phases out after approximately 13-16 adjusted games.

5. **TourneyCast:** Monte Carlo simulation tool for bracket prediction.

6. **T-Ranketology:** Bracket projection tool.

### Accuracy

- 2018-19 season through March: 73.5% favorite accuracy
- Mean absolute error: 9.0 points for scoring margins
- Mean absolute error: 13.8 for totals
- Listed as an NCAA Selection Committee reference tool

### Data Access

- **Entirely free.** All ratings, tools, historical data, and simulations are available without charge.
- Considered the most generous free resource in college basketball analytics.

---

## Source 3: Haslametrics

**URL:** [Haslametrics About Page](https://haslametrics.com/about.php)

### Methodology Details

**Core metric:** All-play percentage -- estimated favored-to-win percentage vs. every other D-I team. Efficiency is calculated as points scored per 100 trips upcourt vs. the average opponent.

**Data source distinction:** Erik Haslam uses **play-by-play logs** for over 90% of games, claiming this provides more informative statistics than box-score-only approaches.

### Unique Features

1. **Garbage-time filtering:** Truncates data from portions of games deemed mathematically decided, preventing bench player statistics from contaminating analysis. This is a meaningful methodological choice -- most other systems either don't filter or use cruder blowout-discounting approaches.

2. **Shot selection analysis:** Tracks frequency, distance from basket, location, and defensive context for shooting performance. Breaks down field goal %, three-point %, mid-range %, and near-proximity %.

3. **Time-dependent vs. time-independent views:** Users can toggle between recent-game-weighted ratings or equally-weighted season-long assessments.

4. **Preseason baselines (since 2020-21):** Incorporate team prestige, prior season ratings, player transfers, recruiting scores, and coaching changes.

5. **Additional metrics:** Pace, momentum, consistency, strength of schedule, record quality, and away-from-home ratings.

### Data Access

- **All data is free.** The site explicitly states: "The data displayed on this site is free of charge."
- Less polished interface than KenPom or Torvik, but valued for its unique play-by-play-derived insights.

---

## Source 4: TeamRankings -- Multi-Model Ensemble

**URL:** [Under the TeamRankings Hood, Part 4](https://www.teamrankings.com/blog/ncaa-basketball/under-the-teamrankings-hood-part-4-models-models-everywhere)

### Methodology Details

TeamRankings is unique among the major systems in that it explicitly runs **six different statistical models** and presents them individually rather than blending into a single number.

#### The Six Models

1. **Predictive Power Ratings Model**
   - Iterative algorithm analyzing all D-I game results
   - Produces margin-of-victory expectations adjusted for location and opponent strength
   - Limitation: Reacts slowly to injuries or sudden team changes

2. **Similar Games Model**
   - Finds historical tournament games with statistically comparable teams
   - Incorporates power ratings, team statistics, travel distances, game timing, and Vegas lines
   - Weakness: Struggles with uncommon matchup scenarios

3. **Simulation Model**
   - Possession-based (tempo-free) efficiency statistics
   - Projects possession-by-possession outcomes
   - "Bottoms up" analysis of playing styles and matchup dynamics
   - Limitation: Assumes consistent playing style

4. **Decision Tree Model (Machine Learning)**
   - ~100 different decision tree models with results averaged
   - Analyzes games since 1999 with hundreds of input variables
   - Claimed to be "most accurate model" though performance varies by sport
   - Weakness: Opaque explanations; historical trends may not apply to modern game

5. **Vegas Implied Model**
   - Treats betting lines as efficient market predictions
   - Rapidly adjusts to market reactions (injuries, suspensions)
   - Risk: Vulnerable to public bias

6. **Seed Difference Model (tournament only)**
   - Historical outcomes by seed matchups since 1998
   - Identifies selection committee inefficiencies

### Preseason Ratings

Two-stage regression model:
- Stage 1: Prior-year predictive ratings + player stats + recruiting data
- Stage 2: Adds transfer portal information

Training data goes back to 2007-08.

### Data Access

- Paid subscription service with multiple tiers
- Some basic rankings visible for free
- Bracket prediction tools and detailed matchup analysis behind paywall

---

## Source 5: EvanMiya -- Player-Level Bayesian Approach

**URLs:**
- [EvanMiya.com](https://evanmiya.com/)
- [Bayesian Performance Rating (EvanMiya Blog)](https://blog.evanmiya.com/p/bayesian-performance-rating)
- [About EvanMiya Blog](https://blog.evanmiya.com/about)

### Background

Created by Dr. Evan Miyakawa (Ph.D., Baylor, 2022). Featured in Sports Illustrated, CBS Sports, ESPN, and the AP.

### Methodology Details

**Core innovation: Bayesian Performance Rating (BPR)**

Unlike KenPom/Torvik which are fundamentally team-level systems, EvanMiya is built from **player-level ratings** up. BPR combines three model types:

1. **Box BPR:** Trained specifically on D-I data to determine which statistical skills are most valuable at the college level. More accurate than generic box-score models because it's college-specific.

2. **Adjusted Plus-Minus (RAPM):** Measures on-court impact from play-by-play data, controlling for teammates and opponents.

3. **Bayesian integration:** Uses box score values as informed priors for the plus-minus model via Bayesian linear regression, allowing the models to reinforce each other rather than compete.

**Player Skill Projections:** Uses a dynamic linear model (DLM) trained on 10+ years of game-by-game data for every D-I player. Adjusts for opponent strength, offensive usage, year-over-year improvement curves, and recent form.

### Unique Features

- Player-level granularity allows for roster-change sensitivity (transfers, injuries)
- Lineup-specific analysis
- "Keys to Victory" automated scouting reports
- "Relative Ratings" for matchup-specific analysis

### Data Access

- Blog articles are free
- Site analytics tools have a paid subscription tier
- Publicly available system accuracy estimated ~2% better than ensemble models using only team-level ratings

---

## Source 6: ShotQuality -- Shot-Level Analytics via Computer Vision

**URLs:**
- [ShotQuality.com](https://shotquality.com)
- [ShotQuality at Colgate University](https://www.colgate.edu/success-after-colgate/entrepreneurship/entrepreneurship-innovation-blog/shotquality-turning-passion)

### Methodology Details

ShotQuality represents a fundamentally different data paradigm: rather than working with box scores or play-by-play logs, it uses **computer vision and AI** to extract shot-level data from game video.

**Key inputs:**
- Defensive distance on each shot
- Shooter ability profiles
- Shot type and location
- Play type analysis

**Scale:** 50M+ data points across NCAA, NBA, and WNBA.

### Unique Features

- **Proprietary shot-tracking data** not available anywhere else -- this is their primary competitive moat
- Measures expected value of every shot taken, allowing "luck adjustment" at the shot level rather than the game level
- Can identify teams that are shooting better or worse than their shot quality suggests (regression candidates)
- Live betting functionality for all NCAA men's basketball games

### Data Access

- Paid subscription with premium tiers
- No free tier for detailed analytics
- Founded by Simon Gerszberg (Colgate University graduate, started 2020)

---

## Source 7: Odds Gods -- Ensemble Model with Detailed Methodology

**URL:** [Predicting College Basketball: A Complete Technical Methodology (Odds Gods Blog)](https://blog.oddsgods.net/predicting-college-basketball-methodology)

### Methodology Details

This source provides a detailed technical writeup of building a prediction model that incorporates multiple rating systems, offering insight into how systems can be combined.

**Model:** LightGBM gradient boosted decision trees, 1,545 trees, trained on ~50,000 D-I games from 2014-2026.

**Input features include:**
- Six external ranking systems used as pairwise differences: KenPom, Massey, NET, Moore, Whitlock, Bihl
- Custom Elo rating with dynamic K-factor, 15% season-to-season regression, and 1.75x boost for cross-conference games
- Efficiency metrics: net rating, offensive rating, defensive rating, offensive rebounding %
- Game context: location, days elapsed in season, 5-game scoring margin differential

**Training weighting:** Early season games (weight 1), late regular season/conference tournament (weight 2), NCAA tournament (weight 6). This deliberately prioritizes tournament accuracy.

### Accuracy Metrics

| Metric | 2024 Validation | 2025 Test | 2025 NCAA Tournament |
|--------|-----------------|-----------|----------------------|
| Accuracy | 71.32% | 72.56% | 77.61% |
| Log Loss | 0.551 | 0.54 | 0.473 |
| Brier Score | 0.187 | 0.183 | 0.153 |
| AUC | 0.788 | 0.8 | 0.8865 |

**Comparison to leading systems:** Trails EvanMiya's publicly available system by ~2%. Trails top Kaggle ensemble models (Brier scores ~0.170-0.175) by 1-1.5 points.

### Unique Contributions

- **Monte Carlo tournament simulation:** 10,000 simulations tracking round-by-round advancement probabilities
- **Dynamic bracket repricing:** Recalculates all probabilities contingent on each user selection
- **Markov-style rankings:** Uses power iteration where "credit" transfers proportionally to opponent difficulty, creating meaningful tier separation

---

## Cross-System Comparison and Key Takeaways

### Methodological Spectrum

The systems can be arranged along a **data granularity spectrum:**

```
Team-level box scores --> Play-by-play logs --> Player-level models --> Shot-level tracking
   KenPom, Torvik         Haslametrics          EvanMiya              ShotQuality
```

TeamRankings spans multiple points on this spectrum through its six-model ensemble.

### Adjustment Approaches

- **Additive (KenPom post-2017):** Team effects are summed. AdjEM is a linear measure where the difference between +31 and +28 equals the difference between +4 and +1.
- **Multiplicative (Torvik, older KenPom):** Team effects are multiplied through the Pythagorean formula. Produces a win probability (Barthag) rather than a point margin.

### Recency Weighting

- **KenPom:** Weights recent games more heavily (specifics less documented)
- **Torvik:** Explicit decay: 100% within 40 days, -1%/day from 40-80 days, 60% floor
- **Haslametrics:** Offers toggle between recency-weighted and equal-weighted views

### Garbage Time / Blowout Handling

- **Haslametrics:** Most aggressive -- truncates play-by-play data when game is mathematically decided
- **Torvik:** Discounts blowout victories; GameScript filters garbage time via play-by-play
- **KenPom:** Less explicit blowout handling

### Preseason Priors

All major systems incorporate some form of preseason prior that phases out:
- **KenPom:** Prior-year data as Bayesian weight, phases out during conference play
- **Torvik:** Phases out after 13-16 adjusted games
- **Haslametrics (since 2020-21):** Team prestige + prior ratings + transfers + recruiting + coaching changes
- **TeamRankings:** Two-stage regression using prior-year ratings, player stats, recruiting, and transfer data
- **EvanMiya:** Player-level priors via Bayesian regression on historical performance

### For Bracket Prediction

The systems tend to agree on most tournament matchups. Where they diverge is typically on:
- Mid-major evaluation (strength of schedule adjustment sensitivity)
- Teams with unusual pace or style
- Teams with significant recent roster changes

The evidence suggests that **ensembling across multiple systems** yields better predictions than relying on any single system, with the Odds Gods analysis showing that using KenPom alongside other ratings as inputs to a gradient-boosted model achieved 77.6% tournament accuracy.

---

## Sources

- [KenPom Ratings Explanation](https://kenpom.com/blog/ratings-explanation/)
- [KenPom Ratings Methodology Update](https://kenpom.com/blog/ratings-methodology-update/)
- [KenPom Rankings Explained (SI)](https://www.si.com/college-basketball/kenpom-rankings-explained-who-is-ken-pomeroy-what-do-rankings-mean)
- [Understanding Efficiency Margin (Rock M Nation)](https://www.rockmnation.com/2021/1/4/22211605/advanced-analytics-understanding-efficiency-margin-adjusted)
- [The Ultimate Guide to Predictive College Basketball Analytics (The Power Rank)](https://thepowerrank.com/cbb-analytics/)
- [Torvik Ratings Guide (OddsShark)](https://www.oddsshark.com/ncaab/what-are-torvik-ratings)
- [T-Rank FAQ (Adam's WI Sports Blog)](http://adamcwisports.blogspot.com/p/every-possession-counts.html)
- [Haslametrics About](https://haslametrics.com/about.php)
- [TeamRankings Hood Part 4](https://www.teamrankings.com/blog/ncaa-basketball/under-the-teamrankings-hood-part-4-models-models-everywhere)
- [TeamRankings Preseason Rankings Explained](https://www.teamrankings.com/blog/ncaa-basketball/preseason-rankings-ratings-explained)
- [Bayesian Performance Rating (EvanMiya Blog)](https://blog.evanmiya.com/p/bayesian-performance-rating)
- [ShotQuality](https://shotquality.com)
- [Predicting College Basketball Methodology (Odds Gods)](https://blog.oddsgods.net/predicting-college-basketball-methodology)
- [Top Bracket Picks: KenPom, Haslametrics, Torvik, ShotQuality (The Lines)](https://www.thelines.com/best-expert-bracket-picks-college-basketball-metrics-march-madness-kenpom-torvik-haslametrics-shotquality-2025/)
- [KenPom vs Sagarin (SportsBettingDime)](https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/)
