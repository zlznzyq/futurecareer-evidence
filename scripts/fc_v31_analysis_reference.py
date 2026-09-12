import pandas as pd, numpy as np, statsmodels.api as sm
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, GroupKFold, cross_validate
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from statsmodels.stats.multitest import multipletests

IN='/mnt/data/FutureCareer_Data_Assets_V2.1/US_Occupation_Master_Matrix_V2_1.csv'
OUT=Path('/mnt/data/FutureCareer_Research_Analysis_V3.1'); OUT.mkdir(exist_ok=True)
d=pd.read_csv(IN)

# Numeric coercion
num_cols=['ilo_exposure_mean','observed_exposure','Context','Interaction','Judgment','Physicality','Responsibility','HumanMoat_seed_equal_weight','Employment, 2025','Employment change, percent, 2025–35','Occupational openings, 2025–35 annual average','Median annual wage, dollars, 2025','Occupational transfer rate, 2025–35 annual average','Percent self-employed, 2025']
for c in num_cols:
    if c in d: d[c]=pd.to_numeric(d[c],errors='coerce')

# Major SOC and SOC6
d['soc6']=d['_soc6'].astype(str).str.extract(r'(\d{2}-\d{4})',expand=False)
d['major_soc']=d['soc6'].str[:2]

# IMPORTANT: aggregate O*NET detailed occupations to unique SOC6 to avoid pseudo-replication.
# BLS outcomes are identical within SOC6; O*NET/AI/HM measures are averaged, with mapping confidence retained conservatively.
conf_rank={'A':3,'B':2,'C':1,'D':0}
def worst_conf(x):
    vals=[v for v in x.dropna().astype(str) if v in conf_rank]
    return min(vals,key=lambda v:conf_rank[v]) if vals else np.nan
agg={
    'title': lambda x:' | '.join(pd.unique(x.dropna().astype(str))[:4]),
    'ilo_exposure_mean':'mean','observed_exposure':'mean',
    'Context':'mean','Interaction':'mean','Judgment':'mean','Physicality':'mean','Responsibility':'mean',
    'HumanMoat_seed_equal_weight':'mean',
    'Employment, 2025':'first','Employment change, percent, 2025–35':'first',
    'Occupational openings, 2025–35 annual average':'first','Median annual wage, dollars, 2025':'first',
    'Occupational transfer rate, 2025–35 annual average':'first','Percent self-employed, 2025':'first',
    'Typical education needed for entry':'first','mapping_confidence':worst_conf,
}
for c in ['Adaptability','Computers and information technology','Creativity and innovation','Critical and analytical thinking','Customer service','Detail oriented','Fine motor','Interpersonal','Leadership','Mathematics','Mechanical','Physical strength and stamina','Problem solving and decision making','Project management','Science','Speaking and listening','Writing and reading']:
    if c in d: agg[c]='first'

soc=d.dropna(subset=['soc6']).groupby('soc6',as_index=False).agg(agg)
soc['major_soc']=soc['soc6'].str[:2]
soc['onet_rows_per_soc']=d.dropna(subset=['soc6']).groupby('soc6').size().reindex(soc['soc6']).values
soc['growth']=soc['Employment change, percent, 2025–35']/100.0
soc['opening_rate']=(soc['Occupational openings, 2025–35 annual average']/soc['Employment, 2025'])
soc['log_wage']=np.log(soc['Median annual wage, dollars, 2025'].where(soc['Median annual wage, dollars, 2025']>0))
soc['transfer']=soc['Occupational transfer rate, 2025–35 annual average']/100.0
soc['log_emp']=np.log(soc['Employment, 2025'].where(soc['Employment, 2025']>0))
soc['self_emp']=soc['Percent self-employed, 2025']/100.0

# Education ordinal, transparent coding
edu_order={
'No formal educational credential':0,'High school diploma or equivalent':1,'Some college, no degree':2,
'Postsecondary nondegree award':2.5,"Associate's degree":3,"Bachelor's degree":4,"Master's degree":5,
'Doctoral or professional degree':6
}
soc['education_ord']=soc['Typical education needed for entry'].map(edu_order)

# Winsorized outcomes (1/99)
def wins(s,p=.01):
    lo,hi=s.quantile(p),s.quantile(1-p); return s.clip(lo,hi)
for c in ['growth','opening_rate','log_wage','transfer']:
    soc[c+'_w']=wins(soc[c])

# Human Moat measurement at SOC level
hmcols=['Physicality','Judgment','Interaction','Responsibility','Context']
hm_complete=soc.dropna(subset=hmcols).copy()
Z=StandardScaler().fit_transform(hm_complete[hmcols])
pca=PCA().fit(Z)
pc1=pca.transform(Z)[:,0]
# orient higher PC1 to correlate positively with equal-weight HM
if np.corrcoef(pc1,hm_complete['HumanMoat_seed_equal_weight'])[0,1]<0:
    pc1=-pc1; pca.components_[0]*=-1
