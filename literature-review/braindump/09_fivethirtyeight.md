# FiveThirtyEight's March Madness Model: Methodology, Evolution, and Accuracy

## Summary

FiveThirtyEight (now under ABC News, with Nate Silver continuing independently via Silver Bulletin) has produced probabilistic NCAA tournament forecasts since 2011, making it one of the longest-running public March Madness prediction models. The core approach is an **ensemble method**: blending multiple computer power rating systems into a single composite rating, then using that composite to simulate the tournament thousands of times and produce round-by-round advancement probabilities for every team.

Key takeaways from the research:

- **Ensemble of ratings**: The model has always combined multiple independent rating systems (historically 5-6 for men's, 4 for women's) rather than relying on a single metric, on the theory that blending smooths out idiosyncratic errors that compound in single-elimination formats.
- **Elo as a backbone**: FiveThirtyEight built its own Elo ratings for college basketball (men's back to the 1950s, women's back to 2001), which serve as one component of the ensemble.
- **Adjustments matter**: The model incorporates injury/suspension adjustments (via Win Shares), travel distance effects, and in-tournament performance updates.
- **Accuracy is solid but bounded**: The model typically achieves ~70% game-level accuracy and competitive Brier scores, but performance degrades in later rounds and is subject to the fundamental reality that many tournament games are near coin-flips. The Harvard Sports Analysis Collective has argued that "statistically predicting the NCAA tournament is largely a fool's errand" and that the gap between a good bracket and a great bracket is mostly luck.
- **The model has evolved significantly**: From a simpler composite in 2011 to its current form, the model has changed its component ratings, weighting schemes, and technical infrastructure. Nate Silver's post-FiveThirtyEight version (Silver Bulletin) now uses proprietary COOPER/SBCB ratings with 5/8 weight to COOPER and 3/8 to KenPom, runs 100,000 simulations (upgraded from Excel-based calculations), and leverages AI tooling.

---

## Source 1: FiveThirtyEight Methodology Page

**Title:** How Our March Madness Predictions Work
**URL:** https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
**Also:** https://fivethirtyeight.com/features/how-our-march-madness-predictions-work/

### Methodology Details

**Men's Model — Six Rating Systems:**
1. Ken Pomeroy's ratings (KenPom)
2. Jeff Sagarin's Predictor ratings
3. Sonny Moore's ratings
4. Joel Sokol's LRMC ratings (Logistic Regression Markov Chain)
5. ESPN's Basketball Power Index (BPI)
6. FiveThirtyEight's own Elo ratings

These six are blended into a single composite. The rationale: "each system has different features and bugs, and blending them helps to smooth out any rough edges that matter because even small differences can compound over the course of a single-elimination tournament."

**Human rankings** comprise one-fourth of the final rating:
- NCAA selection committee's 68-team S-curve
- AP and coaches' preseason rankings
- Previous season's Sagarin ratings (reverted to mean) for unranked teams

**Women's Model — Four Systems:**
- Sokol's LRMC, Moore's, Massey Ratings, and FiveThirtyEight's women's Elo. The NCAA does not publish women's S-curve data, so seeds are used instead.

### Key Adjustments

- **Injuries/Suspensions:** Point deductions based on Sports-Reference.com's Win Shares, which estimate player contributions while adjusting for schedule strength (prevents overvaluing players who pad stats against weak opponents).
- **Travel Distance:** Accounts for how far teams travel to game sites, treating extreme cases as equivalent to home/road games. (Removed for 2021 bubble tournament.)
- **In-Tournament Updates:** Winning teams receive rating bonuses based on score and opponent quality.

### Probability Formula

Uses an Elo-derived logistic formula:

```
P(win) = 1.0 / (1.0 + 10^(-travel_adjusted_power_rating_diff * 30.464 / 400))
```

Multi-round advancement uses conditional probabilities: the probability of reaching round N equals the probability of winning in round N-1 multiplied by the probability of reaching round N-1.

### Elo Rating Details

- Calculated game-by-game from historical data (men's since 1950s, women's since 2001)
- Incorporates final scores and game location
- Tournament games weighted slightly higher than regular season ("there are actually fewer upsets in the tournament than you'd expect")
- At season start, teams retain prior-year Elo but with reversion to conference mean

