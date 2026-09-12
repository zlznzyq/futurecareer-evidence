from pathlib import Path
import pandas as pd, json
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data/career_metrics_v0_6.csv')
assert len(df)==867 and df.soc6.is_unique
for c in ['career_evidence_index_beta','market_opportunity_score','growth_score','opening_score','wage_score','future_skill_fit_score','ai_potential_exposure_score','ai_observed_usage_score','HumanMoat_seed_equal_weight','Physicality','Judgment','Interaction','Responsibility','Context']:
 x=df[c].dropna(); assert ((x>=0)&(x<=100)).all(),c
web=json.loads((ROOT/'web/data/careers.json').read_text(encoding='utf-8'))
assert len(web)==867 and len({x['soc'] for x in web})==867
assert all('soc2Context' in x for x in web)
long=pd.read_csv(ROOT/'data/longitudinal/SOC2_Longitudinal_Master_v0_6.csv')
assert long.soc2d_code.is_unique and len(long)>=20
for f in ['README.md','RELEASE_NOTES_v0.6.0.md','docs/LONGITUDINAL_VALIDATION.md','docs/PROCESSING_LOG.md','docs/DATA_SOURCES.md','docs/PUBLIC_LAUNCH_CHECKLIST.md','web/index.html','web/methodology.html','web/app.js','web/style.css']:
 assert (ROOT/f).exists(),f
print('PASS: FutureCareer v0.6.0 release validation')
