# Deep Learning and Neural Network Approaches for March Madness Prediction

## Summary

Deep learning has been applied to NCAA March Madness prediction through a range of architectures: feedforward networks, CNNs, LSTMs, Transformers, and residual networks. The literature reveals a consistent and somewhat humbling finding: **deep learning rarely dominates simpler methods like gradient boosting or logistic regression for this task.** The best-performing systems tend to be ensembles that combine deep learning with traditional ML, or gradient-boosted tree models that outperform neural networks outright.

Key themes across the literature:

- **Feature engineering matters more than architecture.** Elo ratings, KenPom efficiency metrics, and seed differences provide far more predictive lift than switching from logistic regression to a Transformer.
- **LSTMs and Transformers show promise for temporal modeling** of team performance trajectories, but improvements over static feature models are modest (AUC ~0.83-0.85).
- **CNNs have been applied creatively** -- treating box score stat ratios as image-like patterns, or using them within ensemble fusion frameworks -- but do not consistently outperform tree-based methods.
- **Ensemble fusion (CFA)** that strategically combines diverse model types (including neural nets) based on "cognitive diversity" appears more valuable than any single deep architecture.
- **Gradient boosting remains the method to beat**, achieving 76-84% accuracy across multiple independent studies, often outperforming neural networks trained on the same data.

The most promising deep learning direction may be LSTM-based temporal modeling with carefully engineered features (Elo, GLM quality metrics), which achieves the best probability calibration (Brier score 0.1589), important for bracket pool scoring.

---

## Source 1: LSTM vs. Transformer Comparative Study (Habib, 2025)

**Title:** Forecasting NCAA Basketball Outcomes with Deep Learning: A Comparative Study of LSTM and Transformer Models

