# Data Contracts / 数据契约

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | contested_points 从 string[] 升级为结构化数组，含 pro/con position、rebuttals、judge assessment / Upgraded contested_points from string[] to structured array with positions, rebuttals, judge assessment |
| 2026-03-11 | Claude | v0.5.0 版本统一 / v0.5.0 version unification |
| 2026-03-11 | Claude | v0.2.0 升级：移除 PDF 相关字段、pre_mortem 模式、RoundsBilingual schema；新增 report_path / v0.2.0 upgrade: removed PDF fields, pre_mortem mode, RoundsBilingual schema; added report_path |
| 2026-03-11 | Claude | 添加 RoundsBilingual schema; 明确 pdf_outputs 叠加行为 / Added RoundsBilingual schema; clarified pdf_outputs stacking behavior |
| 2026-03-10 22:15 | Claude | FinalReport 添加 verdict_summary 字段; DebateConfig 添加 round_count/pro_model/con_model/judge_model/created_at / Added verdict_summary to FinalReport; added round_count/pro_model/con_model/judge_model/created_at to DebateConfig |

All agents and skills reference these JSON schemas as the single source of truth.
所有 agent 和 skill 引用这些 JSON schema 作为唯一真相来源。

---

## EvidenceItem

An individual piece of evidence from a source.
来自来源的单条证据。

```json
{
  "evidence_id": "evi_<hash_first8>",
  "source_type": "web | twitter | academic | government | other",
  "url": "https://...",
  "publisher": "Publisher Name",
  "published_at": "2026-03-09T12:00:00Z",
  "retrieved_at": "2026-03-09T12:30:00Z",
  "snippet": "Relevant excerpt from source...",
  "hash": "<SHA-256 of snippet>",
  "credibility_tier": "tier1_authoritative | tier2_reputable | tier3_general | tier4_social",
  "freshness_status": "current | stale | timeless",
  "evidence_track": "fact | reasoning",
  "social_credibility_flag": "likely_reliable | needs_verification | likely_unreliable | null",
  "verification_priority": "high | medium | low",
  "corroboration_status": "corroborated | uncorroborated | contradicted | null"
}
```

### Credibility Tiers / 可信度分级
- `tier1_authoritative`: Government agencies, central banks, major wire services (AP, Reuters) / 政府、央行、主要通讯社
- `tier2_reputable`: Major newspapers, established research institutions, peer-reviewed journals / 主要报纸、知名研究机构、同行评审期刊
- `tier3_general`: Blogs, smaller publications, industry reports, company press releases / 博客、小型出版物、行业报告、公司新闻稿
- `tier4_social`: Twitter/X, Reddit, forums, personal posts / Twitter、Reddit、论坛、个人帖子

### Freshness Status / 时效状态
- `current`: Source is recent enough to support current-state claims / 来源足够新，可支持当前状态声明
- `stale`: Source was used for a current-state claim but is now outdated / 来源用于当前状态声明但已过期
- `timeless`: Historical/mechanism/trend evidence; NEVER auto-downgraded / 历史/机制/趋势证据，永不自动降级

### Evidence Track / 证据轨道
- `fact`: Supports claims about the current state of the world / 支持关于当前世界状态的声明
- `reasoning`: Supports mechanism explanation, historical precedent, or trend analysis / 支持机制解释、历史先例或趋势分析

### Social Credibility Flag / 社交可信度标记
- `social_credibility_flag`: Only set for `source_type = "twitter"`. LLM pre-screens for fake news patterns. For non-Twitter sources, set to `null`.
  仅对 Twitter 来源设置。LLM 预筛假新闻特征。非 Twitter 来源设为 `null`。
- `verification_priority`: Derived from social_credibility_flag. `likely_unreliable` → `high`, `needs_verification` → `medium`, otherwise `low`.
  基于假新闻预筛结果推导。
- `corroboration_status`: Set during EvidenceVerify. Tracks whether independent non-social sources confirm this evidence. For non-Twitter sources, set to `null`.
  在 EvidenceVerify 中设置。追踪独立非社交来源是否确认。

---

## ClaimItem

A factual or inferential claim made by a debater.
辩手提出的事实性或推理性声明。

