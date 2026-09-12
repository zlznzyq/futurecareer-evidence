from pathlib import Path
import pandas as pd, numpy as np, shutil, json, hashlib, zipfile, re, math, sys
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt

SRC=Path('/mnt/data/recovered_v05/futurecareer-v0.5.0-final-rc')
LONG=Path('/mnt/data/FutureCareer_v0.6_longitudinal')
ROOT=Path('/mnt/data/futurecareer-v0.6.0-open-research-beta')
if ROOT.exists(): shutil.rmtree(ROOT)
shutil.copytree(SRC,ROOT)
for d in ['data/longitudinal','results/longitudinal','figures_longitudinal','docs','scripts','qa']:
    (ROOT/d).mkdir(parents=True,exist_ok=True)

panel=pd.read_csv(LONG/'data/RPLS_SOC2_Monthly_Panel_2021_2026.csv',parse_dates=['month'])
base=pd.read_csv('/mnt/data/FutureCareer_Research_Analysis_V3.1/Analysis_SOC6_Master_V3_1.csv')
prod=pd.read_csv(ROOT/'data/career_metrics_v0_3.csv')

# ---------- longitudinal rebuild with common windows ----------
# primary common window is 2022-01 through 2026-08 because all four datasets overlap there.
windows={'common_2022':'2022-01-01','post_chatgpt_2023':'2023-01-01','recent_2024':'2024-01-01'}
end=pd.Timestamp('2026-08-01')

def annual_log_trend(g,col,start):
    q=g.loc[(g.month>=pd.Timestamp(start))&(g.month<=end),['month',col]].dropna().sort_values('month')
    if len(q)<12: return (len(q),np.nan,np.nan,np.nan,np.nan)
    y=pd.to_numeric(q[col],errors='coerce').values.astype(float)
    t=(q.month-q.month.min()).dt.days.values/365.25
    ok=np.isfinite(y)&(y>0)
    if ok.sum()<12:return (len(q),np.nan,np.nan,np.nan,np.nan)
    slope=np.polyfit(t[ok],np.log(y[ok]),1)[0]
    ann=(np.exp(slope)-1)*100
    total=(y[ok][-1]/y[ok][0]-1)*100
    return (len(q),y[ok][0],y[ok][-1],total,ann)

rows=[]
for soc,g in panel.groupby('soc2d_code'):
    if not (11<=int(soc)<=53): continue
    r={'soc2d_code':int(soc),'soc2d_name':g.soc2d_name.dropna().iloc[0] if g.soc2d_name.notna().any() else ''}
    for w,start in windows.items():
        for prefix,col in [('employment','employment_sa'),('postings','active_postings_sa'),('salary','salary_sa')]:
            n,s,e,total,ann=annual_log_trend(g,col,start)
            r[f'{prefix}_{w}_n']=n;r[f'{prefix}_{w}_start']=s;r[f'{prefix}_{w}_end']=e;r[f'{prefix}_{w}_total_pct']=total;r[f'{prefix}_{w}_annualized_pct']=ann
        q=g[(g.month>=pd.Timestamp(start))&(g.month<=end)]
        for c in ['rl_hiring_rate','rl_attrition_rate']:
            z=pd.to_numeric(q[c],errors='coerce').dropna();r[f'{c}_{w}_mean']=z.mean() if len(z) else np.nan
        r[f'net_hiring_rate_{w}_mean']=r[f'rl_hiring_rate_{w}_mean']-r[f'rl_attrition_rate_{w}_mean']
    rows.append(r)
trends=pd.DataFrame(rows)

