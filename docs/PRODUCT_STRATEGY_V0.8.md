# Product Strategy v0.8

## Goal
Move from a career database to a career decision tool without weakening research discipline.

`Discover → Understand → Compare → Personalize → Save → Return`

## Features
- **Career Snapshot**: 10-second interpretation of market, wage, AI change and raw facts.
- **Compare**: up to 3 occupations on the same evidence scale.
- **CEI Beta**: retained as a descriptive index, not a success probability.
- **Personal Fit — Limited Open Beta**: user-controlled weights × occupation evidence.
- **Save & Watch**: browser-local saved careers in v0.8; real notifications require a later backend and explicit consent.

## Personal Fit

$$
PersonalFit_{u,o}=\sum_k w_{u,k}S_{o,k},\qquad \sum_k w_{u,k}=1
$$

The score reflects **user preferences × occupation evidence**. It does not predict individual success.

## Retention hypothesis
Users return when saved careers change, new source releases arrive, or their decision priorities change.

## Monetization
Not a v0.8 priority. Future candidates include personalized reports, school dashboards, monitoring and API/data access.
