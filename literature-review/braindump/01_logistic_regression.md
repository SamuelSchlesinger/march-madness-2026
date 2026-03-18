# Logistic Regression and Classical Statistical Models for Predicting March Madness

## Summary

Classical statistical models -- logistic regression, probit models, and rating systems grounded in similar principles -- form the backbone of NCAA tournament prediction. The core insight across all approaches is that **team strength can be estimated from game results and converted into win probabilities via logistic (or probit) functions**. The best classical models achieve roughly **74-75% game-level accuracy** in the tournament, a ceiling that has proven remarkably hard to beat even with modern machine learning. Key factors that drive prediction quality include adjusted offensive/defensive efficiency, margin of victory, strength of schedule, and home-court advantage. The main weaknesses are an inability to capture injuries, momentum, matchup-specific effects, and late-round parity where seeds converge in quality.

The sources below cover five distinct approaches:

1. **LRMC (Logistic Regression / Markov Chain)** -- Georgia Tech's Sokol & Kvam model using only box-score data
2. **KenPom Ratings** -- Pomeroy's adjusted efficiency and pythagorean system
3. **Sagarin Ratings** -- Elo-derived and BLUE-based composite ratings
4. **Multivariable Logistic Regression on Efficiency Metrics** -- Academic models using team performance features
5. **Boulier-Stekler Probit Model** -- Probit regression on tournament seedings
6. **FiveThirtyEight's Composite Model** -- Elo + logistic regression ensemble

---

## 1. LRMC: Logistic Regression / Markov Chain Model

**Source:** Sokol, J. & Kvam, P. "A Logistic Regression/Markov Chain Model for NCAA Basketball." Georgia Tech ISyE.
- Paper: <https://www2.isye.gatech.edu/~jsokol/ncaa.pdf>
- About page: <https://www2.isye.gatech.edu/~jsokol/lrmc/about/>
- Technical explainer (applied to football): <https://blog.collegefootballdata.com/talking-tech-applying-lrmc-rankings-to-college-football-part-one/>
- NBAstuffer overview: <https://www.nbastuffer.com/analytics101/logistic-regression-markov-chain-lrmc/>

### Methodology

LRMC has two stages:

**Stage 1 -- Logistic Regression:** For each game, estimate the probability that Team A beats Team B on a neutral court. The inputs are minimal: which two teams played, who had home court, and the margin of victory. Sokol and Kvam compiled margins of victory from home-and-home matchups and fit a logistic regression on those margins. The regression yields a function that maps observed point differential to a neutral-court win probability (denoted *r_x*). This process also reveals the home-court advantage (approximately 6.5 points in college basketball, identified as the margin at which road win probability equals 50%).

**Stage 2 -- Markov Chain:** The pairwise win probabilities are assembled into a transition matrix. Each row represents a team; columns show the summed probabilities against each opponent, divided by total games played. The matrix is iterated from an initial belief vector until it converges to a steady state. The steady-state values become the team rankings. Teams that have high win probabilities against strong opponents rise; teams that beat only weak opponents are penalized.

### Three Variants
- **Bayesian LRMC:** Uses empirical Bayes to estimate win probabilities with full margin-of-victory and home-court data.
- **Classic LRMC:** Uses standard logistic regression with full margin/home-court data.
- **LRMC(0):** Excludes margin of victory (win/loss only), per NCAA committee preferences. Less accurate than the other two.

### Data Used
Only basic scoreboard data: matchup, location (home/away/neutral), final score. No play-by-play, no advanced stats, no recruiting rankings.

### Reported Accuracy
- Higher-ranked LRMC teams win approximately **75% of games**, including NCAA tournament games.
- Historically picked the winner of more than **74% of tournament games** correctly.
- Outperforms RPI (less than 70% accuracy) and, in five of six test seasons, had Final Four teams collectively ranked higher than any other system tested.
- Rated among the top performers when compared against nearly 100 other ranking systems.

### Strengths
- Minimal data requirements (only box scores) make it robust and hard to overfit.
- The Markov chain component naturally handles strength of schedule without explicit adjustment.
- Mathematically principled: steady-state rankings have a clean probabilistic interpretation.
- Consistently competitive with far more complex models.

