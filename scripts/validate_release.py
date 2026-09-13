from pathlib import Path
import pandas as pd, json, math
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data/career_metrics_v1_0.csv')
assert len(df)==867 and df.soc6.is_unique
for c in ['career_evidence_index_beta','market_opportunity_score','wage_score','future_skill_fit_score','ai_potential_exposure_score','ai_observed_usage_score','HumanMoat_seed_equal_weight','Physicality','Judgment','Interaction','Responsibility','Context']:
    x=df[c].dropna()
    assert ((x>=0)&(x<=100)).all(), c
assert (df.loc[df['career_evidence_index_beta'].notna(),['market_opportunity_score','wage_score','HumanMoat_seed_equal_weight','future_skill_fit_score']].notna().all(axis=1)).all()
web=json.loads((ROOT/'web/data/careers.json').read_text(encoding='utf-8'))
assert len(web)==867 and len({x['soc'] for x in web})==867
assert 'NaN' not in (ROOT/'web/data/careers.json').read_text(encoding='utf-8')
cw=pd.read_csv(ROOT/'data/WEF_BLS_Skill_Crosswalk_v1.csv')
assert len(cw)==10 and (cw.mapping_confidence.between(0,1)).all()
for f in ['README.md','README.zh-CN.md','docs/METRIC_DICTIONARY.md','docs/FUTURE_SKILL_ALIGNMENT_V1.md','docs/PRODUCT_REQUIREMENTS_V1.md','docs/LAUNCH_QA.md','web/index.html','web/methodology.html','web/app.js','web/style.css']:
    assert (ROOT/f).exists(),f
print('PASS: FutureCareer Evidence v1.0.0 launch validation')
