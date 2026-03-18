# Predicting Upsets in the NCAA Tournament

## Summary

Upsets are a defining feature of the NCAA tournament, and understanding what drives them is critical for any bracket prediction model. This review covers historical upset rates by seed matchup, the key team characteristics that correlate with upset potential, and how modelers approach the inherent unpredictability of March Madness.

**Key takeaways:**

- **Upset rates are highly stratified by seed gap.** The 8-9 matchup is essentially a coin flip (48% for the 8-seed). The 5-12 matchup produces upsets ~36% of the time, and the 6-11 matchup at ~36-39%. Upsets of 1, 2, and 3 seeds in the first round are rare (combined 444-36 record historically).
- **The most actionable upset slots are 12 vs. 5, 11 vs. 6, and 10 vs. 7.** These mid-seed matchups each produce upsets roughly one-third of the time.
- **Sweet Sixteen is the round with the highest upset rate (~21%)**, slightly exceeding even the first round (~20%), because mid-seeds that survive the first round face fatigued or overconfident higher seeds.
- **Eight factors consistently appear in upset prediction models**: 3-point dependency, turnover pressure, tempo conflict, experience/roster age, rebounding (especially offensive), free throw shooting, coaching track record, and geography/travel.
- **Tempo is a particularly underrated factor.** Slow-tempo teams (low-60s possessions per 40 minutes) advance ~12% more often than their seed predicts, because controlling pace neutralizes superior talent. High-tempo creates variance -- good for underdogs, bad for favorites.
- **Consistency (low variance in performance) is as important as mean performance** for predicting tournament success. Inconsistent high-seeds are upset-prone; consistent low-seeds are dangerous.
- **Experience matters measurably.** Senior-led teams reach the Sweet 16 at a 28% rate versus 17% for freshman-heavy teams.
- **Even the best models are only ~75% accurate** on individual game outcomes, implying roughly one-quarter of tournament games are genuine toss-ups or upsets.

---

## Source 1: Sports Illustrated -- "Where Do Upsets Happen in the Men's NCAA Tournament?"

**URL:** https://www.si.com/college-basketball/march-madness-brackets-where-do-upsets-happen-in-mens-ncaa-tournament

### Historical Upset Rates by Seed (Round of 64, since 1985)

| Matchup | Higher Seed Record | Higher Seed Win % | Upset Rate |
|---------|-------------------|-------------------|------------|
| 1 vs. 16 | 158-2 | 98.8% | 1.2% |
| 2 vs. 15 | 149-11 | 93.1% | 6.9% |
| 3 vs. 14 | 137-23 | 85.6% | 14.4% |
| 4 vs. 13 | 127-33 | 79.4% | 20.6% |
| 5 vs. 12 | 103-57 | 64.4% | 35.6% |
| 6 vs. 11 | 98-62 | 61.3% | 38.7% |
| 7 vs. 10 | 98-62 | 61.3% | 38.7% |
| 8 vs. 9 | 77-83 | 48.1% | 51.9% |

### Round of 32 Key Vulnerability

- The 3 vs. 6 matchup in the second round is the most upset-prone contest involving a top-3 seed. The 3-seed wins only ~60% of the time, and at least one 3-seed has lost in four of the last five tournaments.
- No. 2 seeds lose in the second round (to 7 or 10 seeds) an average of 1.2 times per tournament.
- Public bias: bracket-fillers overestimate top seeds' Sweet 16 advancement by 9-16 percentage points versus actual historical rates.

---

## Source 2: Basketball.org -- "NCAA First-Round Upsets: Upset Percentage by Seed & Year"

**URL:** https://www.basketball.org/stats/ncaa-first-round-upsets/

### Comprehensive Upset Data (1985-2025)

| Matchup | Games | Upsets | Upset % |
|---------|-------|--------|---------|
| 16 vs. 1 | 160 | 2 | 1.25% |
| 15 vs. 2 | 160 | 11 | 6.88% |
| 14 vs. 3 | 160 | 24 | 15.00% |
| 13 vs. 4 | 160 | 33 | 20.63% |
| 12 vs. 5 | 160 | 57 | 35.63% |
| 11 vs. 6 | 160 | 58 | 36.25% |
| 10 vs. 7 | 160 | 60 | 37.50% |
| 9 vs. 8 | 160 | 71 | 44.38% |

### Year-over-Year Patterns