### Weaknesses
- Cannot incorporate player-level information (injuries, transfers, freshmen impact).
- Margin of victory is used but not decomposed into offensive/defensive components.
- Early-season rankings are noisy due to limited games.
- No mechanism for capturing matchup-specific advantages (e.g., size mismatches, tempo preferences).

---

## 2. KenPom Ratings (Ken Pomeroy)

**Sources:**
- Official site: <https://kenpom.com/>
- Ratings explanation blog post: <https://kenpom.com/blog/ratings-explanation/>
- SI explainer: <https://www.si.com/college-basketball/kenpom-rankings-explained-who-is-ken-pomeroy-what-do-rankings-mean>
- Methodology update: <https://kenpom.com/blog/ratings-methodology-update/>

### Methodology

KenPom is built on **tempo-free, efficiency-based statistics** evaluated on a per-100-possessions basis:

**Core Metrics:**
- **Adjusted Offensive Efficiency (AdjOE):** Points a team would score per 100 possessions against an average Division I team. Adjusted for strength of opposing defenses faced.
- **Adjusted Defensive Efficiency (AdjDE):** Points a team would allow per 100 possessions against an average offense. Adjusted for strength of opposing offenses faced.
- **Net Rating:** AdjOE minus AdjDE, representing expected margin per 100 possessions against an average team on a neutral court.

**Pythagorean Winning Percentage:** Pomeroy adapts Bill James's pythagorean formula to basketball:

```
Win% = (AdjOE^10.25) / (AdjOE^10.25 + AdjDE^10.25)
```

This expected winning percentage (called BARTHAG on the site) is the primary ranking criterion.

**Game Prediction (Log5):** To predict a specific matchup, Pomeroy uses the log5 method -- a formula that combines two teams' pythagorean win percentages to estimate the probability of one beating the other. Originally developed for baseball by Bill James, it accounts for both teams' strengths simultaneously.

**Tempo:** Each team's pace (possessions per 40 minutes) is tracked and used to estimate expected total possessions in a matchup, which in turn yields a predicted final score.

### Design Philosophy
The system is **purely predictive**: it aims to show how strong a team would be "if it played tonight," independent of injuries or emotional factors. It values a 20-point win more than a 5-point win, and prefers teams that lose close games against strong opponents over those that win close games against weak opponents.

### Data Used
Full Division I season results, with statistics dating back to 2002. Continuously updated throughout the season for all 365+ D-I programs.

### Reported Accuracy
No single accuracy figure is published, but KenPom ratings are used by:
- Television broadcasters
- The NCAA tournament selection committee
- College basketball coaching staffs
- Betting markets (as a benchmark)

KenPom-derived features (AdjOE, AdjDE, BARTHAG) appear as top predictors in virtually every published March Madness prediction model, suggesting very high signal quality.

### Strengths
- Tempo-free analysis removes pace as a confound, enabling fair comparison of fast and slow teams.
- Strength-of-schedule adjustment is baked into the efficiency calculations.
- Continuous updates reflect team evolution over the season.
- Highly interpretable: each metric has clear basketball meaning.
- Widely adopted as the gold standard for college basketball analytics.

### Weaknesses
- Does not account for injuries or roster changes directly.
- Treats each game's contribution somewhat equally (some weighting for recency, but limited).
- The pythagorean exponent (10.25) is empirically fit; its stability across eras is assumed, not proven.
- Single-number ratings collapse multidimensional team profiles (shooting, rebounding, turnover rate) into one dimension.
- Subscription model limits full public access to underlying data.

---

## 3. Sagarin Ratings

**Sources:**
- Official site (now discontinued): <http://sagarin.com/sports/cbsend.htm>
- Wikipedia: <https://en.wikipedia.org/wiki/Jeff_Sagarin>
- Point Spreads guide: <https://www.pointspreads.com/guides/sagarin-betting-system-guide/>
- My Top Sportsbooks guide: <https://www.mytopsportsbooks.com/guide/advanced-betting/sagarin-rankings/>

