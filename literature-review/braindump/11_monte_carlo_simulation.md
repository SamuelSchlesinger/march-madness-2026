# Monte Carlo Simulation for March Madness Bracket Prediction

## Summary

Monte Carlo simulation is the dominant computational approach for generating March Madness bracket predictions. The core idea is straightforward: model individual game outcomes as probabilistic events, then simulate the entire tournament thousands or millions of times to estimate each team's probability of advancing to each round. What distinguishes different implementations is (1) how they model individual game win probabilities, (2) how many simulations they run, (3) whether they update team ratings dynamically between rounds, and (4) whether they optimize brackets for pool-winning (expected value maximization) rather than pure accuracy.

A critical insight from the literature is the distinction between **probability-maximizing brackets** (pick the most likely winner in every game) and **expected-value-maximizing brackets** (pick contrarian winners that differentiate your bracket from the field). In a pool setting, the latter strategy dominates for pools larger than ~20 people. Monte Carlo simulation serves both purposes: it can estimate true advancement probabilities and it can power optimizers that search for high-EV bracket configurations given public pick distributions.

FiveThirtyEight notably did NOT use Monte Carlo for March Madness -- they computed conditional probabilities analytically through the bracket tree. This is feasible because the single-elimination structure is a directed acyclic graph, so the combinatorics are tractable. Monte Carlo becomes more valuable when the model includes dynamic rating updates, correlated outcomes, or other features that make analytical computation intractable.

---

## Source 1: Engaging Data -- March Madness Bracket Picker

- **URL**: https://engaging-data.com/march-madness-bracket-picker/
- **Author**: Engaging Data (anonymous)
- **Type**: Interactive web tool with methodology explanation

### Simulation Methodology
- Uses **historical seed-based win probabilities** derived from NCAA tournament data from 1985-2017.
- For matchups with historical precedent (e.g., 1 vs 16 seeds), win probabilities come directly from observed historical frequencies.
- For matchups without historical data (later rounds with unusual seed combinations), applies default rules:
  - **66% win probability** for the higher seed if seed difference >= 5
  - **50/50 coin flip** if seed difference < 5
- Runs **1,000 bracket simulations** per batch.
- Implemented entirely in JavaScript, client-side.

### How Game Outcomes Are Modeled
Each game is a Bernoulli trial with probability derived from historical seed matchup data. A random number is drawn and compared against the win probability to determine the winner. This is a pure seed-based model with no team-specific ratings.

### Bracket Generation
Each simulation produces a complete bracket. The 1,000 simulations are aggregated to show how frequently each team advances to each round. Users can also generate individual brackets one at a time.

### Key Insights
- Simplest possible Monte Carlo approach: historical frequencies as probabilities, no team-specific modeling.
- Demonstrates that even a basic seed-based model captures meaningful structure (1-seeds win the tournament far more often than 16-seeds).
- The tool is pedagogically useful for understanding how Monte Carlo works in this domain.
- Limitation: treats all 1-seeds as equivalent, all 2-seeds as equivalent, etc.

---

## Source 2: Unabated -- Building NCAA Basketball Power Rankings and a Bracket Simulator

- **URL**: https://unabated.com/articles/building-a-march-madness-bracket-simulator
- **Author**: Unabated staff
- **Type**: Technical guide / tutorial

### Simulation Methodology
The article provides the most detailed technical walkthrough of building a bracket simulator from scratch. The approach has three layers:

**Layer 1: Power Ratings**
- Recommends using a weighted average of publicly available rating systems (KenPom, ESPN BPI, etc.) rather than building proprietary models.
- The difference in power ratings between two teams represents the expected point differential on a neutral court.

**Layer 2: Converting Point Spreads to Win Probabilities**
Two methods presented:
- **Normal distribution sampling**: Sample from N(mean_spread, sigma=11.2) where 11.2 is the empirical standard deviation of score differentials in the shot-clock era. If the sampled value > 0, the favored team wins.
- **Logistic regression**: `Win_Prob = 1 / (1 + e^(-0.163 * predicted_score_differential))`. This converts point spreads directly to probabilities without sampling.

