# Evaluation, Calibration, and Backtesting

## Why Evaluation Is Hard

The NCAA tournament presents a uniquely difficult evaluation problem. Each year's bracket produces only 63 men's games (67 with play-in rounds), which means even a decade of historical tournaments yields fewer than 700 data points. This small sample size has three consequences that shape every evaluation decision we make.

First, **point estimates of model performance are unreliable**. A model's log loss on a single tournament is dominated by a handful of games --- one confident wrong prediction on a 12-over-5 upset can swing the score dramatically. Any performance number derived from a single tournament should be treated with deep skepticism.

Second, **year-to-year variance is enormous**. A "chalk" year where favorites win produces flattering scores for conservative models; an upset-heavy year punishes them. Winning Kaggle log loss scores have ranged from 0.41 to 0.55 across different years, and that variation is driven more by the tournament's randomness than by differences in model quality.

Third, **regular season performance does not translate directly to tournament performance**. The single-elimination format, neutral-site venues, and intensity differences mean that a model trained and validated purely on regular season data may not generalize. The best approaches use regular season statistics as features but evaluate against tournament outcomes specifically. A team with a 60% chance of winning each individual game has only about a 13% probability of winning six straight to take the championship --- the tournament format amplifies variance in ways that regular season results do not capture.

These constraints make it essential to evaluate across multiple historical tournaments, use probabilistic rather than binary metrics, and maintain realistic expectations about what any model can achieve.

## Scoring Metrics: Log Loss vs. Brier Score

Two metrics dominate probabilistic evaluation in this domain, and understanding their tradeoffs is important because the choice of metric changes which models look best and how aggressively you should predict.

### Log Loss

Log loss (negative log-likelihood, or cross-entropy loss) is calculated as the negative average of the log probabilities assigned to the correct outcomes. It ranges from 0 (perfect) to infinity, with a coin-flip baseline of approximately 0.693.

The defining characteristic of log loss is that it applies **unbounded penalties to confident wrong predictions**. Predicting 0.95 for a team that loses yields a penalty of roughly 3.0 for that single game --- enough to destroy an entire submission's score. This makes log loss extremely sensitive to overconfidence. As DRatings argues, this sensitivity is a feature in sports contexts because it forces models to honestly represent their uncertainty. A model that hedges appropriately (saying 0.70 instead of 0.95 when it is not sure) will be rewarded under log loss.

However, log loss assumes that the probabilities being scored are well-calibrated. If your model systematically over- or under-estimates probabilities, log loss scores become misleading about underlying model quality.

### Brier Score

The Brier score is the mean squared difference between predicted probability and actual outcome (1 or 0). It ranges from 0 (perfect) to 1, with a coin-flip baseline of 0.25.

Brier score caps the penalty for any single wrong prediction at 1.0, making it **more robust when calibration is imperfect**. It is also decomposable into three components that provide diagnostic value:

- **Reliability (calibration)**: How closely predicted probabilities match observed frequencies. Lower is better.
- **Resolution (discrimination)**: How much predictions differ from the base rate. Higher is better --- it measures whether the model can distinguish strong favorites from toss-ups.
- **Uncertainty**: The inherent unpredictability of the outcomes. This is a property of the data, not the model.

This decomposition makes Brier score particularly useful for diagnosing *where* a model fails: is it poorly calibrated, or does it lack the ability to discriminate between matchup types?

### When to Use Each

Kaggle's March Machine Learning Mania competition used log loss from 2014 through 2022, then switched to Brier score in 2023. The switch had strategic consequences: under Brier score, extreme wrong predictions are penalized less harshly, which encourages slightly more aggressive predictions. Strategies optimized for log loss do not necessarily optimize Brier score, and competitors who ignored this metric change performed worse.

| Metric | Range | Coin-Flip Baseline | Sensitivity to Overconfidence | Best When |
|--------|-------|--------------------|-------------------------------|-----------|
| Log Loss | 0 to infinity | ~0.693 | Very high (unbounded penalty) | Probabilities are well-calibrated |
| Brier Score | 0 to 1 | ~0.25 | Moderate (capped at 1.0) | Calibration may be imperfect; diagnostics needed |
| Accuracy | 0 to 1 | ~0.50 | None (ignores probabilities) | Quick sanity check only |