```json
{
  "claim_id": "clm_<round>_<side>_<seq>",
  "round": 1,
  "speaker": "pro | con",
  "claim_type": "fact | inference | analogy",
  "claim_text": "The claim statement...",
  "evidence_ids": ["evi_abc12345", "evi_def67890"],
  "status": "verified | contested | unverified | stale",
  "last_verified_at": "2026-03-09T12:00:00Z",
  "judge_note": "Judge's assessment...",
  "mandatory_response": false,
  "conflict_details": [
    {
      "source_a": {"evidence_id": "evi_xxx", "position": "Source A claims..."},
      "source_b": {"evidence_id": "evi_yyy", "position": "Source B claims..."},
      "divergence_point": "The specific point of disagreement...",
      "judge_assessment": "Judge's evaluation of the conflict..."
    }
  ]
}
```

### Conflict Details / 冲突明细

`conflict_details` is populated by Judge during verification when sources conflict. Allows FinalReport to explain WHY a claim is contested, not just THAT it is.
当来源冲突时由 Judge 填充。让 FinalReport 能解释声明为何有争议，而不仅仅标记为有争议。

### Claim Status State Machine / 声明状态机

```
                  ┌──────────┐
                  │unverified│
                  └────┬─────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
       ┌────────┐ ┌─────────┐ ┌─────┐
       │verified│ │contested│ │stale│
       └───┬────┘ └────┬────┘ └──┬──┘
           │           │         │
           ├───►contested◄───────┤
           │           │         │
           ├───►stale   │        │
           │           ├───►verified
           │           ├───►stale
           └───────────┘
```

Transitions / 转换:
- `unverified → verified`: Cross-source confirmed / 跨来源确认
- `unverified → contested`: Sources conflict / 来源冲突
- `unverified → stale`: Current-state source expired / 当前状态来源过期
- `verified → contested`: New contradicting evidence / 新的矛盾证据
- `verified → stale`: Fact-track source expired / 事实轨道来源过期
- `contested → verified`: Resolution with new evidence / 新证据解决争议
- `contested → stale`: All sources expired / 所有来源过期
- `stale → verified`: Fresh confirming source found / 找到新鲜确认来源

**Critical rule / 关键规则**: Reasoning-track claims (claim_type=analogy or evidence_track=reasoning) are NEVER auto-transitioned to `stale`.
推理轨道声明永不自动转换为 `stale`。

---

## DebateTurn (Pro/Con Turn Output)

Structured output from a single debate turn.
单次辩论回合的结构化输出。

```json
{
  "round": 1,
  "side": "pro | con",
  "arguments": [
    {
      "claim_text": "Main argument statement...",
      "claim_type": "fact | inference | analogy",
      "evidence_ids": ["evi_abc12345"],
      "reasoning_chain": {
        "observed_facts": "What data/events support this...",
        "mechanism": "Why does this cause that...",
        "scenario_implication": "What follows from this...",
        "trigger_conditions": "What would make this scenario happen...",
        "falsification_conditions": "What would prove this wrong..."
      }
    }
  ],
  "rebuttals": [
    {
      "target_claim_id": "clm_1_con_1",
      "rebuttal_text": "Counter-argument...",
      "evidence_ids": ["evi_def67890"]
    }
  ],
  "mandatory_responses": [
    {
      "point_id": "mrp_1_1",
      "response_text": "Addressing judge's point..."
    }
  ],
  "new_evidence": [],
  "historical_wisdom": {
    "weight": "advisory",
    "references": [
      {
        "historical_event": "Name/description of historical event",
        "era_context": "Historical context and background",
        "parallel_to_current": "How this parallels the current debate topic",
        "key_differences": "Critical structural differences from current situation",
        "lesson_extracted": "The insight or lesson drawn",
        "applicability_caveat": "Limitations of this historical reference"
      }
    ]
  },
  "speculative_scenarios": {
    "weight": "exploratory",
    "scenarios": [
      {
        "scenario_name": "Short descriptive name",
        "premise": "The 'what if' starting condition",
        "chain_of_events": "A → B → C sequence of consequences",
        "probability_estimate": "low (<10%) | medium (10-40%) | high (>40%)",
        "impact_if_realized": "Severity and scope of impact",
        "early_warning_signals": ["Observable precursors to watch for"],
        "what_would_falsify": "What would invalidate this scenario"
      }
    ]
  }
}
```

