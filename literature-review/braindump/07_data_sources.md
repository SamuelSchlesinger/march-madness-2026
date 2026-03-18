# NCAA Basketball Data Sources, Quality, and Pipelines

## Summary

This document catalogs the major data sources available for NCAA Division I men's basketball analytics, with a focus on building prediction models for March Madness. The landscape breaks down roughly as follows:

- **Best all-around advanced metrics**: KenPom (paid, ~$25/yr) and Bart Torvik (free). Both offer adjusted efficiency metrics, tempo-free stats, and historical data back to ~2008. Torvik is the better value proposition for researchers; KenPom is the gold standard for coaching staff and serious bettors.
- **Best historical box-score data**: Sports Reference (sports-reference.com/cbb), with men's data back to ~1947 for basic stats and ~1999 for detailed player stats. Rate-limited and scraping-hostile, but extremely comprehensive.
- **Best ready-to-use ML datasets**: Kaggle's March Machine Learning Mania competition, which ships ~35 CSVs covering teams, seeds, game results, detailed stats, and Massey ordinals. Free, clean, and purpose-built for prediction.
- **Best play-by-play data**: The R ecosystem (hoopR, gamezoneR, bigballR, ncaahoopR) provides free access to ESPN and STATS LLC play-by-play data. gamezoneR is notable for shot location data (170K+ charted shots per season).
- **Best composite rankings**: Massey Ratings aggregates 100+ computer ranking systems and provides CSV exports.
- **Best programmatic access**: The cbbdata R package (by Andrew Weatherman) wraps Torvik, KenPom, and NET data into a single API that updates every 15 minutes during the season.

**Key takeaway for our pipeline**: A practical data pipeline should likely combine Kaggle competition data as a baseline (clean, structured, historical), augmented with Torvik/KenPom for advanced metrics, and optionally play-by-play data from hoopR/gamezoneR for feature engineering. Avoid building scrapers for Sports Reference unless absolutely necessary -- their rate limits and ToS make it fragile.

---

## Detailed Source Profiles

### 1. KenPom (kenpom.com)

- **URL**: https://kenpom.com
- **What's available**: Adjusted offensive/defensive efficiency, adjusted tempo, strength of schedule, luck factor, player-level advanced stats (usage %, rebound %, block %, steal %), team four-factors breakdowns, game predictions. Widely considered the gold standard for tempo-free college basketball analytics.
- **Historical depth**: Data available back to approximately 2002. The kenpompy Python scraper can access data back to 2010.
- **Format**: Web tables. No official CSV export. Data accessible via:
  - **kenpompy** (Python scraper): https://github.com/j-andrews7/kenpompy -- requires paid subscription
  - **cbbdata** (R package): https://cbbdata.aweatherman.com -- requires KenPom subscription with matching email
  - **Official API**: https://kenpom.com/register-api.php -- separate API subscription available
- **Cost**: $24.95/year for web subscription. API access is an additional cost. Free tier shows only the main rankings page (overall ratings table) with no drill-down.
- **Update frequency**: Updated after every game during the season.
- **Known quality issues**: Data is proprietary and derived from Ken Pomeroy's model, so it represents one analyst's methodology rather than raw stats. The free tier is essentially useless for research. Scraping the site violates ToS if done without a subscription.
- **How researchers use it**: The most commonly cited advanced metric source in March Madness prediction literature. Adjusted efficiency margin is a strong single-feature predictor of tournament outcomes. Used as features in ML models, as validation benchmarks, and for seeding analysis.

### 2. Bart Torvik / T-Rank (barttorvik.com)

- **URL**: https://barttorvik.com
- **What's available**: T-Rank ratings (adjusted offensive/defensive efficiency, adjusted tempo), BARTHAG (win probability metric), player-level stats including the "PRPG!" metric (Points Over Replacement Per Adjusted Game At That Usage), game predictions, play-by-play shooting splits, conference analysis, T-Ranketology (bracket projections). Users can filter by custom date ranges, which is a unique and powerful feature.
- **Historical depth**: Player game-level data back to 2008 season (~70,000 D1 games). Team-level data extends further back.
- **Format**: Web tables with some CSV export capability. Programmatic access via:
  - **toRvik** (R package): https://github.com/andreweatherman/toRvik -- 20+ functions, no subscription required
  - **cbbdata** (R package): Wraps Torvik data alongside KenPom and NET
- **Cost**: Completely free. No paywall, no subscription required.
- **Update frequency**: Updated daily during the season.
- **Known quality issues**: Created and maintained by one person (a lawyer by profession). Less established than KenPom, though the methodology is well-documented. The site uses Cloudflare protection that can block automated scraping.
- **How researchers use it**: Increasingly popular as a free alternative to KenPom. The date-range filtering is particularly useful for analyzing "hot" vs "cold" team stretches heading into March. The toRvik R package makes it the most accessible advanced metrics source for programmatic use.