Neither metric alone tells you whether your model is well-calibrated. **Calibration plots are an essential complement** to any numeric scoring metric.

## Calibration vs. Discrimination

A 2024 paper in *Machine Learning with Applications* (Wheatcroft, arXiv:2303.06021) makes a compelling case that **calibration should take priority over accuracy** in sports prediction. The paper compares accuracy-driven and calibration-driven model selection and finds that accuracy-optimized models tend to be overconfident, producing predictions that are further from true probabilities. When applied to betting scenarios, accuracy-optimized models lost a higher percentage of bets than calibration-optimized models, even though they had higher classification accuracy.

This distinction matters. A model can be 75% accurate but poorly calibrated if it always predicts 90% confidence --- it gets the favorite right most of the time, but its stated probabilities are not trustworthy. In contrast, a well-calibrated model that says "70% chance" should win roughly 70% of the time at that stated confidence level.

### Measuring Calibration

- **Calibration plots (reliability diagrams)**: Bin predictions by predicted probability and plot observed win frequency against predicted probability. A well-calibrated model follows the diagonal.
- **Expected Calibration Error (ECE)**: The weighted average of absolute differences between predicted probability and observed frequency across bins. The deep learning literature reports ECE values around 3% for Brier-loss-trained models and 6% for BCE-trained models, indicating that loss function choice has a large effect on calibration (see [Modeling Approaches](modeling-approaches.md) for architecture details).
- **Brier score decomposition**: Separates calibration (reliability) from discrimination (resolution), enabling targeted diagnosis.

### Measuring Discrimination

Discrimination --- the model's ability to separate likely winners from likely losers --- is typically measured by AUC-ROC. A 2025 study comparing LSTM and Transformer architectures found that Transformers optimized with binary cross-entropy achieved the best discriminative power (AUC 0.8473), while LSTMs trained with Brier loss produced better-calibrated probabilities (ECE 3.2%). This suggests a genuine tension between calibration and discrimination that must be managed through loss function selection and post-hoc calibration techniques.

A practical implication: **the choice of training loss function matters as much as model architecture for calibration quality**. This is a finding that emerged clearly from 2024--2025 research and should inform any modeling pipeline (discussed further in [Modeling Approaches](modeling-approaches.md)).

## Cross-Validation Strategies for Temporal Sports Data

Standard k-fold cross-validation is inappropriate for sports prediction because it violates temporal ordering. Shuffling data across seasons allows future information to leak into training folds, producing inflated performance estimates that do not reflect real-world prediction accuracy. This is the single most common methodological error in the sports prediction literature.

### Expanding-Window Cross-Validation

The recommended approach is **expanding-window (walk-forward) cross-validation**: train on all data from seasons 1 through N, test on season N+1, then expand the training window to include season N+1 and test on season N+2, and so on.

The top 1% gold solution in the 2023 Kaggle competition used exactly this approach, training on historical data and using an expanding window across tournament years 2015--2019. Each fold used all data up to year N for training and year N+1 for testing.

An equivalent formulation is **leave-one-season-out cross-validation**, where each season serves as the test set once while all other preceding seasons form the training set. A 2025 Kaggle entry ranking 107th used this approach with 20 folds (2003--2024, excluding the cancelled 2020 tournament).

### Expanding Window vs. Sliding Window

The expanding window uses all available historical data up to the test point. The sliding window uses only a fixed lookback period (say, the last 5 seasons). Expanding windows are generally preferred when historical data is limited --- as it is with tournament games --- because discarding older data reduces an already small training set. However, sliding windows may be appropriate if you believe the game has changed enough that older data is misleading (rule changes, the transfer portal era, NIL impacts).

### Feature Selection Within CV

Feature selection must happen *inside* the cross-validation loop. Selecting features on the full dataset and then cross-validating produces optimistically biased estimates. The 2023 Kaggle gold solution applied recursive feature elimination within each CV fold, removing features iteratively if they degraded the expanding-window CV score.

