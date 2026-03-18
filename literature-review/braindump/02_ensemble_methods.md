# Ensemble Tree Methods for March Madness Bracket Prediction

## Summary

Ensemble tree methods -- Random Forests, Gradient Boosting, and XGBoost -- are among the most popular and effective approaches for predicting NCAA March Madness tournament outcomes. Across the sources reviewed, several consistent themes emerge:

1. **Gradient Boosting and XGBoost consistently outperform Random Forests**, which in turn outperform simpler methods like KNN and basic decision trees. Reported accuracies for game-level predictions range from 64% to 84%, depending on the feature set and evaluation methodology.

2. **Feature engineering matters more than hyperparameter tuning.** Multiple sources emphasize that the choice and construction of features (especially computing stat differentials between teams) drives performance gains far more than tweaking model parameters.

3. **The most predictive features** are efficiency-based metrics (offensive/defensive rating, effective field goal percentage), strength of schedule, turnover margin, and seed. Regular season wins and free throw rate also appear consistently.

4. **Difference vectors** (Team A stat minus Team B stat) are the standard input representation, rather than concatenating raw team stats.

5. **Log loss** is the standard evaluation metric for Kaggle's March Machine Learning Mania competition, with winning scores typically in the range of 0.41 to 0.43. Accuracy on its own can be misleading since the real challenge is calibrating probabilities, not just picking winners.

6. **Luck plays a large role.** Even well-calibrated models face inherent unpredictability -- a single upset can tank log-loss scores. The 2014 Kaggle winners (Matthews and Lopez) estimated that even an optimal model had at best a 50-50 chance of finishing in the top 10 due to randomness.

7. **Model ensembling across different algorithm families** (e.g., logistic regression + XGBoost + neural networks) tends to outperform any single model, especially when the component models exhibit cognitive diversity in their error patterns.

---

## Source 1: College Football Data Blog -- "Talking Tech: Building a March Madness Model using XGBoost"

- **URL**: https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/
- **Method**: XGBoost (gradient boosted trees)
- **Data**: 686 NCAA tournament games from 2013-2024, pulled from the CollegeBasketballData.com REST API via the CBBD Python library. Regular season stats only (no tournament data leakage).

### Features (25 total)
- Pace, offensive rating, defensive rating
- Four factors: free throw rate, offensive rebound percentage, turnover ratio, effective field goal percentage
- Opponent-adjusted versions of the above
- Tournament seed for each team

### Results
- **Overall accuracy**: 64.3% on 2024 tournament games
- **First-round accuracy**: 69.7%
- **Mean Absolute Error**: 7.97 points (noted that ~6.5 is strong)
- 80/20 train/validation split, with 2024 held out as test set

### Hyperparameters
- 100 estimators, 0.05 learning rate, 4 parallel jobs
- Tuning provided minimal improvement over defaults (MAE went from 7.97 to 7.98)