# aggregate SOC6 research metrics to SOC2 with employment weights
m=base.copy();m['soc2d_code']=pd.to_numeric(m.soc6.astype(str).str[:2],errors='coerce')
vars=['ilo_exposure_mean','observed_exposure','HumanMoat_seed_equal_weight','Physicality','Judgment','Interaction','Responsibility','Context']
agg=[]
for soc,g in m.groupby('soc2d_code'):
    if pd.isna(soc) or not (11<=int(soc)<=53):continue
    w=pd.to_numeric(g['Employment, 2025'],errors='coerce').fillna(0).clip(lower=0)
    r={'soc2d_code':int(soc),'soc6_count':g.soc6.nunique(),'employment2025_sum':w.sum()}
    for v in vars:
        x=pd.to_numeric(g[v],errors='coerce');ok=x.notna()&(w>0)
        r[v+'_weighted']=np.average(x[ok],weights=w[ok]) if ok.any() and w[ok].sum()>0 else x.mean()
    agg.append(r)
agg=pd.DataFrame(agg)
long=agg.merge(trends,on='soc2d_code',how='inner')
long.to_csv(ROOT/'data/longitudinal/SOC2_Longitudinal_Master_v0_6.csv',index=False,encoding='utf-8-sig')
panel.to_csv(ROOT/'data/longitudinal/RPLS_SOC2_Monthly_Panel.csv',index=False,encoding='utf-8-sig')

# correlation sensitivity across windows
preds=['ilo_exposure_mean_weighted','observed_exposure_weighted','HumanMoat_seed_equal_weight_weighted']
out_prefixes=['employment','postings','salary']
res=[]
for w in windows:
    outcomes=[f'{p}_{w}_annualized_pct' for p in out_prefixes]+[f'rl_hiring_rate_{w}_mean',f'rl_attrition_rate_{w}_mean',f'net_hiring_rate_{w}_mean']
    for x in preds:
        for y in outcomes:
            q=long[[x,y]].dropna()
            if len(q)>=10:
                pr,pp=pearsonr(q[x],q[y]);sr,sp=spearmanr(q[x],q[y])
                res.append([w,x,y,len(q),pr,pp,sr,sp])
corr=pd.DataFrame(res,columns=['window','predictor','outcome','n','pearson_r','pearson_p','spearman_rho','spearman_p'])
corr.to_csv(ROOT/'results/longitudinal/SOC2_Longitudinal_Sensitivity.csv',index=False)

# Leave-one-SOC2-out sensitivity for headline correlations in common window
loo=[]
headline=['employment_common_2022_annualized_pct','postings_common_2022_annualized_pct','salary_common_2022_annualized_pct','rl_hiring_rate_common_2022_mean','rl_attrition_rate_common_2022_mean']
for x in ['ilo_exposure_mean_weighted','observed_exposure_weighted']:
    for y in headline:
        q=long[['soc2d_code',x,y]].dropna().copy()
        vals=[]
        for drop in q.soc2d_code:
            qq=q[q.soc2d_code!=drop]
            if len(qq)>=10: vals.append(spearmanr(qq[x],qq[y]).statistic)
        if vals:
            loo.append([x,y,len(q),np.min(vals),np.median(vals),np.max(vals),np.mean(np.sign(vals)==np.sign(np.median(vals)))])
loo=pd.DataFrame(loo,columns=['predictor','outcome','n','loo_rho_min','loo_rho_median','loo_rho_max','sign_stability'])
loo.to_csv(ROOT/'results/longitudinal/SOC2_LeaveOneOut_Sensitivity.csv',index=False)

# map SOC2 context into product records (explicitly labeled broad-group context)
soc2cols=['soc2d_code','soc2d_name','employment_common_2022_annualized_pct','postings_common_2022_annualized_pct','salary_common_2022_annualized_pct','rl_hiring_rate_common_2022_mean','rl_attrition_rate_common_2022_mean','net_hiring_rate_common_2022_mean']
ctx=long[soc2cols].copy()
prod['soc2d_code']=pd.to_numeric(prod.soc6.astype(str).str[:2],errors='coerce')
prod=prod.merge(ctx,on='soc2d_code',how='left')
prod.to_csv(ROOT/'data/career_metrics_v0_6.csv',index=False,encoding='utf-8-sig')

