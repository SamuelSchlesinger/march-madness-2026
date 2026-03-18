# Recent Innovations in March Madness Prediction (2024-2026)

## Summary

The 2024-2026 period has seen several notable shifts in how people predict March Madness outcomes:

1. **LLMs enter the bracket game.** ChatGPT, Claude, and Gemini can now produce plausible full brackets -- a sharp contrast from 2024 when AI chatbots struggled with multi-round logic. Across two years of Yahoo Sports testing, LLM-generated brackets correctly predicted 88/126 games (69.8%), including a perfect 8/8 on Elite Eight teams in 2025. However, LLMs tend to produce "chalky" brackets that favor higher seeds and rarely capture Cinderella runs.

2. **Deep learning architectures move beyond gradient boosting.** A 2025 arXiv paper systematically compared LSTM and Transformer architectures for NCAA prediction, finding that Transformers optimized with BCE achieve the best discriminative power (AUC 0.8473) while LSTMs trained with Brier loss produce better-calibrated probabilities (ECE 3.2%). This is the first rigorous head-to-head comparison of these architectures in sports forecasting.

3. **Combinatorial Fusion Analysis (CFA) for ensemble construction.** A 2026 paper introduced CFA -- a framework that measures "cognitive diversity" between models and uses rank-based fusion rather than simple averaging. Their best ensemble (logistic regression + SVM + CNN) achieved 74.60% accuracy, beating all ten major public ranking systems.

4. **Nate Silver's COOPER system replaces the FiveThirtyEight model.** COOPER introduces separate offensive/defensive ratings, individual team home-court advantages, pace-adjusted variance modeling, and crucially allows a team's rating to drop after a win if the win was unimpressive (a Bayesian improvement over the old system). Tournament forecasts blend COOPER (5/8 weight) with KenPom (3/8 weight).

5. **Prediction markets as a new data source.** Kalshi handled $2.27B in college basketball trading volume in February 2026 alone, making prediction market prices a potentially rich new signal for modelers -- aggregated crowd wisdom with real money at stake.

6. **The goto_conversion calibration technique** continues to dominate Kaggle competitions by correcting the favorite-longshot bias in power ratings (specifically 538/Elo-based ratings). This single calibration trick has won gold and silver medals across multiple years.

---

## Source 1: Deep Learning for NCAA Forecasting (LSTM vs. Transformer)

