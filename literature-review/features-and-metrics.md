# Features and Metrics

This chapter synthesizes the literature on which statistics, derived features, and rating systems matter most for predicting NCAA tournament outcomes. The central finding is that a small number of tempo-free efficiency metrics -- adjusted for opponent strength -- dominate prediction accuracy, and aggressive feature reduction costs surprisingly little. We also examine how rating systems themselves serve as powerful meta-features, how to handle the player-level vs. team-level tradeoff, and what feature set we recommend for this project.

## 1. The Hierarchy of Predictive Features

Across every source reviewed, a clear tier structure emerges for feature importance. The convergence is striking: researchers using different methods, datasets, and time periods independently arrive at nearly the same ranking.

**Tier 1 -- Core predictive features** (appear in virtually every successful model):

- Adjusted Efficiency Margin (AdjEM = AdjOE - AdjDE) -- the single strongest predictor. All 24 national champions from 2001--2024 ranked in the top 25 of KenPom's AdjEM. No other metric comes close to this consistency.
- Adjusted Offensive Efficiency (AdjOE) -- points scored per 100 possessions, adjusted for opponent quality. Champions averaged rank 8.25.
- Adjusted Defensive Efficiency (AdjDE) -- points allowed per 100 possessions, adjusted for opponent quality. Champions averaged rank 16.33 (offense matters slightly more for champions, but both are essential).
- Seed or composite power rating (e.g., Barthag).

**Tier 2 -- Strong supporting features:**

- Strength of schedule (SOS) -- consistently the second or third most important feature in gradient-boosted models.
- Effective field goal percentage (eFG%).
- Turnover rate (per possession).
- Offensive rebounding rate.

**Tier 3 -- Useful but secondary:**

- Free throw rate (FTA/FGA).
- Two-point shooting percentage allowed.
- Steals, assists, blocks per game.
- Simple Rating System (SRS).

**Tier 4 -- Low or no predictive value:**

- Adjusted tempo -- champions ranged from rank 1 to 200+; the average rank was ~134. Fast or slow pace does not predict tournament success.
- Non-conference SOS -- only 3 of 24 champions ranked in the top 60.
- Three-point shooting percentage -- high game-to-game variance makes it unreliable for tournament prediction despite regular-season value.
- Conference tournament results -- small sample, high variance.
- Luck rating -- by definition captures randomness.

The practical takeaway is that if you can only measure one thing about a team, measure its adjusted efficiency margin. If you can measure four things, add AdjOE, AdjDE, and a composite power rating. You will be within 1 percentage point of accuracy achievable with 16+ features.

## 2. Tempo-Free Efficiency Metrics and Why They Dominate

The foundational insight of modern college basketball analytics is that raw box score totals are misleading. Teams play at vastly different speeds -- anywhere from 55 to 90+ possessions per 40-minute game. A team scoring 80 points in 80 possessions (1.00 points per possession) is performing worse offensively than one scoring 70 in 60 possessions (1.17 PPP).

**Per-possession normalization** removes the influence of tempo so that teams playing at different speeds can be compared fairly. The standard possession estimation formula is:

```
Possessions = FGA - OREB + TO + (0.475 * FTA)
```

The 0.475 multiplier is specific to the college game. For accuracy, possessions should be calculated for both teams and averaged.

All major rating systems (KenPom, BPI, T-Rank, Haslametrics) use per-possession metrics as their foundation. Offensive and defensive efficiency are expressed as points per 100 possessions, then adjusted for opponent quality via iterative least-squares regression (KenPom) or multiplicative Pythagorean methods (Torvik).

**Why these metrics dominate tournament prediction specifically:** Defense, rebounding, and turnover control are "repeatable traits" -- they hold up under the stress of tournament play (unfamiliar venues, quick turnarounds, travel). Shooting-dependent metrics, especially three-point percentage, are disrupted more by these conditions. Teams in the top 5 nationally in turnover rate at both ends scored 21 points per game off miscues. TCU went 13-0 when their offensive rebounding rate exceeded 36%, but just 9-11 when it did not.

The per-possession prediction methodology works by projecting a game's expected pace (based on both teams' tempo preferences), then applying each team's offensive and defensive efficiency to generate an expected point spread. This properly accounts for style mismatches -- e.g., a run-and-gun team vs. a pack-line defense.

For more on how these metrics feed into specific model architectures, see [Modeling Approaches](modeling-approaches.md).