# web JSON enrichment
webpath=ROOT/'web/data/careers.json'
records=json.loads(webpath.read_text(encoding='utf-8'))
ctxmap=ctx.set_index('soc2d_code').to_dict('index')
for x in records:
    try:s2=int(str(x['soc'])[:2])
    except:continue
    c=ctxmap.get(s2,{})
    def clean(v): return None if pd.isna(v) else round(float(v),3) if isinstance(v,(float,np.floating)) else v
    x['soc2Context']={k:clean(v) for k,v in c.items()}
webpath.write_text(json.dumps(records,ensure_ascii=False),encoding='utf-8')

# ---------- figures ----------
figdir=ROOT/'figures_longitudinal'
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':10})
# scatter 1
for i,(x,label) in enumerate([('ilo_exposure_mean_weighted','ILO potential exposure'),('observed_exposure_weighted','Anthropic observed AI use')],1):
    y='employment_common_2022_annualized_pct';q=long[[x,y]].dropna();rho=spearmanr(q[x],q[y]).statistic
    plt.figure(figsize=(6.4,4.8));plt.scatter(q[x],q[y],s=35,alpha=.75)
    for _,r in q.iterrows():
        pass
    plt.xlabel(label);plt.ylabel('RPLS employment annualized trend, %')
    plt.title(f'Longitudinal external validation: employment (Spearman ρ={rho:.2f}, n={len(q)})')
    plt.tight_layout();plt.savefig(figdir/f'FigureL{i}_AI_Employment_300dpi.png',dpi=300);plt.close()
# hiring attrition
q=long[['ilo_exposure_mean_weighted','rl_hiring_rate_common_2022_mean','rl_attrition_rate_common_2022_mean']].dropna().sort_values('ilo_exposure_mean_weighted')
plt.figure(figsize=(6.5,4.8));plt.plot(q.ilo_exposure_mean_weighted,q.rl_hiring_rate_common_2022_mean,marker='o',label='Hiring');plt.plot(q.ilo_exposure_mean_weighted,q.rl_attrition_rate_common_2022_mean,marker='o',label='Attrition');plt.xlabel('ILO potential AI exposure');plt.ylabel('Mean RPLS rate');plt.title('Hiring and attrition across SOC2 groups, 2022–2026');plt.legend(frameon=False);plt.tight_layout();plt.savefig(figdir/'FigureL3_Hiring_Attrition_300dpi.png',dpi=300);plt.close()

# ---------- docs ----------
(ROOT/'docs/LONGITUDINAL_VALIDATION.md').write_text('''# Longitudinal External Validation\n\n## Purpose\n\nRPLS adds a public historical labor-market layer. It is used for **external validation**, not as SOC6 career history.\n\n## Grain\n\nRPLS occupation files are SOC 2-digit. FutureCareer's main research unit is SOC6. Therefore:\n\n```text\nSOC6 cross-sectional analysis\n+ SOC2 longitudinal external validation\n```\n\nA SOC6 career page may show its broader SOC2 trend only when clearly labeled **Broad occupation-group context**.\n\n## Common window\n\nThe primary longitudinal window is **2022-01 through 2026-08**, because employment, postings, salary, hiring and attrition all overlap there.\n\nSensitivity windows:\n\n- 2023-01 through 2026-08\n- 2024-01 through 2026-08\n\nThis avoids comparing metrics estimated from different start dates.\n\n## Trend\n\nFor positive series:\n\n$$\nTrend_o=100(\\exp(\\hat\\beta_o)-1)\n$$\n\nwhere $\\hat\\beta_o$ is the annual slope from a log-linear fit.\n\n## Aggregating AI / Human Structure\n\nSOC6 measures are aggregated to SOC2 using 2025 BLS employment weights:\n\n$$\nX_g=\\frac{\\sum_{j\\in g}Employment_jX_j}{\\sum_{j\\in g}Employment_j}\n$$\n\n## Robustness\n\nThe release reports:\n\n- Pearson correlation;\n- Spearman correlation;\n- three time windows;\n- leave-one-SOC2-out Spearman sensitivity.\n\nWith only about 22 major groups, these are exploratory results.\n\n## Interpretation boundary\n\nDo not write:\n\n> AI caused hiring / employment changes.\n\nAllowed:\n\n> At the broad SOC2 level, AI exposure is associated with observed historical labor-market dynamics.\n\nThe analysis is too aggregated and observational for causal claims.\n''',encoding='utf-8')