### Live Updates

During games, logistic regression uses: time remaining, score differential, pregame win probabilities, possession data, and free-throw information.

---

## Source 2: FiveThirtyEight Historical Accuracy Self-Assessment

**Title:** How FiveThirtyEight's NCAA Tournament Forecasts Did
**URL:** https://fivethirtyeight.com/features/how-fivethirtyeights-ncaa-tournament-forecasts-did/

### Accuracy Metrics

- **Game-level accuracy:** ~70% if using pre-tournament probabilities to build a straight bracket
- **Against Vegas lines:** 26-31 overall record placing hypothetical bets on differences between FiveThirtyEight's implied spreads and Vegas. In the Round of 64: 17-13, and 5-2 when perceived edge was 3+ points.
- **Brier Score ranking:** Third overall among major prediction models in the assessed year. The Power Rank ranked first, NumberFire second (leaning heavily on favorites).

### Performance Patterns

- Model starts strong in early rounds but weakens as the tournament progresses (fewer games, more variance, harder to distinguish between elite teams)
- All tested models outperformed the "chalk model" (always picking higher seeds)
- Slight overconfidence detected in specific probability ranges: teams predicted at 25-30% and 80-85% win probability performed better than forecasted

### Brier Score Historical Range

- **Best men's Brier score:** Not explicitly stated, but performance tracked since 2014
- **Worst men's Brier score:** 0.212 in 2021 ("the worst since we started predicting March Madness in 2014"), a year when favorites won only 62.7% of games ("easily the lowest for any year in our sample")
- **Women's Brier scores:** Best was 0.107 (2015), worst was 0.162 (2018), with 0.133 in 2021 and 0.118 in 2019

### Data Sources Referenced

FiveThirtyEight publishes historical forecast data on GitHub:
https://github.com/fivethirtyeight/data/blob/master/historical-ncaa-forecasts/historical-538-ncaa-tournament-model-results.csv

---

## Source 3: Nate Silver's Post-FiveThirtyEight Model (Silver Bulletin, 2025-2026)

**Title:** 2025 March Madness Predictions / 2026 March Madness Bracket Predictions
**URLs:**
- https://www.natesilver.net/p/2025-march-madness-ncaa-tournament-predictions
- https://www.natesilver.net/p/2026-march-madness-ncaa-tournament-predictions

### Evolution from FiveThirtyEight

After leaving FiveThirtyEight, Nate Silver rebuilt the model under Silver Bulletin with significant changes:

**2025 Version:**
- New proprietary rating: **SBCB (Silver Bulletin College Basketball)**, recalibrated on 250,000+ historical games
- Weighting: 50% SBCB, 50% composite of external systems (KenPom, Sonny Moore, ESPN BPI, Massey, NCAA S-Curve)
- Described as a "Bayesian" rating system

**2026 Version:**
- Rating renamed to **COOPER**
- Weighting shifted: **5/8 COOPER, 3/8 KenPom** (simplified from the broader ensemble)
- Infrastructure: Upgraded from Excel-based calculations to code running **100,000 simulations**
- AI tools used to help "smooth out some of the code's rough patches"

### Key Methodology Details

- Injury handling improved with timeline-based adjustments (e.g., adjusting expected return dates dynamically)
- Travel distance effects still incorporated
- In-tournament over/underperformance tracked and used predictively ("often fairly predictive")
- Model updates daily during tournament play

### Insights

The shift from a broad ensemble (6 systems) to a narrower blend (COOPER + KenPom) represents a philosophical evolution: Silver appears to trust his proprietary rating enough to give it dominant weight, while keeping KenPom as a strong external check. The move away from Excel to proper simulation code is a meaningful technical upgrade enabling more sophisticated scenario modeling.

---

## Source 4: Harvard Sports Analysis Collective — Critiques

**Title:** Bracketology (various posts)
**URL:** https://harvardsportsanalysis.org/tag/bracketology/

### Core Critique

> "Statistically predicting the NCAA tournament, despite what FiveThirtyEight and others may tell you, is largely a fool's errand."

### Key Arguments

