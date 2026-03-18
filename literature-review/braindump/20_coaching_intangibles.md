# Coaching Effects, Tournament Experience, and Intangible Factors in March Madness Prediction

## Summary

This review covers research on "soft" or situational factors in NCAA tournament prediction: coaching quality and tenure, player/program tournament experience, travel distance and time zone effects, venue dynamics, and psychological intangibles like confidence and momentum. The evidence is mixed but instructive:

- **Travel distance** has the strongest empirical support as a predictive factor. Teams traveling 150+ miles see winning odds drop ~33.6%, and crossing 2+ time zones eastward drops win rates below 38%. Favorites traveling 1,000+ miles win only 59% of games vs. 76% when staying within 500 miles.
- **Coaching tenure** matters qualitatively (experienced tournament coaches make better in-game adjustments), but has not been isolated as a statistically significant standalone predictor in most formal models. Leading models like COOPER and LRMC do not include explicit coaching variables.
- **Player experience** (class year, returning minutes) shows surprisingly little predictive power when controlling for team quality. R-squared values near zero in regression analyses.
- **Tournament "intangibles"** (confidence, preparedness) can be partially quantified via network analysis (weighted wins against tournament-caliber opponents). A Harvard model using these outperformed KenPom and ESPN consensus brackets.
- **Seed** remains the dominant predictor, doing "almost all the heavy lifting" in regression models. Most intangible factors are already partially captured by seeding.

**Modeling implications**: Travel distance is the most actionable intangible to include in a prediction model. Coaching and experience effects are likely already embedded in team efficiency ratings and seeding. Network-analysis-derived "confidence" metrics represent the most promising novel intangible feature.

---

## Source 1: Harvard Sports Analysis Collective -- "Quantifying Intangibles: A Network Analysis Prediction Model for the NCAA Tournament" (2011)

- **URL**: https://harvardsportsanalysis.org/2011/05/quantifying-intangibles-a-network-analysis-prediction-model-for-the-ncaa-tournament/
- **Factors studied**: Confidence/preparedness and tournament experience as intangibles beyond standard efficiency metrics.
- **Quantification method**:
  - **Weighted Wins**: A network analysis metric where credit is proportional to opponent quality. Beating a 2-seed = 1/2 weighted win; beating a 15-seed = 1/15. Two 12-seed wins + one 6-seed win = 0.33 weighted wins.
  - **NCAA Experience**: Returning minutes percentage multiplied by previous year's NCAA tournament wins.
  - **Statistical approach**: Ordered probit regression over 5 years of tournament data (2007-2011), with tournament wins (0-6) as the dependent variable.
- **Results**:
  - Both Weighted Wins and NCAA Experience were significant predictors after controlling for regular-season strength.
  - Interaction term significant at 10% level (p = 0.047).
  - Bracket accuracy: 44 of 63 games correct, two Final Four teams identified.
  - Outperformed KenPom rankings, TeamRankings bracket, and ESPN consensus using standard 1/2/4/8/16/32 scoring.
- **Key insight**: Tournament play differs fundamentally from regular-season play. Psychological factors (confidence, preparedness) enhance predictive accuracy beyond standard stats alone. The premise that "NCAA Tournament games are the same as regular season games" is dubious -- bigger arenas, brighter spotlights, and higher stakes change the dynamics.
- **Modeling implication**: Consider adding a "weighted wins vs. tournament-caliber opponents" feature and an experience interaction term to a bracket model. These are relatively cheap to compute from box scores and roster data.

---

## Source 2: Harvard Sports Analysis Collective -- "A Method to the Madness: Predicting NCAA Tournament Success" (2019)

- **URL**: https://harvardsportsanalysis.org/2019/03/a-method-to-the-madness-predicting-ncaa-tournament-success/
- **Factors studied**: Offensive/defensive performance, three-point shooting, and team experience as predictors of tournament overperformance.
- **Quantification method**:
  - Data from 2002-2017 NCAA tournaments (KenPom and Kaggle).
  - Dependent variable: "performance" = actual games won minus average games won by teams of that seed historically.
  - Used R-squared to measure correlation of each factor with overperformance.
- **Results**:
  - Defense R-squared = 0.006
  - Offense R-squared = 0.013
  - Combined offensive-defensive rank R-squared = 0.019
  - Three-point rate R-squared = 0.0009
  - Three-point percentage R-squared = 0.0009
  - **Experience R-squared = 0.0002** -- "No correlation between having more experienced players and outperforming expectations."
- **Key insight**: Debunks the conventional wisdom that experience matters. Once you control for seed (which already captures team quality), player experience adds essentially zero predictive value. Same for offense, defense, and three-point shooting -- all show "very little correlation" with tournament overperformance.
- **Modeling implication**: Do not invest heavily in player experience features. They are noise once team quality is accounted for. The unpredictability itself is a key feature of the tournament, not a flaw in the model.

