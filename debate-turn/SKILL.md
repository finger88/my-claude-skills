---
name: debate-turn
description: >
  Constructs a complete structured debate turn with 5-element reasoning chains,
  rebuttals, and evidence references. Use this skill when a debater agent needs to
  construct an argument, build a debate turn, generate rebuttals against opponent,
  respond to mandatory judge response points, create a structured argument with
  evidence and causal reasoning chain, or produce a debate round output with
  historical wisdom and speculative scenarios.
license: MIT-0
compatibility: Requires bash and shasum. Internet access for evidence search.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, argument, reasoning-chain, rebuttal
  emoji: "🎤"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# DebateTurn
# 辩论回合

Construct a complete, structured debate turn with reasoning chains, rebuttals, mandatory responses, and evidence references.
构建包含推理链、反驳、必答回应和证据引用的完整结构化辩论回合。

## When to Use / 何时使用

- When pro-debater or con-debater agent constructs their round output / 正方或反方 agent 构建其回合输出时
- See `references/data-contracts.md` for the DebateTurn output schema

## Input / 输入

- `topic`: The debate topic
- `side`: "pro" or "con"
- `round_number`: Current round (1-indexed)
- `opponent_last_turn_path`: Path to opponent's previous turn JSON (null for round 1)
- `judge_ruling_path`: Path to previous round's judge_ruling.json (null for round 1)
- `evidence_store_path`: Path to evidence_store.json
- `claim_ledger_path`: Path to claim_ledger.json

## Output / 输出

- Structured DebateTurn JSON written to the designated round file path
- See `references/data-contracts.md` for exact schema

## Core Workflow / 核心工作流

### Step 1: Read Context / 读取上下文

1. Read the evidence store to understand available evidence
2. If round > 1:
   - Read opponent's last turn to identify points to rebut
   - Read judge's ruling to find mandatory response points targeting this side
   - Read claim ledger to understand current claim statuses

### Step 2: Address Mandatory Points FIRST / 首先处理必答点

**This is NON-NEGOTIABLE / 这是不可协商的**

For each `mandatory_response_point` from the judge targeting this side:
1. Read the point and understand what the judge requires
2. Construct a substantive response (not a dismissal)
3. Attach evidence where possible
4. Include in the `mandatory_responses` array of the output

The orchestrator will REJECT turns that skip mandatory points.

### Step 3: Construct Arguments / 构建论点

Build 2-4 new arguments, each following the **complete reasoning chain**:

```
Observed facts → Mechanism → Scenario implication → Trigger conditions → Falsification conditions
```

For each argument:
1. **Observed facts**: Cite specific data, events, or statistics from evidence store
2. **Mechanism**: Explain the causal relationship (WHY does A lead to B?)
3. **Scenario implication**: What follows if this mechanism holds?
4. **Trigger conditions**: What specific events would activate this scenario?
5. **Falsification conditions**: What evidence would DISPROVE this argument?

**Every argument MUST have all 5 elements.** Use semantic understanding to build a coherent chain — do not fill in a template mechanically.

**Every factual claim MUST reference evidence_ids** from the evidence store. Claims without evidence are structurally invalid.

### Step 4: Generate Rebuttals / 生成反驳

If round > 1, identify the opponent's strongest 1-3 arguments and construct rebuttals:

1. Target the opponent's **causal chain**, not just their conclusion
2. Identify the weakest link in their reasoning chain (faulty mechanism? missing trigger? unfalsifiable?)
3. Provide counter-evidence from the evidence store
4. Each rebuttal references the `target_claim_id` from the claim ledger

**Attack strategy / 攻击策略**: Prioritize attacking arguments the judge flagged as having causal validity issues. These are the most vulnerable.

### Step 5: Evidence Search (if needed) / 证据搜索（如需）