### Key Insights
- **Feature engineering > hyperparameter tuning**: The author found that adding better features would yield more improvement than optimizing model parameters.
- The API had many unused statistics that could improve the model.
- No opponent adjustment was applied to some metrics, which was identified as a weakness.
- The sequential nature of gradient boosting (each tree learns from predecessors' errors) was cited as the reason for preferring it over random forests.

---

## Source 2: Adeshpande3 -- "Applying Machine Learning to March Madness"

- **URL**: https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness
- **Method**: Multiple models compared; gradient boosted trees performed best
- **Data**: 115,000+ NCAA regular season games from 1993-2016, sourced from Kaggle and Sports-Reference.

### Features (16 per team, used as difference vectors)
- Basic stats: wins, points per game (scored/allowed), three-pointers, turnovers, assists, rebounds, steals
- Conference factors: Power 6 conference membership, regular season and tournament championships
- Advanced metrics: Simple Rating System (SRS), strength of schedule
- Historical: tournament appearances and national championships since 1985
- Location: home/away/neutral

### Results
- **Gradient Boosted Trees accuracy**: 76.37% (averaged over 100 train/test splits)
- Outperformed logistic regression, decision trees, KNN, and random forests

### Key Insights
- **Number of regular season wins** was the single most important feature.
- Strength of schedule and location were the next most important.
- **Difference vectors** (subtracting opponent stats) worked better than concatenating raw stats for each team.
- The author emphasized that dataset selection and feature engineering bias model outputs, and cautioned about responsible application.

---

## Source 3: Machine Learning Madness (Dang, Khosla, Kumar, Le, Petrillo)

- **URL**: https://mehakumar.github.io/machine-learning-madness/
- **Method**: Compared 6 models; Gradient Boosting and Random Forest were the top two
- **Data**: 25 basic team statistics from NCAA seasons, with stat differentials computed for each matchup.

### Features
- Wins, losses, rankings
- Shooting stats: field goals, three-pointers, free throws (made and attempted)
- Rebounds, assists, steals, blocks, turnovers
- Playoff seeding information
- All features represented as **difference between teams** in a matchup

### Results

| Method             | Log Loss | Accuracy |
|--------------------|----------|----------|
| Gradient Boosting  | 0.40913  | 84.126%  |
| Random Forest      | 0.41800  | 82.539%  |
| Neural Networks    | 0.61184  | 76.190%  |
| K-Nearest Neighbors| 0.58330  | 71.428%  |
| Linear Regression  | 0.63213  | --       |
| Ridge Regression   | 0.63210  | --       |

### Key Insights
- **Gradient Boosting was the best method** with 84% accuracy and 0.409 log loss.
- Random Forest was a close second (82.5%, 0.418 log loss).
- Both ensemble tree methods substantially outperformed neural networks, KNN, and regression approaches.
- The baseline of always picking the higher seed yielded 76% accuracy; both tree ensembles beat this decisively.
- Using stat differentials rather than raw stats was critical.

---

## Source 4: Paul Lindquist -- "Machine Learning vs. March Madness"

- **URL**: https://github.com/paul-lindquist/machine-learning-vs-march-madness
- **Method**: 6 classification models compared: Logistic Regression, KNN, Decision Tree, Random Forest, Bagging Classifier, XGBoost
- **Data**: 8 years of NCAA basketball from Kaggle's "March Machine Learning Mania 2021" competition. KenPom ratings for team strength.

### Features
- KenPom efficiency ratings and rankings
- Binary outcome for the favored team (1 = win, 0 = loss)
- Various team performance metrics

### Results
- **Top 3 models**: Logistic Regression, XGBoost, Random Forest
- **Best overall**: Logistic Regression at 82% accuracy with lowest standard deviation
- **Underdog prediction accuracy**: 71%
- All three top models consistently outperformed the baseline (always betting on favorites)

### Key Insights
- **Logistic regression slightly edged out XGBoost and Random Forest** in this study, primarily due to lower variance across cross-validation folds.
- Training on regular season data and testing on postseason tournaments was the right paradigm.
- KenPom ratings as the core feature set provided a strong signal.
- Even when XGBoost was not the top performer, it was competitive and in the top tier.

---

## Source 5: NCAA Bracket Prediction Using Machine Learning and Combinatorial Fusion Analysis (2025 arXiv paper)

- **URL**: https://arxiv.org/html/2603.10916v1
- **Method**: 5 base models (Logistic Regression, SVM, Random Forest, XGBoost, CNN) combined via Combinatorial Fusion Analysis (CFA) to create 52 ensemble configurations
- **Data**: NCAA tournament data from 2001-2022 (excluding 2020), from Kaggle's March Machine Learning Mania and KenPom.

### Features
- Started with 44 features, reduced to **26 optimal features** via Recursive Feature Elimination with Cross-Validation (RFECV)
- Four categories: offensive efficiency, defensive efficiency, strength of schedule, luck/unpredictable factors

### Results
- **Best ensemble (Logistic Regression + SVM + CNN via rank combination)**: 74.60% accuracy
- This outperformed the best public ranking system (73.02%)
- Score combination variant: 71.43%
- Models optimized using log loss function via randomized parameter search

### Key Insights
- **Cognitive diversity matters for ensembles**: Combining models that make errors in different regions of the input space produced better results than combining similar models.
- Interestingly, the best ensemble did NOT include XGBoost or Random Forest -- it combined LR, SVM, and CNN, suggesting that diversity of model type matters more than individual model strength.
- Rank combination (converting predictions to ordinal rankings before merging) outperformed score combination (averaging probabilities).
- The ensemble showed a 1.58% improvement over the best individual base model.

---

## Source 6: Matthews and Lopez -- 2014 Kaggle Competition Winners

- **URL**: https://statsbylopez.com/2014/12/04/building-an-ncaa-mens-basketball-prediction-model/
- **Paper**: https://arxiv.org/abs/1412.0248
- **Method**: Two-model ensemble combining logistic regressions (not tree-based, but relevant as a competition-winning ensemble benchmark)
- **Data**: Sports book point spreads + Ken Pomeroy efficiency metrics

### Approach
- **Model 1 (Point Spread Model)**: Used actual Vegas spreads for Round 1, estimated spreads for later rounds
- **Model 2 (Efficiency Model)**: Team efficiency metrics from KenPom
- Merged the two probabilistic frameworks to produce final predictions

### Results
- Won the 2014 Kaggle March Machine Learning Mania competition
- Their odds of winning increased 10x to 50x relative to random chance
- Even under optimal probability scenarios, they estimated at best a 50-50 chance of finishing top 10

### Key Insights
- **Luck is a dominant factor**: The 2014 tournament had a 7-seed champion (UConn), producing higher log-loss for all models. Rare outcomes punish even well-calibrated models.
- This is relevant context for tree-based approaches: no matter how good your XGBoost model is, a single Cinderella run can destroy your log-loss score.
- Combining market-derived probabilities (Vegas lines) with statistical models provided an edge, suggesting that **incorporating betting market data as a feature** could benefit tree-based models too.
- The sfirke tutorial repository (https://github.com/sfirke/predicting-march-madness) implements a similar approach and achieved top 10% in 2016, top 25% in 2017.

---

## Cross-Cutting Observations

### What Works
- **Stat differentials** as inputs (Team A minus Team B) rather than raw or concatenated stats
- **Efficiency metrics** (KenPom, four factors) as core features
- **Gradient Boosting/XGBoost** for capturing nonlinear feature interactions
- **Ensemble diversity**: Combining fundamentally different model types
- **Regular season training, tournament testing** to avoid leakage
- **Vegas lines or KenPom rankings** as strong baseline features to include

### What Does Not Work Well
- Hyperparameter tuning alone (diminishing returns)
- Homogeneous ensembles (combining similar models)
- Ignoring the role of luck and variance in tournament outcomes
- Using accuracy as the sole metric (log loss is more informative for probability calibration)
- Raw stat concatenation instead of difference vectors

### Typical Performance Ranges
- **Game-level accuracy**: 64-84% depending on features and evaluation setup
- **Log loss**: 0.40-0.63 (Kaggle competition winners ~0.41-0.43)
- **Beating the seed baseline** (~76% by always picking higher seed) is the real bar to clear

### Recommended Feature Categories
1. Offensive/defensive efficiency ratings (KenPom or equivalent)
2. Four factors (eFG%, turnover rate, offensive rebound rate, FT rate)
3. Strength of schedule
4. Tournament seed
5. Win-loss record and momentum indicators
6. Vegas lines or market-derived probabilities (if available)
