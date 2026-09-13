# Analytics & Feedback

## Why no hidden backend exists in v1.0

GitHub Pages is a static host. FutureCareer therefore does not pretend to have a first-party event database.

## Launch recommendation

Use a privacy-aware analytics layer only after configuration.

The repository ships an analytics adapter in:

```text
web/analytics.js
web/config.js
```

Default:

```text
analyticsProvider: "none"
```

No analytics provider is contacted by default.

## Recommended first option: GoatCounter

Why:
- lightweight;
- aggregate/privacy-oriented;
- no unique user tracking by default;
- sufficient for first-stage product questions.

Events designed for launch:

```text
career_open
compare_add
compare_open
fit_open
career_save
evidence_open
share_career
feedback_open
```

The adapter deliberately does **not** transmit:
- free-text search queries;
- Personal Fit slider values;
- personal attributes.

## Heatmaps / session recordings

A tool such as Microsoft Clarity can provide richer behavioral analysis, but it introduces a materially larger privacy/consent surface. Do not add it silently. If used later, implement consent management and publish the privacy disclosure first.

## Survey fallback

For the first China-facing beta, create a short questionnaire in a China-accessible service and paste its public URL into:

```text
web/config.js → surveyUrl
```

The UI will then expose a feedback button.

Suggested questions:

1. 你是否能理解 CEI / 0–100 分数代表什么？（1–5）
2. 哪个模块最有帮助？Snapshot / Compare / Personal Fit / Evidence / Watch
3. 哪个数字最难理解？
4. 你最希望增加哪类中国本地数据？
5. 这个网站是否帮助你缩小职业选择范围？（1–5）
6. 你是否愿意一周/月后回来查看职业变化？
7. 一条开放反馈。

Avoid collecting name, phone, health, politics or other unnecessary personal data.
