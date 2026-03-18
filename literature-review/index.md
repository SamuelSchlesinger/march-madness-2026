# March Madness Prediction: Literature Review

## Introduction

Predicting the NCAA Men's Basketball Tournament -- March Madness -- sits at the intersection of sports analytics, machine learning, game theory, and behavioral economics. The tournament's single-elimination format, 68-team field, and compressed schedule create a prediction problem that is both tractable enough to model and random enough to resist mastery. Across 40 years of the modern tournament (1985-2025), regularities have emerged -- 1-seeds win 99% of first-round games, 12-seeds upset 5-seeds roughly a third of the time, and adjusted efficiency margin is the single strongest predictor of championship potential -- but roughly 25% of tournament games remain genuinely unpredictable from pre-game information. This literature review synthesizes findings from 25 research areas to map the current state of the art and identify opportunities for our own model.

The landscape of March Madness prediction is dominated by a small number of powerful ideas. Tempo-free efficiency metrics, pioneered by Dean Oliver and operationalized by Ken Pomeroy, form the foundation of virtually every serious model. Ensemble methods -- combining multiple independent rating systems rather than relying on any one -- consistently outperform single models, as demonstrated by FiveThirtyEight's composite approach and Kaggle competition results. Bayesian frameworks provide principled uncertainty quantification, which matters because calibrated probabilities (not binary picks) are what separate good models from great ones. And bracket optimization, which translates predictions into pool-winning strategies, is a fundamentally different problem from prediction itself, requiring game-theoretic reasoning about public pick distributions and scoring system incentives.

Perhaps the most important finding across all the literature is the persistence of a ~74-75% accuracy ceiling on individual game predictions. This ceiling holds whether you use logistic regression, gradient-boosted trees, LSTMs, Transformers, or Bayesian hierarchical models. The implication is that marginal improvements in prediction accuracy are hard-won and easily overwhelmed by tournament randomness. The most promising avenues for improvement lie not in chasing higher accuracy on individual games, but in better probability calibration, smarter feature engineering (particularly around roster continuity, travel distance, and player-level analytics), and strategic bracket construction that exploits inefficiencies in public pick distributions.

---

## Key Findings Across All Research Areas

### 1. Adjusted Efficiency Margin Is the Dominant Predictor

Every successful model reviewed uses some form of adjusted offensive and defensive efficiency (points per 100 possessions, corrected for opponent strength and game location). KenPom's AdjOE and AdjDE appear as top predictors even in models not built by Pomeroy. All 24 national champions from 2001-2024 ranked in the top 25 of KenPom's adjusted efficiency margin. Dean Oliver's Four Factors (effective FG%, turnover rate, offensive rebound rate, free throw rate) explain 99.8% of the variance in offensive efficiency, with eFG% alone accounting for ~47% of the sensitivity.

### 2. The ~74-75% Accuracy Ceiling Is Real

Multiple independent approaches converge on roughly the same game-level accuracy: LRMC at 74%, logistic regression on efficiency metrics at 74.6%, Sagarin at 75%, seed-based probit at 73.5%, and even the best deep learning models (Transformer AUC 0.85) do not break through. This suggests that roughly one-quarter of tournament games are dominated by factors no pre-game model can capture -- hot shooting, referee variance, injury timing, and genuine randomness.

### 3. Ensembles Outperform Individual Models

FiveThirtyEight's blend of six computer rating systems plus human rankings, the Massey composite of 100+ systems, and Kaggle competition results all demonstrate that combining diverse models reduces variance and improves robustness. The most effective ensembles combine structurally different model types (e.g., logistic regression + SVM + CNN) to maximize "cognitive diversity," as demonstrated by Combinatorial Fusion Analysis research achieving 74.60% accuracy.

### 4. Calibration Matters More Than Accuracy

For bracket pools scored by log loss or Brier score, and for any probabilistic application, the quality of probability estimates matters more than binary accuracy. Research shows accuracy-optimized models tend to be overconfident and perform worse in betting and bracket contexts than calibration-optimized models. The choice of loss function (Brier vs. binary cross-entropy) affects calibration more than the choice of model architecture.

### 5. Simple Models Are Surprisingly Competitive

Logistic regression with 4 features (ADJOE, ADJDE, BARTHAG, 2P% allowed) achieves 74.6% accuracy -- matching the best deep learning architectures. Single XGBoost models frequently outperform complex ensembles of XGBoost + LightGBM + CatBoost + neural networks. The "chalk bracket" (always picking the higher seed) scores ~30% better than the average bracket and matches or beats most expert picks. Model complexity yields diminishing returns on this problem.

### 6. Feature Engineering Dominates Model Choice

Across all studies, the representation of features matters more than the algorithm. Computing stat *differences* between opposing teams (rather than concatenating raw stats), using per-possession rates (rather than per-game totals), adjusting for opponent quality, and selecting features via cross-validation are consistently more impactful than switching from one model family to another.

### 7. Betting Markets Set the Bar

Vegas closing lines are the toughest benchmark for any prediction model. Academic research finds NCAA tournament betting markets are broadly efficient. Models may find edges in early rounds (FiveThirtyEight went 17-13 in the Round of 64, 5-2 with 3+ point edges), but later rounds are harder. The most promising approach combines statistical models with market data rather than treating them as competitors.

### 8. Tournament Dynamics Are Distinct from Regular Season

Fewer upsets occur in the tournament than Elo differences predict. The Sweet 16 has the highest upset rate (~21%) of any round. Travel distance significantly affects outcomes (150+ miles reduces winning odds by ~33.6%). Slow-tempo teams do not reliably benefit from controlling pace (contradicting a popular hypothesis). And bracket structure creates path dependencies -- 11-seeds have reached the Final Four 6 times, more than seeds 9, 10, 12-16 combined, partly due to favorable bracket positioning.

