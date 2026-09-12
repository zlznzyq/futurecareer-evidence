# Reproducibility

## Fast path

The repository already contains processed public research outputs. Validate the release with:

```bash
python scripts/validate_release.py
```

## Rebuild the RPLS longitudinal panel

1. Download the four public occupation Timeseries files listed in `data/raw_external/README.md`.
2. Place them in `data/raw_external/`.
3. Run:

```bash
python scripts/build_longitudinal.py
```

## Cross-sectional research

`data/research_input/US_Occupation_Master_Matrix_V2_1.csv` is the frozen research input used by the V3.1 cross-sectional analysis. The original analysis script is preserved as `scripts/fc_v31_analysis_reference.py` for auditability.

The public release separates three levels:

```text
upstream raw data
→ frozen/derived research input
→ research outputs + product metrics
```

This prevents the website from silently changing when an upstream source updates.

## Release integrity

`MANIFEST.csv` contains SHA-256 hashes for release files.