hm_complete['HM_PCA1']=pc1
# standardized equal weight
hm_complete['HM_equal_z']=StandardScaler().fit_transform(hm_complete[['HumanMoat_seed_equal_weight']]).ravel()
soc=soc.merge(hm_complete[['soc6','HM_PCA1','HM_equal_z']],on='soc6',how='left')

# Cronbach alpha at SOC level
X=hm_complete[hmcols].dropna().values
k=X.shape[1]; alpha=k/(k-1)*(1-X.var(axis=0,ddof=1).sum()/X.sum(axis=1).var(ddof=1))
loadings=pd.DataFrame({'dimension':hmcols,'PC1_loading':pca.components_[0]})
variance=pd.DataFrame({'component':np.arange(1,6),'explained_variance_ratio':pca.explained_variance_ratio_})

# Correlations
corrvars=['ilo_exposure_mean','observed_exposure','HM_equal_z','HM_PCA1','growth','opening_rate','log_wage','transfer']
pear=soc[corrvars].corr(method='pearson'); spear=soc[corrvars].corr(method='spearman')

# Standardized robust regression helper with controls and major SOC FE
def zscore(s):
    return (s-s.mean())/s.std(ddof=0)

def fit_model(outcome, ai, hm='HM_equal_z', interaction=False, controls=True, winsor=False, weighted=False, highconf=False):
    ycol=outcome+('_w' if winsor else '')
    cols=[ycol,ai,hm,'major_soc']
    if controls: cols += ['log_emp','education_ord','self_emp']
    if highconf: cols += ['mapping_confidence']
    x=soc[cols].copy().dropna()
    if highconf: x=x[x['mapping_confidence'].isin(['A','B'])].copy()
    y=zscore(x[ycol])
    Xd=pd.DataFrame(index=x.index)
    Xd['AI']=zscore(x[ai]); Xd['HM']=zscore(x[hm])
    if interaction: Xd['AIxHM']=Xd['AI']*Xd['HM']
    if controls:
        for c in ['log_emp','education_ord','self_emp']: Xd[c]=zscore(x[c])
    # major SOC FE
    fe=pd.get_dummies(x['major_soc'],prefix='major',drop_first=True,dtype=float)
    Xd=pd.concat([Xd,fe],axis=1)
    Xd=sm.add_constant(Xd)
    if weighted:
        weights=np.sqrt(np.maximum(x['Employment, 2025'] if 'Employment, 2025' in x else soc.loc[x.index,'Employment, 2025'],1))
        model=sm.WLS(y,Xd,weights=weights).fit(cov_type='HC3')
    else:
        model=sm.OLS(y,Xd).fit(cov_type='HC3')
    rows=[]
    for term in ['AI','HM','AIxHM','log_emp','education_ord','self_emp']:
        if term in model.params:
            rows.append({'outcome':outcome,'ai_source':ai,'hm_spec':hm,'interaction':interaction,'controls':controls,'winsor':winsor,'weighted':weighted,'high_mapping_conf':highconf,'term':term,'std_beta':model.params[term],'robust_se':model.bse[term],'p_value':model.pvalues[term],'n':int(model.nobs),'r2':model.rsquared,'adj_r2':model.rsquared_adj})
    return rows

regs=[]
for outcome in ['growth','opening_rate','log_wage','transfer']:
  for ai in ['ilo_exposure_mean','observed_exposure']:
    for hm in ['HM_equal_z','HM_PCA1']:
      for interaction in [False,True]:
        regs += fit_model(outcome,ai,hm,interaction,controls=True)
    # robustness variants equal HM interaction
    regs += fit_model(outcome,ai,'HM_equal_z',True,controls=True,winsor=True)
    regs += fit_model(outcome,ai,'HM_equal_z',True,controls=True,highconf=True)
regs=pd.DataFrame(regs)
# BH FDR across non-control focal tests
mask=regs['term'].isin(['AI','HM','AIxHM'])
regs['p_fdr_bh']=np.nan
regs.loc[mask,'p_fdr_bh']=multipletests(regs.loc[mask,'p_value'],method='fdr_bh')[1]

# Predictive benchmark: random KFold AND major-SOC GroupKFold. Use Ridge + one-hot education/major implicitly numeric controls.
def cv_models(outcome, ai):
    use=soc[[outcome,ai,'HM_equal_z','log_emp','education_ord','self_emp','major_soc']].dropna().copy()
    models={
      'AI only':[ai],
      'HM only':['HM_equal_z'],
      'AI + HM':[ai,'HM_equal_z'],
      'AI + HM + controls':[ai,'HM_equal_z','log_emp','education_ord','self_emp'],
    }
    res=[]
    for name,features in models.items():
        X=use[features]; y=use[outcome]
        pipe=Pipeline([('scale',StandardScaler()),('ridge',Ridge(alpha=1.0))])
        for scheme,cv,groups in [
            ('Random5',KFold(5,shuffle=True,random_state=42),None),
            ('MajorSOC_Group',GroupKFold(n_splits=min(5,use['major_soc'].nunique())),use['major_soc'])]:
            sc=cross_validate(pipe,X,y,cv=cv,groups=groups,scoring={'r2':'r2','mae':'neg_mean_absolute_error','rmse':'neg_root_mean_squared_error'})
            res.append({'outcome':outcome,'ai_source':ai,'model':name,'cv_scheme':scheme,'n':len(use),'cv_r2_mean':sc['test_r2'].mean(),'cv_r2_sd':sc['test_r2'].std(),'mae_mean':-sc['test_mae'].mean(),'rmse_mean':-sc['test_rmse'].mean()})
    return res