## Backtesting on Historical Tournaments

Backtesting --- running your model on past tournaments as if predicting them in real time --- is the closest thing we have to a controlled experiment. FiveThirtyEight and its successor (Nate Silver's COOPER system) have continuously backtested tournament forecasts since 2011, refining source weightings and adjustments based on observed performance.

### How to Backtest Properly

1. **Strict temporal separation**: The model must use only data available before each historical tournament. This includes both features (team statistics) and any hyperparameters or model selection decisions.
2. **Pre-game indicators only**: Season averages, ratings, and other statistics computed before the game. Never include outcome-dependent features like final score margins from the game being predicted.
3. **Multiple tournament years**: Evaluating on a single historical tournament is almost meaningless given the 63-game sample size. Performance should be aggregated across at least 5--10 tournament years.
4. **Report confidence intervals**: With small samples, bootstrap resampling or multi-year aggregation is needed to distinguish signal from noise. A model that beats a baseline by 0.02 log loss over 5 tournaments may not have a statistically significant edge.

### A Subtle Trap: Seed-Based Overfitting

The 1-16, 2-15, 3-14 seed matchup structure makes early rounds highly predictable --- favorites win roughly 72--75% of tournament games. A model that merely learns seed differentials will appear strong in aggregate while adding no value for the competitive later-round matchups that actually determine bracket success. Backtesting should report performance broken out by round, not just overall, to catch this failure mode.

## Overfitting Risks and Common Pitfalls

Overfitting is the central risk in March Madness prediction. The literature identifies several recurring failure modes:

**Temporal leakage.** Using future season data in training, or mixing years in k-fold CV. This is the most common source of inflated performance metrics in sports prediction research.

**Overfitting to small tournament samples.** With fewer than 700 tournament games in a decade, models can memorize historical upsets that were genuinely random events. Regularization (L1/L2 penalties), conservative feature counts, and ensemble methods are standard countermeasures.

**Over-engineering features.** Building elaborate features from box score data without validating that they improve out-of-sample tournament prediction. Multiple Kaggle competitors report that adding more features degraded rather than improved performance.

**Complex models on noisy data.** Multiple Kaggle competitors report that ensembles of XGBoost + LightGBM + CatBoost + neural networks performed *worse* than a single tuned XGBoost model. The data is too noisy and the sample too small for complex architectures to generalize. This is discussed further in [Modeling Approaches](modeling-approaches.md).

**Overconfident predictions.** Under log loss, predicting 0.95 for a team that loses yields a penalty of roughly 3.0 for that single game. Even under Brier score, extreme wrong predictions are costly. Models should be calibrated to avoid unwarranted certainty.

**Predictions clustered around 0.5.** The opposite failure mode: models that refuse to commit, predicting every game at 0.48--0.52, score poorly because they cannot differentiate heavy favorites from coin flips. Good calibration means matching the true underlying probability --- sometimes that is 0.95, and sometimes it is 0.55.

**Confusing accuracy with calibration.** A model that always predicts the favorite at 90% confidence will have high accuracy (favorites usually win) but terrible calibration and will be punished by proper scoring rules.

**Training on tournament data directly.** With so few tournament games per year, building a model specifically on tournament outcomes rather than using regular season features to predict tournament games risks severe overfitting.

## Betting Lines as the Ultimate Benchmark

Every academic study of NCAA tournament betting markets reaches the same conclusion: **the market is broadly efficient, and the closing line is the single most accurate predictor of outcomes**. This makes betting lines the toughest and most honest benchmark for any prediction model.

### What the Research Shows

Hickman (2020) examined tournament betting data from 1996 to 2019 and found the market operates at an efficient level overall, with very little detectable bias based on seeding. A separate study of weak-form market efficiency across multiple sports found that NCAA basketball markets are generally efficient and no odds-based strategy yields statistically significant long-term profits.

FiveThirtyEight tested their model against Vegas by converting win probabilities into implied point spreads and placing hypothetical bets whenever their line diverged from the market. The results were instructive: a 26-31 overall record, but 17-13 in the Round of 64, and 5-2 when the model had a 3+ point edge in early rounds. In later rounds, the model went 6-15 --- the market gets more efficient as the tournament progresses and public attention concentrates on fewer games.

### Specific Biases Worth Knowing

Despite overall efficiency, some exploitable patterns have been identified:

- Big underdogs (20+ point spreads) cover more often than the efficient market would imply.
- ACC teams have historically underperformed against the spread in opening rounds, possibly due to "brand name" inflation.
- College basketball exhibits the strongest longshot bias of any major sport --- the market systematically overprices large underdogs on the moneyline.

These biases are discussed further in the context of data inputs in [Data Sources & Quality](data-sources-and-quality.md).

### Models and Markets Are Complementary

The most promising approach treats models and markets as complementary rather than competitive. Vegas lines incorporate real-time situational information (injuries, travel, motivation) that statistical models miss, while models can identify structural edges (efficiency mismatches, pace differentials) that the market may underweight. KenPom picks the correct winner 60.5% of the time in games with spreads of 7 points or fewer, but when spreads are 3 points or fewer, accuracy drops to 52.7% --- barely above a coin flip. Vegas has a slight edge in these close games because it incorporates information that season-long efficiency metrics cannot capture.

Nate Silver's COOPER system operationalizes this complementarity by blending its proprietary ratings (5/8 weight) with KenPom (3/8 weight), acknowledging that no single system captures all relevant information.

### Prediction Markets as an Emerging Signal

Prediction markets are rapidly becoming a significant new data source. Kalshi handled $2.27 billion in college basketball trading volume in February 2026 alone. Unlike traditional sportsbooks, prediction markets charge transparent transaction fees rather than baking margins (vigorish) into prices, which may produce less distorted implied probabilities. Their accuracy relative to traditional books has not been rigorously compared for tournament prediction, but the sheer volume of money at stake suggests these prices encode meaningful information. This is an emerging area with implications for both feature engineering and benchmarking --- see [Recommended Approach](recommended-approach.md) for how to incorporate market data.

## Kaggle Competition Insights

Kaggle's March Machine Learning Mania competition (running annually since 2014) provides the largest public laboratory for tournament prediction methods. Studying multiple years of solutions reveals consistent patterns in what separates winners from the field.

### What Distinguishes Top Entries

1. **Probability calibration over raw accuracy.** Winners ensure their predicted probabilities are well-calibrated. A model that says 0.70 should win 70% of the time at that confidence level. The `goto_conversion` calibration technique, which corrects the favorite-longshot bias in power ratings, has won gold and silver medals across multiple Kaggle years.

2. **Established rating systems as features.** KenPom, Sagarin, Moore, and similar expert systems encode decades of domain knowledge. Using them as inputs --- rather than reinventing them from raw box scores --- is a consistent trait of top entries. The 2023 gold solution selected the top 10 most historically accurate external rating systems and used them as features in an XGBoost model.

3. **Restraint in model complexity.** Logistic regression and single XGBoost models frequently outperform deep learning and multi-model ensembles for this problem. A 2025 entry found that an ensemble of XGBoost + LightGBM + CatBoost + MLP performed worse than a single tuned XGBoost model. The data is too noisy and the sample too small for complex models to reliably generalize.

4. **Feature differencing.** Computing the difference in statistics between two teams in a matchup, rather than feeding absolute team stats, is a universally adopted technique. It prevents models from memorizing team-specific biases and guarantees symmetry: swapping team order flips the prediction appropriately.

5. **Strategic submission management.** Some winners exploited the two-submission rule by hedging on the championship game --- each submission gave a different team 100% win probability, guaranteeing one submission would perfectly predict the final. This meta-game optimization reflects the reality that in a large competition, you are competing against other submissions, not just against the games.

6. **Expanding-window cross-validation.** Validated rigorously across multiple historical tournament years, never on a single tournament or with standard k-fold.

### What Does Not Work

- Predictions clustered around 0.5 (refusing to commit).
- Post-processing scaling of predictions (did not improve scores in the 2023 gold solution).
- Complex ensembles for this sample size.
- Ignoring the evaluation metric (strategies optimized for log loss do not necessarily optimize Brier score).
- Neglecting the women's tournament (since 2023, the competition combines men's and women's brackets, which require different calibration because the women's tournament has fewer upsets).

