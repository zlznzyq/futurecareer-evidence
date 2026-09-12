# Data Provenance and Quality Gates

## Provenance chain

Every displayed metric follows:

```text
source
→ source version
→ raw field
→ occupation mapping
→ transformation
→ release metric
→ web JSON
→ UI
```

## Quality gates

A public metric is blocked if any of the following is true:

- source is unknown;
- occupation mapping cannot be identified;
- transformation is undocumented;
- scale is ambiguous;
- a SOC2 value is presented as SOC6;
- a missing value is silently imputed;
- a third-party sample is presented as population data.

## Missing data

Default rule:

> preserve missingness.

No arbitrary zero-fill is allowed unless zero is explicitly the source value.

## Crosswalks

Multi-mappings are retained with mapping count/confidence. Extreme ILO–Anthropic gaps require mapping QA before being used as public case studies.

## Versioning

Public releases must preserve:

- source version;
- crosswalk version;
- metric version;
- model version;
- release date;
- SHA-256 manifest.
