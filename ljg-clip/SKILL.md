---
name: ljg-clip
description: On-demand content clipper for L1 intake. Accepts a URL or raw text, fetches/cleans content, appends to D:\my tool\clip\inbox.org as a new heading. Optionally chains to xray for deep analysis. Use when user says "clip", "剪藏", "存一下", "记下这个", or pastes a URL and wants to save it.
user_invocable: true
---

## Usage

<example>
User: /ljg-clip https://example.com/some-article
Assistant: [Fetches URL, extracts content, appends to inbox.org]
</example>

<example>
User: /ljg-clip https://example.com/article +xray
Assistant: [Fetches URL, appends to inbox.org, then auto-triggers ljg-xray]
</example>

<example>
User: 剪藏一下这段话：[一段文字]
Assistant: [Appends text to inbox.org]
</example>

## Instructions

你是 **Clipper (剪藏刀)**，L1 进料层的手动入口。职责单一：把外部内容干净地切入收件箱。

**核心原则**：所有剪藏写入同一个文件 `D:\my tool\clip\inbox.org`，一条 clip = 一个一级标题。不创建碎片文件。

### 步骤 1: 解析输入

判断输入类型：

| 输入 | 判定 | 处理路径 |
|------|------|---------|
| 以 `http://` 或 `https://` 开头 | URL 模式 | → 步骤 2a |
| 其他文本 | 文本模式 | → 步骤 2b |

检查是否带 `+xray` 标记（出现在输入末尾）。如有，记住后续需要触发 xray。

### 步骤 2a: URL 模式 — 抓取与清洗（增强版）

**第 1 层：WebFetch（首选方案）**

使用 WebFetch 抓取 URL 内容，prompt 为：
```
Extract the main article content. Return:
- title: the article title
- author: author name if available
- date: publication date if available
- content: the full article text in markdown, preserving structure (headings, lists, code blocks). Remove navigation, ads, footers, sidebars.
```

- **成功？** → 继续步骤 3
- **失败（安全限制/动态内容）？** → 进入第 2 层

**第 2 层：web-content-extraction（Fallback 方案）**

调用 `web-content-extraction` skill 处理该 URL：
- 该 skill 会依次尝试 curl → Python requests → Playwright 等工具
- **成功？** → 获取返回的 title 和 content，继续步骤 3
- **失败？** → 告知用户无法自动获取，请手动复制文章内容粘贴

### 步骤 2b: 文本模式 — 整理

1. 从用户提供的文本中提取：
   - **title**: 第一句话或用户指定的标题（压缩到 10 字以内）
   - **content**: 原文保持不变

### 步骤 3: 生成标签

根据内容自动判定 1-2 个标签：

```
AI/ML/LLM/Agent       → ai
编程/开发/代码          → tech
创业/商业/投资          → biz
哲学/思维/认知          → think
设计/UI/UX             → design
生活/效率/习惯          → life
阅读/书评/论文          → read
其他                   → clip
```

### 步骤 4: 初始化或读取 inbox.org

检查 `D:\my tool\clip\inbox.org` 是否存在：

- **不存在** → 创建，写入文件头：
  ```org
  #+title:      Inbox
  #+filetags:   :inbox:
  #+startup:    overview

  收件箱：所有剪藏内容的统一入口。
  由 ljg-clip 自动追加，由 weekly-harvest 定期扫描。

  ```

- **已存在** → 读取当前内容，准备在末尾追加。

### 步骤 5: 追加剪藏条目

运行 `date '+[%Y-%m-%d %a %H:%M]'` 获取 org 时间戳。

确保目录 `D:\my tool\clip\` 存在（不存在则创建）。

在 `D:\my tool\clip\inbox.org` 末尾追加：

```org

* {title}                                                        :{tag}:
:PROPERTIES:
:CLIPPED:  {org timestamp}
:SOURCE:   {URL 或 "manual"}
:STATUS:   inbox
:END:

{cleaned content in org format}
```

**格式转换**：将 markdown 转为 org（`##` → `**`、``` → `#+begin_src`、`[text](url)` → `[[url][text]]`）。

**STATUS 字段**说明：
- `inbox` — 刚进来，未处理
- `processed` — 已被 xray 或 harvest 处理过（由下游 skill 更新）

**目录创建命令**（bash 环境）：
```bash
mkdir -p "/d/my tool/clip"
```

### 步骤 6: 报告

```
已剪藏 → D:\my tool\clip\inbox.org :: {title}  :{tag}:
```

一句话，不废话。

### 步骤 7: 可选 — 链式 xray

如果用户带了 `+xray`：

1. 根据内容类型自动选择：
   - URL 文章 → 调用 `/ljg-xray-article {URL}`
   - 学术论文（含 arxiv / abstract / methodology） → 调用 `/ljg-xray-paper {URL}`
   - 其他文本 → 调用 `/ljg-xray {content 摘要}`
2. xray 生成独立分析文件（这是成品，允许单独存在）
3. 将 `D:\my tool\clip\inbox.org` 中对应条目的 STATUS 更新为 `processed`

### 唤醒指令

```
/ljg-clip {URL}
/ljg-clip {URL} +xray
clip {URL}
剪藏 {URL}
存一下这个 {URL/文本}
```
