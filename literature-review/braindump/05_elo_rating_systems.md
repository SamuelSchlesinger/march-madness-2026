# Elo Ratings, Power Ratings, and Team Ranking Systems for March Madness Prediction

## Summary

Rating and ranking systems are the backbone of quantitative March Madness prediction. The landscape includes pure Elo systems (FiveThirtyEight, COOPER), efficiency-based systems (KenPom, BPI, T-Rank), hybrid approaches (Sagarin), result-based selection tools (NET), and least-squares methods (Massey). Most serious forecasting efforts blend multiple systems rather than relying on any single one.

Key themes across all systems:

- **Margin of victory matters** but must be handled carefully. Most systems cap or dampen blowout margins to avoid overweighting garbage time.
- **Home court advantage** is consistently worth roughly 3-4 points, though some systems (COOPER, BPI) model it per-venue or incorporate travel distance.
- **Schedule strength** is the single most important adjustment in college basketball, where the quality gap between top and bottom teams is enormous compared to pro sports.
- **Preseason priors** remain predictive deep into the season because 30-35 games is a small sample; systems that ignore preseason information tend to underperform.
- **No system accounts well for injuries, suspensions, or motivation**, creating persistent blind spots.
- **Accuracy ceiling** for game-level predictions appears to be around 73-75% straight-up, with most well-designed systems clustering in the 71-74% range.

---

## 1. FiveThirtyEight Elo Ratings (and Composite Model)

**Source:** [How Our March Madness Predictions Work](https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/)

### Rating Methodology

FiveThirtyEight calculated Elo ratings for men's college basketball teams dating back to the 1950s, using game-by-game results incorporating final score and game location. Their March Madness forecast was a composite model blending six computer power ratings:

1. Ken Pomeroy's ratings
2. Jeff Sagarin's "predictor" ratings
3. Sonny Moore's ratings
4. Joel Sokol's LRMC ratings
5. ESPN's Basketball Power Index (BPI)
6. FiveThirtyEight's own Elo ratings

The rationale: "each system has different features and bugs" and blending smooths irregularities that matter in single-elimination tournaments.

### Weighting

