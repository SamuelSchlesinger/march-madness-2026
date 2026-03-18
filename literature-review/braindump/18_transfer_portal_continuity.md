# Transfer Portal, Roster Turnover, and Team Continuity in March Madness Predictions

## Summary

The transfer portal era (post-2021) has fundamentally reshaped how college basketball rosters are constructed and, consequently, how prediction models must account for team composition. Key takeaways from the literature and analysis:

1. **Continuity is measurable but its predictive value is debated.** KenPom's "Minutes Continuity" metric (percentage of returning minutes from prior season) is the standard measure. Average continuity has dropped to historic lows -- 34.0% in 2024-25, down from 39.1% the prior year. Some analysts argue continuity is overrated; others find a modest positive correlation with performance.

2. **Player-level projection is the frontier.** Tools like Bart Torvik's RosterCast and Evan Miyakawa's BPR-based transfer rankings attempt to project how individual players will perform in new environments, but accuracy remains a significant challenge. Fit, coaching system, and development culture matter as much as raw talent.

3. **Position-specific retention matters more than aggregate continuity.** Returning a lead guard or an anchor frontcourt player has outsized impact compared to generic "returning minutes" percentages. This suggests models should weight positional continuity differently.

4. **Coaching quality and institutional culture moderate the continuity effect.** Programs like Arizona and UConn consistently extract above-expectation performance from transfers, while others (North Carolina, Arkansas, Indiana) have underperformed despite strong portal classes. This suggests a "transfer development" factor that is hard to capture in simple roster turnover metrics.

5. **Experience still predicts championships.** 17 of 23 national champions since 2002 had a junior or senior as their top contributor. This held even as the portal era reshaped how that experience was acquired.

6. **For prediction models:** Continuity is most predictive early in the season (November-December), when newly assembled rosters are still gelling. By March, talent and coaching quality dominate. Models should likely incorporate continuity as a time-decaying feature.

---

## Source 1: HoopsHQ -- "Why Continuity Is Overrated"

- **URL:** https://www.hoopshq.com/long-reads/weekend-hot-takes-continuity-is-overrated
- **Author:** Alex Squadron
- **Context:** Analysis piece from the 2024-25 season

### How They Measure Continuity
- Uses KenPom's continuity metric: percentage of a team's returning minutes from the prior season
- Notes average continuity hit an all-time low of 34.0% in 2024-25 (down from 39.1%)

### Key Arguments and Data
- **Zero-continuity teams can succeed:** Kentucky (0.0% continuity, projected 8th in SEC) beat Duke, Florida, Mississippi State, Texas A&M, and Tennessee. West Virginia (also 0.0%) defeated Gonzaga before mid-December.
- **Low-continuity overachievers:** Memphis (315th in continuity), Illinois (345th), Vanderbilt (347th), Louisville (352nd), Maryland (starts only one returner), St. John's (270th)
- **High-continuity underperformers:** Gonzaga (72.7% continuity, 4th nationally) lost to low-continuity Kentucky and West Virginia early. Houston (four returning starters) dropped three November games.
- **Temporal effect:** Continuity advantages show most during the first month of the season, as newly-constructed teams are still gelling.

### Insight for Modeling
- Coaching quality and player recruitment skill matter more than raw continuity
- "Programs with strong cultures and good coaches can assemble winning teams relying mostly on the portal, as long as they recruit the right players"
- Suggests continuity should be a secondary feature in models, not a primary predictor

---

## Source 2: Evan Miyakawa (EvanMiya) -- "Which Schools Get the Most Out of Transfers"

- **URL:** https://blog.evanmiya.com/p/which-schools-get-the-most-out-of
- **Platform:** EvanMiya blog (Substack)

