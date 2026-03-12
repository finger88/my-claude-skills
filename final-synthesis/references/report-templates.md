# Report Templates — FinalSynthesis
# 报告模板 — 最终综合

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Extracted from SKILL.md for progressive disclosure / 从 SKILL.md 提取，渐进式披露 |

---

## Output Format: `full_report` (default)

Generate complete FinalReport with all sections as defined in SKILL.md workflow.

## Output Format: `executive_summary`

Generate a condensed version:
1. One-paragraph summary of the debate conclusion (bilingual)
2. Top 3-5 verified facts (bullet points)
3. Top 2-3 contested points with one-sentence explanation each
4. Scenario outlook: base case + top 2 triggers only
5. Top 3 watchlist items

Write to `reports/executive_summary.json` AND `reports/final_report.json` (full version still generated for reference).

Present the executive summary to the user, with a note that the full report is available.

## Output Format: `decision_matrix`

Generate a structured decision matrix:
1. Extract the core decision dimensions from the debate (LLM identifies 4-8 key factors)
2. For each dimension:
   - Factor name
   - Pro side's evidence/argument summary (1-2 sentences)
   - Con side's evidence/argument summary (1-2 sentences)
   - Evidence strength: strong | moderate | weak (based on claim statuses)
   - Judge's assessment note
3. Overall recommendation: Which side has stronger evidence across factors?
4. Key uncertainty: What single factor could flip the conclusion?

Write to `reports/decision_matrix.json` AND `reports/final_report.json`.

---

## Red Team Report Format / 红队报告格式

When `config.mode = "red_team"`, replace the standard FinalReport structure with:

```json
{
  "topic": "...",
  "mode": "red_team",
  "risk_assessment": [
    {
      "risk_id": "risk_1",
      "risk_description": "...",
      "severity": "critical | high | medium | low",
      "likelihood": "high | medium | low",
      "risk_score": "severity x likelihood qualitative",
      "red_team_argument": "How and why this risk could materialize...",
      "blue_team_mitigation": "Proposed mitigation and residual risk...",
      "judge_verdict": "Is mitigation feasible? Is residual risk acceptable?",
      "evidence_ids": ["..."]
    }
  ],
  "unmitigated_risks": ["Risks where Blue Team had no effective response..."],
  "risk_matrix_summary": "Overall risk posture assessment...",
  "recommended_actions": ["Prioritized list of actions to reduce risk..."]
}
```

---

## Markdown Report Template / Markdown 报告模板

Generate a structured Markdown report for human consumption.

Output: `reports/debate_report.md` (inside workspace directory)

Structure:

```markdown
# Debate Report: <topic>
## Executive Summary
<executive_summary from Step 4.5>

## Decision Matrix
| Factor | Assessment | Confidence | Key Evidence |
|---|---|---|---|

## Verified Facts
| # | Claim | Status | Sources | Track |
|---|---|---|---|---|

## Contested Points

### CP-1: <point title>
**Status**: <resolution_status>

**Pro Position**: <pro's strongest argument + evidence refs>

**Con Position**: <con's strongest argument + evidence refs>

**Key Rebuttals**:
- **[Pro → Con]** <target>: <argument> (Evidence: evi_xxx)
- **[Con → Pro]** <target>: <argument> (Evidence: evi_yyy)

**Judge Assessment**: <evaluation>

---

### CP-2: ...
(repeat for each contested point, ~200-400 words each)

## Key Arguments by Round
### Round N
| Side | Core Argument | Strength | Key Evidence |
|---|---|---|---|

## Scenario Outlook
| Scenario | Probability | Trigger | Timeframe |
|---|---|---|---|

## Watchlist
| # | Item | Why It Matters | Monitor How |
|---|---|---|---|

## Evidence Inventory
| ID | Source | Type | Tier | Freshness | Track |
|---|---|---|---|---|---|

## Conclusion Profiles (if Red Team mode)
| Dimension | Assessment | Confidence |
|---|---|---|

## Methodology
- Rounds: N, Mode: balanced/red_team
- Evidence items: X, Sources verified: Y
- Generated: <timestamp>

---

# 辩论报告：<topic>
## 执行摘要
...
## 争议点
### 争点-1: <标题>
**状态**: ...
**正方立场**: ...
**反方立场**: ...
**关键反驳**: ...
**裁判评估**: ...

---

### 争点-2: ...

## 各轮关键论点
...
## 情景展望
...
## 监控清单
...
## 证据清单
...
## 方法论
...
(complete semantic Chinese translation of all English sections above)
```
