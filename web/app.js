let careers=[],current=null,compare=[];
const $=s=>document.querySelector(s);
fetch('data/careers.json').then(r=>r.json()).then(d=>careers=d);
const fmt=x=>x==null?'—':Number(x).toFixed(1);
const money=x=>x==null?'—':'$'+Number(x).toLocaleString();
const pctText=v=>v==null?'暂无数据':`相对分 ${fmt(v)} / 100`;
function bar(v){return `<div class="bar"><i style="width:${Math.max(0,Math.min(100,v||0))}%"></i></div>`}
function metric(name,v,key,meaning){
 return `<div class="card"><h3>${name}</h3><div class="score">${fmt(v)}</div><div class="scaleText">${pctText(v)}</div>${bar(v)}<p class="sub">${meaning}</p><div class="why" onclick="explain('${key}')">为什么？查看来源与算法 →</div></div>`
}
$('#search').oninput=e=>{let q=e.target.value.trim().toLowerCase(),s=$('#suggestions');if(!q){s.innerHTML='';return}
let hits=careers.filter(x=>(x.title+' '+(x.titleZh||'')+' '+x.soc).toLowerCase().includes(q)).slice(0,8);
s.innerHTML=hits.map(x=>`<div class="suggestion" onclick="show('${x.soc}')"><b>${x.title}</b>${x.titleZh?` · ${x.titleZh}`:''}<br><span class="sub">SOC ${x.soc}</span></div>`).join('')};
function show(soc){current=careers.find(x=>x.soc===soc);$('#suggestions').innerHTML='';$('#search').value=current.title;render();$('#detail').scrollIntoView({behavior:'smooth'})}
function summary(x){
 let parts=[];
 if(x.market!=null) parts.push(x.market>=70?'市场机会相对较强':x.market<35?'市场机会相对偏弱':'市场机会处于中间区间');
 if(x.aiPotential!=null) parts.push(x.aiPotential>=60?'AI可影响程度较高':x.aiPotential<30?'AI可影响程度较低':'AI可影响程度中等');
 if(x.human!=null) parts.push(x.human>=65?'工作较依赖人的判断/互动/情境':'人的工作结构需结合五维细看');
 return parts.join('；')+'。';
}
function render(){let x=current,d=$('#detail');d.classList.remove('hidden');$('#comparePanel').classList.add('hidden');
d.innerHTML=`<div class="container">
<div class="careerhead"><div><h2>${x.title}${x.titleZh?`<span class="zhTitle">${x.titleZh}</span>`:''}</h2><div class="sub">SOC ${x.soc} · 映射可信度 ${x.mappingConfidence||'—'} · 数据覆盖 ${fmt(x.confidence)}/100 (${x.confidenceGrade||'—'})</div><button class="compareAdd" onclick="addCompare()">+ 加入比较</button></div>
<div class="cei"><div class="sub">Career Evidence Index · Beta</div><div class="num">${fmt(x.cei)}</div><div class="scaleText">描述性综合指数，不是成功概率</div></div></div>
<div class="plainSummary"><b>一句话：</b>${summary(x)}</div>
<div class="notice"><b>先别把AI分数当“淘汰概率”。</b> AI可影响程度只说明技术能触及多少任务；就业结果要结合市场和真实使用一起看。</div>
<h3 class="sectiontitle">先看这6个数字</h3><div class="grid">
${metric('市场机会',x.market,'market','就业增长 + 岗位机会率')}
${metric('工资位置',x.wageScore,'wage','2025中位工资的职业间相对位置')}
${metric('未来技能匹配 · Beta',x.skillFit,'skill','当前技能与未来增长技能方向的匹配')}
${metric('AI可影响程度',x.aiPotential,'ilo','理论上GenAI可影响职业任务的程度')}
${metric('AI实际使用',x.aiObserved,'anthropic','Anthropic数据中观察到的AI使用')}
${metric('人的工作结构 · Beta',x.human,'human','工作对判断、人际、责任、情境和具身活动的依赖')}</div>
<h3 class="sectiontitle">人的工作结构：不要只看总分</h3><div class="human">
${metric('具身活动',x.physicality,'physicality','需要身体/现场活动的程度')}
${metric('判断',x.judgment,'judgment','需要判断和决策的程度')}
${metric('人际互动',x.interaction,'interaction','需要与人沟通协作的程度')}
${metric('责任',x.responsibility,'responsibility','决策后果与责任要求')}
${metric('情境依赖',x.context,'context','工作依赖复杂情境和自主决策的程度')}</div>
<h3 class="sectiontitle">原始事实 · BLS</h3><div class="evidence">
<div class="card"><h3>2025–35就业增长</h3><div class="score">${x.growthRaw==null?'—':fmt(x.growthRaw)+'%'}</div><p class="sub">BLS官方预测</p></div>
<div class="card"><h3>年均岗位机会</h3><div class="score">${x.openingsRaw==null?'—':Number(x.openingsRaw).toLocaleString()}</div><p class="sub">BLS原表口径</p></div>
<div class="card"><h3>2025中位工资</h3><div class="score">${money(x.wageRaw)}</div><p class="sub">BLS</p></div>
<div class="card"><h3>职业转移率</h3><div class="score">${x.transferRate==null?'—':fmt(x.transferRate)+'%'}</div><p class="sub">BLS 2025–35</p></div></div>
${x.rpls?`<h3 class="sectiontitle">历史劳动力市场背景 · SOC2</h3><div class="notice">以下是该职业所属<b>职业大类</b>的历史趋势，不代表这个SOC6职业本身。</div><div class="evidence">
<div class="card"><h3>Employment trend</h3><div class="score">${fmt(x.rpls.employmentTrend)}%</div><p class="sub">RPLS 2022–2026 · annualized</p></div>
<div class="card"><h3>Posting trend</h3><div class="score">${fmt(x.rpls.postingTrend)}%</div><p class="sub">RPLS SOC2</p></div>
<div class="card"><h3>Salary trend</h3><div class="score">${fmt(x.rpls.salaryTrend)}%</div><p class="sub">RPLS SOC2</p></div>
<div class="card"><h3>Net hiring</h3><div class="score">${fmt(x.rpls.netHiring)}</div><p class="sub">Hiring − Attrition · SOC2</p></div></div>`:''}
</div>`}
const info={
market:['市场机会','BLS 2025–2035就业增长分与岗位机会率分的Beta组合。','BLS Employment Projections 2025–2035','$0.55×GrowthScore + 0.45×OpeningScore$'],
wage:['工资位置','2025中位工资在当前可比较职业集合中的相对位置。','BLS 2025','100 × percentile rank'],
skill:['未来技能匹配 · Beta','把BLS职业技能结构与WEF 2025未来技能方向对齐。','BLS Skills 2025 + WEF Future of Jobs 2025','documented weighted alignment'],
ilo:['AI可影响程度','衡量GenAI潜在任务暴露。它不是失业概率。','ILO 2025 refined GenAI exposure','source-aligned exposure scale'],
anthropic:['AI实际使用','来自Anthropic Economic Index的观察使用信号，不代表全部AI市场。','Anthropic Economic Index','source-aligned observed-use measure'],
human:['人的工作结构 · Beta','由O*NET可观察工作活动和情境变量构建；V0.3平行分析更支持两因子结构。','O*NET 31.0','five-dimension transparent research seed']
};
function explain(k){let a=info[k]||['人的工作结构维度','来自O*NET职业活动/情境变量，经统一处理形成可比较值。','O*NET 31.0','see Metric Dictionary'];
$('#modalContent').innerHTML=`<h2>${a[0]}</h2><p>${a[1]}</p><hr><p><b>来源</b><br>${a[2]}</p><p><b>计算</b><br>${a[3]}</p><p><b>怎么读</b><br>0–100用于职业间比较，不是概率。完整字段、公式和粒度见 <a href="methodology.html">Methodology</a>。</p>`;$('#modal').classList.remove('hidden')}
$('#closeModal').onclick=()=>$('#modal').classList.add('hidden');
function addCompare(){if(!compare.find(x=>x.soc===current.soc)&&compare.length<3)compare.push(current);alert(`已加入比较（${compare.length}/3）`)}
document.addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement!==$('#search')){e.preventDefault();$('#search').focus()}});