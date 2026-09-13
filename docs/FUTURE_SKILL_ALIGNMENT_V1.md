# Future Skill Alignment v1

## Purpose
Replace the earlier provisional skill-fit number with an auditable mapping.

## WEF source
World Economic Forum, *Future of Jobs Report 2025*, top skills on the rise toward 2030.

## Formula

$$
F_o=
\frac{\sum_j BLS_{o,j}\times RankWeight_j\times MappingConfidence_j}
{\sum_j RankWeight_j\times MappingConfidence_j}
$$

- `BLS_{o,j}`: BLS 2025 occupation skill percentile.
- `RankWeight`: 10 for WEF rank 1 through 1 for rank 10.
- `MappingConfidence`: documented in `data/WEF_BLS_Skill_Crosswalk_v1.csv`.
- Unmapped WEF skills are excluded rather than guessed.

## Important
This is a transparent **Beta alignment index**, not a validated forecast of future employability.