- In 34 of 40 tournaments since 1985, at least one 12-seed has beaten a 5-seed. Exceptions: 1988, 2000, 2007, 2015, 2018, 2023.
- Multiple 12-seed upsets occurred in 2013, 2014, 2019, 2024, and 2025 (two or three 12-seeds winning).
- No clear secular trend toward more or fewer upsets over time -- variance is the constant.
- Average of ~8 upsets per tournament, with a range from 3 (2007) to 14 (2021, 2022).

---

## Source 3: TheSportsGeek -- "March Madness Upsets by Round"

**URL:** https://www.thesportsgeek.com/blog/march-madness-upsets-by-round-study/

### Upset Rates by Round (Since 2003)

| Round | Upset Rate | Games with Upsets |
|-------|-----------|-------------------|
| First Round (R64) | 20.02% | 141 of 704 |
| Second Round (R32) | 19.89% | 70 of 352 |
| Sweet 16 | 21.02% | 37 of 176 |
| Elite 8 | 18.18% | 16 of 88 |
| Final Four | 13.64% | 6 of 44 |
| Championship | 9.09% | 2 of 22 |

### Key Findings

- The Sweet 16 has the highest upset rate of any round at ~21%, slightly above the first two rounds.
- The first and second rounds have nearly identical upset rates (differ by only 0.13 pp), suggesting that surviving the first round does not confer a meaningful advantage in the second.
- Upsets become progressively rarer after the Elite Eight -- the Championship has seen only 2 upsets (by spread) since 2003.
- 2021 was the peak upset year with 19 total upsets; 2025 had an unusually low 9.3% first-round upset rate.

### Modeling Implication

Models should not assume upset probability declines linearly with round. The Sweet 16 spike suggests that mid-seeds that survive early rounds may actually have momentum or matchup advantages that inflate their chances relative to naive seed-based models.

---

## Source 4: ESPN -- "Giant Killers: Most Probable First-Round Upsets"

**URL:** https://www.espn.com/mens-college-basketball/story/_/id/48223542/ncaa-tournament-upsets-first-round-giant-killers-march-madness-2026

### ESPN's Upset Prediction Methodology

ESPN evaluates double-digit seeds for upset potential using several key metrics:

1. **Turnover generation and conversion**: Teams that force turnovers and convert them to points are strong upset candidates. Turnover points per game is a key differentiator.
2. **Three-point shooting dependency**: Teams relying heavily on perimeter shooting (e.g., 43% of scoring from three) create volatility -- they can beat anyone on a hot night or lose to anyone on a cold one. This cuts both ways: a 3-dependent favorite is more vulnerable, and a 3-dependent underdog has higher ceiling variance.
3. **Offensive rebounding / second-chance points**: Directly correlated with upset potential. Second-chance points extend possessions and can neutralize talent gaps.
4. **Defensive efficiency vulnerabilities**: Favorites whose defensive efficiency dropped due to injuries or late-season slumps are flagged as upset targets.

### Historical Context

Only 5 double-digit seeds won in the first round of the 2025 tournament, a below-average year for upsets.

### Practical Modeling Note

ESPN's framework is essentially a matchup-specific analysis rather than a blanket seed-based model. They look at how specific team strengths/weaknesses interact in a given pairing, which is more predictive than seed difference alone.

---

## Source 5: Splash Sports -- "The Ultimate Guide to Predicting March Madness" and "Upset-Proof Your Picks"

**URLs:**
- https://splashsports.com/blog/the-ultimate-guide-to-predicting-march-madness
- https://splashsports.com/blog/upset-proof-your-picks-strategies-to-capitalize-on-march-madness-upsets

### Eight Key Upset Prediction Factors

1. **3-point dependency** -- Teams living and dying by the three create variance; upset-prone when cold, dangerous when hot.
2. **Turnover pressure** -- Low-seed teams that force turnovers can disrupt higher-seed offenses and generate cheap points.
3. **Tempo conflict** -- A major underrated factor. Slow-tempo teams (low 60s possessions/40 min) advance ~12% more than their seed predicts. Controlling pace neutralizes talent advantages.
4. **Experience** -- Senior-led teams reach the Sweet 16 at a 28% rate; freshman-heavy teams at 17%. Veterans handle tournament pressure better.
5. **Rebounding** -- Offensive rebounding extends possessions and limits damage from cold shooting spells.
6. **Free throw rate and accuracy** -- Converting uncontested scoring opportunities matters disproportionately in tight games.
7. **Coach track record** -- Coaches with tournament experience make better in-game adjustments and prepare teams for the unique pressures of the event.
8. **Geography** -- Travel distance and proximity to fan bases affect performance, particularly in early rounds.

### Five Critical Statistical Indicators for Bracket-Busters