### Methodology
- **Core metric:** Bayesian Performance Rating (BPR) -- "the best single metric for capturing a college basketball player's value that he brings while on the court, on a per-possession basis"
- BPR incorporates individual efficiency stats, on-court play-by-play impact, and adjusts for teammate offensive strength and opponent defensive strength
- **Key innovation:** Measures transfer performance *relative to preseason projections*, not absolute production. This isolates the school's development effect from the player's inherent talent.
- **Statistical approach:** Uses Bayesian regression with shrinkage-to-mean to account for small sample sizes at individual programs

### Transfer Portal Ratings
- Each transfer receives a 5-star rating predicting value in next season on a per-possession basis, independent of destination school
- "Expected Transfer Improvement" metric quantifies how much transfers outperform projections at specific schools
- Team Efficiency Differential measures strength gap between sending and receiving programs

### Key Findings
- **Top programs for transfer development:** Arizona (volume approach, ~3 transfers/year) and UConn (quality approach, fewer but more impactful transfers)
- **Best mid-major:** Drake; San Diego State leveraged transfers toward 2023 Final Four
- **Underperformers:** North Carolina, Arkansas, Indiana -- transfers systematically underperform projections, suggesting development/system problems
- **Counterintuitive finding:** Landing high-profile transfers does not indicate coaching effectiveness; elite recruits succeed anywhere

### Data Sources
- EvanMiya.com player database with BPR ratings
- Transfer portal entry/commitment tracking
- Five years of transfer performance data

### Prediction Challenges
- "It's very hard to accurately predict every transfer who will have a big impact in the following year"
- Projecting fit in a new environment is the hardest part of transfer modeling

---

## Source 3: Mid-Major Madness -- "Did Continuity Actually Matter Last Season?"

- **URL:** https://www.midmajormadness.com/2021/8/25/22630784/ncaa-tournament-drexel-saint-marys-loyola-marshall-basketball-teams-to-watch-mid-major-basketball
- **Context:** Analysis of 2020-21 season continuity effects

### Methodology
- Uses KenPom Minutes Continuity to measure returning minutes percentage
- Compares year-over-year KenPom rating changes for teams with highest continuity

### Key Data
- **2020-21 season (COVID era):** 8 of 10 mid-major teams with highest returning minutes improved their KenPom rating
- **Success stories:** Drexel jumped from KenPom 244 to 158 (first NCAA Tournament since 1996); Loyola Chicago rose to KenPom 10 with Sweet 16 run (from 101); Marshall reached KenPom 92
- **Counterexamples:** USC Upstate and Central Connecticut had high continuity but stagnated or declined
- **Pre-pandemic comparison (2018-19 to 2019-20):** High-continuity teams performed *worse*. Air Force (most returning minutes nationally) dropped from 8-10 to 5-13. Seattle (4th in continuity) declined 24 KenPom spots.

### Conclusion
- Continuity provides a modest advantage but is not deterministic
- The pandemic may have amplified continuity's effect (returning players had bigger edge when everyone else was disrupted)
- Normal years show much weaker continuity signal

---

## Source 4: PBS NewsHour -- "How NCAA's Transfer Portal Transformed March Madness"

- **URL:** https://www.pbs.org/newshour/show/how-ncaas-transfer-portal-transformed-march-madness
- **Context:** Reporting on 2025 tournament

### Key Statistics
- More than 53% of rotation players in the 68-team men's tournament field previously played at another D-I school
- Roughly one-third of top-8 minute players on each roster played for a different D-I program just last season

### Structural Changes
- NCAA eliminated sit-out requirements in 2021; further loosened rules in April 2024 (no restrictions on when/where to transfer)
- Programs now bid on players "sort of like free agents in professional sports"
- NIL monetization created financial incentives that accelerate movement

### Impact on Coaching
- Several coaches retired partly due to portal dynamics: Tony Bennett (Virginia), Jay Wright (Villanova), Jim Larranaga (Miami)
- Tom Izzo (Michigan State) notably reached Elite Eight *without* using the transfer portal -- an increasingly rare approach

### Implications for Prediction
- Roster composition is far less stable year-to-year, making preseason projections harder
- Historical team trajectories are less meaningful when rosters turn over 50%+
- Models need to shift from team-level continuity to player-level projection

