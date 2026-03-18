# Bracket Strategy and Pool Optimization

This chapter synthesizes the literature on how to translate game-level probability estimates into pool-winning brackets. The core insight is that building an accurate bracket and building a bracket that wins a pool are fundamentally different objectives. Accuracy asks "who will win each game?" while pool optimization asks "what set of picks maximizes my chance of finishing first in this specific competition?" The gap between these two questions drives everything that follows.

For the modeling foundations that produce the probability estimates consumed by bracket strategy, see [Modeling Approaches](modeling-approaches.md). For how tournament structure shapes the landscape these strategies operate in, see [Tournament Dynamics](tournament-dynamics.md).

## 1. Probability-Maximizing vs. Expected-Value-Maximizing Brackets

The single most important conceptual distinction in the bracket strategy literature is between two optimization targets:

- **Probability-maximizing (chalk) brackets** pick the most likely winner of every game. This maximizes expected score and produces the single most probable bracket outcome in any given year. The chalk bracket scores roughly 20.4 points more than the average bracket and performs as well or better than most expert picks (Flerlage Twins, 2016). It is the baseline any model must beat.

- **Expected-value-maximizing (pool-winning) brackets** pick the combination of outcomes that maximizes the probability of finishing first in a specific pool. This is a game-theoretic problem: your bracket competes against other entries, so you need picks that are both correct and differentiated from the field. As PoolGenius frames it, the optimization target is expected pool-winning probability, not expected score.

These two objectives diverge because bracket pools are zero-sum competitions. Picking the chalk favorite as champion may be the single most likely outcome, but if 40% of the pool also picks that team, you gain no separation when you are right and fall behind everyone who picked a different correct champion when you are wrong. The literature is unanimous: maximizing expected score and maximizing win probability are different problems, and the difference grows with pool size.

This distinction connects to a broader theme in [Evaluation & Calibration](evaluation-and-calibration.md): models should be evaluated not just on accuracy metrics (Brier score, log loss) but on their downstream utility for the specific decision context.

## 2. Pool Size Effects on Optimal Strategy

Pool size is the primary variable that determines where on the chalk-to-contrarian spectrum an optimal bracket should sit. PoolGenius analyzed 21,709 real pools and found their optimizer's win rate relative to random expectation varied substantially:

| Pool Size | Win Rate vs. Random |
|-----------|-------------------|
| 10 or fewer | 2.2x |
| 11-30 | 2.9x |
| 31-50 | 3.3x |
| 51-100 | 3.4x |
| 101-250 | 3.7x |
| 251-1,000 | 3.6x |
| 1,001-9,999 | 2.0x |
| 10,000+ | 1.3x |

The practical implications fall into three regimes:

**Small pools (fewer than 10 entries).** Go chalk. In a 10-person pool, you start with roughly a 10% win probability by random chance. Picking favorites across the board is a strong strategy because opponents tend to hurt themselves with poorly chosen upsets. A 2009 study in the Journal of Applied Social Psychology found that conservative strategies achieve 87.5% game-level accuracy versus 75.2% for typical public brackets. In small pools, accuracy dominates differentiation.

**Mid-size pools (25-100 entries).** Balance risk and value. The key principle is to concentrate risk selectively rather than distribute it uniformly. One effective approach: pick a mildly contrarian champion (a strong 2-seed or 3-seed with lower public ownership) while keeping early rounds relatively chalky. The reverse also works -- chalk champion with some early-round upsets. The point is that a bracket with 67 interdependent decisions should not be uniformly aggressive or uniformly conservative.

**Large pools (100+ entries).** Maximize leverage. In a 1,000-person pool, the chalk bracket is extremely unlikely to win because dozens of other entries will be nearly identical to it. You need differentiation, which means targeting underowned teams and accepting lower expected accuracy in exchange for higher win probability. The optimizer's edge peaks in the 100-1,000 range, then declines in massive pools (10,000+) where variance overwhelms strategy.

Jeremy Losak's research at Syracuse corroborates this framework from a behavioral economics perspective: public brackets exhibit systematic biases (discussed in Section 7 below) that make contrarian positioning viable in larger pools.