**Layer 3: Dynamic Rating Updates**
This is a distinctive feature. After each simulated round, team ratings are updated based on performance relative to expectation:
```
rating_diff = B1 * (score_diff - expected) + B2 * (score_diff - expected) * ln(game_number)
```
The rating update itself is sampled from a normal distribution centered on the regression estimate, with standard deviation equal to the model residuals. This captures the idea that a team that dramatically outperforms expectations in Round 1 is probably better than their pre-tournament rating suggested.

### How Game Outcomes Are Modeled
Each game is modeled by sampling from a normal distribution centered on the expected point differential. The winner is determined by the sign of the sampled value. This naturally captures both the mean expectation and the uncertainty around it.

### Bracket Optimization
The article references PoolGenius's Bracket Builder Tool, which considers "contrarian picking depending on pool size and structure." This hints at the expected-value optimization approach but doesn't detail the algorithm.

### Key Insights
- The dynamic rating update is a sophisticated feature that most simpler models lack. It models the idea that tournament performance reveals information about true team quality.
- Using the standard deviation of 11.2 points as the noise parameter is an empirically grounded choice.
- The logistic regression formula `1/(1+e^(-0.163*x))` is a clean, practical conversion from point spreads to probabilities.

---

## Source 3: arxiv (2503.21790v1) -- March Madness Tournament Predictions Model: A Mathematical Modeling Approach

- **URL**: https://arxiv.org/html/2503.21790v1
- **Authors**: Academic paper (2025)
- **Type**: Research paper

### Simulation Methodology
- Uses **logistic regression** to model individual game outcomes.
- Four input features (computed as differences between opposing teams):
  - Adjusted Offensive Efficiency (ADJOE)
  - Adjusted Defensive Efficiency (ADJDE)
  - Power Rating (BARTHAG, from Barttorvik)
  - Two-Point Shooting Percentage Allowed (2PD)
- L2 regularization to prevent overfitting.
- Features are standardized (mean 0, std 1).
- Runs **100 Monte Carlo simulations** per bracket (relatively small number).

### How Game Outcomes Are Modeled
The logistic regression model outputs P(team A wins) for each matchup. A random number is drawn from Uniform(0,1) and compared against this probability to determine the winner. The model is:
```
P(Y=1|x) = 1 / (1 + e^(-eta))
where eta = B0 + B1*x1 + B2*x2 + ... + Bp*xp
```

### Accuracy Results
- **Individual game accuracy**: 74.6% on test data
- **Full bracket accuracy** varied significantly:
  - 2023 South/Midwest: 65.63% games correct (Spearman rho = 0.75)
  - 2023 East/West: 43.75% correct (Spearman rho = 0.49)
  - 2022 South/West: 56.25% correct (Spearman rho = 0.63)
  - 2022 East/Midwest: 50% correct (Spearman rho = 0.37)

### Key Insights
- Only 100 simulations is quite low -- most practitioners use 10,000-50,000+. The small number likely reflects this being an academic exercise rather than a production system.
- The feature selection is notable: they found that ADJOE, ADJDE, and BARTHAG were the most predictive, while 2-point shooting defense added marginal value.
- The variable bracket-level performance (43-66% across different regions/years) illustrates the fundamental difficulty: even with 74.6% game-level accuracy, bracket-level outcomes are highly volatile.
- Static team ratings (no in-tournament updates) are acknowledged as a limitation.

---

## Source 4: Nathan Brixius -- Predicting the NCAA Tournament Using Monte Carlo Simulation

- **URL**: https://nathanbrixius.com/2014/03/19/predicting-the-ncaa-tournament-using-monte-carlo-simulation/
- **Author**: Nathan Brixius
- **Type**: Blog post with Excel implementation

### Simulation Methodology
- Runs **10,000 simulated tournaments**.
- Team strength ratings follow **normal (bell curve) distributions** rather than being fixed point estimates. Each team's rating is a distribution with a mean and standard deviation, and each simulation samples from this distribution.
- Winners are determined by comparing sampled ratings using Excel IF statements.
- Built in Microsoft Excel using Frontline Systems' Analytic Solver Platform.

### How Game Outcomes Are Modeled
Each simulation:
1. Samples a strength value for each team from their respective normal distributions.
2. Compares the sampled strengths of the two teams in each matchup.
3. The team with the higher sampled strength wins.

