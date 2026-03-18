# Tournament Dynamics: Seeds, Upsets, Structure, and Intangibles

This chapter synthesizes findings on the structural and situational factors that shape NCAA tournament outcomes. It draws on historical seed performance data (1985--2025), upset prediction research, coaching and experience effects, transfer portal dynamics, conference strength biases, and bracket structure analysis. The goal is to identify which dynamics a prediction model must account for and which it can safely ignore.

For complementary perspectives, see [Modeling Approaches](modeling-approaches.md) on algorithmic choices, [Feature Engineering & Metrics](features-and-metrics.md) on operationalizing these dynamics as model inputs, [Bracket Strategy & Optimization](bracket-strategy.md) on translating probabilities into pool-winning brackets, and [Recommended Approach](recommended-approach.md) for the integrated design.

---

## 1. Historical Seed Performance and the Chalk Baseline

Seed number alone is an extraordinarily strong predictor of tournament outcomes. Across 40 tournaments (1985--2025, 160 regions), first-round win rates follow a remarkably clean gradient:

| Matchup | Higher Seed Win % | Upset Rate |
|---------|-------------------|------------|
| 1 vs. 16 | 98.8% | 1.2% |
| 2 vs. 15 | 93.1% | 6.9% |
| 3 vs. 14 | 85.6% | 14.4% |
| 4 vs. 13 | 79.4% | 20.6% |
| 5 vs. 12 | 64.4% | 35.6% |
| 6 vs. 11 | 61.3% | 38.7% |
| 7 vs. 10 | 61.3% | 38.7% |
| 8 vs. 9 | 48.1% | 51.9% |

The smoothness of this gradient suggests a latent continuous strength variable underlying the discrete seed assignments. Once the seed gap drops below about three lines (the 5-12 through 8-9 range), the matchups become genuinely competitive.

The "chalk bracket" -- always picking the higher seed -- is a surprisingly powerful baseline. It scores roughly 20.4 points more than the average bracket (~30% better) and matched or beat all 12 CBS analysts in a 2016 test by Flerlage. No. 1 seeds have won 26 of 40 championships. Seeds 1--3 are a combined 444--36 in opening-round games. Only seeds 1--6 carry overall winning records across all tournament games.

**Why this matters for modeling:** Any model that cannot outperform the chalk bracket is not adding value. The chalk baseline is the floor, not the ceiling. At the same time, chalk is a poor *pool-winning* strategy precisely because it is the most common approach -- everyone picks it, so it provides no differentiation when it succeeds (see [Bracket Strategy & Optimization](bracket-strategy.md)).

---

## 2. Upset Patterns: Which Matchups Are Volatile, What Drives Upsets

### The actionable upset slots

The most productive upset slots are the 5-12, 6-11, and 7-10 matchups, each producing upsets roughly one-third of the time. In 34 of 40 tournaments, at least one 12-seed has beaten a 5-seed. Multiple 12-over-5 upsets occurred in 2013, 2014, 2019, 2024, and 2025. The average tournament produces roughly 8 upsets, with a range from 3 (2007) to 14 (2021, 2022). There is no clear secular trend toward more or fewer upsets over time -- variance is the constant.

At the extremes, 16-over-1 upsets have occurred exactly twice (UMBC over Virginia in 2018, FDU over Purdue in 2023) in 160 attempts. Neither upset team advanced past the Round of 32, suggesting the result reflected the 1-seed's underperformance more than the 16-seed's genuine strength. The 15-over-2 upset occurs at a more meaningful rate (~6.9%), including three consecutive years from 2021 to 2023.

### What drives upsets

Eight factors appear consistently across the upset prediction literature:

1. **Three-point dependency.** Teams living and dying by the three create variance. A 3-dependent favorite is vulnerable on a cold night; a 3-dependent underdog has a higher ceiling on a hot one.
2. **Turnover pressure.** Low-seeds that force turnovers disrupt higher-seed offenses and generate cheap transition points.
3. **Tempo conflict.** Slow-tempo teams (low-60s possessions per 40 minutes) advance roughly 12% more often than their seed predicts, because controlling pace neutralizes superior talent. This is one of the most underrated factors in the literature.
4. **Experience and roster age.** Senior-led teams reach the Sweet 16 at a 28% rate versus 17% for freshman-heavy teams. Veterans handle single-elimination pressure better.
5. **Offensive rebounding.** Second-chance points extend possessions and can neutralize shooting slumps.
6. **Free throw shooting.** Reliable conversion of uncontested scoring opportunities matters disproportionately in tight games.
7. **Coaching track record.** Coaches with tournament experience make better in-game adjustments, though isolating this effect from team quality is difficult (see Section 5).
8. **Geography and travel.** Distance from campus to venue affects performance measurably, especially in early rounds (see Section 4).

