# Reproducible Processing Log

This file is intentionally detailed. The public README stays short.

## Inputs

### O*NET
- Version: 31.0
- Occupational structure, tasks, skills, abilities, activities and context.

### BLS
- Employment Projections: 2025–2035
- Skills: 2025
- Tables used include 1.2, 1.10, 1.12 and 6.5.

### ILO
- 2025 refined GenAI occupational exposure.
- ISCO-08 taxonomy.

### Anthropic
- Economic Index releases supplied in the project archive.
- Observed occupation/task AI-use evidence.

### Crosswalks
- O*NET-SOC 2019 → SOC 2018
- SOC 2010 ↔ SOC 2018
- ISCO-08 ↔ SOC 2010

## Processing order

### Step 1 — preserve raw files
Never edit the source files in place.

### Step 2 — normalize identifiers
Convert occupation identifiers to explicit string keys.

### Step 3 — crosswalk
Build:

```text
O*NET-SOC
→ SOC2018
→ SOC2010
→ ISCO08
```

Keep one-to-many mappings.

### Step 4 — map ILO
For occupations with multiple valid ISCO mappings, retain:

```text
mean exposure
minimum exposure
maximum exposure
mapping count
mapping confidence
```

### Step 5 — map Anthropic
Join observed-use measures at the compatible SOC/task level.
Keep release/version metadata.

### Step 6 — construct O*NET Human Structure proxies
Build five dimensions from observable O*NET variables:

```text
Physicality
Judgment
Interaction
Responsibility
Context
```

### Step 7 — aggregate research unit
BLS outcomes are SOC6.

Therefore:

```text
1,016 O*NET detailed rows
→ 867 unique SOC6 research occupations
```

This prevents duplicated BLS outcomes from being treated as independent observations.

### Step 8 — BLS outcomes
Construct:

$$
Growth_o=
\frac{Employment_{2035}-Employment_{2025}}
{Employment_{2025}}
$$

$$
OpeningRate_o=
\frac{AnnualOpenings_o}{Employment_{2025,o}}
$$

Use log wage in robustness models.

### Step 9 — product normalization
For comparable numeric indicators:

$$
Score_o=100\times PercentileRank(x_o)
$$

Raw values remain stored.

### Step 10 — measurement validation
Human Structure:
- Cronbach alpha
- PCA
- parallel analysis with 2,000 random simulations
- exploratory factor analysis
- BLS-skill discriminant validity

Random seed:

```text
20260912
```

### Step 11 — independent AI validation
From BLS Table 1.12, flag SOC6 occupations whose utilization notes explicitly contain:

```text
AI
artificial intelligence
```

Aggregate to unique SOC6.

Compare ILO and Anthropic scores between flagged and unflagged occupations.

### Step 12 — exposure gap
For occupations with both AI measures:

$$
Gap_o=
Percentile(Anthropic_o)-Percentile(ILO_o)
$$

Do not interpret extreme gaps without manual mapping review.

### Step 13 — regression validation
Current research models use:
- HC3 robust standard errors
- major occupation fixed effects
- education controls
- log employment size
- self-employment controls
- alternative Human Structure definitions

### Step 14 — predictive validation
Use:
- random 5-fold CV
- major-SOC grouped CV

Grouped CV is the stricter benchmark.

### Step 15 — release
Each release contains:
- processed data
- results
- figures
- methodology
- source/version notes
- SHA-256 manifest

## Known non-reproducible external dependency

Full licensed historical job-posting data has not yet been obtained.

Revelio samples are excluded from population inference and production scores.

## Required rule

A future contributor must be able to trace:

```text
Displayed score
→ transformed metric
→ raw value
→ occupation mapping
→ source/version
```

## Release QA

The public release runs `scripts/validate_release.py` after processed metrics and web JSON are generated. It verifies occupation uniqueness, score ranges, JSON integrity and required documentation.

## RPLS longitudinal extension

1. Preserve four public RPLS occupation CSVs.
2. Parse month and use seasonally adjusted series.
3. Outer-join by month × SOC2.
4. Use 2022-01–2026-08 as the primary common window.
5. Estimate annualized log trends.
6. Aggregate SOC6 AI/Human metrics to SOC2 with BLS employment weights.
7. Run Pearson/Spearman correlations.
8. Re-estimate over 2023–2026 and 2024–2026.
9. Run leave-one-SOC2-out rank-correlation sensitivity.
10. Export only broad-group historical context to the website.

## Public-release provenance gate

See `docs/METRIC_DICTIONARY.md` and `docs/PROVENANCE.md`. A number cannot enter the public UI without a documented source, raw field or upstream metric, transformation, geography/occupation grain, and release version.
