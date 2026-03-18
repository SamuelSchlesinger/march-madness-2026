# Model Evaluation, Calibration, Backtesting, and Validation for March Madness Predictions

## Summary

Evaluating March Madness prediction models requires careful attention to probabilistic scoring metrics, temporal validation strategies, and the unique challenges posed by single-elimination tournament data. The key takeaways from the literature are:

1. **Log loss and Brier score are the two dominant evaluation metrics**, each with distinct tradeoffs. Log loss is more sensitive to probability differences and punishes confident wrong predictions severely. Brier score is more robust when calibration is imperfect. Kaggle's March Machine Learning Mania competition switched from log loss to Brier score in 2023, reflecting an ongoing debate about which metric better captures predictive quality.

2. **Calibration matters more than raw accuracy** for probabilistic predictions. A model that says "70% chance" should win roughly 70% of the time at that confidence level. Research in sports betting shows that calibration-optimized models outperform accuracy-optimized models, because accuracy-driven models tend to be overconfident on incorrect predictions.

3. **Temporal validation is essential**. Standard k-fold cross-validation violates the temporal structure of sports data. The recommended approach is expanding-window or walk-forward cross-validation, where the model is trained on all data up to year N and tested on year N+1, then the window expands. Top Kaggle solutions use expanding-window CV across multiple tournament years (e.g., 2015-2019).

4. **Overfitting is the central risk** when working with small tournament samples. The NCAA tournament provides only 63 men's games per year (67 with play-in games). Even a decade of historical tournaments gives fewer than 700 games. Regularization, feature selection via cross-validation, and ensemble methods are standard countermeasures.

5. **Regular season performance does not directly translate to tournament performance.** The single-elimination format, neutral-site games, and intensity differences mean that models trained and evaluated purely on regular season data may not generalize. The best approaches use regular season statistics as features but evaluate against tournament outcomes.

6. **Ensembling multiple rating systems** (e.g., KenPom, Sagarin, BPI) is consistently effective, as combining diverse models reduces the variance inherent in any single system. FiveThirtyEight's model is built on a composite of six power ratings selected for their historical tournament track records.

---

## Source 1: DRatings -- Log Loss vs. Brier Score

- **URL**: https://www.dratings.com/log-loss-vs-brier-score/
- **Type**: Technical comparison article focused on sports prediction

### Evaluation Metrics Discussed

- **Log Loss**: Ranges from 0 to infinity. A perfect model scores 0; a coin-flip model scores ~0.693. Calculated as the negative average of log probabilities assigned to the correct outcomes. More sensitive to differences in predicted probabilities, making it better at distinguishing between well-calibrated and poorly-calibrated models.
- **Brier Score**: Ranges from 0 to 1. A perfect model scores 0; a coin-flip model scores ~0.25. Calculated as the mean squared difference between predicted probability and actual outcome. More robust when calibration is imperfect.

### Key Insight: Log Loss is Preferred for Sports

DRatings argues that in sports contexts, log loss "greatly outperforms" the Brier Score. The reasoning: Brier Score caps the penalty for any single incorrect prediction at 1.0, whereas log loss applies an unbounded penalty to confident wrong predictions. This means log loss better differentiates between models that are overconfident versus appropriately uncertain.

### Pitfalls

- Log loss assumes well-calibrated probabilities. If your model systematically over- or under-estimates probabilities, log loss scores become misleading.
- Brier score is less sensitive to probability differences, so it may not distinguish between a model predicting 60% and one predicting 55% for the same event.
- Neither metric alone tells you whether your model is well-calibrated; a calibration plot is needed as a complement.

---

## Source 2: Kaggle March Machine Learning Mania (2023 Competition and Top Solutions)

- **URL (Competition)**: https://www.kaggle.com/c/march-machine-learning-mania-2023
- **URL (Top 1% Solution Writeup by maze508)**: https://medium.com/@maze508/top-1-gold-kaggle-march-machine-learning-mania-2023-solution-writeup-2c0273a62a78
- **Type**: Competition platform and practitioner writeup