### Reasoning Chain (MANDATORY) / 推理链（必需）

Every argument MUST contain all 5 elements. Use semantic understanding, not mechanical templates.
每个论点必须包含全部 5 个要素。用语义理解构建，不要机械填模板。

1. **Observed facts / 观察到的事实**: Concrete data, events, or statistics
2. **Mechanism / 机制**: Causal explanation (why A leads to B)
3. **Scenario implication / 场景推演**: What follows if the mechanism holds
4. **Trigger conditions / 触发条件**: What would activate this scenario
5. **Falsification conditions / 证伪条件**: What would disprove this argument

### Historical Wisdom / 历史智慧

Advisory section for historical references and lessons. NOT subject to verified/contested status determination.
建议性板块，用于历史引用和教训。不受 verified/contested 状态判定约束。

- `weight: "advisory"` — This content informs analysis but is not treated as factual evidence
- Each reference MUST include `key_differences` and `applicability_caveat` (intellectual honesty requirement)
- Unlike analogies in `arguments[]`, historical_wisdom references are not constrained by the <15% content share rule
- 与 arguments[] 中的类比不同，historical_wisdom 不受 <15% 内容占比规则的约束

### Speculative Scenarios / 推演场景

Exploratory section for imaginative scenario planning. Controlled by `config.speculation_level`.
探索性板块，用于想象力场景规划。受 `config.speculation_level` 控制。

- `weight: "exploratory"` — These are thought experiments, not predictions
- `conservative` config → this section is OMITTED entirely
- `moderate` config → generate 1-2 evidence-grounded scenarios
- `exploratory` config → generate 2-4 scenarios including black swans and non-linear paths
- Every scenario MUST include `what_would_falsify` (falsifiability requirement carries over from v2)

---

## JudgeRuling

Judge's structured output after auditing a round.
裁判审计回合后的结构化输出。

```json
{
  "round": 1,
  "verification_results": [
    {
      "claim_id": "clm_1_pro_1",
      "original_status": "unverified",
      "new_status": "verified",
      "reasoning": "Cross-source confirmed by Reuters and Bloomberg..."
    }
  ],
  "causal_validity_flags": [
    {
      "claim_id": "clm_1_con_2",
      "issue": "correlation presented as causation",
      "severity": "critical | moderate | minor"
    }
  ],
  "mandatory_response_points": [
    {
      "point_id": "mrp_1_1",
      "target": "pro | con | both",
      "point": "What must be addressed...",
      "reason": "Why this needs response..."
    }
  ],
  "historical_wisdom_assessment": [
    {
      "side": "pro | con",
      "historical_event": "...",
      "relevance_grade": "strong_parallel | moderate_parallel | weak_parallel",
      "honesty_grade": "honest | partially_honest | misleading",
      "note": "..."
    }
  ],
  "round_summary": "Neutral summary of key developments..."
}
```

### Historical Wisdom Assessment / 历史智慧评估

Judge evaluates the QUALITY of historical reasoning, not whether the historical lesson supports pro or con. A well-analyzed weak parallel is better than a poorly analyzed strong one.
Judge 评估历史推理的质量，而非历史教训支持正方还是反方。

---

## FinalReport

Final synthesis output after all debate rounds.
所有辩论回合后的最终综合输出。