---

## Source 3: Clay, Bro, & Clay (2014) -- "Geospatial Determinants of Game Outcomes in NCAA Men's Basketball" (via Winthrop Intelligence)

- **URL**: https://www.researchgate.net/publication/272507595_Geospatial_Determinants_of_Game_Outcomes_in_NCAA_Men's_Basketball
- **Summary coverage**: https://winthropintelligence.com/2014/02/17/travel-affect-ncaa-basketball-outcomes/ (page no longer accessible; findings widely cited)
- **Factors studied**: Travel distance, time zones crossed, elevation change, temperature change.
- **Quantification method**:
  - Analyzed 3,296 individual team performances from 1,648 tournament games over 26 years (1985/86 through 2010/11).
  - Logistic regression with geospatial disruption as the guiding hypothesis.
- **Results**:
  - Traveling 150+ miles from home reduces odds of winning by 33.6% (odds ratio = 0.664).
  - Teams from the West crossing 2+ time zones eastward: winning percentage drops below 38%.
  - Possible mechanism: early-round games played during daytime favor eastern teams' circadian rhythms ("body-clock sweet spot").
  - The shift to pod format in 2002 had no significant independent effect on results, but higher seeds now travel shorter distances for early rounds, and their winning percentages in those rounds increased as a result.
- **Modeling implication**: Travel distance is a real, measurable factor. Include distance-from-campus-to-venue as a feature. Time zone direction (east vs. west travel) may matter more than raw distance. Consider interaction with game time (early afternoon games penalize westward-origin teams more).

---

## Source 4: TeamRankings / Stat Geek Idol -- "And Albuquerque Is Where? The Effect of Travel Distance on NCAA Tournament Play"

