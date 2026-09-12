from pathlib import Path
import pandas as pd, numpy as np
from scipy.stats import pearsonr, spearmanr

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw_external'
OUT=ROOT/'data/longitudinal'; RES=ROOT/'results/longitudinal'
OUT.mkdir(parents=True,exist_ok=True); RES.mkdir(parents=True,exist_ok=True)
required=['employment_soc.csv','postings_by_occupation.csv','hiring_and_attrition_by_occupation.csv','salaries_soc.csv']
missing=[f for f in required if not (RAW/f).exists()]
if missing: raise SystemExit('Missing raw RPLS files in data/raw_external: '+', '.join(missing))
emp=pd.read_csv(RAW/'employment_soc.csv'); post=pd.read_csv(RAW/'postings_by_occupation.csv'); ha=pd.read_csv(RAW/'hiring_and_attrition_by_occupation.csv'); sal=pd.read_csv(RAW/'salaries_soc.csv')
for d in [emp,post,ha,sal]: d['month']=pd.to_datetime(d['month'])
for c in ['salary_nsa','salary_sa']:
    sal[c]=pd.to_numeric(sal[c].astype(str).str.replace('$','',regex=False).str.replace(',','',regex=False),errors='coerce')
post=post[post.soc2d_code.between(11,53)].copy(); sal=sal[sal.soc2d_code.between(11,53)].copy()
panel=emp.merge(post,on=['month','soc2d_code'],how='outer',suffixes=('_emp','_post')).merge(sal,on=['month','soc2d_code'],how='outer').merge(ha,on=['month','soc2d_code'],how='outer',suffixes=('','_ha'))
namecols=[c for c in panel if 'soc2d_name' in c];panel['soc2d_name']=panel[namecols].bfill(axis=1).iloc[:,0];panel=panel.drop(columns=[c for c in namecols if c!='soc2d_name']).sort_values(['soc2d_code','month'])
panel.to_csv(OUT/'RPLS_SOC2_Monthly_Panel.csv',index=False,encoding='utf-8-sig')
print('Built',len(panel),'SOC2-month rows. Run scripts/validate_release.py for release checks.')