### Consistency as an upset predictor

Templin's model at the University of Kansas identifies consistency (low game-to-game variance) as the critical predictor -- more important than raw offensive or defensive power. Inconsistent high-seeds are upset-prone because their "off" games coincide with single-elimination consequences. Consistent low-seeds are dangerous because their floor is close to their ceiling. This has a direct modeling implication: include the standard deviation of key metrics as features, not just their means (see [Feature Engineering & Metrics](features-and-metrics.md)).

---

## 3. The Sweet 16 as the Highest Upset-Rate Round

A counterintuitive finding from the data: the Sweet 16 has the highest upset rate of any round at approximately 21%, slightly exceeding even the first round (~20%). The full picture since 2003:

| Round | Upset Rate |
|-------|-----------|
| First Round (R64) | 20.0% |
| Second Round (R32) | 19.9% |
| Sweet 16 | 21.0% |
| Elite 8 | 18.2% |
| Final Four | 13.6% |
| Championship | 9.1% |

The first and second rounds have nearly identical upset rates (differing by only 0.13 percentage points), which undermines the notion that surviving the first round confers a meaningful advantage. Upset probability does not decline linearly with round progression. The Sweet 16 spike likely reflects a selection effect: mid-seeds that survive their first two games have already demonstrated they belong, and they may face fatigued or overconfident higher seeds who had easier early paths.

**Modeling implication:** Do not assume a monotonic decline in upset probability across rounds. Model each round's dynamics separately. The Sweet 16 deserves special treatment -- naive seed-based models will underestimate upset probability in this round.

---

## 4. Travel Distance as the Strongest Intangible

Travel distance has the strongest empirical support of any "soft" factor in the literature. Clay, Bro, and Clay (2014) analyzed 3,296 individual team performances across 26 years and found:

- **Traveling 150+ miles from home reduces the odds of winning by 33.6%** (odds ratio = 0.664).
- Teams from the West crossing 2+ time zones eastward see winning percentages drop below 38%.
- When both teams stay within 500 miles, favorites win 76% and cover the spread 55% of the time. When both travel 1,000+ miles, favorites win only 59% and cover only 43%.

The mechanism is partly logistical (fatigue, circadian disruption for early-afternoon tip-offs that correspond to morning for West Coast teams) and partly structural: the NCAA places higher seeds closer to home, so travel distance is correlated with seeding but not fully captured by it.

Silver's COOPER model incorporates travel distance through a cube-root transformation: `5 * m^(1/3)`, where `m` is miles traveled. This produces diminishing marginal impact -- going from 0 to 500 miles matters more than going from 1,500 to 2,000. The TeamRankings analysis further suggests that the *differential* in travel distance between opponents, not just the absolute distance, is the more predictive feature.

**Modeling implication:** Travel distance is the most actionable intangible to include. Compute distance-from-campus-to-venue for both teams and use the differential. Consider time zone direction as an interaction term, especially for early-afternoon games. The cube-root formula from COOPER is a concrete, implementable approach.

---

## 5. Coaching and Experience Effects

### The evidence is weaker than intuition suggests

Coaching quality and tournament experience are among the most commonly cited "intangible" factors, but the empirical evidence is sobering:

- **Player experience** has an R-squared of 0.0002 with tournament overperformance once seed is controlled for (Harvard Sports Analysis, 2002--2017 data). That is, experience adds essentially zero predictive value beyond what team quality already captures.
- **Coaching tenure** has not been isolated as a statistically significant standalone predictor in any formal multivariate model found in the literature. Leading models like COOPER and LRMC include no explicit coaching variables.
- The LRMC model (Georgia Tech) uses only scoreboard data -- game outcomes, home/away status, and margin of victory -- and outperforms systems that incorporate far richer feature sets. This demonstrates that coaching and experience effects are largely already embedded in the outcomes those models use as inputs.

### What does work

Two nuances preserve a role for experience-adjacent features:

1. **Weighted wins against tournament-caliber opponents.** The Harvard network analysis model (2011) constructed a "confidence" metric using weighted wins (credit proportional to opponent quality) and an NCAA tournament experience interaction term. This model outperformed KenPom and ESPN consensus brackets. The key insight is that playing and winning against strong opponents in pressure situations is informative beyond raw efficiency, but the metric captures opponent quality, not coaching per se.

2. **Seed as a proxy.** The regression analysis by Yard Couch found that seed (entered as log base 2) does "almost all of the heavy lifting," with a p-value of 4.5 x 10^-10. The remaining variance explained by other variables is marginal. Since the selection committee already incorporates coaching reputation and program pedigree into its seeding decisions, seed is a compressed summary of exactly the intangibles people want to model separately.