### Methodology

Jeff Sagarin (MIT-trained statistician) published ratings in USA Today from 1985 until the partnership ended in 2023.

**Historical Approach (two methods):**
1. **Elo Chess:** Adapted from Arpad Elo's chess rating system. Purely based on wins and losses; does not consider margin of victory. Teams gain/lose rating points based on the opponent's strength and the expected vs. actual outcome.
2. **BLUE (Best Linear Unbiased Estimator):** A least-squares regression approach that factors in scoring margins. Solves a system of linear equations to find ratings that best explain observed margins of victory across all games simultaneously.

**Modern Approach (three methods combined):**
1. **Predictor:** Takes only game scores into account. Includes margin of victory with diminishing returns for blowouts.
2. **Golden Mean:** Another scoring-based system; exact equations never publicly disclosed.
3. **Recent:** Places greater weight on recent games than early-season results.

These three are blended into an **Overall Rating**. The exact blending formula was never revealed.

**Home-Court Advantage:** Adds 4 points for home-court advantage in college basketball predictions.

**Prediction Use:** Subtract one team's rating from the other; the difference is the predicted point spread. Add home-court adjustment as needed.

### Data Used
Complete game results across Division I, including scores and locations.

### Reported Accuracy
- **75% success rate** predicting game winners.
- **53% success rate** against the point spread (above the ~52.4% breakeven for bettors).

### Strengths
- Long historical track record (1985-2023).
- Multiple sub-models provide robustness.
- Recency weighting captures team trajectory.
- Simple to use: subtract ratings to get predicted spread.

### Weaknesses
- Proprietary/secret formulas -- impossible to replicate or audit.
- Discontinued in 2023; no longer updated.
- No per-possession normalization (unlike KenPom).
- Margin-of-victory component does not distinguish offensive from defensive contributions.
- Does not account for roster changes, injuries, or matchup specifics.

---

## 4. Multivariable Logistic Regression on Efficiency Metrics

**Source:** "March Madness Tournament Predictions Model: A Mathematical Modeling Approach." arXiv:2503.21790v1.
- Link: <https://arxiv.org/html/2503.21790v1>

### Methodology

A **generalized linear model** with three components:
1. A linear predictor combining team statistics with learned coefficients.
2. A **logit link function** converting the linear predictor to a win probability.
3. A **Bernoulli distribution** for the binary win/loss outcome.

Key design choices:
- **Feature differencing:** Rather than using raw team stats, the model uses the *difference* between opposing teams' statistics, halving dimensionality while preserving predictive information.
- **L2 regularization** to prevent overfitting.
- **Mean-value imputation** for missing data.
- **Standardization** of all features.

After feature selection based on coefficient magnitude, four predictors remained:
1. **Adjusted Offensive Efficiency (ADJOE)** -- points scored per 100 possessions
2. **Adjusted Defensive Efficiency (ADJDE)** -- points allowed per 100 possessions
3. **Power Rating (BARTHAG)** -- pythagorean win expectancy (from KenPom)
4. **Two-Point Shooting Percentage Allowed (2PD)**

Tournament brackets were simulated via Monte Carlo methods using the logistic probability function for each game.

### Data Used
NCAA tournament data from 2013 to 2023, with an 80/20 train-test split.

### Reported Accuracy
- **74.6% test accuracy** on individual game prediction.
- **43.75% to 65.63%** full-bracket naive accuracy across different regional brackets.
- **Spearman rank correlation:** 0.365 to 0.747 (moderate to strong positive association between predicted and actual finish order).