bench=[]
for outcome in ['growth','opening_rate','log_wage','transfer']:
    for ai in ['ilo_exposure_mean','observed_exposure']:
        bench += cv_models(outcome,ai)
bench=pd.DataFrame(bench)

# Dimension-level regressions to see which HM dimensions drive results
# standardized, controls + FE, one dimension at a time with ILO
Dim=[]
for outcome in ['growth','opening_rate','log_wage','transfer']:
 for dim in hmcols:
    cols=[outcome,'ilo_exposure_mean',dim,'log_emp','education_ord','self_emp','major_soc']
    x=soc[cols].dropna().copy(); y=zscore(x[outcome]); Xd=pd.DataFrame(index=x.index)
    for src,name in [('ilo_exposure_mean','AI'),(dim,'DIM'),('log_emp','log_emp'),('education_ord','education_ord'),('self_emp','self_emp')]: Xd[name]=zscore(x[src])
    fe=pd.get_dummies(x['major_soc'],drop_first=True,dtype=float); Xd=pd.concat([Xd,fe],axis=1); Xd=sm.add_constant(Xd)
    m=sm.OLS(y,Xd).fit(cov_type='HC3')
    Dim.append({'outcome':outcome,'dimension':dim,'std_beta':m.params['DIM'],'robust_se':m.bse['DIM'],'p_value':m.pvalues['DIM'],'n':int(m.nobs),'r2':m.rsquared})
Dim=pd.DataFrame(Dim); Dim['p_fdr_bh']=multipletests(Dim['p_value'],method='fdr_bh')[1]

# Descriptive table
desc=[]
for v in corrvars+['Employment, 2025','education_ord','self_emp']:
    s=soc[v].dropna(); desc.append({'variable':v,'n':len(s),'mean':s.mean(),'sd':s.std(),'p25':s.quantile(.25),'median':s.median(),'p75':s.quantile(.75),'min':s.min(),'max':s.max()})
desc=pd.DataFrame(desc)

# Save
soc.to_csv(OUT/'Analysis_SOC6_Master_V3_1.csv',index=False,encoding='utf-8-sig')
desc.to_csv(OUT/'Table1_Descriptive_Statistics.csv',index=False,encoding='utf-8-sig')
pear.to_csv(OUT/'Table2_Pearson_Correlation.csv',encoding='utf-8-sig')
spear.to_csv(OUT/'Table2_Spearman_Correlation.csv',encoding='utf-8-sig')
regs.to_csv(OUT/'Table3_Robust_Regressions.csv',index=False,encoding='utf-8-sig')
bench.to_csv(OUT/'Table4_Predictive_Benchmark.csv',index=False,encoding='utf-8-sig')
Dim.to_csv(OUT/'Table5_HumanMoat_Dimension_Results.csv',index=False,encoding='utf-8-sig')
loadings.to_csv(OUT/'HumanMoat_PCA_Loadings_SOC6.csv',index=False,encoding='utf-8-sig')
variance.to_csv(OUT/'HumanMoat_PCA_Variance_SOC6.csv',index=False,encoding='utf-8-sig')
pd.DataFrame([{'soc6_n':len(soc),'hm_complete_n':len(hm_complete),'cronbach_alpha':alpha,'pca_pc1_variance':pca.explained_variance_ratio_[0],'duplicate_onet_rows_collapsed':int(len(d)-len(soc))}]).to_csv(OUT/'Measurement_Summary.csv',index=False,encoding='utf-8-sig')

# concise console highlights
print('SOC6 N',len(soc),'collapsed',len(d)-len(soc),'alpha',alpha,'PC1',pca.explained_variance_ratio_[0])
print('\nKey controlled interaction rows:')
print(regs[(regs.interaction==True)&(regs.hm_spec=='HM_equal_z')&(regs.winsor==False)&(regs.high_mapping_conf==False)&(regs.term.isin(['AI','HM','AIxHM']))][['outcome','ai_source','term','std_beta','p_value','p_fdr_bh','r2','n']].to_string(index=False))
print('\nBench group CV:')
print(bench[(bench.cv_scheme=='MajorSOC_Group')&(bench.model=='AI + HM + controls')][['outcome','ai_source','cv_r2_mean','mae_mean','n']].to_string(index=False))