**Modeling implication:** Do not invest heavily in standalone coaching or experience features. They are noise once team quality is accounted for. The roughly 55% of variance unexplained by seed and basic statistics is mostly genuine randomness, not recoverable signal from intangibles. If you want to capture experience effects, "weighted wins vs. tournament-caliber opponents" is the most promising operationalization (see [Feature Engineering & Metrics](features-and-metrics.md)).

---

## 6. Roster Continuity in the Transfer Portal Era

### The landscape has changed

The NCAA's elimination of transfer sit-out requirements in 2021 fundamentally altered roster construction. As of the 2025 tournament, over 53% of rotation players in the 68-team field had previously played at another Division I school. Average minutes continuity (KenPom's metric for returning minutes) has dropped to historic lows -- 34.0% in 2024--25, down from 39.1% the year before.

### Continuity's predictive value is modest and time-varying

The evidence is mixed:

- **In favor:** 8 of 10 high-continuity mid-major teams improved their KenPom rating during the COVID-affected 2020--21 season. Continuity advantages are most visible in November and December, when newly assembled rosters are still gelling.
- **Against:** Kentucky (0.0% continuity in 2024--25) beat Duke, Florida, and Tennessee early in the season. Memphis, Illinois, and other low-continuity teams outperformed expectations. Gonzaga (72.7% continuity, 4th nationally) lost to low-continuity teams. Pre-pandemic data (2018--19 to 2019--20) showed high-continuity teams performing *worse*, not better.

The clearest finding is temporal: continuity matters in early season, but by March, talent and coaching quality dominate. This suggests continuity should enter a model as a time-decaying feature -- weighted heavily in November, discounted substantially by tournament time.

### What matters more than aggregate continuity

- **Position-specific retention.** Returning a lead guard or anchor frontcourt player has outsized impact compared to generic "returning minutes" percentages.
- **Total experience, not just returning experience.** In the portal era, a team can have high experience (many juniors and seniors) but low continuity (those players are new to the program). Seventeen of 23 national champions since 2002 had a junior or senior as their top contributor.
- **Program transfer development.** Some programs (Arizona, UConn) systematically extract above-expectation performance from transfers. Others (North Carolina, Arkansas, Indiana) consistently underperform with portal additions. EvanMiya's BPR-based analysis quantifies this as "Expected Transfer Improvement" by program.

**Modeling implication:** For a March prediction model, raw continuity is likely a weak feature. Total roster experience (juniors/seniors as a share of minutes) is more useful. If building a preseason model, continuity and program-level "transfer alpha" are more valuable. By tournament time, the season's results have already revealed whether a reconstituted roster has gelled.

---

## 7. Conference Strength Biases and Mid-Major Underseeding

### The circular logic problem

Power conference teams inflate each other's metrics in a self-reinforcing loop. When Team A beats Team B and both are highly rated, Team A earns a Quad 1 win and Team B gets a "good loss." Mid-major teams cannot access this loop regardless of their actual quality. Wieland's simulation study quantifies the damage: realistic conference-heavy scheduling inflates rating system error by 54% compared to a hypothetical random-schedule baseline.

The structural numbers are stark. In 2018--19, high-major conference games were Quad 1 results 47.9% of the time, compared to just 6.4% for mid- and low-major conference games. Power conference teams accumulate resume-building opportunities simply by playing their conference schedule, while a 25-win mid-major may have zero Quad 1 opportunities.

### Empirical evidence of committee bias

Coleman, Lynch, and DuMond's peer-reviewed study (Economics Bulletin, 1997--2006 data) found that SEC teams were seeded approximately 2 positions higher than a predictive model indicated. This is a large effect -- a single seed line dramatically changes a team's bracket path and opponent quality.

The tournament results confirm the bias works in the other direction: mid-major teams consistently outperform their seeds.

- 12-seeds (predominantly mid-majors): 35.6% first-round win rate
- 11-seeds (frequently mid-majors or bubble teams from power conferences): 38.7% first-round win rate

Both rates exceed what naive seed-based models would predict for teams at those seed lines, strong evidence that these teams are systematically undervalued by the committee.

### Conference-specific patterns

| Conference Cluster | Tournament Pattern |
|---|---|
| Missouri Valley, WCC, AAC | Overperform seed expectations by ~12% |
| Big Ten | Underperform in early rounds; physical half-court style struggles at neutral sites |
| Pac-12, SEC (2000--2012 era) | Disappointing early exits despite large tournament fields |

**Modeling implication:** Treat mid-major 11- and 12-seeds as bracket value plays. Consider a conference adjustment that discounts power conference teams on the 4--5 seed line (the most likely overseeded positions) and upgrades mid-majors. Non-conference strength of schedule is an important signal: mid-majors that sought and won tough out-of-conference games have demonstrated their quality against the cross-conference information deficit.

---

## 8. Bracket Structure Effects

### The 11-seed anomaly

