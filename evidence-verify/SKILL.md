---
name: evidence-verify
description: >
  Performs cross-source verification, credibility validation, and independent re-search
  for debate evidence. Use this skill when the judge needs to verify evidence
  independently, cross-check sources, validate a claim's supporting evidence, check
  if Twitter-only claims have independent corroboration, perform independent source
  verification, assess evidence credibility, or determine claim verification status.
license: MIT-0
compatibility: Internet access needed for independent source verification.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, evidence, verification, cross-source
  emoji: "✅"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# EvidenceVerify
# 证据验证

Cross-source verification, credibility scoring, and Twitter signal validation for debate claims.
辩论声明的跨来源验证、可信度评分和 Twitter 信号验证。

## When to Use / 何时使用

- When Judge audits a round (primary use) / Judge 审计回合时（主要用途）
- When Orchestrator needs to re-verify claims during refresh / Orchestrator 在刷新时需要重新验证声明
- When a debater wants to pre-verify their own evidence / 辩手想预验证自己的证据时

## Input / 输入

- `claim`: A `ClaimItem` with `evidence_ids[]`
- `evidence_store_path`: Path to evidence_store.json
- `independent_search`: Boolean — if true, run fresh WebSearch (used by Judge)

## Output / 输出

- Updated `status` recommendation for the claim
- `verification_notes`: Explanation of verification result
- `confidence_level`: "high" | "medium" | "low"

## Core Workflow / 核心工作流

### Step 1: Gather Referenced Evidence / 收集引用的证据

Resolve `evidence_ids` to full `EvidenceItem` objects from the evidence store.

If any `evidence_id` is not found in the store, flag as `evidence_missing` and note in verification.

### Step 2: Source Independence Check / 来源独立性检查

For **critical claims** (claims central to the argument or with high impact):
- Require ≥ 2 independent sources (different publishers, different URLs)
- Sources from the same publisher group do NOT count as independent
- Wire services (AP, Reuters) redistributed by multiple outlets count as ONE source

For **non-critical claims** (peripheral supporting points):
- 1 reputable source is acceptable

Use LLM judgment to determine criticality based on how central the claim is to the debate.

### Step 3: Twitter Signal Validation + Corroboration (v3) / Twitter 信号验证 + 关联确认

If ANY evidence supporting a claim has `source_type = "twitter"`:

1. **Check social_credibility_flag** (set by SourceIngest):
   - If `likely_unreliable`: Flag claim as high verification priority. Auto-set status ceiling to `unverified` unless strong independent evidence exists.
   - If `needs_verification`: Standard verification process, but actively search for corroboration.

2. **Corroboration search** (enhanced from v2):
   - For `verification_priority = "high"` Twitter claims: ALWAYS run an independent WebSearch query derived from the claim text
   - Search specifically for non-social (tier1/tier2/tier3) sources that confirm or deny the claim
   - Update the Twitter EvidenceItem's `corroboration_status`:
     - `corroborated`: Found ≥1 independent non-social source confirming
     - `uncorroborated`: No independent confirmation found
     - `contradicted`: Found independent source(s) that directly contradict the claim

3. **Status determination** (unchanged logic, new data):
   - Twitter + corroborated → eligible for `verified` (if other conditions met)
   - Twitter + uncorroborated → maximum `unverified` with note "twitter-only, uncorroborated"
   - Twitter + contradicted → `contested` with note "twitter claim contradicted by [source]"
   - Twitter + `likely_unreliable` + uncorroborated → `unverified` with note "flagged (suspected misinformation)"

### Step 4: Cross-Source Agreement / 跨来源一致性

Use LLM to compare snippets across evidence items:

1. Do the sources agree on the core factual claim?
2. Are there contradictions between sources?
3. Do sources add complementary details or conflict?

If sources **agree**: strengthens verification
If sources **partially conflict**: flag specific points of disagreement → `contested`
If sources **fully contradict**: → `contested` with detailed note

### Step 5: Independent Re-Search (Judge Only) / 独立重新搜索（仅 Judge）

When `independent_search = true` (invoked by Judge):

1. Run fresh WebSearch with queries derived from the claim text
2. Compare results against debater-provided evidence
3. Check: Does independent search confirm, contradict, or add nuance?
4. This is the Judge's independent verification — do NOT trust the debater's citations alone

### Step 6: Determine Status / 判定状态

Based on all checks:

| Condition | Recommended Status |
|---|---|
| ≥2 independent non-social sources agree | `verified` |
| Sources partially conflict | `contested` |
| Only 1 source, or only social sources | `unverified` |
| Fact-track source expired (stale evidence) | `stale` |
| Evidence items not found | `unverified` with "evidence_missing" note |

## Error Handling / 错误处理

- Cannot fetch original source for re-verification → note as "source_unreachable" but don't auto-invalidate the claim
- Independent search returns no results → note "no independent confirmation found" but don't auto-reject
