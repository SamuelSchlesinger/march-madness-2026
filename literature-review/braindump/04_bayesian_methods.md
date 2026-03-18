# Bayesian Methods for March Madness Prediction

## Summary

Bayesian statistical methods offer a principled framework for NCAA tournament prediction by treating team strengths as latent variables with uncertainty, updating beliefs as new game data arrives, and producing full probability distributions over outcomes rather than point estimates. The approaches surveyed here range from lightweight Elo-based systems with implicit Bayesian updating (FiveThirtyEight) to fully specified hierarchical models implemented in probabilistic programming languages (PyMC3, Stan). A recurring theme is the decomposition of team ability into offensive and defensive components, with Poisson or Normal likelihoods for scoring, and the use of MCMC (typically NUTS or Metropolis-Hastings) to sample from posterior distributions. Prediction accuracy across methods tends to hover around 67-74% on individual game outcomes, with seed-based baselines at roughly 72%. The primary advantage of Bayesian approaches over frequentist alternatives is uncertainty quantification: credible intervals on team strengths, full posterior predictive distributions over game scores, and the ability to propagate uncertainty through bracket simulations.

Key takeaways for building a model:

- **Hierarchical structure** (team-level parameters drawn from a population distribution) provides natural regularization and handles the unbalanced schedule problem in college basketball.
- **Bradley-Terry / logistic models** on team strength differences are the workhorse for binary win/loss prediction; Poisson models on scores provide richer output.
- **Priors matter less than structure**: weakly informative priors (Normal(0, large_sd)) work well; the data dominates with hundreds of games per season.
- **Sum-to-zero constraints** on team ratings ensure identifiability.
- **Composite approaches** (blending multiple rating systems) tend to outperform any single model, as FiveThirtyEight demonstrates.
- **Tournament-specific adjustments** (fewer upsets than regular season, neutral-court effects, travel distance) improve calibration.

---

## Source 1: Barnes Analytics -- Hierarchical Bayesian Model in PyMC3

**Title:** Predicting March Madness Winners with Bayesian Statistics in PYMC3!
**URL:** https://barnesanalytics.com/predicting-march-madness-winners-with-bayesian-statistics-in-pymc3/
**Type:** Blog post / tutorial

### Model Structure

A three-level hierarchical Bayesian model inspired by sports analytics work in soccer and rugby:

1. **Global parameters:** Home court advantage, intercept, and standard deviations governing the spread of team-level parameters.
2. **Team-specific latent variables:** Each team has an offensive strength parameter and a defensive strength parameter.
3. **Game-level predictions:** Scoring intensities for each team in each game are derived from the relevant offensive/defensive parameters.

The scoring intensity for the home team in a given game is:

```
home_theta = exp(intercept + home * advantage + offense[home_team] + defense[away_team])
away_theta = exp(intercept + offense[away_team] + defense[home_team])
```

The likelihood is **Poisson** with these theta values as rate parameters, treating basketball scores as discrete counts.

### Priors

- `Flat` (non-informative) priors for home advantage and intercept.
- `HalfStudentT(nu=3, sd=2.5)` for standard deviation hyperparameters.
- `Normal` priors for team offensive and defensive strength parameters, centered around group means.
- Team parameters are centered around their group means to reduce shrinkage and improve relative strength estimation.

### Data

- Kaggle 2017 March Madness dataset: 5,395 games from a single season.
- Restructured from winner/loser format to home/away format.
- Binary dummy variable for court advantage (home=1, away=0, neutral=0).
- Teams re-indexed for computational convenience.

### Inference

- **Sampler:** NUTS (No-U-Turn Sampler) via PyMC3.
- **Iterations:** 1,000 posterior samples with 1,000 tuning/burn-in steps.
- **Runtime:** ~15 minutes on older hardware.

### Predictive Accuracy

The model generates game outcome probabilities by sampling from the posterior. Example simulation for two specific teams:

- Team A at home: 48.4% win probability
- Team A away: 18.9% win probability
- Neutral court: 32.1% win probability

No aggregate accuracy metric reported on tournament outcomes. The author describes this as a "broad strokes super simple" model.

### Key Insights