Eleven-seeds have reached the Final Four 6 times (LSU 1986, George Mason 2006, VCU 2011, Loyola-Chicago 2018, UCLA 2021, NC State 2024) -- more than seeds 9, 10, 12, 13, 14, 15, and 16 *combined* (which total 4). This is almost certainly a bracket structure effect, not a reflection of 11-seeds being intrinsically better than 10- or 12-seeds.

The mechanism: an 11-seed that wins its first-round game faces a 3-seed in the second round (or a 14-seed, which is extremely rare). A 10-seed that wins faces a 2-seed. A 12-seed that wins faces a 4-seed. The 3-seed opponent in the second round is the most favorable draw for a mid-seed, because 3-seeds have the highest second-round upset rate among top-3 seeds (they lose roughly 40% of second-round games). If the 11-seed clears the second round, it enters the Sweet 16 where upset rates peak at 21%.

### Region balancing and geographic placement

The selection committee balances regions so that the sum of "true seed" numbers in each region's top-4 seed lines differs by no more than 6 points. This prevents extreme "regions of death" but does not eliminate variation -- some regions are meaningfully tougher than others, especially at the 5--12 seed lines where the committee has more flexibility.

Geographic placement gives higher seeds a de facto home-court advantage. Top seeds (1--3) have a median travel distance under 500 miles, with 2-seeds averaging the lowest at 321 miles. This interacts with the travel distance effect described in Section 4: the committee's placement rules partially embed a travel advantage into seeding, but not completely.

### The bracket is not a re-seeded tournament

Because pairings are fixed by bracket position (not re-seeded each round), a team's advancement probability depends on who else is in its bracket quadrant. A 1-seed facing a strong 4-seed and 5-seed in its quadrant has a harder path than one with weaker teams at those lines. This path dependency is invisible to models that only consider pairwise matchup probabilities in isolation.

**Modeling implication:** Account for bracket position, not just seed-vs-seed matchup probability. When simulating the tournament via Monte Carlo (see [Modeling Approaches](modeling-approaches.md)), the full bracket tree must be simulated, not just independent pairwise games. The 11-seed Final Four anomaly specifically suggests that models should give 11-seeds a modest boost in deep advancement probability relative to adjacent seed lines.

---

## 9. Implications for Modeling and Bracket Construction

The findings in this chapter point to several concrete modeling decisions:

### What to include

1. **Seed-based priors as the foundation.** Historical upset rates by matchup provide a strong, well-calibrated baseline. Layer team-specific adjustments on top, but do not stray far without good reason.

2. **Travel distance differential.** The strongest intangible. Use a cube-root transformation (per COOPER) or threshold approach (per Clay et al.). Include time zone direction for early-round games.

3. **Consistency (variance) as a feature.** Model the standard deviation of scoring margin, efficiency, and other key metrics -- not just the means. Inconsistent favorites are upset-prone; consistent underdogs are dangerous.

4. **Conference adjustment for mid-major underseeding.** Systematically upgrade mid-major 11- and 12-seeds and consider discounting power conference 4- and 5-seeds.

5. **Bracket structure in simulation.** Simulate the full bracket tree. Give 11-seeds a structural bonus for deep advancement. Model round-specific upset rates rather than assuming monotonic decline.

### What to downweight or omit

6. **Standalone coaching variables.** Not significant once team quality is accounted for. The information is already in the efficiency ratings and the committee's seeding.

7. **Raw player experience.** Near-zero R-squared after controlling for seed. Total roster experience (juniors/seniors share of minutes) is a better feature than "returning minutes" continuity.

8. **Aggregate continuity.** Weak by March. If used at all, treat as a time-decaying feature with near-zero weight at tournament time.

### Calibration targets

9. **Aim for well-calibrated probabilities, not binary upset predictions.** The best models are only ~75% accurate on individual game outcomes (Sokol, Georgia Tech). A model that says a 12-seed has a 35% chance of winning is more useful than one that tries to pick *which* 12-over-5 upset will occur.

10. **Use heavy-tailed distributions for score differentials.** Normal distributions underestimate the frequency of extreme outcomes. T-distributions or similar fat-tailed alternatives better capture the tournament's inherent volatility.

11. **The Sweet 16 is not the second round.** Models should not treat later rounds as uniformly more predictable. The ~21% upset rate in the Sweet 16 exceeds the first round and demands separate treatment.

### The accuracy ceiling

Even the best models top out around 75% game-level accuracy. The remaining 25% represents genuine uncertainty -- games that are close to toss-ups regardless of what information a model has access to. This ceiling has a strategic consequence: the value of a prediction model lies not in calling individual upsets but in calibrating the *probability* of upsets correctly and placing them in the *most likely slots*. For how to translate these calibrated probabilities into pool-winning brackets, see [Bracket Strategy & Optimization](bracket-strategy.md).