# concise release notes
(ROOT/'RELEASE_NOTES_v0.6.0.md').write_text('''# FutureCareer v0.6.0 — Open Research Beta\n\n## New\n\n- Public RPLS historical labor-market layer\n- 2022–2026 common-window longitudinal validation\n- employment, job openings, salary, hiring and attrition dynamics\n- three-window sensitivity analysis\n- leave-one-SOC2-out robustness\n- broad occupation-group context in the web dataset\n\n## Research stance\n\nThe longitudinal evidence does not support treating AI exposure as a direct job-decline probability.\n\nResults remain exploratory because RPLS occupation history is SOC2, not SOC6.\n\n## Public promise\n\nThe open version is designed to be reproducible without a proprietary labor-market database.\n''',encoding='utf-8')

# update README with longitudinal section
readme=(ROOT/'README.md').read_text(encoding='utf-8')
longsec='''\n## New in v0.6 — public longitudinal labor-market evidence\n\nFutureCareer now adds public RPLS occupation time series for:\n\n- employment;\n- job openings;\n- hiring and attrition;\n- salaries.\n\nThe historical layer is SOC2 and is kept separate from the SOC6 career-level analysis. The primary common window is **2022–2026**.\n\n![Longitudinal employment validation](figures_longitudinal/FigureL1_AI_Employment_300dpi.png)\n\nThis makes the public research pipeline reproducible without requiring a proprietary job-posting database.\n\n[Read the longitudinal methodology →](docs/LONGITUDINAL_VALIDATION.md)\n'''
readme=readme.replace('## Human Structure',longsec+'\n## Human Structure')
readme=readme.replace('**v0.5.0 Research Beta — release candidate**','**v0.6.0 Open Research Beta — release candidate**')
(ROOT/'README.md').write_text(readme,encoding='utf-8')

# update changelog
with open(ROOT/'CHANGELOG.md','w',encoding='utf-8') as f:
    f.write('''# Changelog\n\n## v0.6.0 — Open Research Beta\n\n### Added\n- public RPLS historical labor-market layer\n- SOC2 monthly panel, 2021/2022–2026\n- common 2022–2026 validation window\n- sensitivity windows beginning 2023 and 2024\n- leave-one-group robustness\n- longitudinal research figures\n- SOC2 context fields for the web layer\n\n### Guardrail\nSOC2 historical data are never presented as SOC6-specific historical facts.\n\n## v0.5.0 — Research Beta\nSee repository history for the measurement-validation release.\n''')

# update processing log
with open(ROOT/'docs/PROCESSING_LOG.md','a',encoding='utf-8') as f:
    f.write('''\n## RPLS longitudinal extension\n\n1. Preserve four public RPLS occupation CSVs.\n2. Parse month and use seasonally adjusted series.\n3. Outer-join by month × SOC2.\n4. Use 2022-01–2026-08 as the primary common window.\n5. Estimate annualized log trends.\n6. Aggregate SOC6 AI/Human metrics to SOC2 with BLS employment weights.\n7. Run Pearson/Spearman correlations.\n8. Re-estimate over 2023–2026 and 2024–2026.\n9. Run leave-one-SOC2-out rank-correlation sensitivity.\n10. Export only broad-group historical context to the website.\n''')