### 3. Sports Reference College Basketball (sports-reference.com/cbb)

- **URL**: https://www.sports-reference.com/cbb/
- **What's available**: Comprehensive box scores, team stats, player stats, schedules, results, conference standings, coaching records (3,000+ coaches), award histories. Both men's and women's basketball.
- **Historical depth**:
  - Men's basic stats (points, FG, FT, PF): back to **1947-48**
  - Men's detailed player stats: back to **1998-99**
  - Schedules and results: back to **1979-80**
  - Women's player/team stats: back to **1987-88**
  - Women's schedules: back to **2002-03**
- **Format**: HTML tables (designed for browser consumption). Programmatic access via:
  - **sportsipy** (Python): https://sportsreference.readthedocs.io -- scrapes Sports Reference pages
  - **Stathead** (official paid tool): https://stathead.com -- allows complex queries, season/career finders
- **Cost**: Free for browsing. Stathead subscription required for advanced queries.
- **Update frequency**: Updated regularly during season.
- **Known quality issues**:
  - **Aggressive anti-scraping policies**: Rate limited to 20 requests/minute (10/min for FBref/Stathead). Exceeding limits results in IP bans lasting up to a day.
  - **ToS explicitly prohibits** automated scraping, bots, and using data to train AI models.
  - Data is excellent quality but access friction is high for programmatic use.
- **How researchers use it**: Primary source for historical context and long-run trend analysis. Often used manually rather than programmatically due to scraping restrictions. The sportsipy package exists but must be used carefully to avoid bans.

### 4. Kaggle March Machine Learning Mania

- **URL**: https://www.kaggle.com/competitions/march-machine-learning-mania-2026
- **What's available**: ~35 CSV files including:
  - Team identifiers and metadata
  - Tournament seeds (historical)
  - Regular season game results (compact and detailed)
  - Tournament game results (compact and detailed)
  - Detailed box score statistics
  - Conference affiliations
  - Geographic data (game cities, distances)
  - Massey ordinals (composite computer rankings from 100+ systems)
  - Coach data
  - Both men's (TeamIDs 1000-1999) and women's (TeamIDs 3000-3999) data
- **Historical depth**: Regular season and tournament data back to approximately **2003** for detailed stats; basic results go further back. The Massey ordinals alone provide a rich feature set.
- **Format**: Clean CSV files, well-documented, ready for pandas/R ingestion. Competition runs annually.
- **Cost**: Completely free. Requires a Kaggle account.
- **Update frequency**: Dataset released/updated annually for each year's competition (typically in February/March). Historical data is cumulative.
- **Known quality issues**: Data is curated and generally clean. Some known issues with early years having less complete detailed stats. The submission format requires predicting probabilities for all possible matchups, which is pedagogically useful.
- **How researchers use it**: The single most popular entry point for March Madness prediction projects. Thousands of public notebooks demonstrate approaches ranging from logistic regression to deep learning. The competition's log-loss scoring metric encourages well-calibrated probability estimates rather than just picking winners.

### 5. NCAA Official Stats Portal (stats.ncaa.org)

- **URL**: https://stats.ncaa.org
- **What's available**: Official NCAA statistics for all divisions and sports. For basketball: team and individual stats, play-by-play data, game results, leader boards.
- **Historical depth**: Varies. Play-by-play data available for recent seasons. Historical team stats go back many years.
- **Format**: Dynamically-loaded web pages (JavaScript-rendered). No official API or CSV export.
- **Cost**: Free.
- **Update frequency**: Updated during the season by official scorekeepers.
- **Known quality issues**:
  - **Scraping is technically difficult**: The site uses dynamic content loading, so traditional HTTP-based scrapers (e.g., BeautifulSoup, rvest) fail. Requires headless browser tools like chromote or Selenium.
  - **Data entry errors**: Play-by-play data is entered by human game trackers. Known issues include events attributed to players who were not on the court, unclean substitution records, and occasional scoring discrepancies.
  - **The bigballR package** specifically warns about these tracker errors.
  - The site's interface is clunky and not researcher-friendly.
- **Programmatic access**:
  - **bigballR** (R): https://github.com/jflancer/bigballR -- wraps stats.ncaa.org for schedules, rosters, and play-by-play
  - **NCAAStatScraper** (Python): https://github.com/ryansloan/NCAAStatScraper -- extracts stats into CSVs
  - **ncaa-api** (free API): https://github.com/henrygd/ncaa-api -- pulls from ncaa.com for scores, stats, standings, schedules
- **How researchers use it**: Primarily used as a source for official play-by-play data when other sources are unavailable. The bigballR package can calculate lineup data and on/off stats from the PBP data, which is valuable for advanced analysis.

### 6. ESPN BPI (Basketball Power Index)

