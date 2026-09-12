# GitHub 部署步骤

目标：

- 仓库：https://github.com/zlznzyq/futurecareer-evidence
- 网站：https://zlznzyq.github.io/futurecareer-evidence/

## 第1步：创建空仓库

GitHub右上角：

```text
+ → New repository
```

填写：

```text
Repository name: futurecareer-evidence
Description: Open, explainable career evidence for the AI era.
Visibility: Public
```

不要勾选：

```text
Add a README
Add .gitignore
Choose a license
```

因为项目包里已经有。

## 第2步：本地解压

把本发布包解压到例如：

```text
C:\Users\你的用户名\Desktop\futurecareer-evidence
```

## 第3步：打开CMD

```bat
cd C:\Users\你的用户名\Desktop\futurecareer-evidence
```

## 第4步：先做本地质量检查

```bat
python scripts\validate_release.py
```

必须看到：

```text
PASS
```

## 第5步：初始化Git

```bat
git init
git branch -M main
git add .
git commit -m "Release FutureCareer Evidence v0.7.0 beta"
git remote add origin https://github.com/zlznzyq/futurecareer-evidence.git
git push -u origin main
```

如果GitHub要求登录，按浏览器提示授权。

## 第6步：检查README

打开：

https://github.com/zlznzyq/futurecareer-evidence

确认：

- Hero图正常；
- Research figures正常；
- 中文README链接正常；
- Methodology/Data Source链接正常。

## 第7步：部署Pages

GitHub仓库：

```text
Settings → Pages
```

在：

```text
Build and deployment → Source
```

选择：

```text
GitHub Actions
```

然后打开：

```text
Actions → Deploy GitHub Pages
```

等待绿色✓。

网站应出现在：

https://zlznzyq.github.io/futurecareer-evidence/

## 第8步：完善About

仓库首页右侧About：

```text
Description:
Open, explainable career evidence for the AI era.

Website:
https://zlznzyq.github.io/futurecareer-evidence/
```

Topics：

```text
future-of-work
ai
labor-economics
career
onet
open-data
research
```

## 第9步：Social Preview

```text
Settings → Social preview
```

上传：

```text
assets/futurecareer-preview.png
```

## 第10步：正式Release

```text
Releases → Draft a new release
```

Tag：

```text
v0.7.0-beta
```

Title：

```text
FutureCareer Evidence v0.7.0 — Open Research Beta
```

Release正文使用仓库中的Release Notes。

## 第11步：Pin到个人主页

打开：

https://github.com/zlznzyq

```text
Customize your pins
```

把 `futurecareer-evidence` 放第一位。
