---
name: source-ingest
description: >
  Searches, fetches, and normalizes web sources into structured EvidenceItem format
  for debate evidence stores. Use this skill when the debate system needs to search
  for evidence, gather sources for a topic, ingest and normalize sources, fetch web
  content for evidence, build the initial evidence store, find supporting data for
  arguments, perform domain-aware credibility assessment, or pre-screen social media
  sources for misinformation indicators.
license: MIT-0
compatibility: Requires bash and shasum. Internet access for WebSearch and WebFetch.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, evidence, web-search, source-verification
  emoji: "🔍"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# SourceIngest
# 来源获取

Search, fetch, and normalize sources into `EvidenceItem` format for the debate evidence store.
搜索、抓取并将来源规范化为 `EvidenceItem` 格式，供辩论证据存储使用。

## When to Use / 何时使用

- During debate initialization to gather initial evidence / 辩论初始化时收集初始证据
- During scheduled refresh to find updated sources / 定时刷新时查找更新来源
- When a debater needs additional evidence mid-round / 辩手在回合中需要额外证据时

## Input / 输入

- `topic`: The debate topic (string)
- `evidence_store_path`: Path to existing evidence_store.json (for deduplication)
- `search_scope`: "broad" (initialization) or "focused" (mid-round supplementary)

## Output / 输出

- Updated `evidence_store.json` with new `EvidenceItem` objects appended
- See `references/data-contracts.md` for EvidenceItem schema

## Core Workflow / 核心工作流

### Step 1: Keyword Generation (LLM) / 关键词生成

Given the debate topic, generate 3-5 diverse search queries using semantic understanding:

- Include queries targeting **fact-track** evidence (current state, recent data, breaking news)
- Include queries targeting **reasoning-track** evidence (mechanisms, historical parallels, academic research)
- Vary query angles: direct topic, related metrics, counterarguments, expert opinions
- Do NOT hardcode search queries; derive them from the actual topic context

**Domain-Aware Search (v3) / 领域感知搜索:**

Read `domain` from config.json to adapt search query strategy:
- For `tech`: include queries targeting official docs, GitHub issues, technical benchmarks
- For `health`: include queries targeting clinical evidence, systematic reviews
- For `finance`: include queries targeting financial data, regulatory filings
- For general/geopolitics: current behavior (no change needed)

### Step 2: Multi-Source Search / 多来源搜索

For each generated query:

1. Use **WebSearch** to find relevant results
2. For each promising result, use **WebFetch** to extract content
3. If WebFetch fails on JavaScript-heavy pages, note the URL for potential Playwright MCP fallback
4. Categorize `source_type`:
   - `web`: Standard web articles, blog posts
   - `twitter`: Tweets/X posts (signal layer only)
   - `academic`: Research papers, journal articles
   - `government`: Government reports, central bank statements
   - `other`: Everything else

### Step 3: Normalization / 规范化

For each fetched source, produce an `EvidenceItem`:

1. Extract the most relevant snippet (the passage supporting or refuting the topic)
2. Compute `hash` using `scripts/hash-snippet.sh <snippet_text>`
3. Assign `evidence_id`: `evi_` + first 8 characters of hash
4. Assign `credibility_tier` using LLM judgment based on publisher reputation:
   - `tier1_authoritative`: Government, central banks, AP/Reuters
   - `tier2_reputable`: Major newspapers, research institutions
   - `tier3_general`: Blogs, industry reports, press releases
   - `tier4_social`: Twitter, Reddit, forums
5. Assign `evidence_track`:
   - `fact`: If the snippet describes current state, recent events, live data
   - `reasoning`: If the snippet explains mechanisms, cites history, or analyzes trends
6. Set `freshness_status` to `current` initially (FreshnessCheck will refine later)
7. Record `published_at` and `retrieved_at` timestamps

#### Domain-Aware Credibility (v3) / 领域感知可信度

When assigning `credibility_tier`, read `config.json` for the `domain` field and apply domain-appropriate judgment:

**Guiding principle / 指导原则:** Tier reflects authority IN THE RELEVANT DOMAIN, not generic media reputation.
用领域内的权威性判断 tier，而不是通用的媒体声誉。

| Domain | tier1 guidance | tier2 guidance |
|---|---|---|
| geopolitics | Government statements, AP/Reuters, UN reports | Major newspapers, think tanks (RAND, Brookings, IISS) |
| tech | Official documentation, RFCs, IEEE/ACM | Reputable tech blogs (with deep analysis), conference papers |
| health | WHO, CDC, NIH, Lancet/NEJM/BMJ | Medical school research, clinical trial databases, Cochrane |
| finance | Central banks, SEC filings, Bloomberg/Reuters data | Research reports, industry analysis, audited financials |
| philosophy | Primary texts, Stanford Encyclopedia of Philosophy | Academic journals, established scholars' published works |
| culture | Primary sources, official archives | Academic publications, established cultural institutions |
| general | Falls back to current default tiers | Falls back to current default tiers |

**Critical rule / 关键规则:** This table is GUIDANCE for LLM judgment, NOT a lookup table to hardcode. The LLM should use semantic understanding of the source's authority within the domain context.
这个表是给 LLM 判断的指导，不是硬编码查找表。LLM 应该用语义理解来判断来源在该领域的权威性。

### Step 3.5: Social Media Credibility Pre-Screen (v3) / 社交媒体可信度预筛

For each evidence item where `source_type = "twitter"`:

Use LLM to assess the tweet/post for fake news indicators:

**Check for these patterns / 检查以下特征:**
1. Extreme emotional language without factual basis / 无事实依据的极端情绪化语言
2. Claims without any cited sources or references / 没有引用任何来源的声明
3. Internal contradictions within the post / 帖子内部自相矛盾
4. Extraordinary claims without proportionate evidence / 非凡声明缺少相应的证据
5. Account context: is the publisher described as authoritative or unknown? / 发布者是否为已知权威来源

**Set `social_credibility_flag`:**
- `likely_reliable`: No fake news indicators, source appears authoritative
- `needs_verification`: Some indicators present, or source credibility unclear
- `likely_unreliable`: Multiple fake news indicators, high risk of misinformation

**Set `verification_priority`:**
- `likely_unreliable` → `high` (prioritize independent verification)
- `needs_verification` → `medium`
- `likely_reliable` → `low`

For non-Twitter sources, set these fields to `null`.

### Step 4: Deduplication / 去重

1. Read existing `evidence_store.json`
2. Compare hashes of new items against existing items
3. Skip items with matching hashes (already ingested)
4. Append only genuinely new items

### Step 5: Persistence / 持久化

1. Write the updated array to `evidence_store.json`
2. Log the ingestion event via `scripts/append-audit.sh`

## Error Handling / 错误处理

| Scenario | Action |
|---|---|
| WebFetch fails for a URL | Retry once; if still fails, skip with note in audit trail |
| No search results for a query | Broaden keywords, try alternative angles |
| All queries return no results | Write `{"insufficient_evidence": true}` flag in evidence store; log warning |
| Duplicate evidence | Skip silently (dedup by hash) |

## Quality Guidelines / 质量准则

- Prefer tier1/tier2 sources over tier3/tier4 when available
- Gather evidence from BOTH sides of the debate topic (not just supporting evidence)
- Include at least one search query designed to find counterarguments
- For Twitter/X sources, always note them as `tier4_social` — they serve as signals, never as standalone proof