### Evaluation Metric

- The competition used **Brier Score** starting in 2023 (previously log loss). The formula: `BrierScore = (1/N) * sum((predicted_prob - actual_outcome)^2)`.
- The switch from log loss to Brier score was noted to encourage slightly more aggressive predictions, since Brier score penalizes confident wrong predictions less harshly than log loss does.

### Validation Methodology (from Gold Solution)

- **Expanding Window Cross-Validation**: The top solution trained on historical data and used an expanding window CV across tournament years 2015-2019. Each fold used all data up to year N for training and year N+1 for testing.
- **Recursive Feature Elimination**: Features were removed iteratively if they dropped the expanding-window CV score. This prevented overfitting to noise in the small tournament dataset.
- **External Ratings as Features**: Rather than building ratings from scratch, the solution leveraged the top 10 most historically accurate external rating systems (KenPom, Sagarin, Moore, etc.), filtered by data availability.

### Common Pitfalls

- Using standard k-fold cross-validation that mixes data from different years, allowing future information to leak into training.
- Over-engineering features from box score data without validating that they improve out-of-sample tournament prediction.
- Ignoring the metric change: strategies optimized for log loss do not necessarily optimize Brier score.

### Best Practices

- Use established rating systems as inputs rather than trying to reinvent them.
- Validate across multiple historical tournament years, not just one.
- Keep the model simple (XGBoost with curated features outperformed complex architectures).

---

## Source 3: "Machine Learning for Sports Betting: Should Model Selection Be Based on Accuracy or Calibration?"

- **URL**: https://www.sciencedirect.com/science/article/pii/S266682702400015X
- **Also at**: https://arxiv.org/abs/2303.06021
- **Type**: Peer-reviewed research paper (Machine Learning with Applications, 2024)

### Core Argument

Model calibration should take priority over accuracy in sports prediction tasks. The paper compares accuracy-driven and calibration-driven model selection on sports betting data and demonstrates:

- **Accuracy-driven models tend to be overconfident**, producing predictions that are further from ground-truth probabilities. This is a known issue with classification models: in regions of sparse data or high uncertainty, models default to more extreme, overconfident predictions.
- **Calibration-driven models** produce probability estimates that better match observed frequencies, leading to more reliable decision-making.

### Evaluation Metrics Recommended

- **Calibration plots** (reliability diagrams): Bin predictions by predicted probability and plot observed frequency against predicted probability. A well-calibrated model follows the diagonal.
- **Brier Score decomposition**: The Brier score can be decomposed into reliability (calibration), resolution (how much predictions differ from the base rate), and uncertainty (inherent unpredictability). This decomposition is more informative than the raw score alone.
- **Expected Calibration Error (ECE)**: The weighted average of the absolute difference between predicted probability and observed frequency across bins.

### Validation Methodology

- Temporal train/test splits to respect chronological ordering.
- Comparison of multiple model families (logistic regression, random forests, gradient boosting, neural networks) under both accuracy-optimized and calibration-optimized selection criteria.

### Key Finding

When applied to betting scenarios, accuracy-optimized models lost a higher percentage of bets than calibration-optimized models, even though they had higher classification accuracy. This is because accuracy rewards getting the most likely outcome right but says nothing about whether the stated probability is trustworthy.

---

## Source 4: FiveThirtyEight -- How Our March Madness Predictions Work

- **URL**: https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
- **Also**: https://fivethirtyeight.com/features/march-madness-predictions-2015-methodology/
- **Type**: Methodology documentation

### Model Architecture

- Built on a **composite of six computer power ratings**, each selected for its historical track record in tournament prediction. This ensemble approach reduces variance from any single rating system's biases.
- Uses direct probability calculation rather than Monte Carlo simulation, leveraging the single-elimination bracket structure to compute exact advancement probabilities.
- Incorporates **injury adjustments** based on Sports-Reference.com's win shares.