This is equivalent to modeling game outcomes with a probit-like model where the probability of team A beating team B depends on the overlap of their strength distributions.

### Bracket Generation
Results are aggregated across all 10,000 simulations:
- Raw win counts by team (summing to 10,000)
- Pivot table summaries
- Visualization charts showing championship probabilities

### Key Insights
- Using distributions for team strength (rather than point estimates) is a principled way to capture uncertainty about team quality, not just game-level randomness.
- The Excel-based implementation makes this accessible to non-programmers.
- The author suggests extensions: correlated distributions by conference, simulation-optimization models for tuning.
- 10,000 simulations is a reasonable number for stable probability estimates (championship probabilities for top teams converge well at this scale).

---

## Source 5: Biophysics and Beer -- More March Madness Monte Carlo Style

- **URL**: https://mglerner.github.io/posts/more-march-madness-monte-carlo-style.html
- **Author**: M.G. Lerner
- **Type**: Technical blog post

### Simulation Methodology
This is the most theoretically interesting approach found. Rather than independent sampling of each game, the author treats bracket generation as an **energy optimization / statistical mechanics problem**:

- Uses **KenPom's log5 formula** for win probabilities:
  ```
  win_pct = (A - A*B) / (A + B - 2*A*B)
  ```
  where A and B are team strength ratings.
- Defines an energy function: `energy = -win_pct` for each game outcome.
- Treats the bracket as a state in "bracket space" and performs a **Monte Carlo walk** through this space (akin to Metropolis-Hastings sampling).

### Temperature Parameter
A temperature parameter controls the exploration/exploitation tradeoff:
- **Low temperature**: Favors the most probable outcomes (chalk bracket).
- **High temperature**: Approaches random outcomes (maximum entropy).
- **Calibration**: The author calibrates temperature by checking that 8-vs-9 seed matchups come out near 50/50, since historically these are close to coin flips.

### Bracket Space Navigation
A `Bracket.swap` method enables transitions between bracket configurations, allowing systematic exploration of the space rather than independent sampling. This is fundamentally different from the standard "simulate each game independently" approach.

### Output
The system tracks:
- Bracket energy values across simulations
- The lowest-energy bracket (most probable overall bracket)
- The most frequently occurring bracket
- These can differ, which is itself an interesting finding.

### Key Insights
- The statistical mechanics analogy is powerful: it naturally connects to the question of how much randomness to inject into bracket generation.
- The temperature parameter is essentially a hyperparameter controlling how "chalky" vs "chaotic" generated brackets are.
- The Monte Carlo walk approach can potentially find high-probability brackets more efficiently than independent sampling, since it explores the neighborhood of good brackets.
- Running 1,000 trials showed rapid convergence when Final Four teams were constrained.

---

## Source 6: GPU-Accelerated Monte Carlo (GitHub)

- **URL**: https://github.com/gbarbalinardo/march-madness-bracket
- **Author**: Giuseppe Barbalinardo
- **Type**: Open-source code repository

### Simulation Methodology
- Uses KenPom statistics (March 2015 data) as input.
- Leverages **CUDA and NumbaPro** for GPU-accelerated parallel simulation.
- Two parallelization strategies:
  - **Vectorize**: Converts Python functions into NumPy ufuncs for element-wise operations.
  - **Guvectorize**: Handles array-based operations for generalized universal functions.

### Key Insights
- Demonstrates the computational scalability of Monte Carlo bracket simulation -- GPU acceleration enables running millions of simulations in reasonable time.
- The implementation shows that the per-simulation compute is embarrassingly parallel: each tournament simulation is independent.
- Practical detail: the input is a JSON file with team statistics, making it easy to update year-to-year.

---

## Source 7: Lumivero / @RISK -- March Madness Predictions with Monte Carlo

- **URL**: https://lumivero.com/resources/blog/march-madness-predictions-with-risk/
- **Author**: Lumivero (formerly Palisade)
- **Type**: Commercial software blog post

### Simulation Methodology
- Uses **@RISK**, a commercial Monte Carlo simulation add-in for Excel.
- Assigns probability distributions to key factors: offensive/defensive efficiency, historical performance, rebounds, team momentum.
- Simulates "thousands of tournament outcomes."
- No specific distribution types or simulation counts are given.

