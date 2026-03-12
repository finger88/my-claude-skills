---
name: final-synthesis
description: >
  Generates the final debate report with verified facts, probable conclusions, enriched
  contested points, scenario outlook, conclusion profiles, and 24h watchlist. Use this
  skill when the orchestrator needs to generate the final debate report, synthesize all
  rounds into conclusions, create output with watchlist and scenario outlook, produce
  the debate summary, compile verified facts and contested points, or generate bilingual
  Markdown and English JSON reports.
license: MIT-0
compatibility: Requires bash and jq for JSON validation.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, report, synthesis, conclusion-profiles
  emoji: "📊"
---

# FinalSynthesis
# 最终综合

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | Enrich contested points to per-point subsections; switch from inline bilingual to English JSON + two-part MD (EN first, then CN appendix) / 争议点从单行表格升级为逐点子章节；语言从行内双语改为英文 JSON + 双段 MD（英文在前，中文附后） |

Generate the final debate report with verified facts, probable conclusions, contested points, scenario outlook, and 24h watchlist.
生成包含已验证事实、可能结论、争议点、情景展望和 24h 监控清单的最终辩论报告。

## When to Use / 何时使用

- After all debate rounds are complete / 所有辩论回合完成后
- When evidence state changes during refresh trigger report regeneration / 刷新时证据状态变化触发报告重新生成
- See `references/data-contracts.md` for FinalReport output schema

## Input / 输入

- `workspace_path`: Path to the debate workspace directory
- All round data: `rounds/round_*/` (pro_turn, con_turn, judge_ruling for each round)
- `claim_ledger_path`: Path to claim_ledger.json
- `evidence_store_path`: Path to evidence_store.json
- `config_path`: Path to config.json

## Output / 输出

- `FinalReport` JSON written to `reports/final_report.json`
- Markdown report written to `reports/debate_report.md`
- Human-readable summary for the user (bilingual Chinese + English)

## Core Workflow / 核心工作流

### Step 0: Read Output Format / 读取输出格式

Read `config.json` for `output_format` field. This controls the report detail level.

### Step 1: Aggregate All Rounds / 聚合所有回合

1. Read all round data chronologically (round 1, 2, ..., N)
2. Read the final claim ledger
3. Track how each claim's status evolved across rounds:
   - Was it challenged? When was it verified?
   - Did the judge flag issues? Were they resolved?

### Step 2: Categorize Claims / 分类声明

From the final claim ledger, categorize:

**Verified Facts / 已验证事实**:
- Claims with `status = verified`
- Cross-source confirmed
- Present as factual statements with source references
- Include ONLY claims verified by the Judge's independent check

**Probable Conclusions / 高概率结论**:
- Claims with strong reasoning chains that survived all rounds
- Claims where evidence supports but doesn't fully confirm
- Present with appropriate confidence qualifiers ("likely", "evidence suggests")

**Contested Points / 争议点**:
- Claims with `status = contested` in the claim ledger
- For EACH contested point, synthesize:
  1. **The core issue / 核心问题**: What exactly is being disputed?
  2. **Pro position / 正方立场**: Pro's strongest argument + key evidence (trace back to `rebuttals[]` and `arguments[]` across rounds)
  3. **Con position / 反方立场**: Con's strongest argument + key evidence
  4. **Key rebuttals / 关键反驳**: Extract the most impactful rebuttals from both sides' `rebuttals[]` arrays across all rounds. Include the rebuttal target, the counter-argument, and supporting `evidence_ids`
  5. **Judge assessment / 裁判评估**: Summarize the Judge's `verification_results` and `causal_validity_flags` relevant to this point
  6. **Resolution status / 解决状态**: Did the debate move toward resolution? (`unresolved` / `leaning_pro` / `leaning_con` / `partially_resolved`)
- Use LLM semantic judgment to identify the strongest arguments — don't just dump all rebuttals
  用 LLM 语义判断识别最强论点，不要简单堆砌所有反驳
- Also check `conflict_details` in ClaimItem for source-level conflicts
  同时检查 ClaimItem 中的 `conflict_details` 了解来源层面的冲突

**Items Requiring Verification / 待验证项**:
- Claims with `status = unverified`
- Include suggested verification methods (what data would resolve this?)
- Prioritize by importance to the overall debate conclusion

### Step 2.5: Generate Conclusion Profiles / 生成结论画像

For each major conclusion in `verified_facts` and `probable_conclusions`:

1. **Identify the conclusion**: Group related claims into a single conclusion statement
2. **Link source claims**: Reference the `claim_id`s that support this conclusion
3. **Evaluate each of the 10 dimensions** using LLM semantic judgment:
   - Read the claim statuses from claim_ledger
   - Read the Judge's verification results and causal validity flags
   - Read the evidence store for source quality and diversity
   - Consider the debate trajectory (did this conclusion strengthen or weaken across rounds?)
4. **Write a concise rationale** for each dimension (1-2 sentences, bilingual)

**Guidelines / 指导原则:**
- NOT every conclusion needs all 10 dimensions. Focus on the dimensions that are most informative for each specific conclusion.
  不是每个结论都需要全部 10 个维度。聚焦于对该特定结论最有信息量的维度。