- The Poisson likelihood for basketball scoring is a reasonable starting point but imperfect (basketball scores are not strictly Poisson-distributed due to pace effects and the discrete nature of 2-point and 3-point scoring).
- Forest plots of posterior distributions clearly separate strong from weak teams on both offense and defense.
- The model naturally handles counterfactual reasoning (what if teams played on a neutral court?) which is critical for tournament prediction where all games are on neutral courts.
- Planned enhancements include incorporating advanced basketball statistics (e.g., four factors, tempo) beyond raw final scores.

---

## Source 2: FiveThirtyEight -- Composite Bayesian Elo System

**Title:** How Our March Madness Predictions Work
**URL:** https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
**Additional methodology:** https://fivethirtyeight.com/features/march-madness-predictions-2015-methodology/
**Type:** Methodology documentation

### Model Structure

FiveThirtyEight uses a **composite power rating** system that blends multiple rating sources, then converts rating differences into win probabilities via a logistic function. This is not a single generative Bayesian model, but it embeds Bayesian reasoning at multiple levels:

1. **Elo ratings** are updated game-by-game using a Bayesian-like update rule where the posterior rating after a game depends on the prior rating and the game outcome.
2. **Preseason priors** come from AP/coaches' polls and prior-year Sagarin ratings reverted to the mean.
3. **Composite blending** of multiple independent rating systems acts as a form of Bayesian model averaging.

**Win probability formula:**

```
P(win) = 1 / (1 + 10^(-rating_difference * 30.464 / 400))
```

### Component Systems (Seven-System Composite)

**Five computer rankings (75% weight):**
1. Ken Pomeroy pythagorean ratings
2. Jeff Sagarin predictor ratings
3. Sonny Moore power ratings
4. Joel Sokol LRMC (Logistic Regression Markov Chain) ratings
5. ESPN Basketball Power Index (BPI/PVA variant)

**Two human-derived rankings (25% weight):**
1. NCAA selection committee S-curve (68-team ranking)
2. Preseason AP and coaches' poll rankings (weighted equally)

All systems are **normalized to have the same mean and standard deviation** before blending.

### Data Incorporated

- Complete game-by-game results for the current season (and historically back to the 1950s for Elo).
- Final scores and game locations.
- Travel distances between team home and game site.
- Injury data via Sports-Reference win shares methodology (adjusted for strength of schedule).
- Preseason rankings as informative priors on team quality.

### Bayesian Updating Mechanism

- **Elo ratings** start each season reverted toward conference mean (a shrinkage prior).
- After each game, ratings update based on the surprise in the outcome: upsets produce larger updates than expected wins.
- Tournament-specific adjustment: historically there are **fewer upsets in the NCAA tournament** than expected from regular-season Elo differences, possibly because tournament conditions (neutral sites, better officiating) reduce noise.

### Post-Aggregation Adjustments

1. **Injury adjustments:** Based on win shares; a key player's absence reduces team rating.
2. **Travel distance adjustment:** Teams traveling far face an effective 2-3 point disadvantage.
3. **In-tournament updating:** After each round, ratings adjust based on performance.

### Bracket Probability Calculation

Rather than Monte Carlo simulation, FiveThirtyEight uses **direct conditional probability calculation**: the chance of reaching round N equals the chance of reaching round N-1 multiplied by the probability of beating each possible opponent in round N, weighted by each opponent's probability of being there.

### Predictive Accuracy

- "Called" tournament winners correctly in two of three years (at time of writing).
- Strong calibration: teams listed at 70% win probability historically won ~70% of the time.
- No specific log-loss or Brier score reported in the methodology documentation.

### Key Insights

- **Ensemble methods dominate:** Blending 7 independent rating systems provides robustness that no single model achieves.
- The 75/25 split between computer and human rankings reflects the finding that human rankings contain signal (committee expertise, knowledge of injuries/momentum) not fully captured by algorithms.
- **Elo as implicit Bayesian updating** is computationally cheap and interpretable, even if less statistically rigorous than a full hierarchical model.
- The tournament-specific upset adjustment is an important empirical finding: regular-season models slightly overpredict upsets in tournament settings.

---

## Source 3: Kaggle Bradley-Terry Model for March Madness

**Title:** Bradley-Terry Model | Kaggle - Men's March Madness 2019
**URL:** https://youhoo0521.github.io/kaggle-march-madness-men-2019/models/bradley_terry.html
**Type:** Kaggle competition notebook / analysis