1. **Most games are near coin-flips:** From a statistical standpoint, the margin between teams in most tournament matchups is small enough that outcomes are dominated by randomness.
2. **Luck vs. skill ceiling:** "The difference between a good bracket and a great bracket is luck." Statistical models can separate poor predictions from competent ones, but distinguishing excellent brackets from merely good ones relies on chance.
3. **Diminishing returns of complexity:** The "Balance Wins Championships" analysis suggests successful teams demonstrate versatility across multiple dimensions, implying tournament performance involves complex interactions that simple (or even moderately complex) models may not capture.
4. **Four Factors analysis:** Harvard developed upset-identification methods using efficiency metrics (shooting, turnovers, rebounding), but acknowledged that substantial irreducible uncertainty remains.

### Relevance to FiveThirtyEight

This critique does not argue that FiveThirtyEight's model is bad — rather that the ceiling for any model is low given the fundamental randomness of single-elimination tournaments among relatively evenly matched teams. The ensemble approach and probabilistic framing are the right responses to this reality, but consumers of these predictions should calibrate expectations accordingly.

---

## Source 5: Simplified Replication and Component Analysis

**Title:** March Madness FiveThirtyEight Model Challenge
**URL:** https://www.justinholman.com/2014/03/20/march-madness-fivethirtyeight-model-challenge/

### Key Finding

Justin Holman, using the model as a statistics teaching exercise, replicated FiveThirtyEight's predictions using only **two variables** (NCAA seeding + Sonny Moore's ratings) and achieved R-squared = 0.9398 against Silver's full model output.

### Implication

A substantial portion of the model's predictive power derives from relatively simple factors. The additional complexity (multiple rating systems, injury adjustments, travel distance) provides marginal improvement. This is not necessarily a critique — in tournament prediction, marginal edges compound across rounds — but it suggests that the "heavy lifting" is done by basic team quality measures, with the ensemble and adjustments serving as refinement.

---

## Source 6: Comparative Model Accuracy (KenPom, Sagarin, BPI)

**Title:** Various comparison analyses
**URLs:**
- https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/
- https://melissapprice.com/2021/03/15/comparing-ncaa-ranking-systems/

### KenPom Standalone Performance

- Games with Vegas spread <= 7 points: KenPom correct 60.5% of the time (250/413)
- Games with Vegas spread <= 3 points: Only 52.7% (98/186) — barely above coin-flip
- In 2021 tournament head-to-head: KenPom outperformed Sagarin, BPI, and RPI

### Why FiveThirtyEight Ensembles

These results illustrate why FiveThirtyEight blends multiple systems: no single rating system dominates across all contexts. KenPom is strongest overall but has blind spots. Sagarin captures different signal. BPI adds travel distance, rest days, and altitude. The ensemble approach hedges against any single system's weaknesses.

### BPI Differentiation

ESPN's BPI is described as a "hybrid of RPI and KenPom" that separates itself by factoring in travel distance, days of rest, and altitude — variables that overlap with FiveThirtyEight's own adjustments.

---

## Cross-Cutting Themes

### What Makes the FiveThirtyEight Approach Effective

1. **Ensemble diversity:** Combining independently-developed rating systems reduces model-specific bias
2. **Probabilistic framing:** Presenting probabilities rather than picks acknowledges irreducible uncertainty
3. **Continuous recalibration:** The model has been refined annually based on tracked performance
4. **Adjustments for non-rating factors:** Injuries, travel, and tournament momentum capture real effects that pure ratings miss
5. **Transparency:** Publishing methodology and historical data enables external validation

### What Limits It

1. **Fundamental randomness ceiling:** Single-elimination tournaments among reasonably matched teams have a hard accuracy ceiling that no model can exceed
2. **Late-round degradation:** Model performance drops in later rounds where sample sizes shrink and team quality converges
3. **Injury information asymmetry:** Publicly available injury data may lag behind what teams and Vegas know
4. **Diminishing marginal returns:** Much of the predictive power comes from basic team quality; the elaborate ensemble adds modest improvement over simpler approaches
5. **Calibration drift:** Overconfidence detected in certain probability ranges suggests the model's confidence intervals need periodic adjustment
6. **Post-FiveThirtyEight fragmentation:** With Silver departed and FiveThirtyEight under ABC News, the model's continuity and maintenance are uncertain
