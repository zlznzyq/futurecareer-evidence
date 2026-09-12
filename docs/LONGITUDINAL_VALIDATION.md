# Longitudinal External Validation

## Purpose

RPLS adds a public historical labor-market layer. It is used for **external validation**, not as SOC6 career history.

## Grain

RPLS occupation files are SOC 2-digit. FutureCareer's main research unit is SOC6. Therefore:

```text
SOC6 cross-sectional analysis
+ SOC2 longitudinal external validation
```

A SOC6 career page may show its broader SOC2 trend only when clearly labeled **Broad occupation-group context**.

## Common window

The primary longitudinal window is **2022-01 through 2026-08**, because employment, postings, salary, hiring and attrition all overlap there.

Sensitivity windows:

- 2023-01 through 2026-08
- 2024-01 through 2026-08

This avoids comparing metrics estimated from different start dates.

## Trend

For positive series:

$$
Trend_o=100(\exp(\hat\beta_o)-1)
$$

where $\hat\beta_o$ is the annual slope from a log-linear fit.

## Aggregating AI / Human Structure

SOC6 measures are aggregated to SOC2 using 2025 BLS employment weights:

$$
X_g=\frac{\sum_{j\in g}Employment_jX_j}{\sum_{j\in g}Employment_j}
$$

## Robustness

The release reports:

- Pearson correlation;
- Spearman correlation;
- three time windows;
- leave-one-SOC2-out Spearman sensitivity.

With only about 22 major groups, these are exploratory results.

## Interpretation boundary

Do not write:

> AI caused hiring / employment changes.

Allowed:

> At the broad SOC2 level, AI exposure is associated with observed historical labor-market dynamics.

The analysis is too aggregated and observational for causal claims.
