# FutureCareer Evidence

> **用公开数据，把 AI 时代的职业变化讲清楚。**

FutureCareer Evidence 是一个开放、可解释的职业证据项目。当前覆盖 **867 个美国 SOC6 职业**，把劳动力市场、AI 暴露、真实 AI 使用、技能和工作结构分开呈现。

**它不计算“职业被 AI 淘汰的概率”。**

## 一眼看懂

- **市场机会**：BLS 2025–2035 就业增长 + 岗位机会率
- **工资位置**：BLS 2025 中位工资的职业间相对位置
- **AI 潜在暴露**：ILO 2025
- **真实 AI 使用**：Anthropic Economic Index
- **Human Structure**：O*NET 31.0 的具身、判断、人际、责任、情境变量
- **历史劳动力动态**：RPLS 2022–2026，SOC2 层级

## 0–100 是什么？

默认比较型分数使用：

$$
Score_o=100\times PercentileRank(x_o)
$$

例如 **88.4** 表示该指标约处于可比职业的第 88.4 百分位。

它**不是 88.4% 的成功概率**。

## 为什么值得看？

当前研究发现：

1. AI 潜在暴露与真实 AI 使用相关，但不是同一件事；
2. BLS 明确提到 AI 影响的职业，在 ILO 与 Anthropic 指标上都明显更高；
3. Human Structure 的平行分析更支持两个潜在因子，而不是简单单因子；
4. 公开 RPLS 历史数据没有支持“AI 暴露越高，就业趋势越差”的简单规则；
5. AI 暴露较高的 SOC2 大类同时表现出更高 Hiring 与 Attrition，值得继续研究，但**不能解释为因果**。

## 先看哪里？

- 在线 Demo：https://zlznzyq.github.io/futurecareer-evidence/
- 英文 README：[`README.md`](README.md)
- 数据处理：[`docs/PROCESSING_LOG.md`](docs/PROCESSING_LOG.md)
- 指标字典：[`docs/METRIC_DICTIONARY.md`](docs/METRIC_DICTIONARY.md)
- 数据来源：[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
- 研究结果：[`docs/RESULTS_AT_A_GLANCE.md`](docs/RESULTS_AT_A_GLANCE.md)

## 复现

```bash
python scripts/validate_release.py
```

历史劳动力市场层：

```bash
python scripts/build_longitudinal.py
```

## 边界

- AI Exposure ≠ 失业概率
- SOC2 历史趋势 ≠ 某个 SOC6 具体职业的历史趋势
- BLS 2035 是预测，不是已经发生的未来
- Anthropic 数据代表其系统中的观察使用，不代表全部 AI 使用
- Career Evidence Index 仍是 **Beta 描述性指数**

代码按仓库许可证开放；第三方数据遵循各自原始许可。