```json
{
  "topic": "The debate topic",
  "total_rounds": 3,
  "generated_at": "2026-03-09T18:00:00Z",
  "verdict_summary": "One-sentence overall judgment / 一句话总判断",
  "report_path": "reports/debate_report.md",
  "verified_facts": [
    "Cross-source confirmed factual statements..."
  ],
  "probable_conclusions": [
    "High-confidence conclusions with qualifiers..."
  ],
  "contested_points": [
    {
      "point": "The contested claim or issue",
      "claim_ids": ["clm_1_pro_2", "clm_2_con_1"],
      "pro_position": "Pro's strongest argument on this point with evidence summary / 正方在该点上的最强论点及证据摘要",
      "con_position": "Con's strongest argument on this point with evidence summary / 反方在该点上的最强论点及证据摘要",
      "key_rebuttals": [
        {
          "from": "pro | con",
          "target": "What they're rebutting / 反驳的对象",
          "argument": "The rebuttal content / 反驳内容",
          "evidence_ids": ["evi_xxx"]
        }
      ],
      "judge_assessment": "Judge's evaluation of which side has stronger support / 裁判对哪方支持更强的评估",
      "resolution_status": "unresolved | leaning_pro | leaning_con | partially_resolved"
    }
  ],
  "to_verify": [
    "Claims needing further verification with suggested methods..."
  ],
  "scenario_outlook": {
    "base_case": "Most likely scenario based on verified facts...",
    "upside_triggers": ["Conditions that would improve outlook..."],
    "downside_triggers": ["Conditions that would worsen outlook..."],
    "falsification_conditions": ["What would invalidate base case..."]
  },
  "watchlist_24h": [
    {
      "item": "What to monitor...",
      "reversal_trigger": "What would change conclusions...",
      "monitoring_source": "Where to watch..."
    }
  ],
  "evidence_diversity_assessment": {
    "source_type_distribution": {"web": 15, "academic": 3, "twitter": 8},
    "credibility_tier_distribution": {"tier1": 2, "tier2": 8, "tier3": 10, "tier4": 8},
    "geographic_diversity": "assessment text...",
    "perspective_balance": "assessment text...",
    "diversity_warning": "warning text or null"
  },
  "speculative_frontier": [
    {
      "scenario_name": "...",
      "proposed_by": "pro | con",
      "premise": "...",
      "chain_of_events": "...",
      "probability": "...",
      "impact": "...",
      "early_warnings": ["..."],
      "judge_quality_note": "..."
    }
  ],
  "historical_insights": {
    "key_parallels": ["Most relevant historical parallels and their lessons..."],
    "conflicting_lessons": ["Where historical evidence points in different directions..."],
    "meta_pattern": "Overarching historical pattern, if any..."
  },
  "executive_summary": {
    "summary_paragraph": "One-paragraph executive summary...",
    "top_verified_facts": ["..."],
    "top_contested_points": ["..."],
    "base_case_outlook": "...",
    "top_watchlist_items": ["..."]
  },
  "decision_matrix": {
    "dimensions": [
      {
        "factor": "Factor name",
        "pro_position": "Pro's strongest point on this factor",
        "con_position": "Con's strongest point on this factor",
        "evidence_strength": "strong | moderate | weak",
        "judge_note": "..."
      }
    ],
    "overall_lean": "Slightly favors pro/con because...",
    "key_uncertainty": "The factor most likely to change the conclusion...",
    "recommendation": "Based on current evidence..."
  },
  "conclusion_profiles": [
    {
      "conclusion_id": "concl_1",
      "conclusion_text": "Conclusion description",
      "source_claims": ["clm_1_pro_1", "clm_2_con_3"],
      "profile": {
        "probability": {
          "value": "high (>70%) | medium (30-70%) | low (<30%)",
          "rationale": "Basis for probability judgment"
        },
        "confidence": {
          "value": "high | medium | low",
          "rationale": "How evidence quality affects certainty of probability judgment"
        },
        "consensus": {
          "value": "high | partial | low",
          "rationale": "Degree of disagreement between pro and con"
        },
        "evidence_coverage": {
          "value": "complete | partial | sparse",
          "gaps": "Key missing links in the evidence chain"
        },
        "reversibility": {
          "value": "high | medium | low",
          "reversal_trigger": "What new evidence/event could overturn this conclusion"
        },
        "validity_window": {
          "value": "hours | days | weeks | months | indefinite",
          "expiry_condition": "What condition would invalidate this conclusion"
        },
        "impact_magnitude": {
          "value": "extreme | high | medium | low",
          "scope": "Scope and depth of impact"
        },
        "causal_clarity": {
          "value": "clear_chain | partial_chain | correlation_only",
          "weakest_link": "Weakest link in the causal chain"
        },
        "actionability": {
          "value": "directly_actionable | informational | requires_more_data",
          "suggested_action": "Suggested action if actionable"
        },
        "falsifiability": {
          "value": "easily_testable | testable_with_effort | hard_to_test",
          "test_method": "How to verify this conclusion"
        }
      }
    }
  ]
}
```