# ---------- web changes: add broad dynamics card ----------
app=(ROOT/'web/app.js').read_text(encoding='utf-8')
needle='<h3 class="sectiontitle">AI测量差异</h3>'
insert='''<h3 class="sectiontitle">历史劳动力市场动态 <span class="soc2badge">SOC2宽口径</span></h3><div class="notice">以下是 <b>${x.soc2Context?.soc2d_name||'所属职业大类'}</b> 的公开RPLS历史趋势，不代表该SOC6职业本身。</div><div class="evidence">\n<div class="card"><h3>就业年化趋势</h3><div class="score">${x.soc2Context?.employment_common_2022_annualized_pct==null?'—':fmt(x.soc2Context.employment_common_2022_annualized_pct)+'%'}</div><span class="sub">2022–2026 · RPLS</span></div>\n<div class="card"><h3>招聘发布年化趋势</h3><div class="score">${x.soc2Context?.postings_common_2022_annualized_pct==null?'—':fmt(x.soc2Context.postings_common_2022_annualized_pct)+'%'}</div><span class="sub">2022–2026 · RPLS</span></div>\n<div class="card"><h3>薪资年化趋势</h3><div class="score">${x.soc2Context?.salary_common_2022_annualized_pct==null?'—':fmt(x.soc2Context.salary_common_2022_annualized_pct)+'%'}</div><span class="sub">2022–2026 · RPLS</span></div>\n<div class="card"><h3>平均净招聘率</h3><div class="score">${x.soc2Context?.net_hiring_rate_common_2022_mean==null?'—':fmt(x.soc2Context.net_hiring_rate_common_2022_mean)}</div><span class="sub">Hiring − Attrition</span></div></div>\n'''
if needle in app and '历史劳动力市场动态' not in app: app=app.replace(needle,insert+needle)
(ROOT/'web/app.js').write_text(app,encoding='utf-8')
with open(ROOT/'web/style.css','a',encoding='utf-8') as f:f.write('\n.soc2badge{font-size:10px;background:#eef2ff;color:#4f46e5;padding:4px 7px;border-radius:999px;vertical-align:middle}\n')

# methodology update
meth=(ROOT/'web/methodology.html').read_text(encoding='utf-8')
meth=meth.replace('<h2>限制</h2>','<h2>历史劳动力市场</h2><p>RPLS公开数据提供SOC2职业大类的就业、岗位、招聘/流失和薪资时间序列。网站只把它作为“宽口径职业大类背景”，不会冒充SOC6职业自身历史。</p><h2>限制</h2>')
(ROOT/'web/methodology.html').write_text(meth,encoding='utf-8')

# ---------- launch docs ----------
(ROOT/'docs/PUBLIC_LAUNCH_CHECKLIST.md').write_text('''# Public Launch Checklist\n\n## Repository\n- [ ] Replace GitHub placeholder URL\n- [ ] Set repository description\n- [ ] Add topics\n- [ ] Set social preview image\n- [ ] Enable Issues and Discussions\n- [ ] Create `v0.6.0-beta` tag and release\n\n## GitHub Pages\n- [ ] Settings → Pages → GitHub Actions\n- [ ] Confirm homepage loads\n- [ ] Search 30 occupations\n- [ ] Compare 3 occupations\n- [ ] Open methodology page\n- [ ] Test mobile width\n\n## Research\n- [ ] Do not publish flagged exposure-gap cases without manual QA\n- [ ] Label RPLS as SOC2 context\n- [ ] Do not call CEI a probability\n- [ ] Do not claim causal AI effects\n\n## Outreach\n- [ ] Pin repository on profile\n- [ ] Add live demo to About\n- [ ] Publish launch article\n- [ ] Invite mapping/methodology Issues\n''',encoding='utf-8')
(ROOT/'docs/STAR_GROWTH_PLAYBOOK.md').write_text('''# Ethical GitHub Star Growth Playbook\n\nThe goal is not to game stars. Make the project easy to understand, use and contribute to.\n\n## Launch assets\n\n1. Live GitHub Pages demo.\n2. One strong social-preview image.\n3. README with the 867-occupation scope and 2–3 real findings above the fold.\n4. Reproducibility and data-source links.\n5. A clear first issue for contributors.\n\n## Launch message\n\nLead with the research question, not “please star”.\n\nSuggested hook:\n\n> AI exposure is not the same as career decline. I combined public O*NET, BLS, ILO, Anthropic and historical labor-market data across U.S. occupations to make the evidence inspectable.\n\nThen link to the live demo and repository.\n\n## Good contribution prompts\n\n- challenge an occupation mapping;\n- improve a Human Structure proxy;\n- add another country;\n- reproduce a result;\n- improve accessibility or visualization.\n\nStars should be a consequence of usefulness and credibility.\n''',encoding='utf-8')

