---
name: claim-ledger-update
description: >
  Manages the claim state machine for a multi-agent debate system. Use this skill when
  the orchestrator needs to update the claim ledger, record new claims from a debate turn,
  change claim status based on judge ruling, track claim state transitions, extract claims
  from arguments, perform batch updates from judge rulings, or manage the claim lifecycle
  with audit trail persistence.
license: MIT-0
compatibility: Requires bash and jq for JSON validation and audit trail.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, claims, state-machine, audit-trail
  emoji: "📋"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# ClaimLedgerUpdate
# 声明账本更新

Manage claim state machine transitions, extract claims from debate turns, and persist changes with audit trail.
管理声明状态机转换，从辩论回合中提取声明，并通过审计日志持久化变更。

## When to Use / 何时使用

- After each debate turn to extract and register new claims / 每次辩论回合后提取并注册新声明
- After Judge ruling to update claim statuses / Judge 裁定后更新声明状态
- During refresh when evidence states change / 刷新时证据状态变化时

## Input / 输入

- `action`: "extract_claims" | "update_status" | "batch_update"
- `claim_ledger_path`: Path to claim_ledger.json
- `audit_trail_path`: Path to logs/audit_trail.jsonl
- For `extract_claims`: debate turn JSON (pro_turn or con_turn)
- For `update_status`: claim_id, new_status, reason
- For `batch_update`: JudgeRuling JSON

## Output / 输出

- Updated `claim_ledger.json`
- Audit trail entries appended via `scripts/append-audit.sh`

## Core Workflow / 核心工作流

### Action: extract_claims / 提取声明

When processing a completed debate turn:

1. Read the debate turn JSON (pro_turn.json or con_turn.json)
2. For each argument in the turn, create a `ClaimItem`:
   - `claim_id`: `clm_<round>_<side>_<sequence>` (e.g., `clm_1_pro_1`)
   - `round`: from the turn
   - `speaker`: "pro" or "con"
   - `claim_type`: Use LLM to classify as `fact`, `inference`, or `analogy`
   - `claim_text`: The argument's claim text
   - `evidence_ids`: From the argument's evidence references
   - `status`: `unverified` (initial state for all new claims)
   - `last_verified_at`: null
   - `judge_note`: null
   - `mandatory_response`: false
   - `conflict_details`: [] (empty initially; populated by Judge during verification)
3. Append new claims to claim_ledger.json
4. Log via `scripts/append-audit.sh`:
   ```json
   {"timestamp":"...","action":"claims_extracted","details":{"round":1,"side":"pro","count":3}}
   ```

### Action: update_status / 更新状态

When updating a single claim:

1. Read claim_ledger.json
2. Find the claim by `claim_id`
3. Validate the state transition is legal (see state machine in data-contracts.md):
   - `unverified → verified | contested | stale`
   - `verified → contested | stale`
   - `contested → verified | stale`
   - `stale → verified`
4. **Critical check**: If the claim is reasoning-track (claim_type=analogy OR backed by reasoning-track evidence), REJECT transition to `stale` with reason "reasoning-track claims cannot be auto-staled"
5. Update `status`, `last_verified_at`, `judge_note`
6. Write updated ledger
7. Log the transition via `scripts/append-audit.sh`:
   ```json
   {"timestamp":"...","action":"claim_status_changed","details":{"claim_id":"clm_1_pro_1","old_status":"unverified","new_status":"verified","reason":"..."}}
   ```

### Action: batch_update / 批量更新

When processing a JudgeRuling:

1. Read the JudgeRuling JSON
2. For each item in `verification_results`:
   - Call `update_status` logic for the claim
3. For each item in `mandatory_response_points`:
   - Find the target claim(s) and set `mandatory_response = true`
3b. For each claim with `new_status = "contested"` in verification_results:
   - If the Judge's reasoning describes conflicting sources, extract and structure as `conflict_details`
   - Use LLM to identify: which evidence says what, and where exactly they diverge
   - Append to the claim's `conflict_details` array (don't overwrite existing conflicts)
4. Write updated ledger once (not per-claim)
5. Log batch update to audit trail

## State Machine Enforcement / 状态机执行

All transitions must be validated. Illegal transitions are rejected with an error message. The orchestrator should handle rejected transitions by logging them and continuing (never block the debate for a state machine error).

## Persistence / 持久化

- Use `scripts/append-audit.sh` for atomic audit trail writes
- Write claim_ledger.json directly (overwrite with updated full array)
- Always validate the resulting JSON with `scripts/validate-json.sh <file> claim_item` after writing
