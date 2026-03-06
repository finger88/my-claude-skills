---
name: ljg-paper
description: "Paper deep reader. Takes an academic paper (URL, PDF, or file), runs the atom pipeline (split→squeeze→plain→feynman→博导审稿), and synthesizes a fluent analysis. Focus: what gap does it fill, and would a seasoned advisor take it seriously? Use when user shares an arxiv link, paper URL, PDF, or asks to analyze a research paper. Output to Markdown with customizable path (default: ~/Downloads/). Trigger words: '读论文', '分析论文', 'paper', 'deep read', or when user shares an academic paper."
user_invocable: true
version: "2.2.0"
---

# ljg-paper: 论文深读器

论文 = 一个增量。已有研究走到了某个边界，这篇论文声称往前推了一步。你的任务：这一步踩在哪儿，踩得稳不稳。

认知路径：论文 = 一个增量 → 拆结构(split) → 榨增量(squeeze：到底新了什么？) → 白话方法(plain：核喻让方法论可触摸) → 费曼概念(feynman：关键概念讲透) → 餐巾纸速写(napkin sketch：一张图看清新旧框架对比) → 博导审稿(白话点评，内行判决) → 综合成一篇流畅的解读。

## 核心原则

**输出是一篇文章，不是几份报告拼接。** 原子在后台运行，读者看到的是一段连贯的认知旅程：先知道缺口在哪 → 再看清增量到底是什么 → 把关键概念用费曼技巧讲透 → 用一张餐巾纸速写看清新旧框架的位移 → 然后听一个带了二十年研究生的博导怎么评 → 最后问自己：这篇论文的思想能改变我的什么？

论文和文章的关键区别：文章验的是论点，论文验的是体系——选题眼光、方法成熟度、实验诚意、写作功力。所以最后一步不是逐条挑毛病，是换一个身份——一个见过几千篇论文的博导，用白话给出内行判决。博导的厉害不在于挑刺更狠，在于一眼看出这篇东西在这个方向上的真实位置。

## 输出路径配置

**默认输出路径**: `~/Downloads/`

**自定义路径**: 用户可在执行时指定其他路径

**文件名格式**: `{YYYYMMDD}-{简短标题}-paper.md`
- 简短标题：取论文标题前3-5个关键词，小写，用连字符连接
- 示例：`20260302-context-engineering-agents-paper.md`

## 约束

### L0: 通用约束

#### Markdown 语法

- 使用标准 Markdown 格式
- 标题层级从 `#` 开始，不跳级
- 代码块使用围栏式 (```)

#### ASCII Art

所有图表一律使用纯 ASCII 字符绘制。

允许字符集：`+ - | / \ > < v ^ * = ~ . : # [ ] ( ) _ , ; ! ' " ` 和空格。

禁止一切 Unicode 绘图符号，包括但不限于：
`─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬ ▼ ▲ ► ◄ → ← ↑ ↓ ● ○ ■ □ ◆ ◇`

#### 完成动作

文件写入后，向用户报告：
- 文件完整路径
- 文件大小（行数或字数）
- 简要内容概览

## 执行步骤

### 步骤 0：确认输出路径

1. 检查用户是否指定了自定义输出路径
2. 如无指定，使用默认路径 `~/Downloads/`
3. 验证路径存在，如不存在则询问用户

### 步骤 1：获取内容

- arxiv URL → 调用 ljg-fetch 获取，或 WebFetch 获取摘要+正文
- PDF 文件 → Read 获取（注意 pages 参数限制）
- 本地 markdown/org 文件 → Read 获取
- 论文名称 → WebSearch 查找论文，获取核心内容

获取后，确保拿到：标题、作者、摘要、引言（问题+相关工作）、方法、实验/结果、结论。

### 步骤 2：原子管线（内部执行，不分别输出）

**完整管线说明**: 见 [references/atom-pipeline.md](references/atom-pipeline.md)

**快速概览**:
- **Split（拆）**: 识别缺口、假设、方法、证据、贡献声明
- **Squeeze（榨增量）**: 一句话说清 before vs after，画核心机制图
- **Plain（白话方法）**: 用核喻让方法可触摸
- **Feynman（关键概念）**: 费曼技巧讲透 1-3 个关键概念
- **Napkin Sketch（餐巾纸速写）**: 一张图看清新旧框架位移
- **博导审稿（白话审）**: 内行判决——选题、方法、实验、写作、一句话判决

### 步骤 3：综合输出

将原子管线的中间结果编织成一篇连贯的分析。

**编织原则**：
- 「缺口」段自然过渡到「增量」：知道了缺口在哪，自然想看这一步到底迈了多远。
- 「增量」中核心机制自然过渡到「关键概念」：机制看清了，想把几个关键术语彻底搞懂。
- 「关键概念」自然过渡到「Napkin Sketch」：概念都懂了，自然想用一张图看清新旧框架的结构差异。
- 「Napkin Sketch」自然过渡到「博导审稿」：图看完了，位移一目了然，自然想听一个内行怎么评。
- 「博导审稿」自然过渡到「启发」：博导评完了，知道哪里实哪里虚，自然想问——这篇论文的思想撞进我的体系，哪里会变形？

### 步骤 3b：写作卫生检查

综合输出完成后，对全文执行轻量扫描，只查最高频的 AI 写作惯性：

1. **否定式排比**："不是...而是..."、"不是...是..."、"不再是...而是..."——全文上限两处。超标的改为直接陈述正面内容。
2. **三段式列举**：连续三项并列的改为两项或四项。
3. **破折号过度**：同一段落超过两个破折号的，换成逗号或句号。

扫完列出修改清单（哪句触发哪条，改前→改后）。清单确认后进入步骤 4。

### 步骤 4：生成 Markdown 文件

1. 生成文件名：使用 `date +%Y%m%d` 获取日期前缀
2. 按模板填充综合结果（模板见 [references/template.md](references/template.md)）
3. 写入用户指定的输出路径（默认 `~/Downloads/`）
4. 向用户报告文件路径和概览

## 输出质量标准

**完整标准**: 见 [references/quality-standards.md](references/quality-standards.md)

**快速检查清单**:
- ✅ 缺口要准：用自己的话说清楚研究边界和缺口
- ✅ 增量要锐：一句话说出 before vs after
- ✅ 机制要可视：ASCII 图画出方法内部结构
- ✅ 核喻要承重：去掉核喻，读者就回到看图发呆的状态
- ✅ 概念要费曼：读者能用自己的话复述
- ✅ 速写要一眼：不看正文也能理解位移方向
- ✅ 博导要像博导：白话点评，有判断力，有分寸感
- ✅ 启发要私人：不是泛泛的"可迁移思路"，是具体指出读者体系里哪个零件可以升级、哪个盲区被照亮
- ✅ 零割裂感：像一个人在讲「我读了篇论文，让我告诉你它干了啥、好不好」

## 快速示例

**输入**: `https://arxiv.org/html/2510.21413v4`

**输出**: `~/Downloads/20260302-context-engineering-agents-paper.md`

**内容结构**:
```
# Context Engineering for AI Agents
## 缺口
## 增量
### 核心机制
## 关键概念
## 餐巾纸速写
## 博导审稿
## 带走什么
```

---

*ljg-paper v2.1.0 - 优化版：渐进式披露，Token 效率提升*
