# 首轮行为分析接入：GoatCounter

FutureCareer 默认 **不启用任何第三方分析**。

如果首轮测试希望记录聚合行为：

1. 注册 GoatCounter；
2. 创建站点并获得 code，例如 `futurecareer`;
3. 打开 `web/config.js`;
4. 修改：

```js
analyticsProvider: "goatcounter",
goatCounterCode: "你的code"
```

5. Commit + push。

当前只设计记录：

- career_open
- compare_add
- compare_open
- fit_open
- career_save
- evidence_open
- share_career
- feedback_open

不会上传：

- 搜索框自由文本；
- Personal Fit具体权重；
- 姓名、邮箱、手机号；
- 敏感个人属性。

如果需要热力图/Session Recording，再单独评估 Clarity，并先完成隐私说明与Consent设计。