- For verified facts: focus on confidence, evidence_coverage, validity_window
- For probable conclusions: focus on probability, confidence, reversibility, causal_clarity
- For contested points: focus on consensus, evidence_coverage, falsifiability
- Include the top 3-5 conclusions as full profiles; others can be light profiles (3-4 dimensions only)

### Step 3: Build Scenario Outlook / 构建情景展望

Based on verified facts and probable conclusions:

**Base case / 基准情景**:
- Most likely outcome based on the weight of evidence
- Ground it in verified facts, not speculation

**Upside triggers / 上行触发条件**:
- Specific events or data points that would improve the outlook
- Must be concrete and observable

**Downside triggers / 下行触发条件**:
- Specific events or data points that would worsen the outlook
- Must be concrete and observable

**Falsification conditions / 证伪条件**:
- What would completely invalidate the base case?
- These come from the strongest falsification conditions in the debate

### Step 3.5: Speculative Frontier / 推演前沿

If `config.speculation_level` is not `conservative`:

1. Collect all `speculative_scenarios` from both sides across all rounds
2. Deduplicate scenarios that explore similar premises
3. Sort by: impact_if_realized (highest first), then probability_estimate
4. For each scenario, note which side proposed it and the Judge's quality assessment
5. Present as a separate section — clearly labeled as exploratory, not conclusive

Include in FinalReport:
```json
{
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
  ]
}
```

### Step 3.6: Historical Wisdom Summary / 历史智慧汇总

Collect all `historical_wisdom` references from both sides:

1. Identify the most impactful historical parallels (based on Judge's relevance_grade)
2. Note conflicting historical lessons between sides
3. Extract overarching historical patterns that emerged

Include in FinalReport:
```json
{
  "historical_insights": {
    "key_parallels": ["Most relevant historical parallels and their lessons..."],
    "conflicting_lessons": ["Where historical evidence points in different directions..."],
    "meta_pattern": "Overarching historical pattern, if any..."
  }
}
```

### Step 4: Create 24h Watchlist / 创建 24h 监控清单

Items that could change conclusions if new information arrives within 24 hours:

For each watchlist item:
- `item`: What to monitor (specific data point, event, announcement)
- `reversal_trigger`: What change would reverse current conclusions
- `monitoring_source`: Where to look (specific publications, data sources, feeds)

Focus on:
- Stale claims that could be refreshed with new data
- Contested points where new evidence could tip the balance
- Trigger conditions identified in the scenario outlook

### Step 4.5: Source Diversity Assessment / 来源多样性评估

Analyze the complete evidence store to assess diversity:

1. **Source type distribution / 来源类型分布:**
   Count evidence items by `source_type` (web, twitter, academic, government, other)

2. **Credibility tier distribution / 可信度层级分布:**
   Count by `credibility_tier`. Flag if >70% of evidence is tier3/tier4.

3. **Geographic/perspective assessment / 地域/视角评估:**
   Use LLM to assess: Are sources geographically diverse? Do they represent multiple perspectives/viewpoints?
   Flag if all sources come from a single country or represent only one perspective.

4. **Diversity warning / 多样性警告:**
   Generate a warning if significant gaps exist (e.g., "Evidence heavily skewed toward US English-language media. Consider seeking sources from [relevant other perspectives].")

Include in FinalReport:
```json
{
  "evidence_diversity_assessment": {
    "source_type_distribution": {"web": 15, "academic": 3, "twitter": 8},
    "credibility_tier_distribution": {"tier1": 2, "tier2": 8, "tier3": 10, "tier4": 8},
    "geographic_diversity": "assessment text...",
    "perspective_balance": "assessment text...",
    "diversity_warning": "warning text or null"
  }
}
```

### Step 5: Write Report / 写入报告

1. Assemble into FinalReport JSON schema
2. **Language requirement / 语言要求**:
   - All JSON fields (`final_report.json`) in **English only**
   - Markdown report (`debate_report.md`): **English version first**, then `---` divider, then **complete Chinese translation** appended
   - LLM translates the full report semantically, not field-by-field
3. Write to `reports/final_report.json`
4. Validate with `scripts/validate-json.sh <file> final_report`
5. Log report generation via `scripts/append-audit.sh`

### Output Format Variants & Report Templates
### 输出格式变体和报告模板

See [references/report-templates.md](references/report-templates.md) for:
参见 [references/report-templates.md](references/report-templates.md)：

- `full_report` (default): Complete FinalReport with all sections / 完整报告
- `executive_summary`: Condensed version / 凝缩版
- `decision_matrix`: Structured decision format / 结构化决策格式
- Red Team report JSON structure / 红队报告 JSON 结构
- Complete Markdown report template (EN + CN) / 完整 Markdown 报告模板

## Output Principles / 输出原则

- **No total score / 不使用总分**: Use evidence states, not numerical ratings
- **Traceable / 可追溯**: Every conclusion links back to specific evidence and rounds
- **Balanced / 平衡**: Present contested points fairly with both sides represented
- **Actionable / 可行动**: Watchlist items should be specific enough to actually monitor
- **Honest about uncertainty / 诚实对待不确定性**: Clearly distinguish verified from probable from unverified
- **Language / 语言**: JSON in English; Markdown report has English version followed by complete Chinese translation
