# Historical Seed Performance, Bracket Structure, and Seed-Based Baseline Models

## Summary

Historical seed data from the NCAA tournament (1985-2025, 40 tournaments) reveals powerful regularities that any predictive model must reckon with. The seed number alone is an extraordinarily strong predictor of tournament outcomes, especially in early rounds. A "chalk" bracket that always picks the higher seed scores ~30% better than the average bracket and is competitive with expert picks. However, seed advantages erode in later rounds, and the tournament's bracket structure (region assignment, geographic placement) introduces additional factors. Key findings:

- **No. 1 seeds have won 26 of 40 championships** -- almost twice as many as all other seeds combined.
- **First-round upset rates follow a clean gradient**: 1-seeds win 99.3%, 2-seeds 94.3%, 3-seeds 85%, down to the coin-flip 8v9 game at ~49%.
- **The 5-12 upset is the most famous "value" pick**: 12-seeds win ~36% of the time in the first round.
- **Only seeds 1-6 have overall winning records** across all tournament games.
- **16-over-1 upsets have happened exactly twice** (UMBC over Virginia 2018, FDU over Purdue 2023) in 160 attempts.
- **The "chalk bracket" (always pick the higher seed)** is a surprisingly strong baseline, scoring 20.4 points more than the average bracket and matching or beating most expert picks.
- **Bracket structure matters**: The NCAA committee balances regions so that no region's top-4 seed "true seed" totals differ by more than 6 points, and geographic placement gives higher seeds a travel/fan advantage.

---

## Source 1: NCAA.com -- Records for Every Seed in March Madness (1985-2025)

