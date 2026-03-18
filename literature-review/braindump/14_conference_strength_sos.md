# Conference Strength, Strength of Schedule, and Selection Bias in March Madness Prediction

## Summary

Strength of schedule (SOS) and conference quality are among the most consequential -- and most contentious -- factors in March Madness prediction. Every major rating system (KenPom, NET, BPI, Sagarin, Elo) attempts to adjust raw team performance for opponent quality, but the structure of college basketball scheduling creates systematic problems that no model fully solves. The core tension: teams in power conferences accumulate "quality wins" by beating each other, while mid-major teams with comparable or superior talent face structural barriers to demonstrating their quality. Academic research confirms that the NCAA selection committee exhibits measurable bias toward power conference teams in seeding, and mid-major teams consistently outperform their seeds in the tournament -- evidence that they are systematically undervalued.

Key takeaways:

- **Adjusted efficiency margin** (points per 100 possessions, adjusted for opponent quality and location) is the foundational metric across all major systems, but the adjustment methodology varies significantly between systems.
- **Conference insularity** is the fundamental problem: simulation research shows that estimation error roughly doubles when teams play realistic conference-heavy schedules vs. random schedules, because cross-conference data is sparse.
- **The Quad system and NET rankings** structurally favor power conferences: high-major conference games are Quad 1 results ~48% of the time vs. ~6% for mid/low-majors.
- **Selection committee bias** is empirically documented: power conference teams are seeded ~2 lines higher than models predict, and mid-majors (especially 11 and 12 seeds) win first-round games at rates that exceed their seed-line expectations.
- **Non-conference scheduling** is the key lever for mid-majors, but power conference teams increasingly refuse to schedule strong mid-majors, and conference schedule expansion reduces available non-conference slots.
- **No rating system can fully overcome** the information deficit created by limited cross-conference play; all systems must rely to some degree on priors (preseason rankings, historical conference strength) to fill the gap.

---

## Source 1: Ben Wieland -- "How Conferences Affect College Basketball Team Rating Systems"

**URL**: https://bbwieland.github.io/2024-04-01-cbb-rating-systems/

### Methodology

Wieland conducted a simulation study using 362 synthetic teams with efficiency ratings drawn from actual 2023 KenPom data. He compared four scheduling scenarios:

1. **Random schedule**: 30 randomly selected opponents (ideal case)
2. **Random conferences**: ~20 conference games + 10 non-conference, conferences assigned randomly
3. **True conferences**: Same structure but conferences ranked by actual team strength (realistic)
4. **No non-conference**: ~30 conference-only games (worst case)

He then measured mean absolute error (MAE) of the rating system's estimates vs. true underlying team strength.

### Key Findings

- MAE with random scheduling: **5.30** rating points
- MAE with true conference structure: **8.18** (a 54% increase)
- MAE with no non-conference play: **9.88** (an 86% increase over ideal)
- "Inter-conference play is the glue that holds any predictive rating system together."
- When conferences are grouped by actual strength, the system struggles to tell whether a team's strong record reflects genuine quality or conference weakness.
- Systems compensate by incorporating prior-season conference data, which penalizes current teams for historical weakness.

### Implications for Prediction

- Rating systems are fundamentally less accurate for teams in weak conferences, not because the systems are poorly designed, but because the data is insufficient.
- Mid-season non-conference scheduling slots would dramatically improve rating accuracy.
- The ~10 non-conference games each team plays are disproportionately important for calibrating the entire rating landscape.

---

## Source 2: Mountain West Connection -- "Stats Corner: Understanding Basketball Ranking Methods"

**URL**: https://www.mwcconnection.com/bracketology/78909/stats-corner-understanding-basketball-ranking-methods

### Systems Compared