## Benchmark Score Values

These benchmarks help calibrate expectations. Scores vary by year depending on upset frequency, so ranges matter more than point estimates.

| Benchmark | Log Loss | Brier Score |
|-----------|----------|-------------|
| Coin flip (all 0.50) | ~0.693 | ~0.250 |
| Seed-based baseline | ~0.55--0.58 | ~0.22--0.24 |
| Typical Kaggle median | ~0.55--0.60 | ~0.22--0.28 |
| Strong model target | < 0.50 | < 0.20 |
| Kaggle winning entries | ~0.41--0.50 | ~0.18--0.22 |
| Published deep learning (Transformer, BCE) | --- | 0.164 |
| Published deep learning (LSTM, Brier loss) | --- | 0.159 |

The gap between the seed-based baseline (~0.56 log loss) and Kaggle winners (~0.43 log loss) represents the total improvement available through modeling. Much of this gap is captured by simply using established rating systems as features; further improvements come from calibration techniques, feature engineering, and appropriate model selection.

A useful accuracy reference: the persistent ceiling for individual matchup prediction appears to be around 74--77% across all methods, from logistic regression through Transformers. Seed differentials alone predict roughly 72--75% of games correctly, so the marginal improvement from sophisticated modeling is real but modest.

## Recommended Evaluation Pipeline