### Model Structure

The **Bradley-Terry model** estimates a latent strength parameter alpha_j for each team. The probability that team j defeats team k is:

```
P(j beats k) = exp(alpha_j - alpha_k) / (1 + exp(alpha_j - alpha_k))
```

This is mathematically equivalent to logistic regression on the difference in team strengths. It is the canonical model for paired comparison data.

### Priors

- Team strength parameters: `alpha ~ Normal(0, sigma^2)` with a **uniform hyperprior on sigma**.
- The zero-centered prior encodes the assumption that "an average team has a neutral effect on the outcome of the game."
- This is a **hierarchical specification**: the population-level variance sigma is learned from data rather than fixed.

### Data

- Regular season game outcomes (binary: did team 1 win?) from 2015 NCAA season.
- Tournament game outcomes used for validation.
- Team identifiers and seed information for comparison with seed-based baselines.

### Inference

- Implemented in **Stan**.
- **MCMC sampling:** 1,000 iterations across 4 chains.
- Posterior samples represent "thousands of simulated scenarios of the world based on observed data."

### Predictive Accuracy

- **Log-loss performance** is "comparable to the SeedDiff benchmark model" across 1985-2019 seasons.
- The authors note this is unsurprising because seed difference and estimated team strength contain overlapping information.
- Posterior predictive distributions for closely matched teams show **symmetric, wide histograms** (high uncertainty), while mismatched teams show **skewed histograms** (confident predictions).

### Key Insights

- The Bradley-Terry model is elegant but limited: it only uses win/loss outcomes, ignoring margin of victory, pace, and other game-level features.
- Tournament-qualified teams predominantly show **positive estimated levels**, as expected.
- There is a strong **inverse relationship between seed ranking and estimated strength**, but with notable exceptions (some tournament teams have negative estimated levels).
- The model predicts **more upsets** than a simple seed-difference model in certain matchups, which is an interesting structural difference.
- Future directions include: score-difference modeling, conference-specific hierarchical parameters, and t-distribution priors for robustness against outlier games.

---

## Source 4: Nelson (2012) -- Bayesian Logistic Regression for the NCAA Tournament