### Evidence Diversity Assessment / 来源多样性评估

Included in every FinalReport. Analyzes the evidence store for source diversity gaps.
每份 FinalReport 都包含。分析证据库的来源多样性缺口。

### Speculative Frontier / 推演前沿

Included when `config.speculation_level` is not `conservative`. Collects and deduplicates speculative scenarios from both sides across all rounds.
当 `config.speculation_level` 不为 `conservative` 时包含。收集并去重双方在所有回合中的推演场景。

### Historical Insights / 历史洞察

Summarizes the most impactful historical parallels, conflicting lessons, and overarching patterns from both sides.
汇总双方最有影响力的历史平行、冲突教训和总体模式。

### Executive Summary / 执行摘要

Optional condensed format. Generated when `config.output_format = "executive_summary"`. Also written to `reports/executive_summary.json`.
可选精简格式。当 `config.output_format = "executive_summary"` 时生成。同时写入 `reports/executive_summary.json`。

### Decision Matrix / 决策矩阵

Optional structured decision format. Generated when `config.output_format = "decision_matrix"`. Also written to `reports/decision_matrix.json`.
可选结构化决策格式。当 `config.output_format = "decision_matrix"` 时生成。同时写入 `reports/decision_matrix.json`。

### ConclusionProfile / 结论画像

Multi-dimensional characterization of each major conclusion. Goes far beyond probability alone.
每个主要结论的多维刻画。远超概率单一维度。

**10 dimensions / 10 个维度:**

| Dimension / 维度 | What it measures / 衡量什么 | Why it matters / 为什么重要 |
|---|---|---|
| Probability / 概率 | Likelihood of event occurring / 事件发生可能性 | Most basic judgment / 最基本的判断 |
| Confidence / 置信度 | Certainty of the probability judgment itself / 对概率判断本身的确定性 | "70% probability with low confidence" vs "70% with high confidence" mean very different things / 含义完全不同 |
| Consensus / 共识度 | Degree of disagreement between sides / 正反双方分歧程度 | High consensus = more stable; low consensus = more contested / 高共识更稳固，低共识更有争议 |
| Evidence Coverage / 证据完整度 | Completeness of evidence chain / 证据链完整性 | Reveals blind spots / 发现盲区 |
| Reversibility / 可逆性 | How easily new evidence could overturn conclusion / 新证据推翻结论的难易度 | High reversibility = unstable, needs monitoring / 高可逆 = 不稳定，需持续关注 |
| Validity Window / 时效窗口 | How long the conclusion remains valid / 结论有效期 | Some conclusions expire in 48 hours / 有些结论 48 小时后就可能过时 |
| Impact Magnitude / 影响幅度 | Severity if realized / 如果发生的影响大小 | Low probability + high impact = black swan / 低概率高影响 = 黑天鹅型 |
| Causal Clarity / 因果清晰度 | Completeness of causal chain / 因果链完整性 | Distinguishes correlation from causation / "相关性" vs "因果性" 的区分 |
| Actionability / 可操作性 | Whether it can guide decisions / 能否指导行动 | Decision-makers need actionable conclusions / 决策者需要可操作结论 |
| Falsifiability / 可证伪性 | How easily it can be tested / 验证难易度 | Unfalsifiable conclusions have limited value / 不可证伪的结论价值有限 |

**Key rule / 关键规则:** Each dimension uses LLM semantic judgment, NOT mechanical scoring.
每个维度用 LLM 语义判断，不要用机械评分。

> All FinalReport JSON fields are English-only. Chinese translation appears in debate_report.md as an appended section.
> FinalReport 的所有 JSON 字段仅使用英文。中文翻译出现在 debate_report.md 的附加部分。

---

## DebateConfig

Configuration for a debate session. Written to `config.json` in the workspace root.
辩论会话配置。写入工作区根目录的 `config.json`。

