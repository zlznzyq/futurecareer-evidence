# Metric Dictionary v1.0

Every public number must have a source, formula, grain and interpretation.

| Metric | Formula / transformation | Source | Grain | Meaning |
|---|---|---|---|---|
| Employment Growth | $(E_{2035}-E_{2025})/E_{2025}$ | BLS | SOC6 | projected change |
| Opening Rate | Annual Openings / Employment 2025 | BLS | SOC6 | opportunity relative to occupation size |
| Percentile Score | $100\times PercentileRank(x)$ | derived | release universe | relative position |
| Market Opportunity | $0.55G+0.45O$ | BLS-derived | SOC6 | market summary |
| Wage Position | wage percentile | BLS | SOC6 | relative wage |
| AI Potential Exposure | source-aligned exposure; percentile separate | ILO 2025 | mapped SOC6 | potential task exposure |
| Observed AI Usage | source-aligned use; percentile separate | Anthropic | mapped SOC6 | observed AI use |
| Human Structure Beta | equal mean of 5 dimension composites | O*NET 31.0 | SOC6 | human work structure |
| Future Skill Alignment v1 | weighted mapped BLS skill percentiles | BLS + WEF | SOC6 | alignment with WEF rising skills |
| CEI Beta | $0.35M+0.25W+0.20H+0.20F$ | derived | SOC6 | descriptive composite |
| Personal Fit Beta | normalized user weights × occupation scores | user + derived | session/browser | preference alignment |
| RPLS Trends | annualized log-linear monthly trend | RPLS | SOC2 | broad historical context |

## Human Structure proxies

**Physicality**
- Performing General Physical Activities
- Handling and Moving Objects
- Operating Vehicles, Mechanized Devices, or Equipment

**Judgment**
- Making Decisions and Solving Problems
- Frequency of Decision Making
- Freedom to Make Decisions

**Interaction**
- Contact With Others
- Coordinate or Lead Others
- Deal With External Customers or the Public
- Face-to-Face Discussions
- Resolving Conflicts and Negotiating

**Responsibility**
- Consequence of Error
- Impact of Decisions on Co-workers or Company Results

**Context**
- Conflict Situations
- Freedom to Make Decisions
- Frequency of Decision Making

## Public rule
No metric enters the UI without:
1. source/version;
2. raw/upstream field;
3. transformation;
4. occupation/geographic grain;
5. missing-value rule;
6. interpretation boundary.

## Geographic scope

The current production dataset is primarily **United States occupation data**.

- BLS: U.S.
- O*NET: U.S.
- RPLS: U.S. labor-market context.
- ILO and Anthropic measures are mapped into the U.S. occupation backbone.

U.S. wages and employment projections must not be presented as China-local outcomes.

## Personal Fit missing-data rule

For occupation $o$:

$$
PersonalFit_o=
\frac{\sum_{k\in A_o}w_kS_{o,k}}
{\sum_{k\in A_o}w_k}
$$

where $A_o$ contains only metrics actually available for occupation $o$.

Missing metrics are **not** filled with zero, 50, or another neutral value.