| System | SOS Method | Key Feature |
|--------|-----------|-------------|
| **RPI** (1981-2018) | 75% of rating was SOS: OWP (50%) + OOWP (25%) | Replaced due to fundamental flaws; no efficiency component |
| **NET** (2019-present) | Machine learning; integrates efficiency, opponent strength, location, wins/losses | Quad system categorizes results by opponent NET + venue |
| **KenPom** | Adjusted Efficiency Margin (AEM) = AdjO - AdjD; SOS = average AEM of opponents | Also tracks non-conference SOS separately; includes luck rating |
| **ESPN BPI** | Proprietary; offense + defense components | Methodology not publicly documented in detail |

### The Quad System (NET)

- Quad 1: Home vs. NET 1-30; Neutral vs. 1-50; Away vs. 1-75
- Quad 2: Home 31-75; Neutral 51-100; Away 76-135
- Quad 3: Home 76-160; Neutral 101-200; Away 136-240
- Quad 4: Home 161+; Neutral 201+; Away 241+

Quadrant classifications shift dynamically as opponent rankings change. This means a win can retroactively become more or less valuable.

### KenPom Technical Details

- **Adjusted Tempo**: Possessions per 40 minutes = FGA - OREB + TO + 0.475 * FTA
- **Adjusted Efficiency**: Raw efficiency adjusted for opponent strength using least squares regression
- **Luck Rating**: Deviation from expected 50% win rate in one-possession games
- **Non-Conference SOS**: Tracked separately to reward challenging scheduling

### Divergence Between Systems

Systems can produce significantly different rankings. Example from Mountain West: KenPom ranked San Diego State 49th, Boise State 51st, New Mexico 54th, while NET had them at 60th, 44th, and 46th respectively. These differences arise from differing treatment of margin of victory, game location, and win/loss binary outcomes.

---

## Source 3: Brackets Ninja -- "How Conference Strength Actually Impacts March Madness Performance"

**URL**: https://www.bracketsninja.com/blog/march-madness-conference-performance-history

### Conference Performance Data

**Power conference dominance in late rounds**: Power conferences (ACC, Big East, Big Ten, Big 12, Pac-12, SEC) have produced over 85% of all Final Four teams since 1985. The ACC alone: 21 Final Four appearances.

**Mid-major overperformance in early rounds**:
- No. 12 seeds (predominantly mid-majors): **34.6% first-round win rate** -- highest among all double-digit seeds
- No. 11 seeds (frequently mid-majors): **37.1% first-round win rate**
- This pattern is strong evidence of systematic underseeding

**Conference-specific tournament patterns**:

| Conference | Pattern | Explanation |
|-----------|---------|-------------|
| Missouri Valley | Overperforms by ~12% vs. seed prediction | Consistently underseeded |
| West Coast | Historical overperformer (pre-Gonzaga top seeding) | Undervalued conference |
| American Athletic | Exceeds seed-line expectations | Strong mid-major play |
| Big Ten | Underperforms in early rounds | Physical half-court style struggles at neutral sites |
| Pac-12 | Surprising first-round exits | Talent doesn't always translate |
| SEC | Underperformed 2000-2012 despite large fields | Volume != quality in that era |

### Prediction Insight

"Conference prestige doesn't always match tournament performance." Mid-major teams facing power-conference opponents seeded within 2-3 lines represent bracket value because the selection committee systematically misprices them.

---

## Source 4: Rabbit Hole Sports -- "The Circular Logic of the NCAA Tournament Selection Process"

**URL**: https://rabbitholesports.substack.com/p/the-circular-logic-of-the-ncaa-tournament

### The Circular Logic Problem

The core argument: power conference teams inflate each other's metrics in a self-reinforcing loop. "Every time one team wins they have a quality win and the losing team lost to a quality opponent so nobody gets hurt." This creates a situation where entire conferences appear stronger than warranted because their internal games generate "quality" outcomes for both sides.

### How the Quad System Enables Bias