**Author:** Md Imtiaz Habib (Universite Cote d'Azur)

**URL:** https://arxiv.org/html/2508.02725v1

### Architecture Details

- **LSTM:** 32 hidden units, dropout 0.5, dense layer with 16 ReLU units, L2 regularization
- **Transformer:** Multi-head attention (2 heads), feedforward network (64 units), positional embeddings, comparable regularization
- Both trained with Adam optimizer, ReduceLROnPlateau scheduling, early stopping (patience=10), batch size 32

### Data

- Kaggle March Machine Learning Mania 2025 competition data
- NCAA Division 1 men's and women's basketball, 2003-2024
- Regular season and tournament match records

### Feature Engineering (Three Tiers)

1. **Easy:** Tournament seed, seed differences
2. **Medium:** Season-averaged box score stats (PPG, rebounds, assists, FG%, turnovers, steals, blocks)
3. **Hard:** Elo ratings (K=100), GLM-derived team quality metrics, coach win rates (men only)

### Performance

| Model | Loss | Accuracy | AUC | Brier Score |
|-------|------|----------|-----|-------------|
| LSTM | BCE | 0.7331 | 0.8317 | 0.1617 |
| LSTM | Brier | 0.7280 | 0.8274 | **0.1589** |
| Transformer | BCE | 0.7363 | **0.8473** | 0.1638 |
| Transformer | Brier | 0.7295 | 0.8426 | 0.1609 |

### Key Findings

- **Transformer excels at discriminative ranking** (highest AUC 0.8473) through multi-head attention capturing feature interactions
- **LSTM excels at probability calibration** (lowest Brier score 0.1589), crucial for bracket pool scoring systems
- Advanced features (Elo, GLM) contributed AUC improvements of 0.045-0.049 over seed-only models
- No single architecture/loss combination is universally optimal; choice depends on whether you need ranking or calibrated probabilities
- The paper does not directly compare against logistic regression or gradient boosting baselines, which is a notable gap

### Relevance

This is the most rigorous head-to-head comparison of modern deep learning architectures for March Madness. The temporal inductive bias of LSTMs (simulating progression through tournament rounds) is a genuinely novel modeling idea.

---

## Source 2: Deep Learning + Combinatorial Fusion Analysis (Wu et al., 2026)

**Title:** NCAA Bracket Prediction Using Machine Learning and Combinatorial Fusion Analysis

**Authors:** Yuanhong Wu, Isaiah Smith, Tushar Marwah, Michael Schroeter, Mohamed Rahouti, D. Frank Hsu

**URL:** https://arxiv.org/html/2603.10916v1

### Architecture Details

Five base classifiers:
1. Logistic Regression (L1/L2 regularization)
2. Support Vector Machines (kernel optimization)
3. Random Forest
4. XGBoost (with regularization)
5. **Convolutional Neural Network** (sigmoid output, ReLU hidden layers, Adam optimizer, cross-entropy loss)

These are combined using **Combinatorial Fusion Analysis (CFA):**
- Rank-Score Characteristic (RSC) functions mapping ranks to scores
- Cognitive diversity metric measuring differences between scoring systems
- Three combination methods: average, diversity-weighted, performance-weighted
- 52 ensemble variants generated from score and rank approaches

### Data

- Historical tournament data 2001-2022 (excluding 2020) from Kaggle
- Team statistics from KenPom
- Started with 44 features, refined to 26 via RFECV with 5-fold CV
- Feature categories: offensive efficiency, defensive efficiency, strength of schedule, luck metrics
- Features encoded as differences between competing teams

### Performance

- **CFA rank combination ensemble: 74.60% accuracy**
- Best public ranking system (NET Rankings): 73.02%
- CFA score combination: 71.43%
- Improvement margin: 1.58% over leading public systems
- Best ensemble was "ABE" (logistic regression + SVM + CNN), appearing as top performer across 6 of 10 historical years

### Key Findings

- The CNN was one component of the best-performing ensemble, but **not evaluated independently** against the simpler classifiers
- Success derived from **"cognitive diversity"** between models, not from the neural network alone
- Combined ensemble models in prior research "did not outcompete individual models" -- this CFA approach succeeds by being strategic about which models to fuse
- The key insight is that model diversity (having models that disagree in informative ways) matters more than model complexity

### Relevance

This paper suggests the best use of neural networks in March Madness prediction may be as **one diverse voice in an ensemble**, not as a standalone predictor. The CFA framework is a practical and well-motivated approach to model combination.

---

## Source 3: Evolving Neural Network Architecture (Adithya GV, 2022-2024)

**Title:** March Madness ML -- An experiment on neural networks and the NCAA's March Madness Bracket

**Author:** Adithya GV (GitHub project)

**URL:** https://github.com/adithya-gv/march-madness-ml

### Architecture Details (Progressive Iterations)

- **2022:** 2-layer vanilla network, 880 parameters, seed-based matchup predictions
- **2023:** 3-layer architecture, 1,272 parameters, offensive/defensive ratings + win ratios over 35 years
- **2024:** 4-layer network, 345,425 parameters; input 204 features, hidden layers 500 -> 75 -> 25, output 2 classes
  - Optimizer: Adamax
  - Loss: CrossEntropyLoss
  - Batch size: 32
  - Data augmentation: each matchup duplicated in reversed team order to prevent positional bias

### Data

- Kaggle datasets with KenPom and HeatCheck advanced statistics
- 16 years of historical data (2024 model)
- 102 data points per team in the most advanced version

### Performance

- **2023 actual tournament:** 56/192 points (88th percentile on ESPN)
- **2023 ESPN Second Chance Challenge:** 72/128 points (98th percentile)
- **2024 model retroactively on 2023 bracket:** 119/192 points (102% improvement over 2023 model)
- Successfully predicted unlikely runs like Florida Atlantic (9-seed) reaching the Final Four

### Key Findings

- **Simpler seed-only models excel at picking higher-probability outcomes** (favorites), while statistically-enriched networks better identify earlier-round upsets
- Upset detection creates cascading improvements throughout bracket scoring
- Massive parameter increase (880 -> 345K) combined with richer features produced dramatic improvement
- The practical lesson: for bracket pools, getting a few early upsets right is worth more than correctly picking all the chalk

### Relevance

This is a valuable practitioner's perspective showing how iterative refinement of both architecture and feature engineering drives real-world bracket performance. The insight about seed-based models vs. stats-enriched models having complementary strengths echoes the CFA ensemble findings.

---

## Source 4: Deep Learning with Four Architectures + CFA (Alfatemi et al., 2024)

**Title:** Advancing NCAA March Madness Forecasts Through Deep Learning and Combinatorial Fusion Analysis

**Authors:** Ali Alfatemi, Mohamed Rahouti, Frank Hsu, Christina Schweikert (Fordham University)

**URL:** https://link.springer.com/chapter/10.1007/978-3-031-66431-1_38

**Published in:** IntelliSys 2024, Lecture Notes in Networks and Systems, vol. 1067, Springer

### Architecture Details

Four distinct neural network architectures:
1. **Convolutional Neural Network (CNN)** -- for pattern extraction from team statistics
2. **Recurrent Neural Network (RNN)** -- for sequential game information modeling
3. **Feedforward Neural Network** -- baseline deep learning approach
4. **Residual Network** -- for deeper architectures with skip connections

These are combined using CFA to merge predictions from heterogeneous models.

### Data

- Historical NCAA Men's Tournament dataset
- Domain-specific feature engineering pipeline

### Performance

Specific quantitative results were not available from the preprint abstract. The authors claim the approach "pushes the boundaries of state-of-the-art March Madness forecasting."

### Key Findings

- The heterogeneity of architectures (CNN vs RNN vs feedforward vs residual) is the core contribution -- each captures different aspects of the prediction problem
- CFA fusion of diverse deep architectures is positioned as more effective than any single network
- This is an evolution of the same research group's work (Hsu, Rahouti) that produced Source 2

### Relevance

This paper represents the most architecturally ambitious deep learning approach in the literature, using four different network types. However, the lack of publicly available quantitative results makes it difficult to assess whether this complexity is justified relative to simpler approaches.

---

## Source 5: Gradient Boosting vs. Neural Networks (Deshpande, 2017; Kumar et al.)

These two independent studies reached the same conclusion: gradient boosting outperforms neural networks for March Madness prediction.

### 5a: Applying Machine Learning to March Madness (Deshpande)

**Author:** Adit Deshpande (UCLA CS '19)

**URL:** https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness

**Data:** Kaggle March Machine Learning Mania 2017; Sports-Reference.com; 1993-2016 (115,113 games)

**Features:** 16-dimensional team vectors including PPG, points allowed, 3PT%, turnovers, assists, rebounds, steals, SRS, strength of schedule, Power 6 status, tournament history. Matchups encoded as difference vectors.

**Results:** Gradient Boosted Trees achieved **76.37% accuracy**, outperforming neural networks and other ensemble methods.

**Key quote:** "Always try out a very simple model before experimenting with more complex neural network and ensemble approaches."

### 5b: Machine Learning Madness (Kumar, Dang, Khosla, Le, Petrillo)

**URL:** https://mehakumar.github.io/machine-learning-madness/

**Data:** Sports Reference, 2000-2019 (16 tournaments training, 3 testing), 25 basic statistical features

**Neural Network:** 5 layers, sigmoid activation, Adam optimizer

**Results:**

| Method | Log Loss | Accuracy |
|--------|----------|----------|
| KNN | 0.583 | 71.4% |
| Neural Network | 0.612 | 76.2% |
| Random Forest | 0.418 | 82.5% |
| **Gradient Boosting** | **0.409** | **84.1%** |

**Key Finding:** Gradient boosting achieved 84.1% accuracy vs. the neural network's 76.2%. The neural network had worse log loss (0.612) than even KNN (0.583), suggesting poor probability calibration.

### Relevance

These studies provide the critical baseline: if you are going to use deep learning for March Madness, you need to demonstrate improvement over gradient boosting, which is a high bar. The neural networks in these studies used relatively simple architectures, so the comparison is not entirely fair to modern deep learning -- but it sets the practical benchmark.

---

## Cross-Cutting Observations

1. **The deep learning premium is small or negative.** Across all sources, the best deep learning models achieve 73-76% game-level accuracy, while gradient boosting hits 76-84%. The LSTM/Transformer paper's AUC of 0.85 is competitive but uses much richer features.

2. **Feature engineering is the real differentiator.** Elo ratings, KenPom efficiency metrics, and GLM-derived quality scores contribute more to prediction quality than architecture choice. The LSTM paper showed a 0.045-0.049 AUC gain from better features, likely more than the gain from choosing LSTM over logistic regression.

3. **Deep learning shines in ensemble diversity.** The CFA papers show that including a neural network alongside logistic regression and SVMs creates beneficial "cognitive diversity" that improves ensemble performance. This may be the most practical use case.

4. **Temporal modeling is underexplored.** The LSTM paper's approach of modeling team performance trajectories through a season is theoretically appealing but has not been extensively validated against simpler momentum features.

5. **Calibration vs. discrimination tradeoff.** The LSTM vs. Transformer comparison reveals that these goals are in tension: Transformers rank matchups better (AUC), LSTMs produce better-calibrated probabilities (Brier score). For bracket pools, calibration likely matters more.

6. **Play-by-play and video data remain frontier territory.** No study in this review successfully applies CNNs to play-by-play or video data for tournament prediction. This is a gap that could potentially unlock genuine deep learning advantages.

---

## Sources

- [Habib (2025) - LSTM vs Transformer Comparative Study](https://arxiv.org/html/2508.02725v1)
- [Wu et al. (2026) - NCAA Bracket Prediction with CFA](https://arxiv.org/html/2603.10916v1)
- [Adithya GV - March Madness ML GitHub](https://github.com/adithya-gv/march-madness-ml)
- [Alfatemi et al. (2024) - Deep Learning + CFA (Springer)](https://link.springer.com/chapter/10.1007/978-3-031-66431-1_38)
- [Deshpande - Applying ML to March Madness](https://adeshpande3.github.io/Applying-Machine-Learning-to-March-Madness)
- [Kumar et al. - Machine Learning Madness](https://mehakumar.github.io/machine-learning-madness/)
- [Lee (2022) - Deep Learning in Sports Prediction (Trinity)](https://digitalcommons.trinity.edu/cgi/viewcontent.cgi?article=1065&context=compsci_honors)
