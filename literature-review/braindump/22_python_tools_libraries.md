# Python Tools, Libraries, and Frameworks for March Madness Prediction

## Summary

The Python ecosystem for March Madness prediction is mature and well-documented across dozens of open-source projects and blog posts. The most common stack centers on **pandas** for data wrangling, **scikit-learn** for classical ML models (logistic regression, random forests), and **XGBoost** for gradient-boosted trees, which consistently emerge as top performers. Deep learning approaches using **TensorFlow/Keras** and **PyTorch** exist but tend to be overkill for the dataset sizes involved (hundreds to low-thousands of tournament games). **PyMC** offers a compelling Bayesian alternative that provides full uncertainty quantification and natural handling of hierarchical team strength. For data acquisition, **Kaggle** datasets remain the gold standard starting point, supplemented by scraping tools like **sportsipy** (Sports Reference) and **CBBpy** (ESPN). The **CollegeBasketballData.com API** (via the `cbbd` Python package) is a newer, cleaner option.

Key patterns across projects:
- Feature engineering matters more than model choice; offensive/defensive efficiency, four factors, and strength of schedule are consistently the most important features.
- Representing matchups as the *difference* between two team feature vectors is the dominant approach.
- Data leakage is a real risk: you must use only regular-season stats available *before* the tournament.
- Realistic train/test splits (e.g., training on past years, testing on a held-out tournament year) are essential.
- Accuracy in the 64-76% range for individual game prediction is typical; the best projects report ~76% with gradient boosted trees.

---

## Source 1: March-Madness-ML (Adit Deshpande)

- **URL**: https://github.com/adeshpande3/March-Madness-ML
- **Blog post**: https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness
- **Code**: Fully open-source on GitHub

### Tools/Libraries
- numpy, pandas, scikit-learn (core)
- TensorFlow/Keras (neural networks, optional)
- XGBoost (gradient boosting, optional)
- pipenv for environment management

### Data Pipeline
1. CSV files from Kaggle (game results since 1985, tournament seeds, conference info)
2. Basketball Reference for advanced team statistics
3. `DataPreprocessing.py` creates training matrices (xTrain/yTrain)
4. `MarchMadness.py` trains models and generates predictions
5. 16-dimensional team vectors including: wins, PPG, 3-pointers, turnovers, assists, rebounds, steals, SRS, SOS, Power 6 conference flag, conference/tournament championships, historical tournament appearances

### Key Approach
- Binary classification: matchup represented as **Team 1 vector minus Team 2 vector**
- Multiple models tested; **Gradient Boosted Trees achieved 76.37% accuracy** across 100 train/test splits
- Top features by importance: regular season wins, strength of schedule, home-court/location

### Lessons
- Designed for extensibility across years (update data, re-run)
- Training set bias is a real concern; be deliberate about what data you include
- Future directions mentioned: PCA/SVD for dimensionality reduction, incorporating expert opinions, time-series models for momentum

---

## Source 2: Talking Tech - March Madness with XGBoost (CollegeFootballData Blog)

- **URL**: https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/
- **Code**: Tutorial-style with inline code

### Tools/Libraries
- `cbbd` (CollegeBasketballData.com Python API client)
- pandas
- scikit-learn (train_test_split, metrics)
- XGBoost (`XGBRegressor`)

### Data Pipeline
1. Pull 686 NCAA tournament games (2013-2024) via CBBD API
2. Pull team season statistics (regular season only, to prevent data leakage)
3. 25 features per team: offensive/defensive ratings, pace, "four factors" (free throw rate, offensive rebound %, turnover ratio, effective FG%)
4. Hold out 2024 tournament for testing; earlier years split 80/20

### Key Approach
- XGBRegressor predicting point margin rather than binary win/loss
- Gradient boosting chosen over random forests because sequential tree learning from predecessors' errors tends to outperform

### Results
- Validation MAE: ~7.97 points
- 2024 tournament accuracy: 64.3% straight-up picks
- First-round accuracy: 69.7%

### Lessons
- The CBBD API returns many more features than used; significant room for feature expansion
- Opponent-adjusted statistics are a promising enhancement
- Using a regression target (point margin) rather than classification gives richer output
- Preventing data leakage by filtering to regular-season-only stats is critical

---

## Source 3: Bayesian March Madness Prediction with PyMC3 (Barnes Analytics)

- **URL**: https://barnesanalytics.com/predicting-march-madness-winners-with-bayesian-statistics-in-pymc3/
- **Code**: Inline code in blog post

### Tools/Libraries
- PyMC3 (now PyMC v5+)
- pandas, NumPy
- Theano (now PyTensor) for symbolic math
- Matplotlib for visualization

