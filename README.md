<div align="center">

# FutureCareer Evidence

### Open, explainable career intelligence for the AI era

[中文说明](README.zh-CN.md) · [Live Demo](https://zlznzyq.github.io/futurecareer-evidence/) · [Methodology](docs/METRIC_DICTIONARY.md)

**867 U.S. occupations · public evidence · transparent formulas · decision tools**

> **Current data scope: United States.** China-facing beta users should treat U.S. wage/employment evidence as an international reference, not China-local labor-market outcomes.

</div>

![FutureCareer preview](assets/futurecareer-preview.png)

## What it does

FutureCareer helps users:

**understand → compare → personalize → save → revisit**

It separates market opportunity, wages, potential AI exposure, observed AI use, skills and human work structure.

> **AI exposure is not a replacement probability.**

## Decision tools

- Career Snapshot
- CEI Beta
- 3-career Compare
- Personal Fit Open Beta
- Save & Watch preview
- evidence cards with source + formula
- public methodology and reproducible research

## Data

O*NET 31.0 · BLS 2025–2035 · BLS Skills 2025 · ILO 2025 · Anthropic Economic Index · WEF 2025 · public RPLS history.

## Key formulas

$$
Market=0.55\times GrowthScore+0.45\times OpeningScore
$$

$$
CEI=0.35M+0.25W+0.20H+0.20F
$$

$$
PersonalFit=\frac{\sum_k w_kS_k}{\sum_k w_k}
$$

Future Skill Alignment v1 is rebuilt from an explicit WEF→BLS crosswalk with rank weights and mapping-confidence weights.

[See every metric →](docs/METRIC_DICTIONARY.md)

## Research discipline

- fact ≠ score ≠ inference
- source scale ≠ percentile
- SOC2 history ≠ SOC6 career history
- correlation ≠ causation
- missing data are not silently zero-filled

## Run

```bash
cd web
python -m http.server 8000
```

## Status

**v1.0.0 Launch Release Candidate**

Code can be open-sourced under the repository license. Third-party data retain upstream terms.
