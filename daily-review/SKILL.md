---
name: daily-review
description: 飞书日历日记生成器。读取 ICS 文件，解析指定日期的所有事件，智能分类，生成结构化日记。支持单日、日期范围、整月批量生成。Use when user says "日记", "daily", "生成日记", or wants to process ICS calendar exports into daily diary entries.
user_invocable: true
---

## Usage

<example>
User: /daily-review calendar_2025_09.ics 2025-09-01
Assistant: [运行 parse_ics.py 提取事件，分类整理，输出到 daily/2025-09-01.md]
</example>

<example>
User: /daily-review calendar_2025_09.ics 2025-09-01~2025-09-07
Assistant: [批量生成 7 天日记，每天一个文件]
</example>

<example>
User: /daily-review calendar_2025_09.ics --month
Assistant: [生成 9 月所有天的日记]
</example>

## Instructions

### 步骤 1: 解析 ICS

用 `scripts/parse_ics.py` 提取事件数据：

```bash
# 单日
python scripts/parse_ics.py <ics_file> 2025-09-01

# 日期范围
python scripts/parse_ics.py <ics_file> 2025-09-01~2025-09-07

# 整月
python scripts/parse_ics.py <ics_file> --month
```

输出 JSON 数组。每个事件含 `date`, `start`, `end`, `summary`, `description`, `tags` 字段。

如果用户只给了日期没给文件，按 `calendar_YYYY_MM.ics` 推断。如果说"昨天"/"今天"，用当前日期推算。

ICS 文件默认在工作目录下。脚本路径为本 skill 目录下的 `scripts/parse_ics.py`。

### 步骤 2: 智能分类

**先读标签，再语义补充。** 脚本已从 SUMMARY 中提取 `#标签`，按以下规则映射：

| 标签 | 分类 |
|------|------|
| `#工作` | 💼 工作 |
| `#育儿` | 🌱 育儿 |
| `#阅读` | 📖 阅读 |
| `#学习` | 📖 阅读 |
| `#创作`, `#写作` | 🎨 创作 |
| `#生活`, `#娱乐`, `#享受` | 🫀 生活 |

**无标签时语义判断**（一条可多分类）：

| 分类 | 语义信号 |
|------|---------|
| 💼 工作 | 报告、对接、审核、验收、会议、标书、陪标、踏勘、盖章、项目名（央督、用海、海岛） |
| 🌱 育儿 | 兔兔/锦宝、老彬与孩子互动、幼儿园/学校、亲子游戏 |
| 📖 阅读 | 书名《》、读书感受、AI/Gemini 讨论、共学、论文 |
| 🎨 创作 | 提示词、编程项目（非工作）、音乐、lovable |
| 🫀 生活 | 以上都不匹配的 |

宁可多归不要漏。不要因为分类而改变原文。

### 步骤 3: 识别触动时刻

判断标准：**一个月后重读会不会停下来**。信号：情感细节、意外转折、亲密瞬间、内心反思、深度交流。

### 步骤 4: 生成日记

输出到 ICS 文件同级 `daily/YYYY-MM-DD.md`。批量时每天一个文件，已存在的跳过。

```markdown
---
date: {YYYY-MM-DD}
weekday: {周X}
week: {YYYY-WXX}
tags: [{分类列表}]
events_count: {N}
---

# {MM月DD日} {周X}

## 🕰️ 时间线

| 时间 | 摘要 | 分类 |
|------|------|------|
| HH:MM-HH:MM | {SUMMARY 前30字}... | 💼/🌱/📖/🎨/🫀 |

## 💼 工作
{按时间排列，保留原文。DESCRIPTION 以引用块附在下方。无则省略板块。}

## 🌱 育儿
{触动时刻用 > [!触动] 标注}

## 📖 阅读
{标注书名，保留链接}

## 🎨 创作

## 🫀 生活

## ✏️ 当日复盘
{2-3 个具体的复盘问题，用 Obsidian callout：}

> [!question] {问题}

{留空供回复}
```

无事件的分类板块省略。时间线永远保留。

### 关键原则

1. **永远保留原文**。不改写、不美化、不总结。
2. **复盘问题要具体**，基于当天真实事件，不要泛泛。
3. **DESCRIPTION 链接保留**在引用块里。`[图片]` 标记保留原样。
4. **批量生成时跳过已有文件**，避免覆盖用户已写的复盘回复。