- Power conference teams automatically accumulate more Quad 1 opportunities simply by playing their conference schedule
- A 25-win mid-major team may have **zero** Quad 1 opportunities, so any loss looks damaging
- A power conference team with 14-15 wins can still earn a bid if 8+ wins are Quad 1
- Preseason expectations embedded in predictive metrics (BPI includes a declining preseason component) create initial advantages for major programs

### The "Bubble Problem"

The 7th or 8th team from a power conference is consistently favored over the 2nd or 3rd team from a mid-major conference for at-large bids.

### Specific Examples

- **2023**: The ACC sent only 5 teams but went 7-5 in the tournament, while the 8-team Big Ten went 6-8, suggesting the ACC was undervalued
- **Big 12**: Teams with poor non-conference records remained in contention primarily because of conference strength, even with sub-.500 conference records

### Coaching Perspective

Mick Cronin (then Cincinnati head coach) argued the committee is "financially driven" and favors larger institutions to generate ticket sales. Once a conference loses power status, its member programs lose selection consideration.

---

## Source 5: Athletic Director U -- "Mid-Major Scheduling: Where Can Teams Go for Quality Games?"

**URL**: https://athleticdirectoru.com/articles/mid-major-scheduling-where-can-teams-go-for-quality-games/

### The Structural Scheduling Gap

2018-19 season data reveals the scale of the disparity:

| Metric | High-Major | Mid/Low-Major |
|--------|-----------|---------------|
| Conference games that are Quad 1 | **47.9%** | **6.4%** |
| Conference games that are Quad 3/4 | **20.1%** | **80%+** |
| Non-conference Quad 1/2 games | **38.5%** | **31.2%** |

Non-conference scheduling is more balanced than conference scheduling, but the gap is still significant. And conference schedules are expanding, reducing the number of non-conference games available.

### Why Mid-Majors Can't Schedule Up

- FOIA requests revealed that top-50 NET teams including Wisconsin, Michigan State, Ohio State, UCLA, Kansas, and Florida refused non-conference matchups with strong mid-majors
- Power conference teams fill their ~5-6 open non-conference home dates to satisfy season ticket package expectations, preferring guaranteed wins
- The expansion to 20-game conference schedules further reduces non-conference slots

### Impact on Selection

Each Quad 1 or Quad 2 victory increases at-large likelihood by approximately **5.7%**. Since mid-majors have dramatically fewer opportunities for these wins, they face a structural ceiling on their tournament probability regardless of how well they play their available games.

### Proposed Reforms

1. Mid-major conferences should reduce conference schedules from 18 to 16 games
2. Implement rotational scheduling based on conference standings
3. Create post-season home-and-home series between top finishers from participating conferences

---

## Source 6: FiveThirtyEight / Nate Silver -- March Madness Prediction Methodology

**URLs**:
- https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
- https://www.natesilver.net/p/introducing-cooper-silver-bulletins

### FiveThirtyEight Model (Historical)

**Rating construction**: Blended six computer ratings (KenPom, Sagarin predictor, Sonny Moore, LRMC, ESPN BPI, FiveThirtyEight Elo) at 75% weight with human rankings (committee S-curve, AP/coaches polls) at 25% weight.

**Rationale for including human rankings**: "A 30- to 35-game regular season isn't all that large a sample," so preseason talent assessments add value. Unranked teams receive prior-season Sagarin ratings reverted toward the mean.

**SOS adjustment via player-level data**: Injury adjustments use Sports-Reference.com win shares, which "estimate the contribution of each player to his team's record while also adjusting for a team's strength of schedule." This prevents overvaluing "a player who was scoring 20 points a game against the likes of Abilene Christian and Austin Peay."

### Nate Silver's COOPER System (Current)