## 3. Scoring System Impacts

The scoring system determines how points are distributed across rounds, which in turn determines which picks matter most. The same bracket should not be submitted to pools with different scoring formats.

| Format | Champion's Share of Total Points | Strategic Emphasis |
|--------|--------------------------------|-------------------|
| 1-2-4-8-16-32 (standard doubling) | ~17% | Late rounds dominate; champion pick is worth 32 first-round picks |
| 1-2-3-4-5-6 (linear) | ~5% | Early rounds matter more; result often decided by Elite Eight |
| 1-1-1-1-1-1 (flat) | Minimal | 83% of points come from the first three rounds; early accuracy is everything |
| 2-3-5-8-13-21 (Fibonacci) | Moderate | Gradual late-round emphasis |
| Seed-based / upset bonus | Varies | Dramatically increases underdog value; double-digit seed runs become profitable |

The standard doubling format (used in roughly 65% of pools) creates an extreme weighting toward champion selection. A poor first round is recoverable with a correct champion pick. This means champion selection is the single highest-leverage decision in most pools.

In flat scoring, by contrast, the first round is determinative. Getting 25 of 32 first-round games right matters far more than picking the champion, because the champion pick is worth no more than any other game.

Upset-bonus formats invert the usual calculus entirely. When a correct 12-over-5 pick earns bonus points, the expected value of picking upsets rises. In these formats, multiple double-digit seeds advancing to the Sweet 16 can be mathematically justified even when each individual upset is unlikely.

## 4. The Leverage Concept

Leverage is the central analytical concept in bracket pool optimization:

> **Leverage = Team's advancement probability - Public pick rate for that team**

Positive leverage means a team is underowned relative to its actual chances. Picking a positive-leverage team gives you differentiation when the pick hits -- you score points that most of your opponents do not.

Negative leverage means a team is overowned. Even if the pick is correct, the benefit is diluted because most of the field also picked that team.

As PoolGenius states: "Any outcome where the public pick rate does not precisely match game-advancement odds provides value on one side." The optimizer's job is to systematically find positive-leverage spots and load the bracket with them.

The optimization problem can be loosely expressed as: maximize E[points_scored * (1 - fraction_of_field_who_also_scored_those_points)], rather than simply maximizing E[points_scored]. This is why bracket pools are fundamentally game-theoretic contests, not prediction exercises.

Leverage is most consequential for champion selection (because of the 32-point weighting in standard scoring) but applies at every stage of the bracket. A 6-seed with 37% first-round win probability and only 20% public pick rate is a positive-leverage upset pick. A 1-seed with 16% championship probability and 25% public ownership is a negative-leverage champion pick.

The betting markets literature reinforces this concept from a different angle. The market's closing line is the best available estimate of true game probabilities (see [Evaluation & Calibration](evaluation-and-calibration.md) for why this is the benchmark). Using market-derived probabilities as the "true" probability in the leverage calculation, and public bracket pick rates as the comparison, gives the cleanest leverage estimates.

## 5. Monte Carlo Simulation for Bracket Generation

Monte Carlo simulation is the dominant computational method for generating bracket predictions and powering bracket optimizers. The standard pipeline is:

1. **Rate teams** using power ratings (KenPom, Elo, composite systems)
2. **Convert ratings to game-level win probabilities** via logistic function, log5, or normal CDF
3. **Simulate each game** as a Bernoulli draw against the win probability
4. **Repeat thousands or millions of times** to estimate advancement probabilities

The literature reveals a wide range of simulation scales:

- 100 simulations (academic exercises) -- too few for stable estimates
- 1,000 simulations -- adequate for rough probability estimates
- 10,000 simulations -- good for stable advancement probabilities
- 50,000+ simulations -- high confidence
- Millions of simulations -- needed for bracket optimization, where the system must evaluate thousands of bracket configurations against each other