## 3. Dean Oliver's Four Factors

Dean Oliver identified four factors that together explain nearly all of offensive efficiency. A 2023 revisiting of the framework (Poropudas) found a 0.998 correlation between four-factor-calculated offensive rating and actual offensive rating -- the decomposition is essentially complete.

The revised sensitivity weights from normalized sensitivity analysis (2022--23 NBA data) are:

| Factor | Definition | Avg. Value | Sensitivity | Marginal Effect |
|--------|-----------|------------|-------------|-----------------|
| eFG% | (FGM + 0.5 * 3PM) / FGA | ~50% | **47%** | +1 pp = +1.77 pts/100 poss |
| ORB% | OREB / (OREB + opponent DREB) | ~28% | **26%** | Larger effect for low-shooting teams |
| TOV% | TO / (FGA + TO - OREB + 0.475 * FTA) | ~19% | **21%** | -1 pp = +1.34 pts/100 poss |
| FTr | FTA / FGA (or FTM / FGA in some formulations) | ~32% | **7%** | Smallest marginal effect |

These revised weights differ meaningfully from Oliver's original estimates of 40/25/20/15. Offensive rebounding is more important than previously thought; free throw rate is substantially less important.

**Non-linear relationships are important.** The factors interact: turnovers are more costly for teams that shoot efficiently (each turnover wastes a higher-expected-value possession), and lower-shooting teams benefit more from offensive rebounds (each extra chance is more valuable when your baseline conversion rate is lower). This means simple linear models using the Four Factors as independent features will miss some signal.

**A critical finding for modeling:** Jordan Sperber's research on 311 games showed that team-level matchups in the Four Factors -- e.g., an elite offensive rebounding team against a poor defensive rebounding team -- add less than 1 point per 100 possessions of predictive value beyond what overall efficiency ratings already capture. This means you should use aggregate efficiency ratings rather than trying to model factor-by-factor matchups. This simplifies the feature space considerably.

## 4. Feature Differencing as Standard Practice

Multiple successful models compute the difference between two teams' statistics rather than using each team's raw values as separate features. This approach has become standard practice for good reasons:

- **Dimensionality reduction.** Instead of 2N features (N stats for each team), you have N difference features.
- **Mathematical symmetry.** P(A beats B) = 1 - P(B beats A), which difference features enforce naturally when fed into a logistic regression or similar model.
- **Prevents school-specific bias.** The model learns about competitive gaps rather than memorizing which teams have historically high or low stats.

The 2025 arXiv paper (March Madness Tournament Predictions Model) used 4 difference features derived from 16 raw features and achieved 74.6% accuracy -- less than 1 percentage point behind the full 16-feature model at 75.4%. Kumar et al. used differences of 25 basic statistics to achieve 84.1% accuracy with gradient boosting. The 2026 Combinatorial Fusion Analysis paper computed difference variables between opposing teams for each of its 26 selected features.

An additional insight from the Combinatorial Fusion Analysis work: **ranks of variables can be more predictive than their raw values.** Converting raw statistics to ordinal ranks before differencing is worth testing as a feature transformation.

## 5. Player-Level vs. Team-Level Features

Most mainstream prediction models operate at the team level. However, the transfer portal era has made roster discontinuity a first-order problem: the team from last year is often not the team playing this year.

**When player-level features add the most value:**

- *Preseason and early-season projections.* When rosters change significantly, team-level models that simply regress last year's rating are at a disadvantage vs. models that project individual players and reassemble the roster. EvanMiya's Bayesian Performance Rating (BPR) system takes this approach, combining box score stats with play-by-play adjusted plus-minus at the player level and aggregating up to team projections.
- *Injury adjustments.* Losing a star player changes expected efficiency dramatically. COOPER incorporates probabilistic injury data weighted by Win Shares for tournament forecasts. BPI down-weights games where key players were absent.
- *Matchup analysis.* Player-level data enables analysis of specific problems (e.g., no rim protector against a paint-attacking team), though the evidence suggests this adds marginal value beyond aggregate efficiency.

**When team-level features are sufficient:**

- *Stable rosters with long track records.* If a team returns most players, team-level efficiency metrics are reliable.
- *By late season.* Team-level models "catch up" because they have enough game data to estimate team strength directly. Preseason priors carry only ~15% weight by season's end in EvanMiya's system.
- *Predicting game outcomes (not margins).* Simple team-level models based on efficiency and SOS achieve 70--75% accuracy, which is already strong.