### Strengths
- High interpretability: each coefficient directly shows how a one-unit change in a feature affects the log-odds of winning.
- Parsimonious: only four features needed.
- Competitive with more complex models (including FiveThirtyEight's approach).
- Objective and reproducible.

### Weaknesses
- Large discrepancies in accuracy across different regional brackets within the same tournament year, suggesting potential model bias or bracket-specific confounds.
- Assumes team statistics are constant within a season -- ignores injuries, mid-season roster changes, and strategic evolution.
- Cannot capture venue dynamics, travel effects, or intangible psychological factors.
- Limited feature set may miss important dimensions (rebounding, free throw rate, turnover rate).

---

## 5. Boulier-Stekler Probit Model

**Sources:**
- Boulier, B. & Stekler, H. "Are Sports Seedings Good Predictors?: An Evaluation." *International Journal of Forecasting*, 15(1), 1999.
  - <https://ideas.repec.org/a/eee/intfor/v15y1999i1p83-91.html>
- Stekler, H. & Klein, A. "Predicting the Outcomes of NCAA Basketball Championship Games." GWU Working Paper 2011-003, 2011.
  - <https://www2.gwu.edu/~forcpgm/2011-003.pdf>
- Related: Caudill (2003) maximum score estimator comparison.

### Methodology

The model uses a **probit function** (the inverse of the standard normal CDF) to relate the outcome of a discrete event (win or loss) to the **difference in tournament seedings** of the two teams:

```
P(Team A wins) = Phi(beta * (Seed_B - Seed_A))
```

where Phi is the standard normal CDF and beta is estimated from historical tournament data. Higher-seeded teams (lower seed numbers) are favored, with the magnitude of the seed difference determining the strength of that prediction.

This is a minimal model: seeds are the *only* input. The probit link function is the key difference from logistic regression -- it uses the normal distribution rather than the logistic distribution, producing slightly different tail behavior.

### Data Used
Regional tournament results from 1985 to 1995 (original study), later extended through 2010.

### Reported Accuracy
- Higher-seeded teams defeated lower-seeded opponents **73.5%** of the time across the first four rounds.
- The probit model improved accuracy over the naive strategy of always picking the higher seed.
- Caudill (2003) showed a maximum score estimator performed slightly better than the probit model.
- **Critical finding:** When evaluated on 2003-2010 data, the model was successful in predicting winners in the first three rounds but performed **no better than chance in the fourth round** (Elite Eight), where seed quality differences shrink.

### Strengths
- Extremely simple and transparent.
- Demonstrates that seeds carry substantial predictive information, especially in early rounds.
- Establishes an important baseline for more complex models to beat.
- Probit link function is well-suited to binary outcomes with normally-distributed latent variables.

### Weaknesses
- Seeds are a very coarse summary of team quality -- two 5-seeds can be dramatically different in strength.
- No margin-of-victory or efficiency information used.
- Prediction quality degrades in later rounds where seed differences are small.
- Does not distinguish between years or conferences.
- Assumes the relationship between seed difference and win probability is constant across eras, which may not hold as the tournament selection process evolves.

---

## 6. FiveThirtyEight Composite Model (Elo + Logistic Regression)

**Sources:**
- "How Our March Madness Predictions Work": <https://fivethirtyeight.com/features/how-our-march-madness-predictions-work/>
- "How FiveThirtyEight Is Forecasting the 2016 NCAA Tournament": <https://fivethirtyeight.com/features/how-fivethirtyeight-is-forecasting-the-2016-ncaa-tournament/>
- Elo ratings and logistic regression analysis: <https://nicidob.github.io/nba_elo/>

### Methodology

FiveThirtyEight uses a **composite rating** built from eight equally-weighted components:

**Six Computer Systems:**
1. FiveThirtyEight's own Elo ratings
2. ESPN's BPI (Basketball Power Index)
3. Sagarin Predictor ratings
4. KenPom ratings
5. Sokol's LRMC ratings
6. Sonny Moore's power ratings

**Two Human Systems:**
7. NCAA selection committee's S-Curve
8. Composite preseason coach/media polls

**Elo Rating System:** FiveThirtyEight's Elo ratings use game-by-game results going back to the 1950s. Key adjustments:
- Home-court advantage
- Travel distance (college teams perform significantly worse when traveling long distances)
- Conference affiliation
- Tournament games are weighted higher than regular-season games (because there are historically *fewer* upsets in tournament play than Elo differences would predict)

**Win Probability via Logistic Regression:** The composite team ratings are converted to game-level win probabilities using a logistic function. For their in-game model, they fit a logistic regression on play-by-play data from five seasons of Division I basketball, incorporating time remaining, score differential, pre-game win probability, and possession status.

**Tournament Simulation:** Because of the single-elimination bracket structure, they calculate advancement probabilities directly rather than relying on Monte Carlo simulation.

**Injury Adjustment:** The model accounts for player injuries by estimating the "replacement player caliber," recognizing that losing a star affects different programs differently (a deep roster absorbs injury better than a thin one).

### Data Used
- Historical game results dating to the 1950s (for Elo)
- Five seasons of Division I play-by-play data (for in-game model)
- ESPN and Sports-Reference.com data
- External rating systems (KenPom, Sagarin, LRMC, BPI, Moore)

### Reported Accuracy
No single accuracy figure was published, but the ensemble approach was designed to be more robust than any individual component. FiveThirtyEight's tournament forecasts were widely regarded as among the best publicly available predictions during their operational period.

### Strengths
- Ensemble of diverse methods (computer + human) provides robustness.
- Elo's historical depth captures long-term program strength.
- Travel distance adjustment is unique and empirically validated.
- Tournament-specific calibration (upsets are rarer than regular season) improves tournament predictions.
- Injury adjustments add a dimension most classical models lack.

### Weaknesses
- Averaging eight systems equally may not be optimal; some systems may be more accurate than others.
- Dependent on external data sources (KenPom, Sagarin, etc.) that may change or become unavailable.
- Elo ratings are slow to react to rapid team changes (transfers, injuries) due to their incremental update nature.
- The in-game logistic regression model cannot capture factors like foul trouble, specific player matchups, or coaching adjustments.
- FiveThirtyEight's sports coverage was discontinued after the site's acquisition and restructuring, limiting future updates.

---

## Cross-Cutting Themes and Takeaways

### The ~74-75% Accuracy Ceiling
Multiple independent approaches converge on roughly the same game-level accuracy: LRMC at 74%, the arXiv logistic regression at 74.6%, Sagarin at 75%, and seed-based probit at 73.5%. This suggests that **roughly 25% of tournament games are genuinely unpredictable** from pre-game information, representing a hard floor of noise from injuries, hot shooting, referee variance, and other stochastic factors.

### Efficiency Metrics are King
Across all models that use team statistics, adjusted offensive and defensive efficiency (per 100 possessions) emerge as the most predictive features. KenPom's AdjOE and AdjDE appear as top predictors even in models not built by Pomeroy. Tempo-free analysis -- normalizing for pace of play -- is essential.

### Logistic vs. Probit Link Functions
The choice between logistic and probit link functions makes little practical difference in prediction accuracy. Both map a linear predictor to a probability. The logistic function has slightly heavier tails, which may better capture extreme upsets, but the difference is marginal. Most practitioners prefer logistic regression due to the interpretability of odds ratios.

### Margin of Victory Matters
Models that incorporate margin of victory (LRMC Classic, Sagarin Predictor, logistic regression on efficiency differentials) consistently outperform win/loss-only models (LRMC(0), Elo chess, probit on seeds). However, diminishing returns are applied to blowouts -- a 30-point win is not twice as informative as a 15-point win.

### Strength of Schedule is Implicitly or Explicitly Handled
- LRMC handles it via the Markov chain steady state.
- KenPom adjusts efficiencies for opponent quality.
- Sagarin's BLUE solves for ratings that explain all observed margins simultaneously.
- The probit model sidesteps it by using seeds (which the committee assigns partly based on SOS).

### Late-Round Prediction is Hard
The Boulier-Stekler finding that probit predictions degrade to chance level by the Elite Eight is echoed across models. As teams converge in quality in later rounds, the signal-to-noise ratio drops, and factors not captured by classical models (coaching adjustments, matchup specifics, pressure) become relatively more important.

### Ensembles Outperform Individual Models
FiveThirtyEight's composite approach -- averaging across LRMC, KenPom, Sagarin, Elo, BPI, and human rankings -- was designed based on the principle that diverse models capture different signals. This is a recurring finding in prediction competitions: simple averages of good models often beat any individual model.