For game-level modeling, the Unabated guide provides a particularly detailed specification. Their approach converts power rating differentials to win probabilities using `Win_Prob = 1 / (1 + e^(-0.163 * predicted_score_differential))`, with an empirically grounded noise parameter of 11.2 points (the standard deviation of score differentials in the shot-clock era). They also incorporate dynamic rating updates between rounds -- if a team dramatically outperforms expectations in Round 1, its rating is adjusted upward for subsequent simulations. This is a meaningful enhancement over the static-rating approaches used by most simpler models.

GPU-accelerated implementations (e.g., Barbalinardo's CUDA-based simulator) demonstrate that the per-simulation computation is embarrassingly parallel, making it feasible to run millions of tournaments in reasonable wall-clock time.

An important alternative: FiveThirtyEight did not use Monte Carlo for March Madness at all. They computed conditional probabilities analytically through the bracket tree, which is feasible because the single-elimination structure is a directed acyclic graph. This is mathematically exact but less flexible than simulation when the model includes dynamic rating updates, correlated outcomes, or other features that make analytical computation intractable.

For more on the modeling approaches that produce the team ratings consumed by Monte Carlo simulation, see [Modeling Approaches](modeling-approaches.md).

## 6. The Statistical Mechanics / Temperature Parameter Approach

One of the most theoretically interesting approaches in the literature comes from M.G. Lerner's "Biophysics and Beer" blog, which treats bracket generation as a statistical mechanics problem.

The core idea: define an energy function over bracket states, where each game outcome contributes `energy = -win_probability` for the chosen winner. The total bracket energy is the sum over all 63 games. Low-energy brackets are more probable; high-energy brackets contain more upsets.

A **temperature parameter** then controls the exploration-exploitation tradeoff:

- **Temperature = 0**: Always pick the favorite. Produces the chalk bracket (the lowest-energy state, i.e., the most probable single bracket).
- **Temperature = infinity**: Approaches random coin flips for every game. Maximum entropy, no information used.
- **Intermediate temperature**: Generates brackets that are "mostly chalk" but include some upsets, calibrated by how much randomness you inject.

The author calibrates temperature by checking that 8-vs-9 seed matchups come out near 50/50, since historically these are close to coin flips. This is an elegant calibration target.

Rather than simulating each game independently, this approach performs a Monte Carlo walk through "bracket space" using a swap operation that transitions between neighboring bracket configurations (akin to Metropolis-Hastings sampling). This can potentially find high-probability brackets more efficiently than independent sampling, because it explores the neighborhood of good brackets rather than drawing each bracket from scratch.

An interesting finding: the lowest-energy bracket and the most frequently occurring bracket can differ, which reflects the distinction between the mode and the mean of the bracket probability distribution.

The temperature metaphor is useful even without the full statistical mechanics machinery. It captures the spectrum from conservative to aggressive bracket construction as a single continuous parameter, and it connects naturally to the pool-size discussion: small pools call for low temperature (chalk), large pools for higher temperature (more upsets, more differentiation).

## 7. Public Pick Rate Biases

The leverage concept is only useful if public pick rates systematically diverge from true probabilities. The literature identifies several persistent biases:

**No. 1 seed overselection.** This is the single most exploitable inefficiency in bracket pools. Losak's research at Syracuse finds that No. 1 seeds are "massively overselected" as champions relative to their actual title probability. Historically, No. 1 seeds win the championship roughly 65% of the time (26 of 40 tournaments), but the four No. 1 seeds collectively receive 50-60%+ of public champion picks, meaning the average No. 1 seed is overowned. The overall No. 1 seed in particular tends to attract disproportionate public attention.

**Familiarity and brand-name bias.** Losak's behavioral economics research shows that fans consistently favor teams they recognize through regional proximity, conference affiliation, or prior media exposure. Even minimal familiarity distorts probability assessments. "Blue blood" programs (Duke, Kentucky, North Carolina, Kansas) tend to be overowned relative to their actual chances.

**Mid-major underselection.** The flip side of brand-name bias: teams from smaller conferences that earn strong seed lines tend to be underowned by the public. When a mid-major earns a 5- or 6-seed with metrics that justify it, the public often picks against them in favor of the more recognizable opponent.

**Upset quota thinking.** Most people pick too many upsets, but they pick them in the wrong places. Public brackets exhibit "quota thinking" -- the belief that a certain number of 12-over-5 upsets must happen each year, leading to upset picks distributed by seed-matchup stereotype rather than by analysis of specific team matchups. PoolGenius research shows that always picking the lower seed yields 87.5% accuracy versus 75.2% for typical public brackets, suggesting the average bracket-maker picks far too many upsets.

**Overestimation of top-seed Sweet 16 advancement.** Sports Illustrated data shows public brackets overestimate top seeds' chances of reaching the Sweet 16 by 9-16 percentage points versus actual historical rates. This creates positive leverage on the teams that would beat those top seeds in the second round.

These biases are what make contrarian strategies viable. If the public priced teams efficiently (pick rates matching true probabilities), there would be no leverage to exploit and the optimal strategy would simply be to maximize accuracy.

## 8. Practical Tools

Several tools operationalize the principles described above:

| Tool | Type | Cost | Key Capability |
|------|------|------|---------------|
| [PoolGenius](https://poolgenius.teamrankings.com/ncaa-bracket-picks/) (TeamRankings) | Web app | ~$25/year | Pool-specific optimization using public pick data, sportsbook odds, and millions of simulations. Reports $2.8M+ in subscriber winnings since 2017. |
| [BracketIQ](https://www.bracketsiq.com/) | Web app | Paid | Integrates KenPom, Torvik, Haslametrics, and EvanMiya data. |
| [BettingPros Bracket Optimizer](https://www.bettingpros.com/ncaab/tournament/bracket-optimizer/) | Web app | Free | Matchup information, odds, and power ranking integration. |
| [DRatings](https://www.dratings.com/predictor/bracketology/) | Web app | Free | Bracketology projections using ratings, RPI, and strength of schedule. |
| [BracketVoodoo](https://www.bracketvoodoo.com/) | Web app | Paid | Bracket optimization tool. |

For raw probability estimates (as opposed to pool-specific optimization), the betting markets provide the strongest signal. Sportsbook closing lines, championship futures odds, and Sweet 16 advancement odds all reflect the consensus of sharp money. Prediction markets (Kalshi, Polymarket) are emerging as an alternative with lower vig and potentially less distorted implied probabilities. The betting markets literature (see the braindump on betting markets) emphasizes that market-derived probabilities should be the starting point, with model-based adjustments layered on top where you have specific reason to believe the market is wrong.

For team-level ratings that feed into custom simulations, KenPom remains the standard. Nate Silver's model weighted KenPom at 3/8ths alongside his proprietary COOPER ratings, and 23 of the last 24 national champions ranked in the top 21 of KenPom's adjusted offensive efficiency. See [Modeling Approaches](modeling-approaches.md) for a full treatment of rating systems.

## 9. Our Recommended Bracket Generation Strategy

Drawing on the full body of literature reviewed above and in companion chapters, we recommend a bracket generation pipeline with three stages:

### Stage 1: Build accurate probability estimates

Use a composite team rating (KenPom efficiency metrics as the backbone, supplemented by tempo, experience, and consistency features from [Modeling Approaches](modeling-approaches.md)) to estimate game-level win probabilities. Validate these against betting market closing lines -- if your model disagrees with the market by more than 2-3 points on a spread-equivalent basis, investigate why before trusting the model. The market is an extremely tough benchmark; edges are most likely in early-round games where the market has less information per matchup.

Run Monte Carlo simulation (10,000+ tournaments minimum; more if computationally feasible) to produce round-by-round advancement probabilities for all 68 teams. Use the logistic conversion `Win_Prob = 1 / (1 + e^(-0.163 * spread))` or a calibrated equivalent. Consider dynamic rating updates between rounds to capture information revelation during the tournament.

### Stage 2: Gather public pick data

Obtain public pick distributions from ESPN, CBS, Yahoo, or aggregator services. These represent the "field" you are competing against. Calculate leverage for each team at each stage: `leverage = advancement_probability - public_pick_rate`.

### Stage 3: Optimize for pool context

Apply the pool-size framework:

- **Small pool (fewer than 10):** Set temperature low. Pick the overall favorite as champion. Minimize upset picks; only deviate from chalk where your model strongly supports it (e.g., a 12-seed whose KenPom profile is better than its opponent's).
- **Mid-size pool (25-100):** Concentrate risk. Pick a positive-leverage champion (typically a strong 2-seed or 3-seed that the public is underweighting) and keep early rounds relatively conservative. Or pick the chalk champion and sprinkle in 2-3 early-round upsets where leverage is highest.
- **Large pool (100+):** Maximize leverage aggressively. Avoid the most popular No. 1 seed as champion. Target underowned contenders. Accept that your bracket will be wrong more often than a chalk bracket, but when it is right, fewer opponents will share those points.

Adjust for scoring system: in standard doubling (1-2-4-8-16-32), weight champion and Final Four selection heavily. In flat or linear scoring, prioritize first-round accuracy. In upset-bonus formats, increase the number of low-seed picks and shift attention toward identifying which specific mid-major or double-digit seeds have favorable matchup profiles.

The temperature parameter from the statistical mechanics framework provides a useful mental model for this calibration, even if you implement it as a set of heuristic adjustments rather than a literal energy-function optimization. The key idea is that pool size and scoring system together determine how much "heat" (randomness, contrarianism) to inject into your bracket.

For more on the specific modeling choices that feed into Stage 1, see [Modeling Approaches](modeling-approaches.md) and [Tournament Dynamics](tournament-dynamics.md). For how to evaluate whether your pipeline is well-calibrated, see [Evaluation & Calibration](evaluation-and-calibration.md). For the full recommended system architecture, see [Recommended Approach](recommended-approach.md).

## Sources

- PoolGenius / TeamRankings Strategy Guide Series (bracket strategy, upset picking, scoring systems, risk-value balance, analysis of 21,709 pools)
- FantasyLabs / PoolGenius NCAA Bracket Picks Optimizer
- Losak, J. -- Syracuse University Analytics Perspective on bracket strategy and behavioral biases
- NCAA Bracket Prediction Using ML and Combinatorial Fusion Analysis (arXiv 2603.10916v1)
- Cosner, C. -- University of Miami, "The Mathematics of Bracketology"
- Engaging Data -- March Madness Bracket Picker (seed-based Monte Carlo)
- Unabated -- "Building NCAA Basketball Power Rankings and a Bracket Simulator"
- March Madness Tournament Predictions Model (arXiv 2503.21790v1)
- Brixius, N. -- "Predicting the NCAA Tournament Using Monte Carlo Simulation"
- Lerner, M.G. -- "More March Madness Monte Carlo Style" (statistical mechanics approach)
- Barbalinardo, G. -- GPU-Accelerated March Madness Monte Carlo (GitHub)
- Lumivero / @RISK -- Monte Carlo simulation for tournament prediction
- NCAA.com -- Historical seed performance records (1985-2025)
- BracketOdds / UIUC (Jacobson) -- Seed advancement probabilities and matchup records
- NCAA.com -- Chalk bracket analysis
- Sports Illustrated, TheSportsGeek, Basketball.org -- Upset rates by seed and round
- ESPN -- "Giant Killers" upset prediction methodology
- Splash Sports -- Eight-factor upset prediction framework
- Templin, J. (University of Kansas) -- Consistency as a predictor of tournament success
- Sokol, J. (Georgia Tech) -- 75% accuracy ceiling for tournament prediction models
- Hickman, D.C. -- "Efficiency in the Madness?" (Journal of Economics and Finance, 2020)
- FiveThirtyEight -- NCAA Tournament forecast performance and market comparison
- "Weak Form Efficiency in Sports Betting Markets" -- Longshot bias in college basketball
- Front Office Sports -- Prediction markets and March Madness (Kalshi, Polymarket)
- KenPom ratings vs. Vegas lines (Betstamp, FOX Sports, Odds Shark)
- theScore -- Using betting odds for bracket construction