**Practically useful player-derived team-level features:**

- Returning minutes percentage (r = 0.36 with offensive efficiency improvement).
- NCAA tournament experience, weighted by minutes played (statistically significant predictor of future tournament success per TeamRankings, though the Harvard Sports Analysis Collective found near-zero marginal value over seed).
- Roster continuity tracked by KenPom and Torvik.

**Our recommendation:** Start with team-level features. Player-level data is harder to collect and integrate, and the marginal accuracy gain over team-level models is modest (estimated ~2% by EvanMiya's own benchmarks). If time permits, returning minutes percentage and a binary indicator for key-player injuries are the highest-value player-derived features to add. See [Data Sources & Quality](data-sources-and-quality.md) for availability of these data.

## 6. Strength of Schedule Adjustments and Conference Effects

Strength of schedule is the single most important *adjustment* in college basketball prediction, because the quality gap between the best and worst Division I teams is enormous. But the structure of college basketball scheduling creates systematic problems that no model fully solves.

**The measurement problem.** Teams play ~30 games per season, with ~20 against conference opponents. Cross-conference data is sparse. A simulation study by Wieland (2024) quantified the damage: rating estimation error roughly doubles (MAE 5.30 to 8.18) when teams play realistic conference-heavy schedules vs. random schedules. Those ~10 non-conference games are disproportionately important for calibrating the entire rating landscape.

**The circular amplification problem.** Power conference teams inflate each other's metrics in a self-reinforcing loop. When one team wins, it gets a "quality win" and the loser gets a "good loss." The Quad system exacerbates this: high-major conference games are Quad 1 results ~48% of the time vs. ~6% for mid/low-majors. A 25-win mid-major may have zero Quad 1 opportunities.

**Empirical evidence of bias.** Academic research (Coleman, Lynch, and DuMond) documents that power conference teams are seeded approximately 2 lines higher than performance metrics predict. Meanwhile, 11 and 12 seeds (predominantly mid-majors) win first-round games at rates of 37.1% and 34.6% respectively -- exceeding seed-line expectations. The Missouri Valley Conference overperforms its seed predictions by ~12%.

**How the major systems handle SOS:**

- *KenPom:* Iterative least-squares regression across all 353 teams simultaneously, adjusting for opponent quality and game location. Tracks non-conference SOS separately.
- *Torvik:* Similar iterative approach with a multiplicative Pythagorean formula. Blowout discounting prevents schedule inflation.
- *COOPER:* Conference-aware Elo reversion -- at season start, ratings revert toward the conference mean, embedding a conference strength prior. Cross-conference games receive a 1.75x K-factor boost.
- *BPI:* SOS simulated 10,000 times from the perspective of a borderline top-25 team.

**Implications for our model:** We should use pre-adjusted metrics (KenPom AdjOE/AdjDE) rather than attempting our own SOS adjustment, since the iterative regression across 353 teams is well-established and difficult to improve upon. However, we should be aware that mid-major teams are likely undervalued by these systems and consider a conference-type indicator or a "mid-major overperformance" adjustment. See [Evaluation & Calibration](evaluation-and-calibration.md) for how to assess whether our model reproduces known biases.

## 7. Feature Selection -- Aggressive Reduction Works

One of the most consistent findings across the literature is that large feature sets can be aggressively pruned with minimal accuracy loss.

| Study | Original Features | Selected Features | Method | Accuracy Loss |
|-------|------------------|-------------------|--------|---------------|
| arXiv 2025 (Math Modeling) | 16 | 4 | Coefficient thresholding (0.45) | <1 pp (75.4% to 74.6%) |
| arXiv 2026 (CFA) | 44 | 26 | RFECV, 5-fold CV, log loss | Not reported (optimized) |
| Kumar et al. | 25 basic stats | 25 (but all basic) | Deliberate exclusion of derived stats | 84.1% (strong) |

The 2025 paper's result is especially telling: dropping from 16 features to just 4 (AdjOE, AdjDE, BARTHAG, and two-point shooting percentage allowed) cost less than 1 percentage point. The reason is clear -- offensive and defensive efficiency dominate, and most other features are either components of efficiency or weakly correlated with outcomes.

**Effective feature selection methods:**

- Coefficient magnitude thresholding in regularized logistic regression.
- Recursive Feature Elimination with Cross-Validation (RFECV).
- Random forest feature importance.

**Important guideline: avoid multicollinearity.** Use raw box score stats *or* derived advanced stats, not both. Kumar et al. deliberately excluded advanced statistics because they are "derived from the others with respect to time or other stats." Mixing raw and derived features creates redundancy that inflates variance without improving prediction.

## 8. Rating Systems as Meta-Features

Rather than engineering features from raw box scores, a powerful approach is to use the outputs of established rating systems directly as model inputs. These systems have already performed sophisticated opponent adjustments, tempo normalization, and iterative calibration -- effectively doing the hardest part of feature engineering for you.

**The evidence for ensembling across systems is strong.** FiveThirtyEight blended six independent rating systems (KenPom, Sagarin, Sonny Moore, LRMC, BPI, and their own Elo), finding that "each system has different features and bugs" and that blending smooths irregularities. The Odds Gods model used six external ranking systems (KenPom, Massey, NET, Moore, Whitlock, Bihl) as pairwise differences fed into LightGBM, achieving 77.6% tournament accuracy.

**Key systems to consider as meta-features:**

| System | What It Captures | Access | Cost |
|--------|-----------------|--------|------|
| KenPom AdjEM/AdjOE/AdjDE | Efficiency, opponent-adjusted | kenpom.com | $24.95/yr |
| Torvik Barthag/AdjOE/AdjDE | Efficiency with recency weighting | barttorvik.com | Free |
| Massey Composite | Ensemble of dozens of systems | masseyratings.com | Free |
| NET | Selection committee's official tool | ncaa.com | Free |
| EvanMiya BPR | Player-level Bayesian ratings | evanmiya.com | Partial paywall |

COOPER blends its own Elo (5/8 weight) with KenPom (3/8 weight), reflecting the principle that combining independent signals improves prediction. The Massey Composite -- which simply averages dozens of rating systems -- has historically been one of the best-performing "systems" precisely because of ensemble effects.

**Practical consideration:** When using multiple rating systems as features, their outputs are correlated (all measure team quality). This is fine for tree-based models (gradient boosting, random forests) which handle correlated features well, but logistic regression will suffer from multicollinearity. For linear models, pick one or two systems and use their components rather than stacking many systems. See [Modeling Approaches](modeling-approaches.md) for how model choice interacts with feature selection.

## 9. Recommended Feature Set for This Project

Based on the literature synthesis, we recommend a tiered approach that balances predictive power against complexity and data availability.

**Minimal viable feature set (4 features, expected accuracy ~74--75%):**

1. AdjOE difference (Team A - Team B), from KenPom or Torvik
2. AdjDE difference
3. Power rating difference (Barthag or AdjEM)
4. Seed difference

This captures the vast majority of signal. It is easy to collect, avoids multicollinearity, and the difference formulation ensures proper symmetry.

**Recommended feature set (8--12 features, expected accuracy ~76--78%):**

All of the above, plus:
5. Strength of schedule difference (KenPom SOS or equivalent)
6. eFG% difference (offensive)
7. Turnover rate difference
8. Offensive rebounding rate difference
9. A second rating system (e.g., Torvik Barthag if using KenPom AdjEM, or vice versa) -- adds ensemble diversity
10. Location indicator (-1, 0, +1 or distance-based)
11. Returning minutes percentage difference (if available)
12. Recent form indicator (e.g., 5-game scoring margin differential or Elo trend)

**Features to deliberately exclude:**

- Adjusted tempo (not predictive of outcomes)
- Non-conference SOS (weak predictor)
- Three-point shooting percentage (too volatile for tournament prediction)
- Raw counting stats if adjusted per-possession stats are included
- Factor-by-factor matchup features (add <1 pt/100 poss beyond aggregate efficiency)

**Feature transformations to test:**

- Rank-based encoding (ranks may outperform raw values per the CFA paper)
- Log or polynomial transforms of efficiency margins (relationships are non-linear)
- Interaction between eFG% and TOV% (turnovers cost more for efficient shooting teams)

For guidance on how to evaluate whether this feature set is well-calibrated and how to measure accuracy, see [Evaluation & Calibration](evaluation-and-calibration.md). For our overall approach to combining these features with a modeling strategy, see [Recommended Approach](recommended-approach.md).