- **URL**: https://www.teamrankings.com/blog/ncaa-basketball/and-albuquerque-is-where-the-effect-of-travel-distance-on-ncaa-tournament-play-stat-geek-idol
- **Factors studied**: Travel distance effects on favorites vs. underdogs, shooting performance, and round-by-round patterns.
- **Quantification method**:
  - 323 tournament games from 2007-2011 (play-in and first round).
  - Distance range: 0 miles (Butler 2011) to 2,666 miles (St. Mary's to Providence, 2010).
  - Lowess smoothing analysis for shooting percentages vs. distance.
- **Results**:
  - Both teams within 500 miles (71 games): favorites won 76%, covered the spread 55%.
  - Both teams traveled 1,000+ miles (39 games): favorites won only 59%, covered only 43%.
  - Underdogs' three-point shooting improved with distance; favorites' two- and three-point shooting declined with distance.
  - Early-round games (Tue-Fri) averaged 24.5 turnovers vs. 23 for weekend games (statistically significant), and the Under hit in 54% of early games.
  - Top seeds (1-3) had median travel under 500 miles; 2-seeds lowest at 321 miles.
- **Key insight**: Travel distance differentially affects favorites and underdogs. Favorites are more disrupted by long travel, which compresses the talent gap. This has ATS (against-the-spread) implications and suggests that distance is a factor even after seeding is accounted for.
- **Modeling implication**: Compute travel distance for both teams in each matchup. The *differential* in travel distance, not just absolute distance, may be a useful feature. The effect is strongest in early rounds when teams have not yet acclimated.

---

## Source 5: Yard Couch -- "Solving March Madness with Regression Analysis" (2021)

- **URL**: https://yardcouch.com/solving-march-madness-with-regression-analysis/
- **Factors studied**: 22 statistical variables including seed, offensive stats, defensive stats, strength of schedule, RPI. Coaching and intangibles were explicitly acknowledged as not included.
- **Quantification method**:
  - Multiple linear regression with tournament wins as the dependent variable.
  - Seed entered as log base 2.
- **Results**:
  - Overall R-squared = 0.447; Adjusted R-squared = 0.41.
  - **Seed (log2)** was overwhelmingly the most significant variable (p = 0.00000000045, coeff = -0.6462).
  - Other significant variables: Field goal % (p = 0.0083), turnovers (p = 0.0348), opponent turnovers (p = 0.0255), offensive rebounds (p = 0.0245), three-points made (p = 0.0223).
  - Blocks (p = 0.8373), opponent rebounds (p = 0.8005), steals (p = 0.6260) were not significant.
  - Counterintuitive: higher points per game slightly reduced predicted wins (coeff = -0.1944), suggesting bracket makers already overvalue scoring.
  - Author noted curiosity about whether coaching tenure correlates with fewer fouls but did not analyze this.
- **Key insight**: Seed does "almost all of the heavy lifting." Once seed is included, most statistical variables add marginal predictive power. The model explicitly omits coaching and intangibles, and still explains ~45% of variance -- suggesting the remaining 55% includes randomness, matchup dynamics, and potentially some intangible factors.
- **Modeling implication**: Any intangible factor worth adding must demonstrate predictive power *beyond* seed. The ~55% unexplained variance sets the ceiling for how much coaching, experience, and situational factors could theoretically contribute.

---

## Source 6: Nate Silver's COOPER Model (Silver Bulletin, 2025-2026)

- **URL**: https://www.natesilver.net/p/introducing-cooper-silver-bulletins
- **Factors studied**: Margin of victory, opponent strength, pace, home court advantage, travel distance, injuries, preseason polls, in-tournament performance updates.
- **Quantification method**:
  - Elo-based rating system. 1 point of basketball = 28.5 Elo points (men's).
  - 6-point "win bonus" (a 67-64 win is treated as 70-61).
  - K-factor = 55 (110 early season).
  - Home court advantage computed per school using historical data.
  - **Travel distance**: factored via formula 5 * m^(1/3), where m = miles traveled.
  - Mean reversion: 30% toward conference average between seasons.
  - Tournament forecast: 5/8 COOPER + 3/8 KenPom. Accounts for injuries (via Win Shares and replacement-level projections), hot-running simulations (early-round upsets trigger rating upgrades), and fat-tailed score distributions.
- **Coaching/intangibles treatment**: No explicit coaching quality, tenure, or experience variables. These are captured indirectly through team performance history. Preseason AP and Coaches' polls serve as a proxy for perceived program quality (which correlates with coaching reputation).
- **Key insight**: The most sophisticated public model in the space does not use coaching as a direct input. Travel distance is included but through a cube-root transformation, meaning it has diminishing marginal impact (going from 0 to 500 miles matters more than 1500 to 2000). The model's accuracy comes from combining multiple rating systems, not from intangible factors.
- **Modeling implication**: If COOPER doesn't use coaching directly, adding a coaching variable would only matter if it captures something that team efficiency ratings miss. The cube-root travel distance formula (5 * m^(1/3)) is a concrete, implementable approach.

---

## Source 7: Kvam & Sokol -- Logistic Regression/Markov Chain (LRMC) Model for NCAA Basketball (Georgia Tech)

- **URL**: https://www2.isye.gatech.edu/~jsokol/ncaa.pdf
- **About page**: https://www2.isye.gatech.edu/~jsokol/lrmc/about/
- **Factors studied**: Game outcomes, home court advantage, margin of victory only. Deliberately minimal input data.
- **Quantification method**:
  - Combined logistic regression and Markov chain model.
  - Uses only basic scoreboard data: which teams played, home/away status, and margin of victory.
  - Empirical Bayes or logistic regression to estimate win probabilities.
  - Higher-ranked teams win approximately 75% of the time, a rate that holds in the tournament.
- **Coaching/intangibles treatment**: Not included. The model's philosophy is that with enough games, intangibles are already reflected in outcomes. The LRMC has outperformed seedings, AP/Coaches polls, RPI, Sagarin, and Massey ratings over multiple years despite using only scoreboard data.
- **Key insight**: A model using zero intangible inputs can still be elite. This is evidence that coaching, experience, and situational factors are largely already embedded in win-loss records and margins. The LRMC correctly predicted Georgia Tech's 2004 Final Four run (as a 3-seed) when most other models did not.
- **Modeling implication**: The burden of proof is on intangible factors. They must demonstrate value above and beyond what simple outcome-based models already capture. This is a high bar.

---

## Cross-Cutting Themes and Recommendations

### What works as a predictive feature:
1. **Travel distance** -- Empirically validated across multiple studies. Use cube-root transformation (per COOPER) or a threshold approach (per Clay et al.). Include time zone direction as an interaction term.
2. **Weighted wins vs. tournament-caliber opponents** -- The Harvard network analysis approach showed genuine predictive lift. This is a proxy for "confidence" and "preparedness."

### What does not work (or is already captured by other features):
1. **Player experience** -- R-squared near zero once seed is controlled for.
2. **Coaching tenure** -- No study has isolated it as significant in a multivariate model. Likely already captured by team ratings.
3. **Raw offensive/defensive stats** -- Very low R-squared for tournament overperformance.

### What might work but needs more research:
1. **Coaching tournament-specific ATS records** -- Anecdotal evidence that certain coaches consistently over/underperform in March, but no rigorous study found.
2. **Conference tournament fatigue** -- Travel burden from conference tournaments could carry over. Under-explored.
3. **First-year coaches at new programs** -- 13 first-year coaches made the 2026 tournament (a record), suggesting institutional momentum matters independent of specific coaching.
4. **Game time and circadian effects** -- Early afternoon games may disadvantage West Coast teams traveling east, per Clay et al.