- Blends COOPER (5/8 weight) with KenPom (3/8 weight)
- **Conference-aware Elo reversion**: At season start, team ratings revert toward the mean of their conference, not the overall mean. This embeds a conference strength prior.
- **Game type weighting**: Conference games and NCAA tournament games receive higher weight because teams compete at full effort and results are more reliable than early-season non-conference matchups.
- **Margin of victory**: Primary input, but binary win/loss also matters.
- **Travel distance**: Accounted for; East Coast teams playing in California perform worse than expected.

### Implications

The use of conference-mean reversion as a prior is notable: it means that a team from a historically strong conference starts each season with a higher baseline. This is rational if conference strength is persistent, but it also means the model will be slow to recognize a conference's decline or a mid-major conference's rise.

---

## Source 7: Coleman, Lynch, and DuMond -- "Major Conference Bias and the NCAA Men's Basketball Tournament"

**URL**: https://ideas.repec.org/a/ebl/ecbull/eb-07l80004.html (also on ResearchGate)

### Methodology

Academic study (Economics Bulletin) analyzing tournament data from 1997-2006. Built a predictive model ("Dance Card") for which teams the selection committee would choose, achieving ~95% accuracy.

### Key Findings

- **SEC teams** were seeded approximately **2 positions higher** (better) than the model predicted based on their actual performance metrics
- **ACC teams** were commonly seeded **lower** than predicted
- Pac-12 and Big 12 teams appeared to receive favorable treatment in selection
- The Missouri Valley Conference was poorly represented relative to its teams' quality

### Significance

This is one of the few peer-reviewed academic studies documenting selection committee bias. The finding of a 2-seed-line advantage for SEC teams is substantial -- in a tournament where a single seed line can dramatically change a team's path through the bracket.

---

## Cross-Cutting Themes

### 1. The Measurement Problem

Every SOS methodology faces the same fundamental challenge: you can only measure teams against opponents they actually played. With ~30 games per season and ~20 of those against conference opponents, the information set for cross-conference calibration is thin. Wieland's simulation quantifies this: realistic scheduling inflates rating error by 54% compared to the ideal random-schedule case.

### 2. The Adjustment Formula

KenPom's approach (the most transparent major system) works as follows:
- Raw offensive efficiency for a game = points scored / possessions * 100
- Adjusted offensive efficiency = (raw OE * national average OE) / opponent's adjusted defensive efficiency
- Final adjusted OE = weighted average of all game-level adjusted OEs, with more weight on recent games
- This is an iterative calculation: adjusting Team A's rating requires knowing Team B's rating, which requires knowing Team C's rating, etc.

### 3. Circular Amplification in Conference Play

Power conference teams create a feedback loop: Team A beats Team B (both rated highly), so Team A gets a Quad 1 win and Team B gets a "good loss." This inflates both teams' resumes. Mid-major teams cannot access this loop regardless of their actual quality. The Quad system, despite being designed to be more nuanced than raw SOS, exacerbates this problem because Quad classifications depend on opponent NET rankings, which themselves reflect conference strength.

### 4. Practical Implications for Bracket Prediction

- **Fade power conference teams on the 4-5 seed line**: These are the most likely to be overseeded based on conference reputation
- **Back mid-major 11 and 12 seeds**: Historical win rates of 37.1% and 34.6% exceed seed-line expectations
- **Adjusted efficiency margin is the best single predictor**, but raw efficiency gap between opponents matters more than seed line in close matchups
- **Non-conference SOS is a signal**: Mid-majors that actively sought and won tough non-conference games are more likely to be genuinely good, not just products of weak-conference inflation
- **Preseason priors are useful but slow to update**: Models using conference-mean reversion will be slow to recognize mid-season shifts in team quality

### 5. The Selection Committee's Incentive Structure

Beyond statistical bias, there are institutional incentives at play. Power conference teams bring larger fanbases, more TV viewers, and more ticket revenue. Multiple coaches have publicly alleged that financial considerations influence selection. Whether or not this is conscious bias, the metrics the committee uses (NET, Quad system) structurally produce the same outcome: power conference favoritism.