### Validation Approach

- **Historical backtesting**: FiveThirtyEight evaluates their model's performance against past tournaments to refine source weightings and adjustments.
- **Live updating**: Since 2016, forecasts update during the tournament as games are played, treating completed games as known outcomes and recalculating probabilities for remaining matchups.
- **Iterative refinement**: Weightings, sources, and adjustments are changed year over year based on observed performance.

### Best Practices

- Combine multiple independent rating systems rather than relying on a single model.
- Account for non-statistical factors (injuries, player availability) that standard models miss.
- Transparency about methodology enables external scrutiny and improvement.

### Pitfalls Acknowledged

- No model can fully capture March Madness unpredictability; even well-calibrated models will frequently be "wrong" on individual games because upsets are genuinely probable events (a 30% upset chance means 3-in-10 times the underdog wins).

---

## Source 5: "Forecasting NCAA Basketball Outcomes with Deep Learning: A Comparative Study of LSTM and Transformer Models"

- **URL**: https://arxiv.org/html/2508.02725v1
- **Type**: Academic paper (arXiv preprint)

### Validation Methodology

- **Strict temporal separation**: Training and validation datasets are partitioned based on temporal boundaries, ensuring models only learn from historical data preceding the tournament season being predicted. This prevents data leakage.
- **Stratified cross-validation**: 10-fold CV with stratification on the prediction target (Win/Loss) to maintain class balance across folds, though the authors note this must be combined with temporal ordering.
- **Feature exclusion**: Outcome-dependent features (like point differentials from the game being predicted) are excluded from the feature set to prevent information leakage.

### Evaluation Metrics

- Classification accuracy, log loss, and AUC-ROC are all reported.
- The paper emphasizes that accuracy alone is insufficient; probabilistic calibration is needed to make predictions actionable.

### Common Pitfalls

- **Data leakage from temporal mixing**: Including future data in training folds is the most common source of inflated performance metrics in sports prediction.
- **Outcome-dependent features**: Using statistics that implicitly encode the result (e.g., final score margins) in the prediction model.
- **Overfit to historical bracket structure**: The 1-16, 2-15, etc., seed matchup structure in early rounds is so predictable that a model can appear strong simply by learning seed differentials, while adding no value for the closer matchups that matter most.

### Best Practices

- Pre-game indicators only (season averages, ratings, etc.) as features.
- Temporal train/test boundaries that mirror real-world prediction scenarios.
- Ensemble methods that combine multiple model architectures.

---

## Source 6: "A Systematic Review of Machine Learning in Sports Betting" (Survey Paper)

- **URL**: https://arxiv.org/html/2410.21484v1
- **Type**: Systematic literature review (arXiv, 2024)

### Cross-Validation in Sports Contexts

- **K-fold cross-validation** (5-fold and 10-fold) is widely employed across the sports prediction literature, but the review notes a critical caveat: standard k-fold violates temporal ordering.
- **Walk-forward (rolling origin) validation** is the recommended alternative: the training set consists only of observations that occurred before the test set. The "origin" rolls forward in time.
- **Expanding window vs. sliding window**: Expanding window uses all historical data up to the test point; sliding window uses only a fixed lookback period. Expanding window is generally preferred when historical data is limited (as with tournament games).

### Evaluation Metrics Survey

The review catalogs metrics used across the sports betting ML literature:
- **Log loss / cross-entropy**: Most common for probabilistic evaluation.
- **Brier score**: Second most common; preferred when calibration is the primary concern.
- **ROI / betting profit**: Domain-specific metric that directly measures economic value but is noisy and dependent on the betting market.
- **Accuracy**: Widely reported but insufficient on its own for probabilistic predictions.
- **Calibration plots**: Recommended as a visual diagnostic but underutilized in practice.

