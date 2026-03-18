# Betting Markets, Vegas Odds, and Market-Based Predictions for March Madness

## Summary

Betting markets for the NCAA tournament are remarkably efficient. Academic research spanning decades finds that point spreads and moneylines generally reflect true game probabilities, with the closing line considered the single most accurate predictor of outcomes. However, specific exploitable biases have been identified: big underdogs (20+ point spreads) cover more than expected, ACC teams historically underperform against the spread in opening rounds, and college basketball exhibits the strongest longshot bias of any major sport. Statistical models like FiveThirtyEight's ELO-based system and the LRMC model can occasionally find edges over Vegas, particularly in early-round games where the model strongly disagrees with the line, but consistently beating the closing line remains extremely difficult. The most promising approach may be combining market data with statistical models rather than treating them as competitors. Prediction markets (Kalshi, Polymarket) are emerging as alternatives to traditional sportsbooks, with tighter spreads due to transparent fee structures, though their accuracy relative to traditional books has not been rigorously compared. For bracket pools specifically, using Vegas odds as a baseline and then selectively deviating based on model insights appears to be the dominant strategy.

---

## Source 1: "Efficiency in the Madness? Examining the Betting Market for the NCAA Men's Basketball Tournament"

- **Author:** Daniel C. Hickman (University of Idaho)
- **Published:** Journal of Economics and Finance, Vol. 44(3), July 2020, pp. 611-626
- **URL:** https://ideas.repec.org/a/spr/jecfin/v44y2020i3d10.1007_s12197-020-09507-7.html

### How They Used Market Data
Examined NCAA tournament betting market data from 1996 to 2019, testing for systematic inefficiencies and behavioral biases related to team seeding and conference affiliation.

### Key Findings
- The market operates at an efficient level overall, with very little detectable bias based on seeding.
- The most significant anomaly: ACC teams tend to cover the spread less than expected, particularly in opening round games. This is a conference-specific bias that could theoretically be exploited.
- No profitable systematic betting strategy based on seeds alone was identified.

### Market vs. Model Accuracy
The paper focuses on market efficiency rather than model comparison. The conclusion supports the efficient market hypothesis for tournament betting: the spread is generally an unbiased predictor of game outcomes.

### Insights
This is the most rigorous academic study specifically focused on the NCAA tournament betting market. The ACC bias finding is interesting because it suggests public perception of "brand name" conferences may inflate lines beyond what performance warrants.

---

## Source 2: FiveThirtyEight's NCAA Tournament Forecast Performance

- **Source:** FiveThirtyEight
- **URL:** https://fivethirtyeight.com/features/how-fivethirtyeights-ncaa-tournament-forecasts-did/

### How They Used Market Data
FiveThirtyEight converted their win probability predictions into implied point spreads using the formula `-qnorm(win_prob, mean = 0, SD = 10.36)` and then compared these against actual Vegas closing lines. They placed hypothetical bets whenever their implied line differed from Vegas.

### Key Findings
- Overall hypothetical betting record: 26-31 (with 10 no-bets) across the men's tournament.
- In the Round of 64: 17-13 record, which they called "strong."
- When the model had a large perceived edge (3+ points different from Vegas): 5-2 record in early rounds.
- In later rounds: 6-15 record, performing poorly. The model tracked Vegas very closely in later rounds, suggesting the market gets more efficient as the tournament progresses.
- Pre-tournament predictions correctly picked 70% of men's game winners.

### Market vs. Model Accuracy
FiveThirtyEight explicitly treats Vegas as the gold standard benchmark. Their model could find edges in early rounds when it strongly disagreed with the market, but could not beat Vegas in later rounds. They used Brier scores for probabilistic evaluation and ranked third among six prediction systems (behind The Power Rank and numberFire).

### Insights
The round-by-round breakdown is revealing: models may have an edge over markets in early rounds where there are many games and the market may not have thoroughly priced all matchups, but as the tournament narrows, market efficiency increases. The 3+ point edge threshold as a filter for high-confidence bets is a practical takeaway for anyone trying to use models against the market.

---

## Source 3: "Weak Form Efficiency in Sports Betting Markets" (NCAA Basketball Component)

- **Source:** Academic paper examining multiple sports betting markets
- **URL:** https://myweb.ecu.edu/robbinst/PDFs/Weak%20Form%20Efficiency%20in%20Sports%20Betting%20Markets.pdf

### How They Used Market Data
Examined point spread data across multiple sports (NFL, NBA, NCAA basketball, NCAA football, MLB, NHL) to test for weak-form market efficiency, specifically looking at whether past betting outcomes can predict future profitability.

