---
name: freshness-check
description: >
  Validates evidence timeliness and tags freshness status based on evidence track type.
  Use this skill when the system needs to check evidence freshness, validate timeliness
  of claims, tag evidence as current or stale or timeless, verify real-time information
  capability, assess source currency, or distinguish fact-track evidence (time-sensitive)
  from reasoning-track evidence (timeless).
license: MIT-0
compatibility: Internet access needed for real-time capability check.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, evidence, freshness, timeliness
  emoji: "⏰"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# FreshnessCheck
# 时效检查

Tag each `EvidenceItem` with appropriate `freshness_status` based on its evidence track and source age.
根据证据轨道和来源年龄为每个 `EvidenceItem` 标记适当的 `freshness_status`。

## When to Use / 何时使用

- Immediately after SourceIngest to tag initial evidence / SourceIngest 之后立即标记初始证据
- During scheduled refresh to re-evaluate freshness / 定时刷新时重新评估时效性
- When Judge needs to verify timeliness of a specific claim / Judge 需要验证特定声明的时效性时

## Input / 输入

- `evidence_store_path`: Path to evidence_store.json
- `current_timestamp`: Current time (ISO8601)

## Output / 输出

- Updated `evidence_store.json` with `freshness_status` field corrected for each item

## Core Workflow / 核心工作流

### Step 1: Classify Evidence Track (LLM) / 分类证据轨道

For each evidence item, use LLM to determine if it supports:

- **Current-state claims / 当前状态声明**: "BTC is at $X today", "Company Y just announced Z", "The latest data shows..."
  → These need fresh sources. `evidence_track` should be `fact`

- **Reasoning/historical claims / 推理/历史声明**: "Historically, when X happened, Y followed", "The mechanism works because...", "Long-term trend analysis shows..."
  → These are valid regardless of age. `evidence_track` should be `reasoning`

If the evidence item already has `evidence_track` set correctly from SourceIngest, verify it. If incorrect, correct it.

### Step 2: Apply Freshness Rules / 应用时效规则

| Evidence Track | Source Age | Freshness Status |
|---|---|---|
| `fact` | ≤ 24 hours | `current` |
| `fact` | > 24 hours but ≤ 7 days | `current` (with note: "aging") |
| `fact` | > 7 days | `stale` |
| `reasoning` | Any age | `timeless` |

**Critical rule / 关键规则**: Reasoning-track evidence is ALWAYS `timeless`. NEVER mark historical, mechanism, or trend evidence as `stale`. This is a core design principle, not a soft guideline.

The 24-hour threshold is a soft guideline for the LLM to apply with semantic judgment:
- Breaking market data older than a few hours may already be stale
- A policy announcement from 3 days ago may still be "current" if no updates exist
- Use judgment, not mechanical cutoffs

### Step 3: System Capability Check / 系统能力检查

Verify that WebSearch can still return results published within the last 24 hours:

1. Run a quick WebSearch for a recent-events query related to the topic
2. Check if results include items from the last 24 hours
3. If yes → system has real-time capability (requirement met)
4. If no → log warning in audit trail: "real-time capability may be degraded"

### Step 4: Update Evidence Store / 更新证据存储

Write the updated evidence items (with corrected `freshness_status`) back to `evidence_store.json`.

## Important Distinction / 重要区分

This system guarantees **real-time information access capability** (can always fetch recent data), NOT that all evidence must be recent. Evidence chains may span any timeframe. A 200-year-old economic theory is valid reasoning-track evidence.

该系统保证的是**实时信息获取能力**（始终能获取近期数据），而非所有证据都必须是最近的。证据链可跨越任何时间跨度。