### Key Insights
- Represents the "commercial tool" approach: less technical transparency, but accessible to business/analytics professionals who already use Excel.
- The emphasis is on modeling uncertainty rather than finding a single prediction.
- The value proposition is identifying high-risk matchups and upset probabilities rather than bracket optimization.

---

## Source 8: FantasyLabs / PoolGenius -- NCAA Bracket Picks Optimizer

- **URL**: https://www.fantasylabs.com/articles/ncaa-bracket-picks-optimizer-build-a-smarter-bracket-win-your-pool/
- **Author**: FantasyLabs staff
- **Type**: Product description with strategic methodology

### Bracket Optimization Methodology
This source focuses on the optimization layer that sits on top of Monte Carlo simulation:

The optimizer processes five variables simultaneously:
1. **Pool-specific parameters**: Number of contestants, scoring rules
2. **Public pick data**: Ownership percentages from major bracket platforms
3. **Team advancement probabilities**: Based on strength metrics
4. **Risk allocation**: Distributed across all 67 picks
5. **Upset bonus adjustments**: When applicable

The system "runs millions of simulations to generate the bracket with the highest expected value."

### Pool Size Strategy
- **Small pools (~20 entries)**: Favor conservative, chalk-heavy selections maximizing accuracy.
- **Large pools (500+ entries)**: Reward strategic contrarian positions where calculated risk-taking separates winning brackets.
- The key metric is the **ownership gap**: the difference between a team's actual championship probability and their public pick percentage.

### Performance Claims
- Subscribers report $10 million in pool winnings since 2017.
- 52% of subscribers win annual bracket prizes.
- Contest victory rates 3x higher than expected.

### Key Insights
- This is the clearest articulation of the distinction between probability-maximizing and EV-maximizing brackets.
- The "ownership gap" concept is the central insight: you want teams that are more likely to win than the public thinks, because picking them gives you differentiation when they do win.
- The optimization problem is: maximize E[points_scored * (1 - fraction_of_field_who_also_scored_those_points)], not simply maximize E[points_scored].
- Pool size fundamentally changes optimal strategy. In a 10-person pool, picking chalk is fine. In a 10,000-person pool, you need to take risks that most of the field won't take.

---

## Cross-Cutting Themes

### 1. The Probability Pipeline
Almost all approaches follow the same pipeline:
1. **Rate teams** (KenPom, Elo, composite ratings, logistic regression)
2. **Convert ratings to game-level win probabilities** (log5, logistic function, normal CDF)
3. **Simulate games** (Bernoulli draws against the win probability)
4. **Aggregate results** (count advancement frequencies across simulations)

### 2. Simulation Scale
- 100 simulations (academic paper) -- too few for stable estimates
- 1,000 simulations (Engaging Data, Biophysics and Beer) -- adequate for rough estimates
- 10,000 simulations (Nathan Brixius, SportsLine) -- good for stable probability estimates
- 50,000 simulations (Versus Sports Simulator) -- high confidence
- Millions of simulations (PoolGenius/FantasyLabs) -- needed for bracket optimization where the search space is enormous

### 3. Dynamic vs Static Ratings
Most simple implementations use static pre-tournament ratings. The Unabated approach is notable for updating ratings between rounds based on performance, which better captures information revelation during the tournament.

### 4. Bracket Optimization is a Different Problem
Estimating advancement probabilities (the Monte Carlo part) is necessary but not sufficient for winning bracket pools. The optimization layer requires:
- Public pick distribution data
- Pool-specific scoring rules
- Pool size
- A search algorithm over the space of possible brackets

### 5. FiveThirtyEight's Analytical Alternative
FiveThirtyEight demonstrated that for a fixed bracket structure with known matchup probabilities, you can compute advancement probabilities analytically using conditional probability chains, without any Monte Carlo sampling. This is mathematically exact but less flexible than simulation (harder to add dynamic updates, correlated outcomes, etc.).

### 6. The Temperature Metaphor
The Biophysics and Beer approach introduces temperature as a control parameter, which elegantly captures the spectrum from "always pick the favorite" (T=0) to "flip a fair coin" (T=infinity). This is a useful conceptual framework even if you don't implement the full statistical mechanics machinery.
