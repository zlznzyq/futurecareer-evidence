# Metric Dictionary

Every public number must have a source, formula and interpretation.

| Public metric | Raw evidence | Transformation | Source | Interpretation |
|---|---|---|---|---|
| Employment Growth | Employment 2025, Employment 2035 | $(E_{2035}-E_{2025})/E_{2025}$ | BLS 2025–2035 | projected employment change |
| Growth Score | Employment Growth | $100\times PercentileRank$ | derived from BLS | relative occupation position |
| Opening Rate | Annual openings, Employment 2025 | $Openings/E_{2025}$ | BLS | openings relative to occupation size |
| Opening Score | Opening Rate | $100\times PercentileRank$ | derived from BLS | relative occupation position |
| Market Opportunity | Growth Score, Opening Score | $0.55G+0.45O$ | transparent beta formula | descriptive market summary |
| Wage Position | Median annual wage 2025 | $100\times PercentileRank$ | BLS | relative wage position |
| AI Potential Exposure | occupation/task exposure | source-aligned scale; percentile stored separately | ILO 2025 | potential GenAI task exposure |
| Observed AI Usage | observed occupation/task usage | source-aligned scale; percentile stored separately | Anthropic Economic Index | observed use in Anthropic data |
| Exposure Gap | ILO percentile, Anthropic percentile | $Pctl(Observed)-Pctl(Potential)$ | derived | potential-vs-observed rank difference |
| Physicality | O*NET activity/context variables | normalized composite | O*NET 31.0 | embodied/physical work structure |
| Judgment | O*NET variables | normalized composite | O*NET 31.0 | judgment/decision structure |
| Interaction | O*NET variables | normalized composite | O*NET 31.0 | interpersonal work structure |
| Responsibility | O*NET variables | normalized composite | O*NET 31.0 | responsibility/consequence structure |
| Context | O*NET variables | normalized composite | O*NET 31.0 | contextual/decision dependence |
| Human Structure Beta | five dimensions | equal-weight seed; alternatives tested | O*NET-derived | descriptive occupational structure |
| Future Skill Fit Beta | BLS skill profile + WEF trend map | documented weighted alignment | BLS Skills + WEF 2025 | alignment with employer-reported future skill directions |
| Career Evidence Index Beta | Market, Wage, Human Structure, Future Skill | $0.35M+0.25W+0.20H+0.20F$ | derived | optional descriptive summary, not forecast probability |
| RPLS Employment Trend | monthly SOC2 employment | annualized log-linear trend | RPLS | broad occupation-group history |
| RPLS Posting Trend | monthly SOC2 postings | annualized log-linear trend | RPLS | broad occupation-group posting history |
| RPLS Salary Trend | monthly SOC2 salary | annualized log-linear trend | RPLS | broad occupation-group salary history |
| Hiring / Attrition | monthly SOC2 rates | source rate / period summary | RPLS | broad occupation-group labor flow |

## Percentile convention

When the product displays a percentile score:

$$
Score_o=100\times PercentileRank(x_o)
$$

The comparison universe and version must remain fixed within a release.

## Important distinction

A source-scaled AI exposure value and an occupation percentile are different quantities. The UI should label both explicitly whenever both are shown.

## No hidden numbers

A metric must not enter the public interface unless the repository contains:

1. raw/source field reference;
2. transformation rule;
3. source/version;
4. missing-value behavior;
5. geographic and occupation granularity.