**Title:** Modeling the NCAA Tournament Through Bayesian Logistic Regression
**Author:** Bryan T. Nelson
**Institution:** Duquesne University (Master's thesis, Computational Mathematics)
**URL:** https://dsc.duq.edu/etd/970
**Type:** Master's thesis

### Model Structure

The model uses **Bayesian logistic regression** where the dependent variable Y is binary (1 = higher seed wins, 0 = lower seed wins) and the predictors X_1, ..., X_n are **differences in regular-season statistics** between the two teams in each matchup:

```
P(Y) = exp(beta_0 + sum(beta_i * X_i)) / (1 + exp(beta_0 + sum(beta_i * X_i)))
```

The key innovation is using **MCMC for both model selection and coefficient estimation**, rather than relying on a single pre-specified model.

### Priors

- Regression coefficients: `beta_i ~ Normal(mu, sigma^2)` with common mean mu and variance sigma^2 across all coefficients.
- Prior on the model itself: `pi(M_0) = 1/2^n` (uniform over all 2^n possible subsets of predictors), making all models equally likely a priori.
- The joint prior on coefficients given a model is the product of independent Normal priors.

### MCMC Methodology

**Two-stage MCMC process:**

1. **Metropolis-Hastings for model selection:** Proposes adding or removing one variable at a time; accepts/rejects based on likelihood ratio. The algorithm explores the 2^n model space efficiently without exhaustive enumeration.
2. **Metropolis sampling for coefficient estimation:** Given a selected model, samples regression coefficients one at a time from their conditional posteriors. Recommends at least 2,500 iterations with thinning (saving every W-th sample) to reduce autocorrelation.

**Monte Carlo integration** is used to approximate the marginal likelihood of each model (integrating out regression coefficients), which is intractable in closed form.

### Data

- Regular-season statistics for all 64 tournament teams, collected for seasons 2003-2012.
- Statistics include: points per game, rebounds, assists, steals, blocks, turnovers, field goal %, 3-point %, free throw %, and various other box score statistics.
- Predictor variables are **differences** (higher seed stat minus lower seed stat) to frame each matchup as a head-to-head comparison.

### Predictive Accuracy

- Evaluated on the 63 actual games of the 2012 tournament.
- **Eight of the Bayesian models performed as well as Pomeroy's rating system.**
- **Four models matched Sagarin's rating system** in accuracy.
- When simulating full brackets (rather than using actual matchups), only **one model outperformed both Pomeroy and Sagarin**.
- Bayesian models on average outperformed least-squares models, though the difference was not always statistically significant by t-test.
- Baseline accuracy: picking higher seed = 72%; Sagarin = 73%; Pomeroy = 74%.

### Key Insights

- The matchup-based approach (using stat differences rather than individual team ratings) allows the model to identify games where a lower seed has a favorable statistical profile against a higher seed, enabling realistic upset prediction.
- MCMC model selection naturally penalizes overly complex models because the likelihood ratio test favors parsimony when additional variables do not improve fit.
- The Normal prior on coefficients acts as a regularizer similar to ridge regression, preventing overfitting to the relatively small training set.
- The thesis demonstrates that Bayesian methods can match established rating systems (Pomeroy, Sagarin) without requiring the complex infrastructure those systems use.

---

## Source 5: Seth Hollander -- Hierarchical Team Ratings with PyMC3

**Title:** Rating college basketball teams (with probabilistic programming!)
**URL:** https://sethah.github.io/ncaa-ratings.html
**Type:** Blog post / tutorial

### Model Structure

A hierarchical Bayesian model where each team has two latent skill parameters:

- **Offensive skill** (beta^o_i): points above/below league average for scoring.
- **Defensive skill** (beta^d_i): points above/below league average for points allowed.

The expected score for a team in a game:

```
E[Score_home] = Intercept + Home_Advantage + Offense_home + Defense_away
E[Score_away] = Intercept + Offense_away + Defense_home
```

The likelihood is **Normal** (not Poisson):

```
Score ~ Normal(mu, sigma)
```

where sigma is a constant noise term.

**Sum-to-zero constraint** on both offensive and defensive ratings ensures identifiability (otherwise the intercept and team effects are not separately identifiable).

### Priors

- Team skill ratings: `Normal(0, sd=100)` -- extremely wide, effectively non-informative.
- Standard deviation of scores: `Uniform(0.01, 20)`.
- Home advantage: `Normal(0, sd=5)` -- weakly informative.
- Intercept: `Normal(mean_score, sd=10)` -- centered on observed average score.

### Inference

- **Framework:** PyMC3.
- **Initialization:** Maximum a Posteriori (MAP) estimation.
- **Sampler:** NUTS (No-U-Turn Sampler).
- **Posterior samples:** 3,000 draws after burn-in.

### Validation Approach

The author validates the model using **synthesized data** with known true parameters:

- 200 games among 5 teams with known offensive and defensive ratings.
- Noise generated as Normal(0, 3).
- All true parameter values fell within the 95% credible intervals from the posterior.
- Results matched OLS (ordinary least squares) estimates exactly, confirming that with flat priors and Normal likelihood, the Bayesian posterior matches the frequentist sampling distribution.

### Key Insights

- **The unbalanced schedule problem** is the central challenge in college basketball rating: "a team's observed output depends on the true skill of the teams that they have played." Hierarchical Bayesian models handle this naturally by jointly estimating all team parameters.
- The model provides "an entire k-dimensional probability distribution for the parameter values," giving uncertainty estimates that point-estimate methods lack.
- The sum-to-zero constraint is critical for identifiability in these additive models.
- With weakly informative priors, the Bayesian and frequentist approaches converge, but the Bayesian framework provides richer output (credible intervals, posterior predictive distributions).
- The Normal likelihood for scores is more appropriate than Poisson for basketball because game scores have a much larger mean (~70 points) and the variance is better captured by a continuous distribution.

---

## Source 6: Bayesian State-Space Models for Team Strength

**Title:** A State-Space Model to Evaluate Sports Teams
**URL:** https://statsbylopez.netlify.app/post/a-state-space-model-to-evaluate-sports-teams/
**Related paper:** arXiv:1412.0248
**Type:** Blog post summarizing academic research

### Model Structure

A **Bayesian state-space model** that treats team strength as a time-varying latent variable. Unlike static models that assume constant team quality throughout a season, this approach allows strengths to evolve:

```
strength[t] = strength[t-1] + noise
```

The model decomposes variability into three components:

1. **Between-season variability:** How much team strength changes from one year to the next.
2. **Within-season variability:** How team strength evolves during a season (injuries, player development, coaching adjustments).
3. **Game-to-game variability:** Random noise in individual game outcomes.

Each team also has its own **home advantage parameter**.

### Data

- Uses **betting market data** (point spreads and over/unders) as observed outcomes rather than raw game scores.
- The rationale is that betting markets aggregate vast amounts of information and are approximately efficient, so they provide a high-signal-to-noise-ratio measure of team quality differences.

### Bayesian Framework

- The state-space formulation is inherently Bayesian: the prior on team strength at time t is the posterior from time t-1.
- MCMC sampling is used to estimate the full posterior distribution over all latent team strengths at all time points.
- The model can be "uniformly applied across sporting organizations" because the state-space structure is general.

### Key Insights

- **Time-varying team strength** is important for March Madness prediction because teams that are improving (or declining) at season's end may be under/over-rated by static models.
- The decomposition of variance into between-season, within-season, and game-to-game components helps quantify how much of basketball outcomes is signal vs. noise.
- Betting market data as the "observed variable" is a pragmatic choice that sidesteps the problem of modeling complex game mechanics directly.
- The state-space approach could be combined with hierarchical models (e.g., conference-level grouping) for additional structure.

---

## Cross-Cutting Themes and Comparative Analysis

### Model Complexity Spectrum

| Source | Model Type | Likelihood | Parameters per Team | Framework |
|--------|-----------|-----------|-------------------|-----------|
| FiveThirtyEight | Composite Elo | Logistic | 1 (power rating) | Custom |
| Kaggle Bradley-Terry | Bradley-Terry | Bernoulli/Logistic | 1 (strength) | Stan |
| Nelson (2012) | Bayesian Logistic Regression | Bernoulli/Logistic | 0 (matchup-based) | Custom MCMC |
| Barnes Analytics | Hierarchical Poisson | Poisson | 2 (off/def) | PyMC3 |
| Hollander | Hierarchical Normal | Normal | 2 (off/def) | PyMC3 |
| Lopez et al. | State-Space | Normal | 2+ (time-varying) | MCMC |

### Accuracy Benchmarks

- **Seed-based baseline:** ~72% (picking higher seed every game, 2003-2011).
- **Sagarin ratings:** ~73%.
- **Pomeroy ratings:** ~74%.
- **Bayesian logistic regression (Nelson):** Comparable to Pomeroy/Sagarin (8 of models matched Pomeroy, 4 matched Sagarin).
- **Bradley-Terry (Kaggle):** Log-loss comparable to seed-difference baseline.
- **PyMC3 Poisson (Barnes):** No aggregate accuracy reported.
- **Composite (FiveThirtyEight):** Strong calibration; ~70% favorite wins ~70% of the time.

### Common Prior Choices

Most approaches use weakly informative priors, reflecting a consensus that with hundreds of games per season, the likelihood dominates:

- **Team strengths:** Normal(0, large_sd) -- centered at "average team"
- **Variance parameters:** HalfStudentT, Uniform, or HalfCauchy -- restricting to positive values
- **Home advantage:** Normal(0, moderate_sd) -- centered at zero, weakly informative
- **Model-level priors:** Uniform over model space (Nelson) or implicit in composite weighting (FiveThirtyEight)

### Practical Recommendations for Implementation

1. **Start with Bradley-Terry in Stan or PyMC** as a baseline -- it is simple, well-understood, and competitive with sophisticated approaches.
2. **Extend to offense/defense decomposition** (Normal likelihood on scores) for richer predictions and better interpretability.
3. **Add hierarchical conference structure** to handle the unbalanced schedule and provide natural shrinkage for teams with fewer games against strong opponents.
4. **Incorporate time-varying strength** via a state-space component to capture late-season momentum.
5. **Use posterior predictive simulation** (not just point estimates) to generate bracket probabilities that account for uncertainty.
6. **Blend with external ratings** (Pomeroy, BPI, Sagarin) as informative priors or as additional likelihood terms, following FiveThirtyEight's demonstrated success with composite approaches.