### Data Pipeline
1. Kaggle March Madness competition data
2. Filter to single season (2017, 5,395 games)
3. Transform winner/loser format into home/away team structure
4. Re-index team identifiers for computational efficiency

### Model Architecture (Hierarchical Bayesian)
- **Global parameters**: home court advantage, offensive/defensive standard deviations (HalfStudentT priors), intercept
- **Team-specific parameters**: offensive and defensive strength (hierarchical Normal priors)
- **Game-level likelihood**: scoring intensity = `exp(intercept + home_advantage + offense[home] - defense[away])`; points modeled as Poisson-distributed
- Posterior sampling: 1,000 iterations with 1,000 tuning steps

### Key Approach
- Hierarchical structure allows teams to share information (partial pooling)
- Can simulate counterfactual matchups across home, away, and neutral venues
- Produces full probability distributions, not just point estimates
- Inspired by Baio & Blangiardo's football/soccer model

### Results
- Example: Team 3 vs Team 172 yields 48.4% home win, 18.9% away win, 32.1% neutral court probability

### Lessons
- Bayesian approach naturally provides uncertainty quantification (crucial for bracket optimization)
- Substantial data preprocessing required before modeling
- Hierarchical structure provides regularization (avoids overfitting to small-sample teams)
- Foundation can be extended with advanced statistics beyond final scores
- PyMC (unlike Stan) supports discrete variables and non-gradient-based samplers

---

## Source 4: March Madness 2025 Prediction (Jonathan Marcu)

- **URL**: https://jtmarcu.github.io/projects/march-madness.html
- **Code**: Project write-up with methodology details

### Tools/Libraries
- Python, scikit-learn, pandas, NumPy, Seaborn