If existing evidence is insufficient for a strong argument:
1. Use WebSearch to find additional supporting evidence
2. Use WebFetch to extract content
3. Normalize into EvidenceItem format (use `scripts/hash-snippet.sh` for hash)
4. Include new evidence in the `new_evidence` array of the output
5. The orchestrator will merge these into the evidence store

### Step 6: Analogy Self-Check / 类比自检

If using historical or classical analogies:
1. Verify ≥ 2 similarities between the historical case and current topic
2. Include ≥ 1 key structural difference
3. Estimate analogy content share — keep under ~15% of total turn content
4. Flag any analogy that might fail AnalogySafeguard review

### Step 7: Historical Wisdom (v3) / 历史智慧

Read `config.json` to check `domain` and topic context.

Generate 1-3 historical references relevant to the debate topic:

1. **Select historical events** that share structural similarities with the current topic
   - Prioritize events from the same domain (e.g., tech debates → historical tech transitions)
   - Cross-domain historical parallels are welcome when structurally relevant
2. **For each reference, complete ALL fields** (no partial entries):
   - `historical_event`: Clear identification of the historical case
   - `era_context`: Sufficient background for readers unfamiliar with the history
   - `parallel_to_current`: Specific, causal parallels (not superficial similarity)
   - `key_differences`: Honest acknowledgment of where the parallel breaks down
   - `lesson_extracted`: The actionable insight, not just "history repeats"
   - `applicability_caveat`: Why this lesson might not apply here
3. **Quality over quantity**: 1 deeply analyzed historical reference > 3 shallow mentions
4. This section is `weight: "advisory"` — use it to add depth, not to substitute for evidence-based arguments

**What this section is NOT / 这个板块不是:**
- NOT a replacement for evidence-based arguments (those go in `arguments[]`)
- NOT subject to the strict AnalogySafeguard rules (but still requires `key_differences`)
- NOT a place for unsupported speculation (that goes in `speculative_scenarios`)

### Step 8: Speculative Scenarios (v3) / 推演场景

Read `config.json` for `speculation_level`:
- If `conservative`: SKIP this step entirely. Set `speculative_scenarios` to `null` in output.
- If `moderate`: Generate 1-2 scenarios grounded in existing evidence
- If `exploratory`: Generate 2-4 scenarios including unconventional/black swan paths

For each scenario:
1. **Start with a clear premise**: "If X happens..." — the premise should be specific, not vague
2. **Build a chain of events**: Show the causal sequence (A leads to B leads to C)
3. **Estimate probability honestly**: Use the three-tier system (low/medium/high)
4. **Assess impact**: What would happen if this scenario materializes?
5. **Identify early warning signals**: What observable events would precede this scenario?
6. **Include falsification**: What would prove this scenario impossible?

**Guidelines / 指导原则:**
- `moderate` scenarios should be plausible extensions of verified facts
- `exploratory` scenarios can include:
  - Black swan events (low probability, high impact)
  - Non-linear cascading effects
  - Scenarios that challenge conventional wisdom
  - "What if the opposite happens?" inversions
- Even `exploratory` scenarios must have an internally consistent causal chain
- Avoid pure fantasy — every scenario should be at least theoretically possible

## Quality Standards / 质量标准

- **Intellectual honesty**: Acknowledge genuine weaknesses in your position while arguing your side
- **Evidence quality**: Prefer tier1/tier2 sources. tier4_social is supplementary only
- **Reasoning depth**: A strong mechanism explanation is worth more than multiple weak claims
- **Falsifiability**: Every argument must include conditions that would prove it wrong
- **No strawmen**: Rebut the opponent's ACTUAL strongest points, not weak versions

## What NOT to Do / 禁止行为

- Do NOT make claims without evidence_ids
- Do NOT skip mandatory response points
- Do NOT use ad hominem attacks
- Do NOT present correlation as causation without justification
- Do NOT hardcode examples — reason from the actual topic
- Do NOT fill reasoning chain elements mechanically — each must be genuinely connected