```json
{
  "topic": "The debate topic",
  "rounds": 3,
  "round_count": 3,
  "pro_model": "Model identifier for pro debater",
  "con_model": "Model identifier for con debater",
  "judge_model": "Model identifier for judge",
  "created_at": "2026-03-09T12:00:00Z",
  "domain": "geopolitics | tech | health | finance | philosophy | culture | general",
  "depth": "quick | standard | deep",
  "evidence_scope": "web_only | academic_included | user_provided | mixed",
  "output_format": "full_report | executive_summary | decision_matrix",
  "speculation_level": "conservative | moderate | exploratory",
  "language": "en | zh | bilingual",
  "focus_areas": ["user-defined dimensions to focus on"],
  "mode": "balanced | red_team",
  "status": "initialized | in_progress | complete"
}
```

### Field Documentation / 字段说明

- `round_count`: Alias for `rounds`. Preferred by scripts. The orchestrator SHOULD write both for compatibility.
  `rounds` 的别名。脚本优先读取此字段。编排器应同时写入两者以保证兼容。

- `pro_model` / `con_model` / `judge_model`: Model identifiers for each agent. Written by orchestrator at debate start. Used in report header.
  各 agent 的模型标识符。由编排器在辩论开始时写入，用于报告头部。

- `created_at`: ISO 8601 timestamp of debate creation. / 辩论创建的 ISO 8601 时间戳。

- `domain`: The subject domain of the debate. Defaults to `"general"` if not provided. When `"general"`, LLM infers the most appropriate domain from the topic text.
  辩论的主题领域。未提供时默认为 `"general"`。为 `"general"` 时，LLM 从话题文本推断最合适的领域。

- `depth`: Controls search and argument intensity. / 控制搜索和论证深度。
  - `quick`: 3 search queries, 2 arguments per turn, lighter verification / 3 条搜索查询，每回合 2 个论点，较轻验证
  - `standard`: 5 search queries, 2-4 arguments per turn, standard verification / 5 条搜索查询，每回合 2-4 个论点，标准验证
  - `deep`: 8 search queries, 3-5 arguments per turn, thorough verification / 8 条搜索查询，每回合 3-5 个论点，深入验证

- `evidence_scope`: Controls what types of evidence sources to include. Defaults to `"web_only"`.
  控制包含哪些类型的证据来源。默认为 `"web_only"`。

- `output_format`: Controls the final report format. Defaults to `"full_report"`.
  控制最终报告格式。默认为 `"full_report"`。

- `speculation_level`: Controls whether `speculative_scenarios` section is generated in DebateTurn (Phase 3). Defaults to `"moderate"`.
  控制 DebateTurn 中是否生成 `speculative_scenarios` 部分。默认为 `"moderate"`。
  - `conservative`: No speculative scenarios generated / 不生成推演场景
  - `moderate`: 1-2 evidence-grounded scenarios / 1-2 个基于证据的场景
  - `exploratory`: 2-4 scenarios including black swans / 2-4 个场景，含黑天鹅

- `mode`: Controls debate structure. Defaults to `"balanced"`.
  控制辩论结构。默认为 `"balanced"`。
  - `balanced`: Standard pro/con debate / 标准正反方辩论
  - `red_team`: Con becomes Red Team (risks), Pro becomes Blue Team (mitigations) / Con 变为红队（风险），Pro 变为蓝队（缓解）

- `language`: Output language. Defaults to `"bilingual"`. / 输出语言。默认 `"bilingual"`。

- `focus_areas`: User-defined dimensions to prioritize in analysis. Defaults to `[]`.
  用户定义的重点分析维度。默认为 `[]`。

---

## Audit Trail Entry (JSONL) / 审计日志条目

Each line in `logs/audit_trail.jsonl` is an independent JSON object.
`logs/audit_trail.jsonl` 中每行是一个独立 JSON 对象。

```json
{"timestamp": "2026-03-09T12:00:00Z", "action": "workspace_initialized | round_started | pro_turn_complete | con_turn_complete | judge_ruling_complete | claim_status_changed | evidence_added | report_generated | refresh_triggered", "details": {}}
```