### Data Pipeline
1. 117,000+ games spanning 2010-2024 (men's and women's)
2. 4 distinct datasets with 34 game metrics
3. SQL-like operations to aggregate team statistics by season
4. Perspective flipping for data symmetry (each game appears from both teams' viewpoint)
5. Stratified sampling to manage class imbalance

### Feature Engineering
- 12 advanced statistics created including offensive/defensive efficiency, shooting percentages, rebound differentials
- Possessions formula: `FGA - OReb + TO + 0.44*FTA`

### Key Approach
- Random Forest classifier with hyperparameter tuning via `RandomizedSearchCV`
- Feature importance: offensive efficiency difference (23%), win percentage differential (19%), scoring margin gap (15%)

### Results
- AUC: 0.753, accuracy: 67%
- Brier Score: 0.199 (good calibration)
- 64% accuracy on close games (margin <= 5 points)
- Women's tournament predictions slightly outperformed men's

### Lessons
- Offensive efficiency is consistently the strongest single predictor
- Temporal weighting (weighting recent games more heavily) is a promising enhancement
- Gradient boosted trees and ensemble methods likely to improve on random forest baseline

---

## Source 5: Machine Learning vs. March Madness (Paul Lindquist)

- **URL**: https://github.com/paul-lindquist/machine-learning-vs-march-madness
- **Code**: Fully open-source on GitHub (Jupyter notebooks)

### Tools/Libraries
- Python, Jupyter Notebook
- scikit-learn (multiple classifiers)
- XGBoost
- pandas (implied by data pipeline)

### Data Pipeline
1. Kaggle March Machine Learning Mania 2021 competition data
2. Raw CSVs in `Kaggle_Datasets` folder
3. Cleaned/processed data exported to `data` directory
4. 8 years of historical NCAA basketball data
5. KenPom ratings used for team rankings

### Models Tested (6 total)
1. Logistic Regression
2. K-Nearest Neighbors
3. Decision Tree
4. Random Forest
5. Bagging Classifier
6. XGBoost

### Key Approach
- Binary target: favored team wins (1) vs. underdog wins (0)
- Focus on underdog prediction as the high-value use case
- Season-long data as training, postseason as test

### Results
- Overall: 82% mean accuracy for single-game predictions
- Underdog predictions: 71% mean accuracy
- **Logistic regression** yielded most consistent accuracy with lowest standard deviation (not always the fanciest model that wins)
- Consistently outperformed the baseline of always picking the favorite

### Lessons
- Using season data for training and postseason for testing generates consistently high accuracy
- Simpler models (logistic regression) can match or beat complex ones for this problem
- KenPom ratings are a high-signal feature source
- Framing as "will the favorite win?" and focusing on underdog detection is a practical angle

---

## Data Acquisition Tools

### Kaggle Datasets
- **March Machine Learning Mania** (annual competition): https://www.kaggle.com/competitions/march-machine-learning-mania-2025/data
- Provides game results since 1985, tournament seeds, conference info, team stats
- Updated annually with the most recent season's data
- The de facto standard starting point for most projects

### sportsipy (formerly sportsreference)
- **PyPI**: https://pypi.org/project/sportsipy/
- **Docs**: https://sportsreference.readthedocs.io/en/stable/
- Free Python API wrapping Sports-Reference.com
- NCAAB modules: Boxscore, Schedule, Rankings, Teams, Conferences
- Example: `Schedule('purdue')` iterates through games with dates, scores, stats
- Covers major North American sports leagues

### CBBpy
- **PyPI**: https://pypi.org/project/CBBpy/
- Scrapes ESPN for NCAA Division 1 basketball data
- Play-by-play records, boxscores, game metadata, player info
- Supports men's and women's basketball
- Uses ESPN game IDs as primary identifier
- Inspired by the R package `ncaahoopR`

### cbbd (CollegeBasketballData.com API)
- REST API client for college basketball data
- Clean interface for team stats, game results, advanced metrics
- Used in the XGBoost tutorial above
- Handles regular season vs. postseason filtering (important for avoiding data leakage)

### basketball-reference-scraper
- **PyPI**: https://pypi.org/project/basketball-reference-scraper/
- Direct scraping of Basketball Reference
- Alternative to sportsipy with potentially different coverage

---

## Recurring Themes and Practical Recommendations

### Model Selection
| Model | Typical Accuracy | Notes |
|-------|-----------------|-------|
| Logistic Regression | 70-82% | Surprisingly competitive, low variance |
| Random Forest | 67-75% | Good baseline, interpretable feature importance |
| XGBoost / Gradient Boosted Trees | 64-76% | Often best performer, requires tuning |
| Neural Networks (TF/PyTorch) | Similar range | Overkill for typical dataset sizes; useful for embeddings |
| Bayesian (PyMC) | N/A (probabilistic) | Best for uncertainty quantification and bracket optimization |

### Feature Engineering Priorities
1. **Offensive/defensive efficiency** (points per 100 possessions) -- consistently the top predictor
2. **Four factors**: eFG%, turnover rate, offensive rebound %, free throw rate
3. **Strength of schedule / SRS** (Simple Rating System)
4. **KenPom ratings** (pre-computed advanced metrics)
5. **Win percentage and scoring margin**
6. **Seed** (strong baseline; seed alone predicts ~70% of games)

### Data Pipeline Best Practices
- Use only regular-season data available before the tournament (avoid leakage)
- Represent matchups as feature differences between teams
- Flip perspectives (each game generates two training examples) for data augmentation
- Hold out entire tournament years for testing, not random game splits
- Update data annually; Kaggle datasets grow each year

### What the Bayesian Approach Adds
- Full posterior distributions over team strengths (not just point estimates)
- Natural uncertainty quantification for each prediction
- Hierarchical structure provides regularization for small-sample teams
- Can simulate thousands of brackets and optimize for expected score under a scoring system
- More principled than calibrating classifier probabilities after the fact

---

## Sources

- [March-Madness-ML (Adit Deshpande) - GitHub](https://github.com/adeshpande3/March-Madness-ML)
- [Applying Machine Learning to March Madness (Adit Deshpande) - Blog](https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness)
- [Talking Tech: March Madness with XGBoost - CollegeFootballData Blog](https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/)
- [Predicting March Madness Winners with Bayesian Statistics in PyMC3 - Barnes Analytics](https://barnesanalytics.com/predicting-march-madness-winners-with-bayesian-statistics-in-pymc3/)
- [March Madness 2025 Prediction - Jonathan Marcu](https://jtmarcu.github.io/projects/march-madness.html)
- [Machine Learning vs. March Madness (Paul Lindquist) - GitHub](https://github.com/paul-lindquist/machine-learning-vs-march-madness)
- [March Machine Learning Mania 2025 - Kaggle](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/data)
- [sportsipy Documentation](https://sportsreference.readthedocs.io/en/stable/)
- [CBBpy - PyPI](https://pypi.org/project/CBBpy/)
- [March Madness Predictions using PyMC3 - Medium (Ceshine Lee)](https://medium.com/the-artificial-impostor/march-madness-predictions-using-pymc3-e64574497f47)
- [NCAA Bracket Prediction Using ML and Combinatorial Fusion Analysis - arXiv](https://arxiv.org/html/2603.10916v1)
- [ncaa-predict: TensorFlow NCAA bracket model (Brendan Long) - GitHub](https://github.com/brendanlong/ncaa-predict)
- [march-madness-ml: Neural network NCAA bracket (Adithya GV) - GitHub](https://github.com/adithya-gv/march-madness-ml)