- **URL**: https://www.espn.com/mens-college-basketball/bpi
- **What's available**: Team power rankings (BPI = points above/below average), game predictions, tournament projections, strength of record, resume rankings. Game predictions account for opponent strength, pace, site, travel distance, rest days, and altitude.
- **Historical depth**: Current season data readily available. Historical seasons accessible by changing the season parameter in the URL. Exact historical depth unclear but likely goes back to ~2012 when BPI was introduced.
- **Format**: HTML tables. Undocumented JSON API endpoints exist (documented by community at https://github.com/pseudo-r/Public-ESPN-API). No official API.
- **Cost**: Free to view on ESPN.com.
- **Update frequency**: Updated daily during the season.
- **Known quality issues**: BPI methodology is proprietary and not fully transparent. The undocumented API endpoints can change without notice, breaking scrapers. ESPN's data is presentation-oriented rather than research-oriented.
- **Programmatic access**:
  - **hoopR** (R): Can pull ESPN data including play-by-play and box scores
  - **CBBpy** (Python): https://pypi.org/project/CBBpy/ -- scrapes ESPN for play-by-play, box scores, and game metadata for any D1 game
  - **Public-ESPN-API**: Community-documented endpoints
- **How researchers use it**: BPI is used as one of many ranking features in ensemble models. ESPN's play-by-play data (accessible through hoopR/CBBpy) is more commonly used than BPI itself.

### 7. Massey Ratings

- **URL**: https://masseyratings.com/cb/ncaa-d1
- **What's available**: Computer ratings from Kenneth Massey's own model, plus a **composite ranking** that aggregates 100+ different computer ranking systems. This composite is uniquely valuable -- it includes KenPom, Sagarin, BPI, T-Rank, RPI, and dozens of other systems in a single view.
- **Historical depth**: Composite data available for many years. The Kaggle competition includes Massey ordinals as a standard feature set.
- **Format**: CSV export available from the website. Also available as part of Kaggle competition data.
- **Cost**: Free.
- **Update frequency**: Updated regularly during the season.
- **Known quality issues**: The composite is only as good as its constituent ranking systems. Some systems in the composite may use similar methodologies, creating hidden correlations. The Massey ordinals in Kaggle data are well-tested and widely used.
- **How researchers use it**: The Massey ordinals (composite rankings) are one of the strongest feature sets in Kaggle competition entries. Many top-performing models use the ordinal rank from multiple systems as input features, effectively ensembling the wisdom of many different rating algorithms.

### 8. Play-by-Play Data Ecosystem (R Packages)

This is a cluster of related tools rather than a single source:

#### hoopR
- **URL**: https://hoopr.sportsdataverse.org
- **Source data**: ESPN (primary), KenPom (requires subscription)
- **What's available**: Live play-by-play, box scores, shot locations (when available), team/player stats. 36+ exported functions.
- **Format**: R package, returns tidy data frames.
- **Cost**: Free (open source). KenPom functions require KenPom subscription.

#### gamezoneR
- **URL**: https://jacklich10.github.io/gamezoneR/
- **Source data**: STATS LLC GameZone
- **What's available**: Play-by-play data with **shot locations**. Over 170,000 charted shots per season (compared to ~70,000 from ESPN).
- **Historical depth**: Back to **2017-18 season**.
- **Format**: R package, tidy data frames.
- **Cost**: Free.
- **Known quality issues**: Dependent on STATS LLC continuing to make GameZone data accessible.

#### ncaahoopR
- **URL**: https://github.com/lbenz730/ncaahoopR
- **Source data**: ESPN
- **What's available**: Play-by-play data, win probability, game flow visualizations.
- **Format**: R package.
- **Cost**: Free.

#### bigballR
- **URL**: https://github.com/jflancer/bigballR
- **Source data**: stats.ncaa.org
- **What's available**: Play-by-play, lineup analysis, on/off court statistics.
- **Format**: R package.
- **Cost**: Free.
- **Known quality issues**: Inherits data quality issues from NCAA stats portal (human tracker errors).

### 9. cbbdata API (Aggregator)

- **URL**: https://cbbdata.aweatherman.com
- **What's available**: A unified API wrapping multiple sources: Bart Torvik data, KenPom data (with subscription), NET rankings, ESPN team/player info. Includes game-by-game logs with box scores and advanced metrics back to 2008, player/team splits, daily NET rankings, and game predictions.
- **Format**: R package with Flask-based API backend. SQL queries and direct file transfers.
- **Cost**: Free for Torvik/NET data. KenPom data requires matching KenPom subscription email.
- **Update frequency**: Database updated every **15 minutes** during the season.
- **Known quality issues**: Maintained by a single developer (Andrew Weatherman). Replaces the older toRvik package. Reliability depends on continued maintenance.
- **How researchers use it**: Best single entry point for R users who want clean, tidy access to multiple data sources without managing separate scrapers.

### 10. SportsDataIO / FantasyData

- **URL**: https://sportsdata.io/ncaa-college-basketball-api
- **What's available**: Real-time scores, stats, odds, and projections for every men's D1 game. Coverage extends beyond the NCAA tournament to NIT, CBI, and other postseason events. Historical database spanning decades.
- **Format**: RESTful JSON API, well-documented.
- **Cost**: **Commercial pricing** -- free trial limited to UEFA Champions League only. NCAA basketball requires contacting sales. Discovery Lab (for students/hobbyists) offers more affordable personal-use access.
- **Update frequency**: Real-time during games.
- **Known quality issues**: Primarily designed for fantasy sports and betting applications. Pricing opacity makes it hard to evaluate for academic/hobbyist use.
- **How researchers use it**: More commonly used by commercial applications (fantasy sports, betting platforms) than academic researchers due to cost.

---

## Data Pipeline Recommendations

### Recommended Starting Stack

1. **Kaggle March ML Mania data** as the foundation (clean, structured, historical, free)
2. **Bart Torvik via cbbdata/toRvik** for advanced metrics (free, programmatic)
3. **KenPom** if budget allows ($25/yr) for the gold-standard adjusted efficiency metrics
4. **Massey ordinals** (included in Kaggle data) as an ensemble of 100+ ranking systems

### For Advanced Feature Engineering

5. **gamezoneR** for shot location data (spatial features, shot distribution analysis)
6. **hoopR/CBBpy** for ESPN play-by-play data (possession-level features)

### Sources to Avoid for Automated Pipelines

- **Sports Reference**: Excellent data but hostile to automated access. Use manually for spot-checking or historical research, not as a pipeline data source.
- **stats.ncaa.org**: Data quality issues and difficult scraping requirements make it a last resort.
- **SportsDataIO**: Cost-prohibitive for non-commercial use.

### Key Considerations for Data Quality

- **Temporal consistency**: Metrics like adjusted efficiency are model outputs, not raw measurements. Different sources may use different methodologies, and those methodologies may evolve over time. Be cautious comparing KenPom 2005 values to KenPom 2025 values.
- **Tracker errors**: Any data derived from play-by-play (including shot locations) inherits human data entry errors. Budget time for data cleaning.
- **Survivorship bias**: Historical data often only covers teams that still exist or are in D1. Conference realignment creates discontinuities.
- **Feature leakage**: Tournament seeding incorporates committee judgment that already reflects team quality metrics. Using both seeds and the metrics that inform seeding can create subtle leakage.

---

## Sources Consulted

- KenPom: https://kenpom.com, https://kenpom.com/register-kenpom.php, https://kenpom.com/register-api.php
- kenpompy: https://kenpompy.readthedocs.io, https://github.com/j-andrews7/kenpompy
- Bart Torvik: https://barttorvik.com, https://barttorvik.com/trank.php
- toRvik: https://github.com/andreweatherman/toRvik, https://torvik.dev
- cbbdata: https://cbbdata.aweatherman.com, https://github.com/andreweatherman/cbbdata
- Sports Reference: https://www.sports-reference.com/cbb/, https://www.sports-reference.com/bot-traffic.html, https://www.sports-reference.com/data_use.html
- sportsipy: https://sportsreference.readthedocs.io
- Kaggle March ML Mania: https://www.kaggle.com/competitions/march-machine-learning-mania-2026
- NCAA Stats: https://stats.ncaa.org
- NCAA API: https://github.com/henrygd/ncaa-api
- bigballR: https://github.com/jflancer/bigballR
- NCAAStatScraper: https://github.com/ryansloan/NCAAStatScraper
- ESPN BPI: https://www.espn.com/mens-college-basketball/bpi
- Public ESPN API: https://github.com/pseudo-r/Public-ESPN-API
- CBBpy: https://pypi.org/project/CBBpy/
- hoopR: https://hoopr.sportsdataverse.org
- gamezoneR: https://jacklich10.github.io/gamezoneR/, https://github.com/JackLich10/gamezoneR
- ncaahoopR: https://github.com/lbenz730/ncaahoopR
- Massey Ratings: https://masseyratings.com/cb/ncaa-d1, https://masseyratings.com/data
- SportsDataIO: https://sportsdata.io/ncaa-college-basketball-api, https://sportsdata.io/developers/data-dictionary/ncaa-basketball
- OddsShark Torvik explainer: https://www.oddsshark.com/ncaab/what-are-torvik-ratings
- Oreate AI Torvik deep dive: https://www.oreateai.com/blog/understanding-torvik-basketball-rankings
- Analytics8 ML guide: https://www.analytics8.com/blog/how-to-use-machine-learning-to-predict-ncaa-march-madness/
- The Power Rank analytics guide: https://thepowerrank.com/cbb-analytics/