- **Title:** Forecasting NCAA Basketball Outcomes with Deep Learning: A Comparative Study of LSTM and Transformer Models
- **URL:** https://arxiv.org/abs/2508.02725
- **Year:** 2025
- **Author:** Md Imtiaz Habib (Universite Cote d'Azur)

### What's New

First systematic comparison of LSTM vs. Transformer architectures under identical conditions for NCAA tournament prediction. Three-tier feature engineering system:

- **Easy features:** Seed differences
- **Medium features:** Season-averaged box-score stats (points, rebounds, assists, turnovers, steals, blocks, shooting percentages)
- **Hard features:** Elo ratings (K=100), GLM-derived team quality metrics, coach win-rate data

Key architectural details:
- LSTM: 32-unit layer, L2 regularization, dropout 0.5, batch size 128
- Transformer: Multi-head attention (2 heads, dim 64), encoder block with feedforward network, learning rate 10^-4

### Key Results

| Model | Loss | Accuracy | AUC | Brier Score | ECE |
|-------|------|----------|-----|-------------|-----|
| LSTM | BCE | 0.7331 | 0.8317 | 0.1617 | 5.8% |
| LSTM | Brier | 0.7280 | 0.8274 | **0.1589** | **3.2%** |
| Transformer | BCE | 0.7363 | **0.8473** | 0.1638 | 6.2% |
| Transformer | Brier | 0.7295 | 0.8426 | 0.1609 | 3.1% |

### Key Insight

**The choice of loss function matters more than architecture choice for calibration.** Brier loss produces dramatically better-calibrated probabilities (ECE ~3%) vs. BCE (~6%), regardless of whether you use LSTM or Transformer. But for pure discrimination/ranking (AUC), Transformer + BCE wins.

Ablation study: GLM team quality (-0.049 AUC drop when removed) and Elo ratings (-0.045 AUC drop) are the most critical features. Seed difference alone is less informative than these derived metrics.

### Limitations

No player-level data, no injury information, static features (no recency weighting or form), no real-time updating during the tournament.

---

## Source 2: Combinatorial Fusion Analysis for NCAA Bracket Prediction

- **Title:** NCAA Bracket Prediction Using Machine Learning and Combinatorial Fusion Analysis
- **URL:** https://arxiv.org/abs/2603.10916
- **Year:** 2026
- **Authors:** Wu, Smith, Marwah, Schroeter, Rahouti, and Hsu

### What's New

Applies Combinatorial Fusion Analysis (CFA) to sports prediction. CFA treats the problem as a ranking problem rather than classification, and measures "cognitive diversity" between models using rank-score characteristic (RSC) functions -- a diversity measure that is independent of the data itself.

Five base models: Logistic Regression, SVM, Random Forest, XGBoost, CNN. These generate 52 ensemble combinations via three integration methods:
- Average combination
- Weighted combination by diversity strength
- Weighted combination by performance

Data: Kaggle March Machine Learning Mania (2001-2022, excluding 2020) plus KenPom analytics. Feature selection via Random Forest + RFECV reduced 44 features to 26 optimal predictors.

### Key Results

- CFA rank combination: **74.60% accuracy** (best result)
- Score combination: 71.43%
- Best public ranking system baseline: 73.02%
- Best individual base model was not as good as the CFA ensemble

The optimal ensemble combined logistic regression + SVM + CNN, identified through historical cross-validation across ten prior tournament years.

### Key Insight

**Rank-based fusion outperforms score-based fusion.** The authors argue that converting model outputs to ranks before combining them is more robust than averaging raw probabilities, because it normalizes for different models having different probability scales and confidence patterns.

The winning combination (LR + SVM + CNN) is notable because it includes models that are quite different in structure -- a linear model, a kernel method, and a neural network -- which maximizes the "cognitive diversity" that CFA measures.

---

## Source 3: Nate Silver's COOPER Rating System

- **Title:** Introducing COOPER: Silver Bulletin's NCAA Basketball Rating System
- **URL:** https://www.natesilver.net/p/introducing-cooper-silver-bulletins
- **Year:** 2025-2026

### What's New

COOPER replaces the old SBCB/FiveThirtyEight system with several innovations:

1. **Bayesian rating updates after wins:** The old system required a team to always gain rating points when it won. COOPER allows a team to LOSE rating points after a win if the win was unimpressive relative to expectations (e.g., Duke barely beating Cal State Bakersfield). This alone improves accuracy by ~1% of games.

2. **Separate offensive/defensive ratings:** PPPG (projected points per game) and PPAG (projected points allowed per game). A team with PPPG=81, PPAG=74 is expected to beat an average opponent 81-74.

3. **Pace-adjusted variance:** Higher-scoring games introduce more variance. An uptempo team favored 90-80 has different upset probability than a defensive team favored 65-55, even at the same expected margin.

4. **Individual team home-court advantages:** Replaces the old one-size-fits-all home court adjustment. Accounts for altitude, fan intensity, etc.

5. **Travel distance effects:** Formula: 5 * m^(1/3) where m = distance in miles.

6. **Impact factors for game weighting:** Conference and tournament games weighted higher. Games weighted by projected closeness (blowout non-conference games contribute less signal).

7. **Mean reversion between seasons:** 60% reversion for women, 70% for men, toward conference averages (not global mean). Reflects NIL era where elite programs maintain dominance more consistently.

### Tournament Forecasting

- Blends COOPER (5/8 weight) with KenPom for men, Her Hoop Stats for women (3/8 weight)
- K-factor of 55 (doubled to 110 for early season)
- 1 basketball point = ~28.5 Elo points
- Model runs "hot" during tournament: updates ratings after each simulated round
- Injury adjustments via Win Shares (top college stars = 7-10 point margin impact)

### 2025 Result

For 2025, Silver's model used 50% SBCB ratings + 50% composite of KenPom, Sonny Moore, ESPN BPI, Massey, and S-Curve. Florida won the championship with a "clutch comeback against Houston." The model has been running tournament forecasts continuously since 2011, with some code dating to 2002-2003.

---

## Source 4: LLM-Based Bracket Prediction (ChatGPT, Claude, Gemini)

- **Sources:**
  - Yahoo Sports: https://sports.yahoo.com/mens-college-basketball/article/march-madness-bracket-picks-we-had-ai-pick-every-game-of-the-mens-ncaa-tournament-heres-who-won-015822345.html
  - Axios: https://www.axios.com/2026/03/17/ai-ready-march-madness-bracket
  - CBS Sports: https://www.cbssports.com/general/news/2026-ncaa-tournament-bracket-projections-comparing-march-madness-ai-picks-from-chatgpt-copilot-gemini/
- **Year:** 2025-2026

### What's New

In 2025, LLMs could barely fill out a coherent bracket (struggling with multi-round elimination logic). By 2026, all three major chatbots -- ChatGPT, Claude, and Gemini -- produce plausible brackets with some upset picks and rationale.

### 2026 Predictions

- **Claude:** Duke over Arizona in championship. Predicted upsets: Akron over Texas Tech, BYU over Gonzaga (citing a key injury). Claude Opus 4.6 variant had Arizona over Duke 67-62.
- **ChatGPT:** Duke as champion. Upset picks: St. John's and VCU as spoilers.
- **Gemini:** Arizona as champion. Upset pick: Miami (Ohio) over Tennessee.

All three produced "chalky" brackets -- almost every Final Four slot went to a 1 or 2 seed.

### Historical Performance (Cumulative 2024-2025)

- Overall: 88/126 games correct (69.8%)
- First round: 49/64 correct (76.6%)
- Second round: 22/32 correct (68.8%)
- Correctly predicted 2024 national champion (first attempt)
- Perfect 8/8 on Elite Eight teams in 2025

### Key Insight

LLMs are surprisingly competitive for "above replacement" bracket prediction but fundamentally limited: they rely on training data and public knowledge, produce consensus/chalky picks, and cannot model the specific probabilistic dynamics that make March Madness unpredictable. They are better thought of as a "wisdom of the internet" aggregator than a novel analytical tool.

---

## Source 5: XGBoost Tutorial with CollegeBasketballData.com API

- **Title:** Talking Tech: Building a March Madness Model using XGBoost
- **URL:** https://blog.collegefootballdata.com/talking-tech-march-madness-xgboost/
- **Year:** 2025

### What's New

This is a practical tutorial demonstrating the CollegeBasketballData.com (CBBD) REST API as a data source for March Madness modeling. The author builds a gradient-boosted model predicting point margins.

Features: 25 features including offensive/defensive ratings, pace, Four Factors (FT rate, ORB%, TO ratio, eFG%) on both sides of the ball, plus seed information.

Data: 686 NCAA tournament games from 2013-2024 via CBBD API. Careful to use only regular season stats (no tournament stats) to avoid data leakage.

### Key Results

- Validation MAE: ~7.97 points
- 2024 tournament accuracy: 64.3% (straight-up picks)
- First round accuracy: 69.7%

The author notes these are modest results and suggests a MAE around 6.5 would be a stronger benchmark. Improvements: opponent-adjusted stats, additional data sources, expanded feature engineering.

### Key Insight

**CBBD API** is highlighted as a useful free/accessible data source for anyone building March Madness models. The tutorial emphasizes the critical importance of avoiding data leakage (only using stats available at prediction time).

---

## Source 6: Prediction Markets as a New Data Source

- **Sources:**
  - SI: https://www.si.com/betting/prediction-market/college/predicting-which-seed-will-win-march-madness-based-on-kalshi-markets
  - Front Office Sports: https://frontofficesports.com/prediction-markets-leverage-march-madness-despite-ncaa-opposition/
  - MLQ: https://mlq.ai/prediction/brief/sports/sports-markets-brief-march-16-2026-march-madness-fuels-prediction-volume-surge-2026-03-16/
- **Year:** 2025-2026

### What's New

Prediction markets (Kalshi, Polymarket) have exploded in scale for March Madness:

- Kalshi: $2.27B in men's college basketball trading volume in February 2026 alone
- Projected $135M-$150M in handle-equivalent volume for the 2026 tournament
- Duke at 19% implied probability to win the championship on Kalshi; Michigan at 18%

These markets offer real-money-weighted crowd probabilities that could serve as a powerful input signal for prediction models, similar to how some models already use Vegas lines but with more granular contract structures (individual game outcomes, seed-based markets, etc.).

### Key Insight

Prediction market prices are a potentially underutilized feature for ensemble models. Unlike Vegas odds (which include vigorish and may be influenced by line management), prediction market contracts are priced purely by supply/demand from participants with skin in the game. The sheer volume ($2.27B/month) suggests these prices encode significant information.

---

## Source 7: Mathematical Modeling with Interpretable Logistic Regression

- **Title:** March Madness Tournament Predictions Model: A Mathematical Modeling Approach
- **URL:** https://arxiv.org/html/2503.21790v1
- **Year:** 2025

### What's New

A deliberate counter-trend to the black-box ML movement. Uses multivariable logistic regression with just four predictors:
- Adjusted Offensive Efficiency (ADJOE)
- Adjusted Defensive Efficiency (ADJDE)
- Power Rating
- Two-Point Shooting Percentage Allowed

Elegant feature engineering: models team-stat *differences* rather than raw values. When input x gives probability p, input -x automatically gives 1-p (mathematical consistency guaranteed by the logistic function's symmetry).

### Key Results

- Individual matchup accuracy: 74.6%
- Full tournament simulation (Monte Carlo, 100 iterations): 65.63% in one bracket half, 43.75% in the other
- Spearman correlation with actual tournament ordering: rho = 0.747 (best bracket half)

### Key Insight

**Interpretability vs. accuracy tradeoff.** This approach achieves comparable matchup accuracy (74.6%) to the CFA ensemble (74.60%) with far fewer features and complete interpretability. Each coefficient directly shows its impact on log-odds of winning. The authors argue this matters when coaching staffs need actionable insights, not just predictions.

---

## Cross-Cutting Themes

### What Actually Moved the Needle (2024-2026)

1. **Loss function choice** (Brier vs. BCE) matters as much as model architecture for calibrated probabilities
2. **Rank-based ensemble fusion** (CFA) outperforms naive averaging of model outputs
3. **Separate offensive/defensive ratings** (COOPER, KenPom-style) continue to be the most important features
4. **Pace/tempo adjustment** affects variance modeling and upset probability in non-obvious ways
5. **Pre-season information** (AP polls, prior season carryover) remains a surprisingly strong signal

### What Has NOT Changed Much

- The ~74-75% accuracy ceiling for individual matchup prediction appears persistent across all methods (logistic regression through Transformers)
- Seed difference remains a strong baseline that's hard to beat by large margins
- No model reliably predicts deep Cinderella runs
- Player-level data (injuries, individual performance) remains underutilized in most published models

### Emerging Opportunities

- **Prediction market prices** as ensemble features (massive new data source with real-money incentives)
- **LLM-based reasoning** for injury/context analysis that statistical models miss (qualitative factors)
- **Transformer architectures** for sequence modeling of team performance trajectories within a season
- **Real-time tournament updating** (Silver's "hot" model approach) where predictions improve as the tournament reveals information