Drawing on the literature and competition evidence, the following pipeline represents current best practice:

1. **Expanding-window temporal CV.** Train on seasons 1 through N, test on season N+1. Repeat across at least 5--10 tournament years. This is non-negotiable --- any other CV strategy risks temporal leakage.

2. **Feature selection within CV.** Use recursive feature elimination or permutation importance inside the CV loop. Never select features on the full dataset before cross-validating.

3. **Primary metric: log loss or Brier score.** Choose based on your use case. Log loss if you need sharp differentiation between well-calibrated and poorly-calibrated models. Brier score if you want a bounded metric with diagnostic decomposition. Report both if possible.

4. **Calibration diagnostics.** Plot reliability diagrams and compute ECE alongside your primary scoring metric. Examine the Brier score decomposition to separate calibration failures from discrimination failures.

5. **Benchmark against baselines.** Always compare against: (a) seed-based predictions using historical seed matchup win rates, (b) closing Vegas lines converted to implied probabilities, and (c) established public rating systems (KenPom, Sagarin). If your model cannot beat these baselines, it is not adding value.

6. **Report by round.** Break out performance by tournament round. A model that looks strong overall but derives all its edge from early-round seed-based predictions is less valuable than one that performs well in competitive later-round matchups.

7. **Report confidence intervals.** With ~63 games per tournament, use bootstrap resampling or multi-year aggregation to assess whether performance differences are statistically meaningful.

8. **Cubic-spline or isotonic calibration.** Apply calibration corrections within each CV fold (not post-hoc on the full dataset). The `goto_conversion` technique for correcting favorite-longshot bias in Elo-based ratings has proven particularly effective in Kaggle competitions.

9. **Market comparison.** Convert your model's win probabilities to implied point spreads and compare against closing lines. This is the most honest test of whether your model contains information the market does not already reflect.

10. **Ensemble with restraint.** If ensembling, prefer combining structurally diverse models (e.g., logistic regression + gradient boosting + a rating-system-based model) over stacking similar architectures. Rank-based fusion (as in Combinatorial Fusion Analysis) may outperform naive probability averaging. But always verify that the ensemble outperforms the single best component --- in this domain, it often does not.

For implementation details on the modeling side of this pipeline, see [Modeling Approaches](modeling-approaches.md). For data source considerations and quality issues that affect evaluation, see [Data Sources & Quality](data-sources-and-quality.md). For how this evaluation pipeline fits into the overall project plan, see [Recommended Approach](recommended-approach.md).