**URL**: [https://www.ncaa.com/news/basketball-men/article/2025-04-16/records-every-seed-march-madness-1985-2025](https://www.ncaa.com/news/basketball-men/article/2025-04-16/records-every-seed-march-madness-1985-2025)

### Historical Data Presented

Comprehensive win-loss records for each seed (1-16) across every round of the tournament from 1985 through 2025.

### Key Statistics

- **No. 1 seeds**: 515+ total wins, the most of any seed. Won 26 national championships.
- **Seeds 1-3 combined**: 444-36 record against lower-seeded opponents in their opening matchups.
- **Seeds 1-6**: The only seeds with overall winning records in the tournament.
- **No. 5 seed**: Highest seed never to win a championship (best finish: runner-up, 4 times).
- **No. 8 seed (Villanova 1985)**: Lowest seed ever to win the championship.

### First-Round Win Rates by Seed

| Matchup | Higher Seed Win Rate |
|---------|---------------------|
| 1 vs 16 | 99.3% (158-2) |
| 2 vs 15 | 94.3% (132-8) |
| 3 vs 14 | 85.0% (119-21) |
| 4 vs 13 | 79.3% (111-29) |
| 5 vs 12 | ~64% (higher seed) |
| 6 vs 11 | ~63% (higher seed) |
| 7 vs 10 | ~61% (higher seed) |
| 8 vs 9 | ~49% (69-71, 9-seed slightly favored) |

### Implications for Modeling

- Seed is the single strongest predictor of first-round outcomes. Any model that ignores seed is leaving enormous signal on the table.
- The 8v9 game is essentially a coin flip, suggesting seed differences below ~3 lines carry little predictive power.
- The gradient from 1v16 to 8v9 is remarkably smooth, suggesting a latent continuous strength variable underlies the discrete seed assignments.

---

## Source 2: BracketOdds (University of Illinois) -- Seed Advancement and Matchup Records

**URLs**:
- [https://bracketodds.cs.illinois.edu/seedadv.html](https://bracketodds.cs.illinois.edu/seedadv.html)
- [https://bracketodds.cs.illinois.edu/seed_records.html](https://bracketodds.cs.illinois.edu/seed_records.html)

### Historical Data Presented

This academic site (maintained by Sheldon Jacobson's research group at UIUC) provides:
- The number of times each seed has won in each round.
- Expected number of wins per seed per round, with standard deviations.
- Seed-vs-seed matchup records for all historically observed pairings.
- Truncated geometric distribution fits to seed advancement probabilities.

### Key Statistics

- Uses data from 1985-2025 (40 tournaments, 160 regions).
- Models seed advancement using truncated geometric distributions, providing a principled probabilistic framework.
- Only includes matchup records for pairings that have occurred 4+ times in later rounds (due to sample size concerns).

### Advancement Probabilities (approximate, by seed)

| Seed | Round of 32 | Sweet 16 | Elite 8 | Final Four | Championship | Winner |
|------|-------------|----------|---------|------------|--------------|--------|
| 1 | ~99% | ~80% | ~55% | ~35% | ~20% | ~16% |
| 2 | ~94% | ~65% | ~40% | ~20% | ~8% | ~4% |
| 3 | ~85% | ~50% | ~25% | ~11% | ~5% | ~3% |
| 4 | ~79% | ~45% | ~20% | ~8% | ~2.5% | ~1.5% |
| 5 | ~64% | ~30% | ~10% | ~3% | ~1% | 0% |
| 8/9 | ~50% | ~15% | ~5% | ~1.5% | <1% | <1% |
| 11 | ~37% | ~15% | ~5% | ~3.75% | 0% | 0% |
| 16 | <1% | 0% | 0% | 0% | 0% | 0% |

### Published Research

Jacobson's group has published peer-reviewed papers on this topic:
- "Seed distributions for the NCAA men's basketball tournament" (Omega, 2011)
- JQAS 2017 paper on bracket probability modeling

### Implications for Modeling

- The truncated geometric distribution provides a clean parametric model for seed advancement that could serve as a Bayesian prior.
- Seed-vs-seed matchup records provide empirical base rates for any pairwise prediction model.
- The diminishing predictive power of seed in later rounds (where stronger teams are already playing each other) suggests that additional features beyond seed become increasingly important as the tournament progresses.

---

## Source 3: NCAA.com -- The Chalk Bracket (Always Pick the Higher Seed)

**URL**: [https://www.ncaa.com/news/basketball-men/bracketiq/2021-02-12/heres-how-your-march-madness-bracket-will-do-if-you-only-pick-better-seeded](https://www.ncaa.com/news/basketball-men/bracketiq/2021-02-12/heres-how-your-march-madness-bracket-will-do-if-you-only-pick-better-seeded)

### Historical Data Presented

Analysis of how a "chalk bracket" (always picking the higher-seeded team, using overall seed ranking for tiebreakers like 1v1 in the Final Four) performs relative to average brackets and expert picks.

### Key Statistics

- A chalk bracket scores **20.4 points more than the average bracket** over multiple years.
- This represents **~30% better performance** than the average bracket.
- The chalk bracket is the **single most likely bracket outcome** in any given year (i.e., the mode of the bracket distribution), though it is still overwhelmingly unlikely to be perfect.

### The Flerlage Twins' Corroborating Analysis

**URL**: [https://www.flerlagetwins.com/2017/02/whats-best-ncaa-bracket-strategy_99.html](https://www.flerlagetwins.com/2017/02/whats-best-ncaa-bracket-strategy_99.html)

Ken Flerlage tested the "Top Seed" method against 12 CBS analysts and the Bracket Voodoo predictive model for the 2016 tournament:
- The Top Seed method **tied the top analyst with 87 points**.
- It **performed as well or better than all 12 CBS analysts**.
- It **significantly outperformed** the Bracket Voodoo predictive model.

The analysis suggests that many "expert" bracket picks and even some predictive models fail to beat the simple higher-seed baseline.

### Implications for Modeling

- The chalk bracket is the **baseline to beat** for any predictive model. If your model cannot outperform "always pick the higher seed," it is not adding value.
- The chalk bracket's strength comes from its robustness: it never makes a catastrophically wrong pick in early rounds, where most bracket points are earned due to volume.
- However, the chalk bracket is a poor choice for **winning bracket pools** because it is the most common strategy; to win a pool you need differentiated picks, which means strategically predicting upsets. This is the tension between accuracy and pool-winning strategy.

---

## Source 4: NCAA.com / ESPN -- History of 16-over-1 Upsets

**URLs**:
- [https://www.ncaa.com/news/basketball-men/article/2026-02-10/history-1-seed-vs-16-seed-march-madness](https://www.ncaa.com/news/basketball-men/article/2026-02-10/history-1-seed-vs-16-seed-march-madness)
- [https://www.espn.com/mens-college-basketball/story/_/id/22800763/umbc-pulled-most-unforgettable-did-just-see-upset-ncaa-tournament-history-knocking-no-1-overall-seed-virginia](https://www.espn.com/mens-college-basketball/story/_/id/22800763/umbc-pulled-most-unforgettable-did-just-see-upset-ncaa-tournament-history-knocking-no-1-overall-seed-virginia)

### Historical Data Presented

Complete history of 1v16 matchups from 1985 to 2025.

### Key Statistics

- **All-time record**: 1-seeds lead 158-2 (98.75% win rate).
- **0-135 before 2018**: No 16-seed had ever won in the first 33 years of the 64-team format.
- **2018: UMBC 74, Virginia 54** -- The first 16-over-1 upset. UMBC was a 20-point underdog. Virginia was the overall No. 1 seed (31-2 regular season). The upset was a blowout: UMBC scored 53 points in the second half against the nation's best defense.
- **2023: FDU 63, Purdue 58** -- The second 16-over-1 upset. FDU held Purdue to 36% shooting.
- **Neither UMBC nor FDU advanced past the Round of 32**, suggesting the upset was more about the 1-seed's underperformance than the 16-seed being genuinely strong.
- **15-seeds have upset 2-seeds 11 times**, including three consecutive years (2021-2023), a much higher rate (~5.7%) than 16v1 upsets (~1.25%).

### Implications for Modeling

- The 16v1 upset rate (~1.25%) is low enough that a model should almost never predict it, but high enough that it is not zero. Two occurrences in the last 7 tournaments suggest the true rate may be increasing (or recent results are a statistical fluctuation).
- The 15v2 upset rate (~5.7%) is meaningful and should be incorporated into models.
- Upset probability is not just about seed difference; specific team characteristics (defensive efficiency, experience, shooting variance) likely explain which 1-seeds are vulnerable.
- UMBC's return to the 2026 tournament adds a narrative dimension but should not affect modeling.

---

## Source 5: SI.com / ESPN -- Cinderella Runs and Lowest Seeds to Advance Deep

**URLs**:
- [https://www.si.com/college-basketball/lowest-seeds-to-ever-win-in-march-madness-which-cinderellas-will-emerge-in-2026](https://www.si.com/college-basketball/lowest-seeds-to-ever-win-in-march-madness-which-cinderellas-will-emerge-in-2026)
- [https://www.espn.com/mens-college-basketball/story/_/id/39742636/march-madness-cinderella-ncaa-bracket-busters-george-mason-fgcu-vcu-st-peters-davidson](https://www.espn.com/mens-college-basketball/story/_/id/39742636/march-madness-cinderella-ncaa-bracket-busters-george-mason-fgcu-vcu-st-peters-davidson)

### Historical Data Presented

Comprehensive history of deep runs by low-seeded teams.

### Key Statistics: Furthest Advancement by Seed

| Seed | Furthest Round | Examples |
|------|---------------|----------|
| 1 | Champion (26 times) | Multiple |
| 2 | Champion (5 times) | Multiple |
| 3 | Champion (4 times) | Multiple |
| 4 | Champion (2 times) | Arizona 1997, UConn 2023 |
| 5 | Runner-up (4 times) | Never won championship |
| 6 | Champion (1 time) | Kansas 1988 |
| 7 | Champion (1 time) | UConn 2014 |
| 8 | Champion (1 time) | Villanova 1985 |
| 9 | Final Four (2 times) | Wichita State 2013, FAU 2023 |
| 10 | Final Four (1 time) | Syracuse 2016 |
| 11 | Final Four (6 times) | LSU 1986, George Mason 2006, VCU 2011, Loyola-Chicago 2018, UCLA 2021, NC State 2024 |
| 12 | Elite Eight (2 times) | Missouri 2002, Oregon State 2021 |
| 13 | Sweet 16 (6 times) | Most recent: Creighton 2021 |
| 14 | Sweet 16 (rare) | |
| 15 | Elite Eight (1 time) | Saint Peter's 2022 |
| 16 | Round of 32 (2 times) | UMBC 2018, FDU 2023 |

### Notable Cinderella Runs in Detail

- **2006 George Mason (11-seed)**: Beat three former champions (Michigan State, UNC, UConn) to reach the Final Four. Perhaps the most impressive route of any Cinderella.
- **2011 VCU (11-seed)**: Entered through the First Four, then beat Georgetown (6), Purdue (3), Florida State (10), and Kansas (1) to reach the Final Four.
- **2018 Loyola-Chicago (11-seed)**: Made the Final Four with Sister Jean as their spiritual guide, winning three games by a combined 8 points.
- **2022 Saint Peter's (15-seed)**: Beat Kentucky (2), Murray State (7), and Purdue (3) to become the first 15-seed in the Elite Eight.
- **2024 NC State (11-seed)**: Most recent 11-seed Final Four appearance.

### The 11-Seed Anomaly

Eleven-seeds have reached the Final Four **6 times**, more than seeds 9, 10, 12, 13, 14, 15, and 16 **combined** (which total 4). This is likely a bracket structure effect: 11-seeds that win their first game face a 3-seed (instead of a 1 or 2), giving them a more favorable path to the Sweet 16.

### Implications for Modeling

- Bracket structure matters: the path a seed faces in subsequent rounds affects how far it can advance. 11-seeds and 12-seeds have structurally easier paths than 9-seeds or 10-seeds after the first round.
- Cinderella runs are rare but not random; they tend to involve teams with specific characteristics (strong defense, veteran rosters, hot shooting).
- The 11-seed Final Four anomaly suggests models should account for bracket position, not just seed-vs-seed matchup probability in isolation.

---

## Source 6: NCAA.org -- Bracket Structure and Region Assignment Process

**URL**: [https://www.ncaa.org/news/2025/3/12/media-center-building-the-brackets-a-deep-dive-on-the-ncaa-tournament-selection-and-seeding-process.aspx](https://www.ncaa.org/news/2025/3/12/media-center-building-the-brackets-a-deep-dive-on-the-ncaa-tournament-selection-and-seeding-process.aspx)

### Historical Data Presented

Detailed description of how the NCAA selection committee constructs the bracket, including seeding, region assignment, and balancing principles.

### Key Structural Rules

1. **Four regions, each with seeds 1-16**: The bracket is a fixed structure where 1 plays 16, 2 plays 15, etc. in the first round.
2. **Overall seed ranking**: The committee assigns an overall seed (1-68), not just a seed line (1-16). The overall No. 1 seed is placed in the most favorable region and location.
3. **Region balancing**: After the top four seed lines are assigned, the committee sums "true seed" numbers in each region. **No more than 6 points should separate the lowest and highest regional totals.** This prevents "regions of death."
4. **Conference separation**: The first four teams from the same conference must be placed in different regions (when they are in the top 4 seed lines).
5. **Geographic placement**: Teams are placed as close to their home as possible among available options, giving higher seeds a de facto home-court advantage.
6. **Bracket position within a region**: The top seed in each region gets the most favorable bracket position (plays closest to home in the earliest rounds).

### Implications for Modeling

- **Region strength is intentionally balanced** but not perfectly so. The 6-point tolerance means some regions are meaningfully tougher than others, especially at the 5-12 seed lines where the committee has more flexibility.
- **Geographic advantage is real**: Higher seeds playing closer to home get a measurable crowd and travel advantage. This is an additional factor beyond pure team quality.
- **Conference clustering effects**: When multiple strong teams from the same conference are separated into different regions, it changes the competitive landscape of each region.
- **The bracket is not a pure seeded tournament**: Because pairings are fixed by bracket position (not re-seeded each round), the actual opponent a team faces depends on who else is in their bracket quadrant. A 1-seed in a quadrant with a strong 4-seed and 5-seed faces a harder path than one with weaker teams at those lines.

---

## Cross-Cutting Themes and Modeling Implications

### 1. Seed is the Dominant Feature, but Not the Only One

Seed alone explains the majority of variance in tournament outcomes, especially in early rounds. Any model should start with seed as a primary feature. The chalk bracket's strong performance confirms this.

### 2. Diminishing Returns of Seed in Later Rounds

As the tournament progresses, seed becomes less predictive because the surviving teams are all relatively strong. Models need additional features (team-level metrics like efficiency, tempo, experience) to differentiate in later rounds.

### 3. Bracket Structure Creates Path Dependencies

The fixed bracket structure means a team's advancement probability depends not just on its own strength but on who else is in its region and bracket quadrant. The 11-seed Final Four anomaly illustrates this: bracket position affects which opponents a team faces if it upsets its first-round matchup.

### 4. The Chalk Baseline is Hard to Beat

The "always pick the higher seed" strategy is the benchmark. It scores ~30% better than the average bracket. Any model that cannot outperform chalk is not adding value. However, chalk is suboptimal for winning bracket pools because it is the most common strategy and lacks differentiation.

### 5. Upset Rates are Relatively Stable

The historical upset rates by seed matchup are remarkably stable over time, suggesting they reflect genuine structural features of the tournament rather than noise. The ~36% upset rate for 12-over-5, ~15% for 13-over-4, and ~5.7% for 15-over-2 are useful calibration targets for any probabilistic model.

### 6. Tail Events Matter for Pool Strategy (but not for accuracy)

Predicting Cinderella runs (like Saint Peter's 2022 or Loyola-Chicago 2018) is nearly impossible but enormously valuable in bracket pools. A model optimized for accuracy should rarely predict deep upsets; a model optimized for pool-winning should occasionally take calculated risks on low-seed teams with favorable matchup profiles.

---

## Sources

- [Records for every seed in March Madness from 1985 to 2025 | NCAA.com](https://www.ncaa.com/news/basketball-men/article/2025-04-16/records-every-seed-march-madness-1985-2025)
- [BracketOdds - Seed Match-up Records (UIUC)](https://bracketodds.cs.illinois.edu/seed_records.html)
- [BracketOdds - How Far Does Each Seed Advance? (UIUC)](https://bracketodds.cs.illinois.edu/seedadv.html)
- [Here's how your bracket will do if you only pick the better-seeded team | NCAA.com](https://www.ncaa.com/news/basketball-men/bracketiq/2021-02-12/heres-how-your-march-madness-bracket-will-do-if-you-only-pick-better-seeded)
- [What's the Best NCAA Bracket Strategy? | Flerlage Twins](https://www.flerlagetwins.com/2017/02/whats-best-ncaa-bracket-strategy_99.html)
- [History of 1 seed vs. 16 seed in March Madness | NCAA.com](https://www.ncaa.com/news/basketball-men/article/2026-02-10/history-1-seed-vs-16-seed-march-madness)
- [UMBC vs. Virginia: How one of the greatest upsets became a blowout | NCAA.com](https://www.ncaa.com/news/basketball-men/article/2020-04-07/umbc-vs-virginia-how-one-greatest-upsets-ncaa-tournament)
- [The Lowest Seeds to Ever Win in March Madness | SI.com](https://www.si.com/college-basketball/lowest-seeds-to-ever-win-in-march-madness-which-cinderellas-will-emerge-in-2026)
- [March Madness Cinderella runs | ESPN](https://www.espn.com/mens-college-basketball/story/_/id/39742636/march-madness-cinderella-ncaa-bracket-busters-george-mason-fgcu-vcu-st-peters-davidson)
- [Building the brackets: A deep dive on NCAA tournament selection | NCAA.org](https://www.ncaa.org/news/2025/3/12/media-center-building-the-brackets-a-deep-dive-on-the-ncaa-tournament-selection-and-seeding-process.aspx)
- [Bracket Strategy Guide | PoolGenius](https://poolgenius.teamrankings.com/ncaa-bracket-picks/articles/bracket-strategy-guide/)
- [NCAA Tournament Records By Seed | PrintYourBrackets](https://www.printyourbrackets.com/ncaa-tournament-records-by-seed.html)
- [History of Records By Seed | BetFirm](https://www.betfirm.com/seeds-national-championship-odds/)
- [March Madness Bracket Tips | BoydsBets](https://www.boydsbets.com/bracket-tips-by-seed/)
- [NCAA Bracket Prediction Using ML and Combinatorial Fusion Analysis | arXiv](https://arxiv.org/html/2603.10916v1)