### Key Findings
- Overall, NCAA basketball betting markets are generally efficient, and no odds-based betting strategy yields statistically significant long-term profits.
- For big favorites (20+ point spreads), a simple strategy of betting the underdog rejects the null hypothesis of a fair bet -- underdogs cover more than the efficient market would imply.
- College basketball exhibits the most significant longshot bias of any sport examined, with the biggest longshot bin showing a negative return of nearly 50%.
- Home-team bias in college basketball is opposite to other sports: big home favorites win and cover more often than implied by market efficiency.

### Market vs. Model Accuracy
The paper does not test specific predictive models but establishes the baseline efficiency of the market. The identified biases (big underdog value, longshot bias) represent the few areas where systematic strategies could theoretically generate returns.

### Insights
The longshot bias finding is particularly relevant for March Madness bracket construction: the market systematically overprices large underdogs on the moneyline (longshots), but underprices them against the spread when the spread is very large. This asymmetry matters depending on whether you are betting individual games or building brackets. For bracket pools, picking a few upsets has strategic value; for betting, fading heavy favorites against the spread has historical support.

---

## Source 4: Prediction Markets for March Madness (Kalshi, Polymarket, et al.)

- **Source:** Front Office Sports
- **URL:** https://frontofficesports.com/prediction-markets-leverage-march-madness-despite-ncaa-opposition/

### How They Used Market Data
Reports on the emergence of prediction market platforms (Kalshi, Polymarket, Robinhood, Coinbase, DraftKings) offering contracts on NCAA tournament outcomes, including outright winners, point spreads, totals, and alternative lines.

### Key Findings
- Kalshi generated $2.27 billion in men's college basketball trading volume in February 2026 alone, exceeding NFL ($1.8B) and NBA ($1.74B) volumes.
- Traditional sportsbooks projected $3.3 billion in legal March Madness wagers for 2026.
- Prediction markets charge transparent transaction fees rather than baking margins into prices, resulting in tighter spreads that may more accurately reflect true probabilities.
- Example: a contract at 50 cents on Kalshi returns $100 profit on a $100 contract if correct, versus $91 at -110 vig on a traditional sportsbook.
- The NCAA opposes prediction markets and has taken action against platforms using NCAA trademarks.
- Platforms work around trademark restrictions: Kalshi uses "March matchups," Robinhood uses "March tournament," DraftKings uses "CBB Tournament."

### Market vs. Model Accuracy
No direct comparison of prediction market accuracy vs. traditional sportsbook accuracy is provided. The theoretical argument is that prediction markets with lower vig and more transparent pricing should produce more accurate implied probabilities, but this has not been rigorously tested for NCAA tournament outcomes.

### Insights
The sheer volume of money flowing through prediction markets ($2.27B on one platform in one month) suggests these markets are becoming liquid enough to be informative. The lower vig structure means implied probabilities derived from prediction market prices may be less distorted than those from traditional sportsbooks, potentially making them a better input for models. This is an emerging area worth monitoring for anyone building tournament prediction systems.

---

## Source 5: KenPom Ratings vs. Vegas Lines for Tournament Prediction

- **Sources:** Betstamp, FOX Sports, Odds Shark
- **URLs:**
  - https://betstamp.com/education/kenpom-march-madness-betting-guide
  - https://www.foxsports.com/stories/college-basketball/kenpom-trends-march-madness-bracket
  - https://www.oddsshark.com/ncaab/what-are-kenpom-ratings

### How They Used Market Data
Compared KenPom's efficiency ratings (adjusted offensive and defensive efficiency) directly against Vegas point spreads to identify where the two systems disagree and which performs better in different contexts.

### Key Findings
- In games where the Vegas spread is 7 points or fewer, KenPom picks the correct winner 60.5% of the time.
- In games with spreads of 3 points or fewer, KenPom accuracy drops to 52.7%, barely above coin-flip.
- When KenPom and Vegas disagree on the spread by 2+ points, betting the underdog may be profitable, as disagreements are often attributable to injuries that KenPom cannot account for.
- 23 of the last 24 national champions ranked in the top 21 of KenPom's adjusted offensive efficiency.
- All 24 national champions ranked in the top 25 of adjusted efficiency margin.
- Nate Silver's model weights KenPom at 3/8ths alongside his proprietary COOPER ratings at 5/8ths, suggesting KenPom is a strong but not sufficient signal.

### Market vs. Model Accuracy
Vegas lines appear to have a slight edge in close games (spreads under 3 points), likely because they incorporate real-time information like injuries, travel, and lineup changes that KenPom's season-long efficiency metrics miss. KenPom excels at identifying championship-caliber teams and is better for longer-term structural predictions (who can win 6 games in a row).