- **75% computer ratings** (the six systems above)
- **25% human rankings** (NCAA S-curve, AP poll, coaches' poll)
- Preseason rankings are incorporated because talent estimates help when regular season data is limited (only 30-35 games)

### Margin of Victory

Incorporated into the Elo update formula but exact formula not publicly disclosed. Tournament games are weighted slightly higher than regular-season games because historically there are fewer upsets in the tournament than expected from Elo differentials alone.

### Home Court & Travel

- Home court advantage is factored into all rating updates
- College teams "perform significantly worse when they travel a long distance" -- travel distance was an explicit adjustment (removed for the bubble-format 2021 tournament)
- Season-to-season reversion is done to the mean of the team's conference, not the overall mean, which is a distinctive feature

### Win Probability Formula

Win probability = `1.0 / (1.0 + 10^(-travel_adjusted_rating_diff * 30.464 / 400))`

### Injury Adjustments

Based on Sports-Reference win shares, estimating each player's contribution to team record while adjusting for strength of schedule.

### Known Biases / Limitations

- Pure Elo is one of the weaker individual components; its value comes from ensemble diversity
- The 25% human component can introduce biases from name recognition and recency
- No accounting for mid-season coaching changes or scheme adjustments
- FiveThirtyEight is now defunct as a standalone operation; Nate Silver's COOPER system is the spiritual successor

---

## 2. COOPER (Nate Silver / Silver Bulletin)

**Source:** [Introducing COOPER: Silver Bulletin's NCAA basketball rating system](https://www.natesilver.net/p/introducing-cooper-silver-bulletins)

### Rating Methodology

COOPER is an Elo-based system producing three metrics:
- **PPPG** (projected points per game)
- **PPAG** (projected points allowed per game)
- **Elo rating** reflecting win probability

### Margin of Victory

Treated linearly without diminishing returns for large margins. Silver's reasoning: teams reduce effort with commanding leads, so final scores may actually *underestimate* quality gaps. The conversion rate is approximately one point in a basketball game = 28.5 Elo points for men's basketball. Winning itself carries additional meaning: "winning a game by any margin is essentially equivalent to 6 points of scoring margin" adjusted against the model's prior expectations.

### K-Factor

- Base K = 55 for standard play
- Escalates up to 2x (K = 110) for early-season games, as early contests reveal more information about team quality
- Games between closely matched teams and high-stakes contests (conference play, NCAA tournament) receive higher weighting via an "impact factor"

### Home Court & Travel

- Individualized home court advantage ratings derived from historical performance at each venue
- Travel distance effect follows the formula: `5 * m^(1/3)` where m = distance in miles (cube root relationship, so marginal effect diminishes with distance)

### Preseason Priors

A "Bayesian" version incorporates AP and Coaches' Poll rankings. Teams expected to be ranked but absent from polls receive downward adjustments, signaling talent departure.

### Pace Adjustment

Rolling pace factor reflecting combined points scored, with separate offensive and defensive ratings derived from pace-adjusted data.

### Track Record

Claims approximately 1% improvement in game prediction accuracy over his prior SBCB system, which Silver notes is material in betting contexts.

### Known Biases / Limitations

- Linear margin of victory treatment is controversial; garbage-time points in blowouts may add noise
- Preseason poll priors can embed media/brand biases
- System is relatively new (introduced ~2024-25) so limited track record

---

## 3. KenPom (Ken Pomeroy Ratings)

**Sources:**
- [Ratings Explanation (kenpom.com)](https://kenpom.com/blog/ratings-explanation/)
- [Pomeroy Ratings FAQ (kenpom.com)](https://kenpom.com/blog/pomeroy-ratings-faq/)
- [KenPom vs. Sagarin (SportsBettingDime)](https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/)
- [KenPom March Madness Guide (betstamp)](https://betstamp.com/education/kenpom-march-madness-betting-guide)

### Rating Methodology

KenPom is an efficiency-based system. The core metrics are:

- **AdjO**: Points a team scores per 100 possessions, adjusted for opponent quality
- **AdjD**: Points a team allows per 100 possessions, adjusted for opponent quality
- **AdjT**: Pace, measured in possessions per 40 minutes
- **AdjEM**: Net efficiency (AdjO minus AdjD)

The per-100-possessions normalization is critical: it removes the influence of tempo so that teams playing at different speeds can be compared fairly. The system is designed to be purely predictive -- "how strong a team would be if it played tonight, independent of injuries or emotional factors."

### Margin of Victory

Margin of victory is central to the system (it *is* an efficiency-based rating). However, KenPom caps margin of victory based on the distribution of margins in a given season, working out to approximately 16 points by the end of the year. As Pomeroy has argued, "on average, there is information in large margins of victory and additional information in even larger margins of victory," but capping prevents a single blowout from being overly influential.

### Home Court Advantage

Factored into predictions. Home court is worth approximately 3-4 points, though the exact value is adjusted.

### Strength of Schedule

Opponent adjustments are iterative -- a team's efficiency ratings are adjusted based on opponent quality, which itself is determined by those opponents' adjusted ratings, creating a system of simultaneous equations that converges to stable values.

### Track Record

- Accurately predicts approximately 73% of games in a season
- More accurate than Sagarin in predicting margin of victory (58.68% of head-to-head comparisons in tracked 2017-19 seasons)
- Widely adopted by sportsbooks as a baseline
- Many Final Four teams and champions rank highly in KenPom metrics
- "Luck" metric identifies teams that have over- or under-performed their efficiency profile, which can flag regression candidates

### Known Biases / Limitations

- Does not account for injuries or suspensions
- Does not account for emotional/motivational factors
- Complete formula is not publicly disclosed
- Early-season ratings can be unstable with small sample sizes
- Purely results-based after the season starts (no preseason priors in the main version, though a preseason version exists)

---

## 4. ESPN's Basketball Power Index (BPI)

**Sources:**
- [BPI and Strength of Record Explained (ESPN)](https://www.espn.com/blog/statsinfo/post/_/id/125994/bpi-and-strength-of-record-what-are-they-and-how-are-they-derived)
- [Explaining the New BPI (ESPN)](https://www.espn.com/mens-college-basketball/story/_/id/7561413/bpi-college-basketball-power-index-explained)

### Rating Methodology

BPI is a predictive power rating measuring team strength relative to an average D-I team on a neutral court. It represents how many points above or below average a team is. Core components are predicted offensive and defensive efficiency ratings (net points per 100 possessions).

### Preseason Model

The preseason BPI integrates four variables via Bayesian hierarchical modeling:

1. **Coach's historical performance**: Adjusted offensive/defensive ratings since 2007-08 across all coaching stops
2. **Recruiting class quality**: Average grades from four recruiting services, with extra weight for five-star recruits
3. **Returning player minutes**: Previous season playing time for returnees and transfers
4. **Returning player performance**: Opponent-adjusted offensive and defensive efficiency

Weighting varies based on roster continuity percentages, and preseason ratings maintain influence well into the season.

### Game Prediction Factors

- Team and opponent strength differential
- Game location (home/road/neutral)
- Rest differential
- Travel distance from home (cross-country vs. standard road games)
- High-altitude effects
- Crowd proximity advantage at neutral sites
- Pace of play

### Margin of Victory

Incorporated through efficiency metrics but extreme outlier performances are down-weighted.

### Injury Adjustments

BPI accounts for missing players: if a team is missing one of its most important players (determined by minutes per game), that game is weighted less heavily.

### Strength of Schedule

BPI's SOS simulates each team's schedule 10,000 times from the perspective of a borderline top-25 team (~25th ranked). Teams facing the toughest schedules generate the lowest expected winning percentage for such a hypothetical competitor.

### Track Record

Strong calibration: teams given 50-60% win probability achieved 56% actual victories; 70-80% probability teams won 74%; 90-100% favorites won 96%. The BPI favorite has won 75.6% of games since 2007-08.

### Known Biases / Limitations

- Proprietary and opaque -- exact methodology not publicly disclosed
- Heavy reliance on preseason priors (recruiting rankings, coaching history) can embed systematic biases
- Recruiting rankings may not reflect actual player development or fit

---

## 5. Bart Torvik's T-Rank

**Sources:**
- [T-Rank (barttorvik.com)](https://barttorvik.com/trank.php)
- [Torvik Ratings Guide (OddsShark)](https://www.oddsshark.com/ncaab/what-are-torvik-ratings)

### Rating Methodology

T-Rank uses the same core framework as KenPom -- adjusted offensive and defensive efficiency per 100 possessions -- but differentiates itself through recency weighting and customizability. Key metric: **Barthag**, the projected win percentage against an average team on a neutral court.

### Recency Weighting

This is T-Rank's distinguishing feature. Games older than 40 days begin losing weight, declining by 1 percentage point per day until reaching 60% weight at 80+ days old. This captures team trajectory and improvement/decline more aggressively than KenPom, which weights all games equally.

### Home Court & Schedule Strength

Similar to KenPom -- iterative opponent adjustments with location factored in.

### Customizability

Users can splice data to determine T-Rank for specific time windows, enabling questions like "who are the best teams over the last month?" This is uniquely useful for March Madness because it can capture late-season surges or slumps.

### Track Record

No formally published accuracy metrics, but T-Rank is widely regarded as comparable to KenPom in predictive accuracy. The recency bias gives it an edge when teams have undergone significant changes (injuries, player development) but can be a liability if recent results are noisy.

### Known Biases / Limitations

- Recency weighting can overreact to small samples of recent games
- Early-season ratings are volatile
- Does not account for injuries or roster changes directly

---

## 6. NCAA Evaluation Tool (NET)

**Sources:**
- [College Basketball's NET Rankings Explained (NCAA.com)](https://www.ncaa.com/news/basketball-men/article/2022-12-05/college-basketballs-net-rankings-explained)
- [How NET Rankings Work (NCAA.org)](https://www.ncaa.org/news/2025/3/3/media-center-how-do-net-rankings-work-in-ncaa-tournament-selection.aspx)

### Rating Methodology

The NET replaced the RPI system before the 2018-19 season as the NCAA's official sorting tool for tournament selection. Since May 2020, it has been reduced to two components:

1. **Team Value Index (TVI)**: Results-based, rewards quality victories, values road/neutral wins more highly
2. **Adjusted Net Efficiency**: Team's net efficiency adjusted for opponent strength and game location

### Important: NOT Primarily a Predictive System

The NET is designed for tournament *selection*, not game prediction. It answers "who deserves to be in the tournament?" not "who would win a head-to-head matchup?" This is a critical distinction.

### Margin of Victory

As of the 2020 update, scoring margin is explicitly NOT a factor in NET rankings. This was a deliberate design choice to avoid incentivizing running up scores.

### Quadrant System

The NET's primary practical use is defining "quadrant" wins and losses:
- **Q1**: Home vs. NET 1-30, Neutral vs. 1-50, Away vs. 1-75
- **Q2**: Home vs. 31-75, Neutral vs. 51-100, Away vs. 76-135
- **Q3**: Home vs. 76-160, Neutral vs. 101-200, Away vs. 136-240
- **Q4**: Everything else

### Known Biases / Limitations

- The exact algorithm uses machine learning models and is not publicly disclosed or reproducible
- Cannot be reverse-engineered from public data
- Being designed for selection rather than prediction means it systematically undervalues efficiency and overvalues raw wins
- Does not incorporate margin of victory, which is known to be predictive
- Mid-major teams with fewer Q1 opportunities are structurally disadvantaged

---

## 7. Sagarin Ratings (Historical)

**Sources:**
- [KenPom vs. Sagarin (SportsBettingDime)](https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/)
- [Dusting Off the Sagarin Ratings (247Sports)](https://247sports.com/college/texas/board/21/contents/dusting-off-the-sagarin-ratings2024--240989305/)

### Rating Methodology

Sagarin ratings were published from 1985 to 2023 (discontinued when USA Today ended its partnership). The system provided three rating variants:

- **Predictor (BLUE)**: Based on expected future scores, most useful for prediction
- **Golden Mean**: Utilized actual scores from games played
- **Recent**: Emphasized recent games more heavily
- **COMBO/Rating**: Combined the above

### Margin of Victory

Incorporated into the predictor and golden mean components. Sagarin pioneered the use of margin of victory combined with opponent strength in predictive modeling.

### Track Record

Less accurate than KenPom in head-to-head comparisons (KenPom won 58.68% of 121 tracked games in 2017-19 seasons). However, Sagarin's long historical track record (nearly four decades) and influence on subsequent analysts (Pomeroy, Torvik) is substantial.

### Known Biases / Limitations

- Now discontinued
- Proprietary methodology never fully disclosed
- Did not emphasize shooting percentage metrics
- Did not account for injuries or suspensions

---

## 8. Massey Ratings

**Source:** [Massey Ratings (masseyratings.com)](https://masseyratings.com/cb/ncaa-d1/ratings)

### Rating Methodology

Massey Ratings use a least-squares approach to simultaneously solve for team ratings that best fit observed game outcomes. The system covers virtually every sport and has been one of the longest-running computer ranking systems in college basketball.

The purpose is to "order teams based on achievement and reward success at winning the games they have played." The system can be tuned toward prediction or toward evaluating past results depending on weighting choices.

### Composite Rankings

Massey's site also hosts a composite ranking that aggregates dozens of other rating systems, providing a useful meta-ranking. This composite has historically been one of the best-performing "systems" because it benefits from ensemble effects.

### Known Biases / Limitations

- "Computer ratings are ignorant of many important factors such as injury, weather, motivation, and other intangibles"
- Exact methodology details are limited in public documentation
- The least-squares approach can be sensitive to outlier results

---

## 9. Odds Gods Custom Elo System (Technical Case Study)

**Source:** [Predicting College Basketball: A Complete Technical Methodology](https://blog.oddsgods.net/predicting-college-basketball-methodology)

This is worth noting as a well-documented open implementation showing how a custom Elo system is built in practice.

### Elo Implementation Details

- **Seasonal regression**: `New_Elo = 0.85 * Previous_Season_Elo + 0.15 * Mean_Elo` (15% regression toward mean for roster turnover)
- **Home court**: 50-point Elo adjustment based on location
- **K-factor** has three components:
  - **K_phase**: 50 (under 5 games), 40 (5-19 games), 15 (20+ games) -- high early-season volatility, stable late
  - **Quality multiplier**: Higher weight for games between elite teams
  - **Cross-conference boost**: 1.75x multiplier for inter-conference play to prevent inflated ratings from "dominating weaker competition"
- Full formula: `K = K_phase * quality_mult * cross_conference_mult`

### Additional Features

- **Elo SOS**: Expanding mean of opponent Elo ratings
- **Elo trend**: OLS slope of Elo over time (momentum)
- **Efficiency metrics**: Net rating, offensive/defensive ratings, rebounding differentials
- **Recent form**: Scoring margin differential over last 5 games

### Model Architecture

LightGBM gradient boosted decision tree classifier (1,545 trees), minimizing binary log loss. Sample weighting: regular season = 1x, late regular season / conference tournaments = 2x, NCAA tournament = 6x.

### Calibration

Isotonic regression on out-of-fold predictions to correct overconfident probability extremes.

### Track Record

- 2025 test set: 72.56% overall accuracy, 0.80 AUC, 0.183 Brier score
- NCAA Tournament specifically: 77.61% accuracy, 0.8865 AUC
- Acknowledged as lagging approximately 2% behind top public alternatives (e.g., Evan Miya's system)

---

## Cross-Cutting Observations

### Accuracy Benchmarks

| System | Approx. Game Accuracy | Notes |
|--------|----------------------|-------|
| KenPom | ~73% | ATS and straight-up |
| BPI | ~75.6% (favorite wins) | Since 2007-08 |
| COOPER | ~1% better than prior SBCB | Limited track record |
| Odds Gods Elo | 72.56% overall, 77.61% tournament | 2025 test set |
| Sagarin | Lower than KenPom | Based on 2017-19 comparison |
| Vegas lines | ~73-74% | The benchmark to beat |

### What Matters Most for March Madness Specifically

1. **Ensemble methods dominate**: FiveThirtyEight's blend of 6+ systems, Massey composite, and similar approaches consistently outperform any single system.
2. **Tournament-specific adjustments help**: Higher stakes may reduce variance; travel/neutral court effects differ from regular season.
3. **Seed-line information is undervalued by pure computer models**: The selection committee implicitly encodes information (injuries, eye test) that computer models miss.
4. **Late-season form has mixed value**: T-Rank's recency weighting is theoretically appealing for March but can overfit to small samples.
5. **Mid-major evaluation is the hardest problem**: All systems struggle with limited cross-conference data for mid-major teams, making 5-vs-12 and 6-vs-11 matchups the highest-variance predictions.

### Persistent Blind Spots Across All Systems

- Injuries and suspensions (only BPI attempts to handle this)
- Coaching adjustments and tactical matchups
- Player motivation and pressure situations
- First-time tournament experience effects
- Referee assignment effects
- Teams that are significantly better or worse than their rating due to lineup changes mid-season

---

## Sources

- [How Our March Madness Predictions Work (FiveThirtyEight)](https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/)
- [Introducing COOPER (Nate Silver / Silver Bulletin)](https://www.natesilver.net/p/introducing-cooper-silver-bulletins)
- [Ratings Explanation (KenPom)](https://kenpom.com/blog/ratings-explanation/)
- [Pomeroy Ratings FAQ (KenPom)](https://kenpom.com/blog/pomeroy-ratings-faq/)
- [BPI and Strength of Record Explained (ESPN)](https://www.espn.com/blog/statsinfo/post/_/id/125994/bpi-and-strength-of-record-what-are-they-and-how-are-they-derived)
- [Explaining the New BPI (ESPN)](https://www.espn.com/mens-college-basketball/story/_/id/7561413/bpi-college-basketball-power-index-explained)
- [T-Rank (Bart Torvik)](https://barttorvik.com/trank.php)
- [KenPom vs. Sagarin (SportsBettingDime)](https://www.sportsbettingdime.com/guides/strategy/kenpom-vs-sagarin/)
- [College Basketball's NET Rankings Explained (NCAA.com)](https://www.ncaa.com/news/basketball-men/article/2022-12-05/college-basketballs-net-rankings-explained)
- [How NET Rankings Work (NCAA.org)](https://www.ncaa.org/news/2025/3/3/media-center-how-do-net-rankings-work-in-ncaa-tournament-selection.aspx)
- [Massey Ratings](https://masseyratings.com/cb/ncaa-d1/ratings)
- [Massey Ratings FAQ](https://masseyratings.com/faq.php)
- [Predicting College Basketball: Complete Technical Methodology (Odds Gods)](https://blog.oddsgods.net/predicting-college-basketball-methodology)
- [NCAA Tournament Metrics Overview (JV's Basketball Blog)](https://hoops.jacobvarner.com/2020/02/21/an-overview-of-kenpom-net-and-other-official-metrics-used-by-the-ncaa-tournament-selection-committee-in-2020.html)