### 9. The Transfer Portal Has Changed the Game

With over 53% of rotation players in the 2025 tournament having previously played at another D-I school, traditional team-level continuity metrics are losing relevance. Player-level projection models (like EvanMiya's BPR) that can project individual transfers into new environments represent the frontier, though predicting transfer fit remains a significant challenge.

### 10. Bracket Optimization Is a Separate Problem

Winning a bracket pool requires differentiation from opponents, not just accuracy. Pool size is the primary strategic variable: small pools favor chalk, large pools demand contrarian picks. The "leverage" concept -- the gap between a team's actual advancement probability and their public pick rate -- is the key to pool-winning strategy. Bracket optimizer tools report 2-4x improvement over random expectation.

---

## Table of Contents

This review is organized into eight synthesis documents, each covering a major theme:

- [Modeling Approaches](modeling-approaches.md) -- statistical, ML, and Bayesian methods for predicting game outcomes, from logistic regression and gradient boosting to LSTMs, Transformers, and hierarchical Bayesian models

- [Data Sources & Quality](data-sources-and-quality.md) -- where to get data (Kaggle, KenPom, Bart Torvik, ESPN, play-by-play packages), quality issues, preprocessing pipelines, COVID-era handling, and data source reconciliation

- [Feature Engineering & Metrics](features-and-metrics.md) -- which statistics matter (adjusted efficiency, Four Factors, Elo), rating systems (KenPom, T-Rank, BPI, NET, COOPER, EvanMiya, ShotQuality), feature selection techniques, and the tier list of predictive features

- [Tournament Dynamics](tournament-dynamics.md) -- upset patterns by seed and round, bracket structure effects, tempo and pace analysis, conference strength and selection bias, historical seed performance, coaching and intangible factors, travel distance effects, and the transfer portal era

- [Evaluation & Calibration](evaluation-and-calibration.md) -- log loss vs. Brier score, calibration diagnostics, temporal validation strategies, overfitting risks, and benchmark performance values

- [Bracket Strategy & Optimization](bracket-strategy.md) -- translating predictions into pool-winning brackets, Monte Carlo simulation, pool size strategy, scoring system analysis, leverage and contrarian picking, and available optimizer tools

- [Tools & Implementation](tools-and-implementation.md) -- Python libraries (scikit-learn, XGBoost, PyMC, pandas), R packages (hoopR, toRvik, cbbdata), data acquisition tools (Kaggle, CBBD API, CBBpy, sportsipy), and practical implementation patterns

- [Recommended Approach](recommended-approach.md) -- our proposed methodology synthesizing the best ideas from across the literature review

---

## Master Bibliography

All unique sources found across the 25 research areas, organized by category.

### Academic Papers and Preprints

| Title | URL | Description |
|-------|-----|-------------|
| March Madness Tournament Predictions Model: A Mathematical Modeling Approach (2025) | https://arxiv.org/html/2503.21790v1 | Logistic regression on 4 efficiency features achieving 74.6% accuracy |
| NCAA Bracket Prediction Using ML and Combinatorial Fusion Analysis (Wu et al., 2026) | https://arxiv.org/html/2603.10916v1 | CFA ensemble of LR + SVM + CNN achieving 74.60% accuracy via rank fusion |
| Forecasting NCAA Basketball Outcomes with Deep Learning (Habib, 2025) | https://arxiv.org/html/2508.02725v1 | LSTM vs. Transformer comparison; best AUC 0.8473, best Brier 0.1589 |
| Advancing NCAA March Madness Forecasts Through Deep Learning and CFA (Alfatemi et al., 2024) | https://link.springer.com/chapter/10.1007/978-3-031-66431-1_38 | Four neural network architectures combined via CFA (Springer/IntelliSys) |
| A Logistic Regression/Markov Chain Model for NCAA Basketball (Sokol & Kvam, Georgia Tech) | https://www2.isye.gatech.edu/~jsokol/ncaa.pdf | LRMC model using only box-score data, ~75% accuracy |
| Are Sports Seedings Good Predictors? (Boulier & Stekler, 1999) | https://ideas.repec.org/a/eee/intfor/v15y1999i1p83-91.html | Probit regression on seed differences, 73.5% accuracy |
| Predicting the Outcomes of NCAA Basketball Championship Games (Stekler & Klein, 2011) | https://www2.gwu.edu/~forcpgm/2011-003.pdf | Extended probit model showing degradation to chance in Elite Eight |
| Modeling the NCAA Tournament Through Bayesian Logistic Regression (Nelson, 2012) | https://dsc.duq.edu/etd/970 | Master's thesis: Bayesian model selection via MCMC for tournament prediction |
| Building an NCAA Men's Basketball Prediction Model (Matthews & Lopez, 2014) | https://arxiv.org/abs/1412.0248 | 2014 Kaggle winner; two-model ensemble combining Vegas spreads and KenPom |
| A State-Space Model to Evaluate Sports Teams (Lopez) | https://statsbylopez.netlify.app/post/a-state-space-model-to-evaluate-sports-teams/ | Time-varying Bayesian team strength using betting market data |
| Dean Oliver's Four Factors Revisited (Poropudas, 2023) | https://ar5iv.labs.arxiv.org/html/2305.13032 | Revised sensitivity analysis: eFG% 47%, ORB% 26%, TOV% 21%, FTr 7% |
| Efficiency in the Madness? (Hickman, 2020) | https://ideas.repec.org/a/spr/jecfin/v44y2020i3d10.1007_s12197-020-09507-7.html | NCAA tournament betting market efficiency; ACC covers less than expected |
| Weak Form Efficiency in Sports Betting Markets | https://myweb.ecu.edu/robbinst/PDFs/Weak%20Form%20Efficiency%20in%20Sports%20Betting%20Markets.pdf | Big underdogs cover more than expected; strongest longshot bias in college basketball |
| Machine Learning for Sports Betting: Accuracy or Calibration? (2024) | https://www.sciencedirect.com/science/article/pii/S266682702400015X | Calibration-driven model selection outperforms accuracy-driven in betting contexts |
| A Systematic Review of Machine Learning in Sports Betting (2024) | https://arxiv.org/html/2410.21484v1 | Survey of evaluation methods; recommends walk-forward validation |
| Predicting NBA Talent from College Basketball Tracking Data (Stats Perform, Sloan 2020) | https://www.sloansportsconference.com/research-papers/predicting-nba-talent-from-enormous-amounts-of-college-basketball-tracking-data | Tracking data log-loss 0.30 vs. PBP 0.40; 650K+ possessions |
| Geospatial Determinants of Game Outcomes in NCAA Men's Basketball (Clay et al., 2014) | https://www.researchgate.net/publication/272507595 | 150+ mile travel reduces winning odds by 33.6%; time zone effects documented |
| Seed Distributions for the NCAA Men's Basketball Tournament (Jacobson, Omega 2011) | https://bracketodds.cs.illinois.edu/seedadv.html | Truncated geometric distribution fits for seed advancement probabilities |
| Major Conference Bias and the NCAA Tournament (Coleman, Lynch, DuMond) | https://ideas.repec.org/a/ebl/ecbull/eb-07l80004.html | SEC teams seeded ~2 lines higher than model predictions; documented bias |
| Deep Learning in Sports Prediction (Lee, 2022, Trinity) | https://digitalcommons.trinity.edu/cgi/viewcontent.cgi?article=1065&context=compsci_honors | Undergraduate honors thesis on deep learning for sports prediction |

### Rating Systems and Analytics Platforms

| Source | URL | Description |
|--------|-----|-------------|
| KenPom Ratings | https://kenpom.com | Gold standard adjusted efficiency ratings; $24.95/year |
| KenPom Ratings Explanation | https://kenpom.com/blog/ratings-explanation/ | Methodology documentation for KenPom's efficiency system |
| KenPom Methodology Update | https://kenpom.com/blog/ratings-methodology-update/ | Switch from multiplicative to additive opponent adjustment |
| KenPom National Efficiency | https://kenpom.com/blog/national-efficiency/ | Cross-era tempo-free normalization details |
| Bart Torvik T-Rank | https://barttorvik.com/trank.php | Free adjusted efficiency ratings with recency weighting |
| Sagarin Ratings (historical) | http://sagarin.com/sports/cbsend.htm | Elo + BLUE composite ratings, 1985-2023 (discontinued) |
| ESPN BPI Explained | https://www.espn.com/blog/statsinfo/post/_/id/125994/bpi-and-strength-of-record-what-are-they-and-how-are-they-derived | Basketball Power Index methodology |
| ESPN BPI Introduction | https://www.espn.com/mens-college-basketball/story/_/id/7561413/bpi-college-basketball-power-index-explained | Original BPI methodology description |
| NCAA NET Rankings Explained | https://www.ncaa.com/news/basketball-men/article/2022-12-05/college-basketballs-net-rankings-explained | Official NCAA evaluation tool replacing RPI |
| How NET Rankings Work (NCAA.org) | https://www.ncaa.org/news/2025/3/3/media-center-how-do-net-rankings-work-in-ncaa-tournament-selection.aspx | NET methodology for tournament selection |
| Massey Ratings | https://masseyratings.com/cb/ncaa-d1/ratings | Least-squares ratings + composite of 100+ systems |
| Haslametrics | https://haslametrics.com/about.php | Play-by-play efficiency with garbage-time filtering |
| TeamRankings Multi-Model | https://www.teamrankings.com/blog/ncaa-basketball/under-the-teamrankings-hood-part-4-models-models-everywhere | Six-model ensemble approach |
| EvanMiya BPR | https://blog.evanmiya.com/p/bayesian-performance-rating | Player-level Bayesian Performance Rating system |
| EvanMiya Transfer Analysis | https://blog.evanmiya.com/p/which-schools-get-the-most-out-of | Transfer portal development rankings by program |
| ShotQuality | https://shotqualitybets.com/stats-explained | Shot-level expected value via computer vision |
| LRMC About Page (Georgia Tech) | https://www2.isye.gatech.edu/~jsokol/lrmc/about/ | LRMC model background and methodology |
| DRatings Bracketology | https://www.dratings.com/predictor/bracketology/ | Bracket projections using ratings, RPI, SOS |

### FiveThirtyEight / Nate Silver

| Source | URL | Description |
|--------|-----|-------------|
| How Our March Madness Predictions Work | https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/ | Full methodology for the FiveThirtyEight composite model |
| How FiveThirtyEight's Forecasts Did | https://fivethirtyeight.com/features/how-fivethirtyeights-ncaa-tournament-forecasts-did/ | Self-assessment: ~70% accuracy, 26-31 vs. Vegas, Brier score analysis |
| 2016 NCAA Tournament Methodology | https://fivethirtyeight.com/features/how-fivethirtyeight-is-forecasting-the-2016-ncaa-tournament/ | Year-specific methodology details |
| 2015 March Madness Methodology | https://fivethirtyeight.com/features/march-madness-predictions-2015-methodology/ | Earlier version of the methodology |
| Historical NCAA Forecast Data (GitHub) | https://github.com/fivethirtyeight/data/blob/master/historical-ncaa-forecasts/historical-538-ncaa-tournament-model-results.csv | Published historical forecast data |
| Introducing COOPER (Silver Bulletin) | https://www.natesilver.net/p/introducing-cooper-silver-bulletins | COOPER Elo system: separate off/def ratings, pace-adjusted variance |
| 2025 March Madness Predictions (Silver Bulletin) | https://www.natesilver.net/p/2025-march-madness-ncaa-tournament-predictions | 50% SBCB + 50% composite; 250K+ historical games |
| 2026 March Madness Predictions (Silver Bulletin) | https://www.natesilver.net/p/2026-march-madness-ncaa-tournament-predictions | 5/8 COOPER + 3/8 KenPom; 100K simulations |

### Kaggle Competition Solutions and Practitioner Guides

| Source | URL | Description |
|--------|-----|-------------|
| Kaggle March Machine Learning Mania (2026) | https://www.kaggle.com/competitions/march-machine-learning-mania-2026 | Annual prediction competition with ~35 CSV datasets |
| 2017 Kaggle 1st Place: Andrew Landgraf | https://medium.com/kaggle-blog/march-machine-learning-mania-1st-place-winners-interview-andrew-landgraf-f18214efc659 | Meta-game optimization; strategic submission management |
| 2015 Kaggle 1st Place: Zach Bradshaw | https://medium.com/kaggle-blog/predicting-march-madness-1st-place-winner-zach-bradshaw-89741aea9fda | Bayesian framework; luck as dominant factor |
| Top 1% Gold Solution 2023: maze508 | https://medium.com/@maze508/top-1-gold-kaggle-march-machine-learning-mania-2023-solution-writeup-2c0273a62a78 | XGBoost with RFE feature selection; expanding window CV |
| Rank 107 Approach 2025 (LinkedIn) | https://www.linkedin.com/pulse/march-machine-learning-mania-2025-rank-107-approach-g13jf | Single XGBoost with leave-one-season-out CV; 2 hours of work |
| Bradley-Terry Model for March Madness | https://youhoo0521.github.io/kaggle-march-madness-men-2019/models/bradley_terry.html | Kaggle notebook: Bradley-Terry in Stan |
| Predicting March Madness (sfirke) | https://github.com/sfirke/predicting-march-madness | R pipeline; top 10% in 2016, top 25% in 2017 |

### Blog Posts and Tutorials

| Source | URL | Description |
|--------|-----|-------------|
| Applying ML to March Madness (Deshpande) | https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness | Gradient boosted trees at 76.37% accuracy; 16-feature vector |
| March-Madness-ML GitHub (Deshpande) | https://github.com/adeshpande3/March-Madness-ML | Open-source implementation of the above |
| Machine Learning Madness (Kumar et al.) | https://mehakumar.github.io/machine-learning-madness/ | 6-model comparison; gradient boosting best at 84.1%/0.409 log loss |
| Machine Learning vs. March Madness (Lindquist) | https://github.com/paul-lindquist/machine-learning-vs-march-madness | 6 classifiers compared; logistic regression most consistent at 82% |
| March Madness ML (Adithya GV) | https://github.com/adithya-gv/march-madness-ml | Neural network evolution: 880 to 345K parameters; 98th percentile ESPN |
| March Madness XGBoost Tutorial (CBBD) | https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/ | XGBoost with CBBD API; 25 features, 64.3% accuracy |
| LRMC Applied to College Football (CFBD) | https://blog.collegefootballdata.com/talking-tech-applying-lrmc-rankings-to-college-football-part-one/ | Technical explainer of LRMC methodology |
| Bayesian March Madness in PyMC3 (Barnes Analytics) | https://barnesanalytics.com/predicting-march-madness-winners-with-bayesian-statistics-in-pymc3/ | Hierarchical Poisson model; offense/defense decomposition |
| Rating College Basketball with PyMC3 (Hollander) | https://sethah.github.io/ncaa-ratings.html | Hierarchical Normal model with sum-to-zero constraints |
| March Madness 2025 Prediction (Marcu) | https://jtmarcu.github.io/projects/march-madness.html | Random Forest; AUC 0.753, Brier 0.199 |
| NCAA Bracket Prediction (Brixius) | https://nathanbrixius.com/2014/03/19/predicting-the-ncaa-tournament-using-monte-carlo-simulation/ | 10K Monte Carlo simulations in Excel |
| Monte Carlo Bracket (Biophysics and Beer) | https://mglerner.github.io/posts/more-march-madness-monte-carlo-style.html | Statistical mechanics approach with temperature parameter |
| Conor Dewey Machine Learning Madness | https://www.conordewey.com/blog/machine-learning-madness-predicting-every-ncaa-tournament-matchup | Composite rating + Elo; logistic regression at 0.540 log loss |
| Nick C. March Machine Learning Madness (2016) | https://nickc1.github.io/machine/learning/2016/03/19/March-Machine-Learning-Madness.html | Logistic regression; 0.562 log loss |
| Solving March Madness with Regression (Yard Couch) | https://yardcouch.com/solving-march-madness-with-regression-analysis/ | Multiple regression; seed (log2) is overwhelmingly dominant |
| ncaahoopR Win Probability Model (Luke Benz) | https://lukebenz.com/post/ncaahoopr_win_prob/ | Logistic regression with time-varying coefficients on PBP data |
| Predicting College Basketball Methodology (Odds Gods) | https://blog.oddsgods.net/predicting-college-basketball-methodology | LightGBM on 6 rating systems; 77.61% tournament accuracy |
| FiveThirtyEight Model Challenge (Holman) | https://www.justinholman.com/2014/03/20/march-madness-fivethirtyeight-model-challenge/ | Replicated FiveThirtyEight with 2 variables at R^2 = 0.94 |
| Predictive Analytics in College Basketball (Data Action Lab) | https://www.data-action-lab.com/2021/11/21/predictive-analytics-in-college-basketball/ | Binomial possession-based framework |
| NBAstuffer LRMC Overview | https://www.nbastuffer.com/analytics101/logistic-regression-markov-chain-lrmc/ | Accessible explanation of the LRMC methodology |
| Elo Ratings Analysis (nicidob) | https://nicidob.github.io/nba_elo/ | Technical analysis of Elo ratings and logistic regression |
| GPU-Accelerated March Madness Bracket (Barbalinardo) | https://github.com/gbarbalinardo/march-madness-bracket | CUDA-accelerated Monte Carlo bracket simulation |
| PyMC3 March Madness (Ceshine Lee) | https://medium.com/the-artificial-impostor/march-madness-predictions-using-pymc3-e64574497f47 | Alternative Bayesian approach in PyMC3 |
| ncaa-predict TensorFlow (Brendan Long) | https://github.com/brendanlong/ncaa-predict | TensorFlow-based NCAA bracket model |
| March Madness Data Card (Halcazar) | https://github.com/alexhalcazar/March_Madness_2025/blob/main/data_card.md | Dataset documentation and preprocessing guide |
| Analytics8 ML Guide | https://www.analytics8.com/blog/how-to-use-machine-learning-to-predict-ncaa-march-madness/ | Practical ML guide for March Madness |

### Upset Analysis and Tournament History

| Source | URL | Description |
|--------|-----|-------------|
| Where Do Upsets Happen? (SI) | https://www.si.com/college-basketball/march-madness-brackets-where-do-upsets-happen-in-mens-ncaa-tournament | Comprehensive upset rates by seed, 1985-2025 |
| NCAA First-Round Upsets (Basketball.org) | https://www.basketball.org/stats/ncaa-first-round-upsets/ | Year-by-year upset data for all seed matchups |
| March Madness Upsets by Round (TheSportsGeek) | https://www.thesportsgeek.com/blog/march-madness-upsets-by-round-study/ | Round-by-round upset rates; Sweet 16 highest at 21% |
| Giant Killers: Most Probable First-Round Upsets (ESPN, 2026) | https://www.espn.com/mens-college-basketball/story/_/id/48223542/ncaa-tournament-upsets-first-round-giant-killers-march-madness-2026 | ESPN's matchup-specific upset indicators |
| Ultimate Guide to Predicting March Madness (Splash Sports) | https://splashsports.com/blog/the-ultimate-guide-to-predicting-march-madness | Eight key upset prediction factors |
| Upset-Proof Your Picks (Splash Sports) | https://splashsports.com/blog/upset-proof-your-picks-strategies-to-capitalize-on-march-madness-upsets | Five critical statistical indicators for bracket-busters |
| Professor Templin's Statistical Model (KU) | https://news.ku.edu/news/article/2017/03/08/professor-develops-statistical-model-predict-ncaa-tournament-winners-based-scoring | Consistency as the critical predictor of tournament success |
| Records for Every Seed 1985-2025 (NCAA.com) | https://www.ncaa.com/news/basketball-men/article/2025-04-16/records-every-seed-march-madness-1985-2025 | Official comprehensive seed records |
| BracketOdds Seed Advancement (UIUC) | https://bracketodds.cs.illinois.edu/seedadv.html | Truncated geometric distribution fits by seed |
| BracketOdds Seed Records (UIUC) | https://bracketodds.cs.illinois.edu/seed_records.html | Seed-vs-seed matchup records |
| The Chalk Bracket (NCAA.com) | https://www.ncaa.com/news/basketball-men/bracketiq/2021-02-12/heres-how-your-march-madness-bracket-will-do-if-you-only-pick-better-seeded | Chalk scores 20.4 pts above average bracket |
| Best NCAA Bracket Strategy (Flerlage Twins) | https://www.flerlagetwins.com/2017/02/whats-best-ncaa-bracket-strategy_99.html | Top-seed method matched or beat all 12 CBS analysts |
| History of 1 vs. 16 Seed (NCAA.com) | https://www.ncaa.com/news/basketball-men/article/2026-02-10/history-1-seed-vs-16-seed-march-madness | 158-2 all-time; UMBC (2018) and FDU (2023) |
| UMBC vs. Virginia (NCAA.com) | https://www.ncaa.com/news/basketball-men/article/2020-04-07/umbc-vs-virginia-how-one-greatest-upsets-ncaa-tournament | Detailed account of the first 16-over-1 upset |
| Lowest Seeds to Win in March Madness (SI) | https://www.si.com/college-basketball/lowest-seeds-to-ever-win-in-march-madness-which-cinderellas-will-emerge-in-2026 | Cinderella run history by seed |
| March Madness Cinderella Runs (ESPN) | https://www.espn.com/mens-college-basketball/story/_/id/39742636/march-madness-cinderella-ncaa-bracket-busters-george-mason-fgcu-vcu-st-peters-davidson | Detailed profiles of famous deep runs |
| Building the Brackets (NCAA.org) | https://www.ncaa.org/news/2025/3/12/media-center-building-the-brackets-a-deep-dive-on-the-ncaa-tournament-selection-and-seeding-process.aspx | Official bracket construction rules |

### Conference Strength and Selection

| Source | URL | Description |
|--------|-----|-------------|
| How Conferences Affect Rating Systems (Wieland) | https://bbwieland.github.io/2024-04-01-cbb-rating-systems/ | Simulation: conference structure inflates rating error by 54% |
| Understanding Basketball Ranking Methods (MWC Connection) | https://www.mwcconnection.com/bracketology/78909/stats-corner-understanding-basketball-ranking-methods | RPI vs. NET vs. KenPom vs. BPI comparison |
| Conference Impact on March Madness (Brackets Ninja) | https://www.bracketsninja.com/blog/march-madness-conference-performance-history | Mid-major overperformance; Missouri Valley +12% |
| Circular Logic of NCAA Selection (Rabbit Hole Sports) | https://rabbitholesports.substack.com/p/the-circular-logic-of-the-ncaa-tournament | Power conference teams inflate each other's metrics |
| Mid-Major Scheduling (Athletic Director U) | https://athleticdirectoru.com/articles/mid-major-scheduling-where-can-teams-go-for-quality-games/ | Quad 1 opportunities: 47.9% for high-majors vs. 6.4% for mid-majors |

### Tempo, Pace, and Style Analysis

| Source | URL | Description |
|--------|-----|-------------|
| Ultimate Guide to Predictive CBB Analytics (The Power Rank) | https://thepowerrank.com/cbb-analytics/ | Four Factors, matchup analysis, ensemble methods |
| Does Slow Tempo Aid Upsets? (Harvard) | https://harvardsportsanalysis.wordpress.com/2010/02/11/putting-theories-to-the-test-does-slow-tempo-aid-ncaa-tournament-upsets/ | Contradicts Oliver: faster tempo associated with more upsets |
| Pace, Favorites, and Tournaments (Gasaway) | https://johngasaway.com/2018/03/21/pace-favorites-and-tournaments/ | +0.09 correlation between pace and tournament success (negligible) |
| KenPom Trends for March Madness (FOX Sports) | https://www.foxsports.com/stories/college-basketball/kenpom-trends-march-madness-bracket | Champions average 134th in tempo; 6 of 24 ranked 200+ |
| Tempo-Free Stats Explainer (Streaking the Lawn) | https://www.streakingthelawn.com/basketball/2013/10/30/4843384/tempo-free-ncaa-basketball-stats-thinking-outside-the-box-score | Accessible introduction to per-possession metrics |
| Tempo/Pace and Efficiency Explained (Maddux Sports) | https://www.madduxsports.com/library/cbb-handicapping/tempopace-and-offensivedefensive-efficiency-explained.html | Practical guide to tempo and efficiency analysis |

### Betting Markets and Prediction Markets

| Source | URL | Description |
|--------|-----|-------------|
| KenPom March Madness Betting Guide (Betstamp) | https://betstamp.com/education/kenpom-march-madness-betting-guide | KenPom vs. Vegas: 60.5% correct in 7-pt spread games |
| Prediction Markets and March Madness (Front Office Sports) | https://frontofficesports.com/prediction-markets-leverage-march-madness-despite-ncaa-opposition/ | Kalshi: $2.27B in CBB trading volume, Feb 2026 |
| How Betting Odds Help Build Brackets (theScore) | https://www.thescore.com/ncaab/news/3501354/amp | Market odds as "most accurate resource" |
| Prediction Market Prices for Seeds (SI) | https://www.si.com/betting/prediction-market/college/predicting-which-seed-will-win-march-madness-based-on-kalshi-markets | Kalshi seed-level probability estimates |
| Sports Markets Brief March 2026 (MLQ) | https://mlq.ai/prediction/brief/sports/sports-markets-brief-march-16-2026-march-madness-fuels-prediction-volume-surge-2026-03-16/ | Prediction market volume analysis |

### Bracket Optimization and Strategy

| Source | URL | Description |
|--------|-----|-------------|
| PoolGenius Bracket Strategy Guide | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/bracket-strategy-guide/ | Comprehensive pool-winning strategy |
| Best Bracket Picks from 21,709 Pools (PoolGenius) | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/what-makes-best-ncaa-bracket-picks/ | Pool size effects: 2-4x improvement over random |
| Danger of Picking Too Many Upsets (PoolGenius) | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/the-danger-of-picking-too-many-upsets/ | Higher seed picks yield 87.5% accuracy vs. 75.2% public |
| Balancing Risk and Value (PoolGenius) | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/balancing-risk-and-value-in-your-bracket/ | Risk-value tradeoff framework |
| Scoring Systems: Why They Matter (PoolGenius) | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/bracket-pool-scoring-systems-why-they-matter-how-to-exploit-them/ | Scoring system comparison: standard, linear, flat, Fibonacci |
| NCAA Bracket Picks Optimizer (FantasyLabs) | https://www.fantasylabs.com/articles/ncaa-bracket-picks-optimizer-build-a-smarter-bracket-win-your-pool/ | Millions of simulations for EV-maximizing brackets |
| Analytics-Driven Bracket Strategies (Syracuse) | https://news.syr.edu/2026/03/11/how-to-win-your-march-madness-bracket-with-analytics-driven-strategies/ | Cognitive biases and #1 seed overselection |
| Mathematics of Bracketology (U. Miami) | https://news.miami.edu/stories/2019/03/the-mathematics-of-bracketology.html | Perfect bracket probability: 1 in 9.2 quintillion |
| Engaging Data Bracket Picker | https://engaging-data.com/march-madness-bracket-picker/ | Interactive seed-based Monte Carlo tool |
| Building a Bracket Simulator (Unabated) | https://unabated.com/articles/building-a-march-madness-bracket-simulator | Dynamic rating updates between rounds; sigma=11.2 |
| @RISK March Madness Predictions (Lumivero) | https://lumivero.com/resources/blog/march-madness-predictions-with-risk/ | Commercial Monte Carlo tool for Excel |

### Coaching, Intangibles, and Player Experience

| Source | URL | Description |
|--------|-----|-------------|
| Quantifying Intangibles via Network Analysis (Harvard, 2011) | https://harvardsportsanalysis.org/2011/05/quantifying-intangibles-a-network-analysis-prediction-model-for-the-ncaa-tournament/ | Weighted wins + experience; outperformed KenPom in brackets |
| A Method to the Madness (Harvard, 2019) | https://harvardsportsanalysis.org/2019/03/a-method-to-the-madness-predicting-ncaa-tournament-success/ | Experience R^2 = 0.0002 when controlling for seed |
| Bracketology (Harvard) | https://harvardsportsanalysis.org/tag/bracketology/ | "Predicting the NCAA tournament is largely a fool's errand" |
| Travel Effects on Tournament Play (TeamRankings) | https://www.teamrankings.com/blog/ncaa-basketball/and-albuquerque-is-where-the-effect-of-travel-distance-on-ncaa-tournament-play-stat-geek-idol | Favorites at 1000+ miles win only 59% vs. 76% within 500 miles |
| Tournament Experience and March Success (TeamRankings) | https://www.teamrankings.com/blog/ncaa-tournament/does-past-ncaa-tournament-experience-lead-to-march-success-the-data-says | Returning minutes r=0.36 with offensive efficiency improvement |

### Transfer Portal and Roster Continuity

| Source | URL | Description |
|--------|-----|-------------|
| Why Continuity Is Overrated (HoopsHQ) | https://www.hoopshq.com/long-reads/weekend-hot-takes-continuity-is-overrated | 0% continuity teams can succeed; coaching > continuity |
| Did Continuity Actually Matter? (Mid-Major Madness) | https://www.midmajormadness.com/2021/8/25/22630784/ncaa-tournament-drexel-saint-marys-loyola-marshall-basketball-teams-to-watch-mid-major-basketball | 8/10 highest-continuity mid-majors improved, but COVID may have amplified |
| How the Transfer Portal Transformed March Madness (PBS) | https://www.pbs.org/newshour/show/how-ncaas-transfer-portal-transformed-march-madness | 53%+ of rotation players previously played elsewhere |
| Finding a Championship Profile (CougCenter) | https://www.cougcenter.com/general/49063/finding-a-march-madness-champion-using-historical-analysis | 17/23 champions since 2002 led by juniors/seniors |

### LLM and AI Bracket Predictions

| Source | URL | Description |
|--------|-----|-------------|
| AI Bracket Picks (Yahoo Sports) | https://sports.yahoo.com/mens-college-basketball/article/march-madness-bracket-picks-we-had-ai-pick-every-game-of-the-mens-ncaa-tournament-heres-who-won-015822345.html | LLMs at 69.8% across 126 games; chalky picks |
| AI Ready for March Madness (Axios) | https://www.axios.com/2026/03/17/ai-ready-march-madness-bracket | LLM bracket improvement from 2024 to 2026 |
| AI Bracket Comparison (CBS Sports) | https://www.cbssports.com/general/news/2026-ncaa-tournament-bracket-projections-comparing-march-madness-ai-picks-from-chatgpt-copilot-gemini/ | ChatGPT vs. Claude vs. Gemini bracket comparison |

### Data Acquisition Tools and Packages

| Tool | URL | Description |
|------|-----|-------------|
| kenpompy (Python) | https://github.com/j-andrews7/kenpompy | Python scraper for KenPom data |
| cbbdata (R) | https://cbbdata.aweatherman.com | Unified API for Torvik + KenPom + NET; updates every 15 min |
| toRvik (R) | https://github.com/andreweatherman/toRvik | 20+ functions wrapping Bart Torvik data |
| hoopR (R) | https://hoopr.sportsdataverse.org | ESPN play-by-play, box scores, 36+ functions |
| gamezoneR (R) | https://jacklich10.github.io/gamezoneR/ | 170K+ charted shots per season from STATS LLC |
| ncaahoopR (R) | https://github.com/lbenz730/ncaahoopR | ESPN play-by-play, win probability, game flow |
| bigballR (R) | https://github.com/jflancer/bigballR | NCAA stats.ncaa.org scraper for PBP and lineups |
| CBBpy (Python) | https://pypi.org/project/CBBpy/ | ESPN scraper for D1 PBP and box scores |
| sportsipy (Python) | https://sportsreference.readthedocs.io | Sports Reference scraper for NCAAB |
| cbbd (Python) | https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/ | CollegeBasketballData.com REST API client |
| NCAAStatScraper (Python) | https://github.com/ryansloan/NCAAStatScraper | NCAA stats.ncaa.org extractor |
| ncaa-api | https://github.com/henrygd/ncaa-api | Free API for ncaa.com scores, stats, standings |
| Public ESPN API | https://github.com/pseudo-r/Public-ESPN-API | Community-documented ESPN JSON endpoints |
| SportsDataIO | https://sportsdata.io/ncaa-college-basketball-api | Commercial real-time API; free trial limited |
| basketball-reference-scraper | https://pypi.org/project/basketball-reference-scraper/ | Python scraper for Basketball Reference |

### Evaluation Metrics and Methodology

| Source | URL | Description |
|--------|-----|-------------|
| Log Loss vs. Brier Score (DRatings) | https://www.dratings.com/log-loss-vs-brier-score/ | Log loss preferred for sports; more sensitive to calibration |
| COVID Impact on Basketball (TeamRankings) | https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/covid-impact-basketball-college/ | Elite teams -6.1 pts after COVID pauses |
| NCAA COVID Statistical Policy | http://fs.ncaa.org/Docs/stats/ForSIDs/COVID-19_Policies.pdf | Official NCAA stat policy changes for 2020-21 |

### Miscellaneous References

| Source | URL | Description |
|--------|-----|-------------|
| KenPom vs. Sagarin (SportsBettingDime) | https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/ | Head-to-head: KenPom won 58.68% of compared predictions |
| Torvik Ratings Guide (OddsShark) | https://www.oddsshark.com/ncaab/what-are-torvik-ratings | Accessible T-Rank explainer |
| Torvik Deep Dive (Oreate AI) | https://www.oreateai.com/blog/understanding-torvik-basketball-rankings | Detailed Torvik methodology analysis |
| KenPom Explained (SI) | https://www.si.com/college-basketball/kenpom-rankings-explained-who-is-ken-pomeroy-what-do-rankings-mean | Sports Illustrated KenPom explainer |
| Sagarin Betting System Guide (PointSpreads) | https://www.pointspreads.com/guides/sagarin-betting-system-guide/ | Practical guide to using Sagarin ratings |
| Sagarin Rankings Guide (MyTopSportsbooks) | https://www.mytopsportsbooks.com/guide/advanced-betting/sagarin-rankings/ | Sagarin methodology overview |
| Dusting Off Sagarin (247Sports) | https://247sports.com/college/texas/board/21/contents/dusting-off-the-sagarin-ratings2024--240989305/ | Historical perspective on discontinued Sagarin system |
| NCAA Metrics Overview (JV's Basketball Blog) | https://hoops.jacobvarner.com/2020/02/21/an-overview-of-kenpom-net-and-other-official-metrics-used-by-the-ncaa-tournament-selection-committee-in-2020.html | Overview of metrics used by NCAA selection committee |
| Understanding Efficiency Margin (Rock M Nation) | https://www.rockmnation.com/2021/1/4/22211605/advanced-analytics-understanding-efficiency-margin-adjusted | Accessible explanation of AdjEM |
| T-Rank FAQ (Adam's WI Sports Blog) | http://adamcwisports.blogspot.com/p/every-possession-counts.html | Detailed T-Rank methodology Q&A |
| Comparing NCAA Ranking Systems (Price, 2021) | https://melissapprice.com/2021/03/15/comparing-ncaa-ranking-systems/ | Cross-system comparison of KenPom, Sagarin, BPI, RPI |
| Top Expert Bracket Picks (The Lines) | https://www.thelines.com/best-expert-bracket-picks-college-basketball-metrics-march-madness-kenpom-torvik-haslametrics-shotquality-2025/ | Expert system bracket comparison |
| Stat Pack 2026 (Basket Under Review) | https://www.basketunderreview.com/march-madness-2026-stat-pack-analyzing-statistical-trends-for-each-first-round-matchup/ | Statistical trends for tournament matchups |
| Using KenPom Player Stats (Basket Under Review) | https://www.basketunderreview.com/how-to-use-kenpom-to-analyze-college-basketball-part-1-player-stats/ | Guide to KenPom player-level data |
| Sagarin (Wikipedia) | https://en.wikipedia.org/wiki/Jeff_Sagarin | Background on Jeff Sagarin and his rating systems |
| ShotQuality at Colgate | https://www.colgate.edu/success-after-colgate/entrepreneurship/entrepreneurship-innovation-blog/shotquality-turning-passion | ShotQuality founding story |
| Sports Reference Data Use Policy | https://www.sports-reference.com/data_use.html | ToS for Sports Reference data |
| Sports Reference Bot Traffic Policy | https://www.sports-reference.com/bot-traffic.html | Rate limits: 20 req/min; scraping prohibited |
| Massey Ratings FAQ | https://masseyratings.com/faq.php | Methodology and purpose of Massey Ratings |
| Massey Ratings Data | https://masseyratings.com/data | CSV export for composite rankings |
| PoolGenius NCAA Bracket Picks | https://poolgenius.teamrankings.com/ncaa-bracket-picks/ | Main bracket optimizer tool |
| BracketIQ | https://www.bracketsiq.com/ | Bracket optimization using KenPom, Torvik, Haslametrics, EvanMiya |
| BettingPros Bracket Optimizer | https://www.bettingpros.com/ncaab/tournament/bracket-optimizer/ | Free bracket optimizer with odds integration |
| BracketVoodoo | https://www.bracketvoodoo.com/ | Bracket optimization tool |
| NCAA Tournament Records By Seed (PrintYourBrackets) | https://www.printyourbrackets.com/ncaa-tournament-records-by-seed.html | Historical seed records |
| Seeds and Championship Odds (BetFirm) | https://www.betfirm.com/seeds-national-championship-odds/ | Seed-based championship probability analysis |
| March Madness Bracket Tips (BoydsBets) | https://www.boydsbets.com/bracket-tips-by-seed/ | Practical bracket-building tips by seed |
| KenPom Subscription | https://kenpom.com/register-kenpom.php | Registration page for KenPom access |
| KenPom API | https://kenpom.com/register-api.php | API access registration |
| TeamRankings Preseason Explained | https://www.teamrankings.com/blog/ncaa-basketball/preseason-rankings-ratings-explained | Two-stage regression preseason model |
| EvanMiya About | https://blog.evanmiya.com/about | Background on Dr. Evan Miyakawa |
| EvanMiya Preseason Projections | https://blog.evanmiya.com/p/preseason-player-projections-with | Player projection methodology |
| Stathead | https://stathead.com | Paid Sports Reference advanced query tool |
| BigDataBall | https://bigdataball.com | Paid game log datasets with odds data |
| SportsDataIO Data Dictionary | https://sportsdata.io/developers/data-dictionary/ncaa-basketball | API documentation for SportsDataIO |
| On3 Transfer Portal Index | https://on3.com/transfer-portal | Team-level transfer talent tracking |
| Basketball Reference Continuity | https://basketball-reference.com/friv/continuity.html | NBA-style roster continuity metrics |