# ---------- reproducibility scripts ----------
shutil.copy2(LONG/'scripts/build_v06.py',ROOT/'scripts/build_rpls_v06_original.py')
shutil.copy2('/mnt/data/build_public_v060.py',ROOT/'scripts/build_public_v060.py') if Path('/mnt/data/build_public_v060.py').exists() else None

# validation script expanded
(ROOT/'scripts/validate_release.py').write_text('''from pathlib import Path\nimport pandas as pd, json\nROOT=Path(__file__).resolve().parents[1]\ndf=pd.read_csv(ROOT/'data/career_metrics_v0_6.csv')\nassert len(df)==867 and df.soc6.is_unique\nfor c in ['career_evidence_index_beta','market_opportunity_score','growth_score','opening_score','wage_score','future_skill_fit_score','ai_potential_exposure_score','ai_observed_usage_score','HumanMoat_seed_equal_weight','Physicality','Judgment','Interaction','Responsibility','Context']:\n x=df[c].dropna(); assert ((x>=0)&(x<=100)).all(),c\nweb=json.loads((ROOT/'web/data/careers.json').read_text(encoding='utf-8'))\nassert len(web)==867 and len({x['soc'] for x in web})==867\nassert all('soc2Context' in x for x in web)\nlong=pd.read_csv(ROOT/'data/longitudinal/SOC2_Longitudinal_Master_v0_6.csv')\nassert long.soc2d_code.is_unique and len(long)>=20\nfor f in ['README.md','RELEASE_NOTES_v0.6.0.md','docs/LONGITUDINAL_VALIDATION.md','docs/PROCESSING_LOG.md','docs/DATA_SOURCES.md','docs/PUBLIC_LAUNCH_CHECKLIST.md','web/index.html','web/methodology.html','web/app.js','web/style.css']:\n assert (ROOT/f).exists(),f\nprint('PASS: FutureCareer v0.6.0 release validation')\n''',encoding='utf-8')

# data sources add RPLS
with open(ROOT/'docs/DATA_SOURCES.md','a',encoding='utf-8') as f:f.write('\n| Revelio Public Labor Statistics | 2021/2022–2026 | public SOC2 employment, openings, hiring/attrition, salary history | https://www.reveliolabs.com/public-labor-statistics |\n')

# ---------- manifest ----------
manifest=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='MANIFEST.csv':manifest.append([str(p.relative_to(ROOT)),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
pd.DataFrame(manifest,columns=['path','bytes','sha256']).to_csv(ROOT/'MANIFEST.csv',index=False)

# zip
ZIP=Path('/mnt/data/FutureCareer_v0.6.0_Open_Research_Beta_GitHub_Ready.zip')
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT.parent))

print('ROOT',ROOT) ; print('ZIP',ZIP);print('LONG',long.shape);print('\nCommon window correlations:')
print(corr[corr.window=='common_2022'].to_string(index=False))
print('\nLOO:');print(loo.to_string(index=False))