### Insights
The complementarity of KenPom and Vegas lines is the key takeaway. KenPom provides a strong structural baseline (efficiency ratings), while Vegas incorporates situational information. A model that blends both -- using KenPom for team quality assessment and Vegas lines as a reality check incorporating injury/situational information -- should outperform either alone. The 2+ point disagreement signal as a potential edge is a concrete, actionable finding.

---

## Source 6: theScore -- How Betting Odds Can Help Build Winning Brackets

- **Source:** theScore
- **URL:** https://www.thescore.com/ncaab/news/3501354/amp

### How They Used Market Data
Used championship winner odds, region winner odds, Sweet 16 advancement odds, and first-round point spreads to construct tournament brackets optimized for pool competition.

### Key Findings
- Betting odds are described as "the most accurate resource" available because millions of dollars in sharp money create efficient lines that project outcomes more accurately than any other single resource.
- The strategic insight is that the goal is not a perfect bracket but a bracket that beats your pool competitors. This means selectively picking less popular but still plausible outcomes.
- Using spread data to identify undervalued teams (those the market likes but the public ignores) provides leverage in pools.
- Avoiding extreme longshot upsets is recommended: they burn you far more frequently than they pay off.

### Market vs. Model Accuracy
No formal comparison, but the article positions market-derived probabilities as the best available starting point, better than any individual model or expert opinion.

### Insights
This source is more practical than academic, but the framing is important: market odds are the Schelling point for prediction, and the goal of any model should be to find places where you have reason to believe the market is wrong, not to replace the market entirely. The pool strategy angle (leverage over competitors) adds a game-theoretic dimension beyond pure prediction accuracy.

---

## Source 7: Odds Gods -- Predicting College Basketball: A Complete Technical Methodology

- **Source:** Odds Gods Blog
- **URL:** https://blog.oddsgods.net/predicting-college-basketball-methodology

### How They Used Market Data
Built a LightGBM gradient-boosted decision tree classifier trained on 50,000 games from 2014-2026, incorporating six ranking systems (KenPom, Massey, NET, Moore, Whitlock, Bihl), custom Elo ratings, efficiency metrics, recent form, and game context.

### Key Findings
- 2025 test set: 77.61% NCAA tournament accuracy, Brier score 0.183, log loss 0.54.
- 2024 validation set: 71.64% tournament accuracy, Brier score 0.187, log loss 0.551.
- The model lags approximately 2% behind Evan Miya's publicly available model.
- The model does NOT incorporate or validate against Vegas lines.

### Market vs. Model Accuracy
No comparison to betting markets was performed. This is a notable gap: a model achieving 77.61% tournament accuracy sounds strong, but without a comparison to the closing line's implied win rate, it is difficult to assess whether this represents an edge over the market.

### Insights
This source illustrates a common pattern in the March Madness prediction space: sophisticated models are built and evaluated on accuracy metrics (Brier score, log loss) but are not benchmarked against the market. This makes it impossible to know whether the model provides any betting value. For our purposes, the methodology is sound but the lack of market comparison is a limitation. A natural next step would be to compare these Brier scores against those achievable by simply using closing line implied probabilities.

---

## Cross-Cutting Themes

### 1. The Market is Hard to Beat
Every academic study concludes that NCAA tournament betting markets are broadly efficient. The closing line is the toughest benchmark. Models that show promise in early rounds often fail in later rounds where market efficiency is highest.

### 2. Specific Biases Exist
Despite overall efficiency, systematic biases have been identified:
- Big underdogs (20+ point spreads) cover more than expected
- ACC teams underperform against opening-round spreads
- College basketball has the strongest longshot bias of any major sport
- Home favorites cover more than expected (opposite of other sports)

### 3. Models and Markets Are Complementary
The most promising approach is not models OR markets, but models AND markets. Vegas lines incorporate real-time situational information (injuries, travel, motivation) that models miss, while models can identify structural edges (efficiency mismatches, pace differentials) that the market underweights.

### 4. Early Rounds Offer More Edge Than Late Rounds
Both FiveThirtyEight's analysis and general market theory suggest that early-round games, where there are many simultaneous matchups and less public attention per game, offer more opportunity for model-based edges than later rounds.

### 5. Prediction Markets Are a Growing Data Source
With $2.27 billion in monthly volume on Kalshi alone, prediction markets are becoming liquid enough to serve as a high-quality probability signal. Their lower vig structure may produce less distorted implied probabilities than traditional sportsbooks.

### 6. Evaluation Must Include Market Benchmarks
Many published models report accuracy and Brier scores without comparing to the closing line. Without this benchmark, it is impossible to assess whether a model adds value beyond what the market already knows. Any serious prediction effort should include closing-line comparison as a standard evaluation metric.