1. **Adjusted Defensive Efficiency** -- Teams that prevent scoring opportunities under tournament pressure.
2. **Rebound Rate** -- Capturing rebounds relative to opponents, limiting second-chance points.
3. **Turnover Margin** -- Committing fewer turnovers while forcing opponent mistakes.
4. **Free Throw Percentage** -- Reliable conversion under pressure.
5. **Experience Under Pressure** -- Qualitative measure of clutch performance and veteran leadership.

### Modeling Approach

- Combine advanced analytics (adjusted efficiency, player-level metrics) with real-time data (injuries, momentum, line movement).
- Use Monte Carlo simulation (thousands of tournament simulations) to generate probabilistic forecasts.
- Teams peaking at the right time display "heightened levels of intensity, adaptability, and resilience."

---

## Source 6: University of Kansas -- Professor Templin's Statistical Model

**URL:** https://news.ku.edu/news/article/2017/03/08/professor-develops-statistical-model-predict-ncaa-tournament-winners-based-scoring

### Model Design

Jonathan Templin's model rates all 351 Division I teams on four variables:

1. **Offensive scoring capability** -- Points scored relative to opponents.
2. **Defensive strength** -- Points allowed relative to opponents.
3. **Home court advantage** -- Accounts for neutral-site tournament play by removing this factor.
4. **Consistency** -- How reliably teams maintain offensive and defensive performance across games.

### Key Finding: Consistency is the Critical Factor

The most important predictor is not raw offensive or defensive power, but **consistency**. Teams with high mean performance but high variance are more likely to be upset, because their "off" games coincide with tournament elimination. Conversely, consistent low-seeds are dangerous because their floor is close to their ceiling.

### Upset Identification Strategy

The model identifies upset-prone matchups by finding:
- **Inconsistent high-seeds** with high scoring potential but volatile game-to-game performance.
- **Consistent low-seeds** whose floor performance is competitive with the high-seed's average.

### Methodology

- Simulates 10,000 random tournament brackets.
- Calculates game-winning probabilities accounting for neutral-site play.
- Model accuracy: predicted Kansas 87-85 over Oklahoma State; actual result was 90-85.

---

## Source 7: Georgia Tech -- Logistic Regression / Markov Chain Model (Sokol)

**URL:** https://www2.isye.gatech.edu/~jsokol/ncaa.pdf

### Key Insight on Model Accuracy Limits

Joel Sokol's long-running research on NCAA tournament prediction establishes an important baseline: **the best models today are correct only about 75% of the time**. This implies that roughly one-quarter of tournament games are genuine upsets or toss-ups that no model can reliably predict.

### Modeling Implication

This 75% accuracy ceiling has profound implications:
- Models should not overfit to predict upsets -- the signal-to-noise ratio is inherently low.
- Instead, models should accurately calibrate *probabilities*. A well-calibrated model says a 12-seed has a 35% chance of winning, not that it *will* win.
- The goal is not to predict individual upsets but to identify the *right number* of upsets and place them in the *most likely slots*.

---

## Practical Modeling Implications

### For Building an Upset-Aware Prediction Model

1. **Use seed-based priors, then adjust.** Historical upset rates by seed matchup provide a strong baseline. Layer team-specific adjustments on top.

2. **Key features to include:**
   - Adjusted offensive and defensive efficiency (KenPom-style metrics)
   - Tempo (possessions per game) -- both absolute and the mismatch between teams
   - Roster experience (percentage of minutes played by upperclassmen)
   - Turnover margin and turnover forcing rate
   - Offensive rebounding percentage
   - Free throw rate (FTA/FGA) and free throw percentage
   - 3-point attempt rate and dependency
   - Scoring consistency (standard deviation of scoring margin)
   - Late-season momentum (last 10 games performance vs. season average)

3. **Model variance, not just means.** Consistency (low variance in game-to-game performance) is as predictive as average performance. Include standard deviation of key metrics as features.

4. **Do not assume linear decline in upset probability by round.** The Sweet 16 actually has a *higher* upset rate than the first round. Model each round's dynamics separately.

5. **Calibrate probabilities, do not predict binary outcomes.** A model that says "35% chance of upset" for every 5-12 game is more useful than one that tries to pick *which* 5-12 game will be the upset.

6. **Use heavy-tailed distributions for score differentials.** Normal distributions underestimate the frequency of extreme outcomes. T-distributions or similar heavy-tailed alternatives better capture the fat tails of tournament scoring.

7. **Account for matchup-specific interactions.** Tempo mismatch, 3-point dependency vs. perimeter defense quality, and turnover-forcing vs. ball-security are more predictive than aggregate team ratings alone.