---

## Source 5: CougCenter / FOX Sports -- Historical Analysis of Championship Profiles

- **URLs:**
  - https://www.cougcenter.com/general/49063/finding-a-march-madness-champion-using-historical-analysis
  - https://www.foxsports.com/stories/college-basketball/kenpom-trends-march-madness-bracket

### Experience as a Predictor
- **17 of 23 national champions since 2002** had a junior or senior as their top contributor
- Last underclassman to lead a champion: Jahlil Okafor (Duke, 2015)
- This 74% rate strongly suggests experienced rosters outperform those relying on young talent

### KenPom Efficiency Thresholds
- 23 of 24 champions ranked top 21 in adjusted offensive efficiency
- 21 of 24 also ranked top 31 in adjusted defensive efficiency
- All 24 champions ranked top 25 in adjusted efficiency margin
- Champions averaged: offensive efficiency rank 8.25, defensive 16.33, overall margin 5.17

### Relevance to Continuity
- Experience matters, but in the portal era, experience can be *acquired* via transfers rather than *developed* internally
- The key question shifts from "how much experience returns?" to "how much experience is on the roster regardless of origin?"

---

## Source 6: Bart Torvik -- RosterCast and Transfer Data Tools

- **URL:** https://barttorvik.com/ and https://torvik.dev/
- **Context:** Analytics platform and open-source R package (toRvik)

### Data Available
- Transfer histories for 5,000+ players back to 2011-12
- Player recruiting rankings for 6,000+ players back to 2007-08
- Returning minutes percentages for all D-I teams (barttorvik.com/returningmins.php)
- RosterCast tool: add/subtract players to project team rating changes

### RosterCast Methodology
- Projects team offensive and defensive efficiency based on roster composition
- Accounts for player-level projections of returning, incoming freshmen, and transfer players
- Useful for scenario modeling (what if Player X transfers in/out?)

### Data Accessibility
- The toRvik R package provides programmatic access to Torvik's data
- Includes transfer_portal() function returning histories with matchable player IDs
- Free and open-source, making it ideal for building custom models

---

## Key Data Sources for Modeling

| Source | URL | What It Provides |
|--------|-----|-----------------|
| KenPom | kenpom.com | Minutes Continuity metric, adjusted efficiency ratings |
| Bart Torvik | barttorvik.com | Returning minutes, RosterCast projections, transfer histories |
| toRvik (R package) | torvik.dev | Programmatic access to Torvik data including transfer histories |
| EvanMiya | evanmiya.com | BPR ratings, transfer portal rankings, player projections |
| On3 Transfer Portal Index | on3.com/transfer-portal | Team-level transfer talent tracking using On3 Performance score |
| Basketball-Reference | basketball-reference.com/friv/continuity.html | NBA-style roster continuity metrics adapted for college |
| 247Sports | 247sports.com | Transfer portal position rankings, commitment tracking |

---

## Modeling Recommendations

Based on the literature review, a prediction model accounting for transfer portal dynamics should consider:

1. **Player-level features over team-level continuity:** Rather than a single "continuity" number, model individual players' projected contributions using BPR or similar per-possession metrics.

2. **Time-varying continuity weight:** Continuity matters more in November/December; discount it as the season progresses and teams gel.

3. **Positional weighting:** Returning a lead guard or anchor big has more impact than returning role players. Weight continuity by position and minutes share.

4. **Program transfer development score:** Some programs systematically over- or under-perform with transfers. Build a historical "transfer alpha" for each program.

5. **Experience composition:** Track total roster experience (juniors/seniors as percentage of minutes) rather than just "returning" experience. In the portal era, a team can have high experience but low continuity.

6. **Coaching stability:** Coaching changes compound roster turnover effects. A new coach with a new roster faces compounding uncertainty.

7. **Portal timing:** Players entering the portal late or arriving late to new programs have less time to integrate, suggesting a "time-to-integrate" feature could help.