### Pitfalls Identified Across the Literature

- Many studies report only accuracy, ignoring calibration entirely.
- Small sample sizes in tournament prediction lead to high variance in performance estimates.
- Publication bias: studies reporting successful predictions are more likely to be published, skewing the field's apparent success rate.
- Market efficiency: well-calibrated models may still not beat betting markets because the market itself is a strong predictor.

---

## Source 7: The Power Rank -- The Ultimate Guide to Predictive College Basketball Analytics

- **URL**: https://thepowerrank.com/cbb-analytics/
- **Type**: Practitioner guide

### Ensemble Methods as a Validation Strategy

- The key to accurate predictions is combining many different power ratings to estimate team strength. Each individual rating system has weaknesses, but the combination provides a more robust predictor.
- This is itself a form of validation: if multiple independent systems agree on a team's strength, confidence in that estimate increases.

### Regular Season vs. Tournament Evaluation

- Regular season data is used to build team ratings, but the evaluation that matters is tournament prediction accuracy.
- The single-elimination tournament format amplifies variance: a team that is 60% likely to win each game has only a ~13% chance of winning six straight games to take the championship.
- Models should be evaluated on their probability calibration across all tournament games, not on whether they "picked the winner."

---

## Cross-Cutting Themes and Recommendations

### Choosing an Evaluation Metric

| Metric | Range | Sensitivity | Best When |
|--------|-------|-------------|-----------|
| Log Loss | 0 to infinity | High (punishes confident errors harshly) | Probabilities are well-calibrated |
| Brier Score | 0 to 1 | Moderate (bounded penalty) | Calibration may be imperfect |
| Accuracy | 0 to 1 | Low (binary, ignores probabilities) | Quick sanity check only |
| Calibration Plot | Visual | N/A | Always (complement to any numeric metric) |

### Recommended Validation Pipeline

1. **Expanding-window temporal CV**: Train on seasons 1 through N, test on season N+1. Repeat for multiple years.
2. **Feature selection within CV**: Use recursive feature elimination or similar inside the CV loop to avoid selection bias.
3. **Calibration diagnostics**: Plot reliability diagrams and compute ECE alongside your primary scoring metric.
4. **Brier score decomposition**: Separate calibration (reliability) from discrimination (resolution) to diagnose where the model fails.
5. **Benchmark against simple baselines**: Seed-based predictions, historical upset rates, and Vegas lines provide baselines that are surprisingly hard to beat.
6. **Report confidence intervals**: With only ~63 tournament games per year, point estimates of model performance are highly uncertain. Use bootstrap resampling or report performance across multiple years.

### Common Pitfalls to Avoid

- **Temporal leakage**: Using future season data in training, or mixing years in k-fold CV.
- **Overfitting to seeds**: Seed differential alone predicts ~75% of tournament games correctly. A model that merely learns seeds will appear strong but adds no value.
- **Confusing accuracy with calibration**: A model can be 75% accurate but poorly calibrated if it always predicts 90% confidence.
- **Evaluating on a single tournament**: One tournament is 63 games, and results are heavily influenced by randomness. Always evaluate across multiple historical tournaments.
- **Ignoring the base rate**: In a typical tournament, favorites (lower seeds) win roughly 72-75% of games. Any model must meaningfully improve on this base rate to be valuable.
- **Training on tournament data directly**: With so few tournament games, training a model specifically on tournament outcomes (rather than using regular season features to predict tournament games) risks severe overfitting.

### Benchmark Log Loss / Brier Score Values

- **Kaggle competition winning entries**: Log loss between 0.41 and 0.43.
- **Coin flip baseline**: Log loss of 0.693; Brier score of 0.25.
- **Seed-based baseline**: Approximate log loss of ~0.55-0.58 (assigning probabilities based on historical seed matchup win rates).
- **Strong model target**: Log loss below 0.50; Brier score below 0.20.
