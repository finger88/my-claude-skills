---
name: debate
description: >
  Launches a multi-agent debate on any topic with real-time evidence verification
  and causal reasoning chains. Use this skill when the user says "debate", "start
  a debate", "run a debate on", "argue about", "red team this", "analyze from
  multiple perspectives", or provides a topic for critical examination. Supports
  balanced and red-team modes, configurable depth and rounds, domain-aware evidence
  gathering, and generates structured Markdown reports with conclusion profiles
  and 24h watchlists.
license: MIT-0
compatibility: Requires bash, jq, python3, and shasum. Internet access for WebSearch.
metadata:
  version: "0.6.0"
  author: xwxga
  homepage: "https://github.com/xwxga/critical-debater"
  tags: debate, multi-agent, evidence-verification, reasoning
  emoji: "🏛️"
---

## Changelog / 变更日志

| 时间 / Time | 作者 / Author | 变更 / Change |
|---|---|---|
| 2026-03-11 | Claude | v0.6.0: Agent Skills open standard compliance — frontmatter restructured, English-only description, progressive disclosure, evals added / Agent Skills 开放标准兼容 — 前置元数据重构、纯英文描述、渐进式披露、添加评测 |
| 2026-03-11 | Claude | v0.5.0: recovered from broken symlink, unified version / 从断开的 symlink 恢复，统一版本号 |

# /debate — Multi-Agent Debate System
# /debate — 多Agent辩论系统

You are launching the Critical Debater multi-agent debate system.
你正在启动 Critical Debater 多 agent 辩论系统。

## Arguments / 参数

The user invoked this command with: $ARGUMENTS

Parse the arguments:
- **First argument**: debate topic (required, quoted string) / 辩论话题（必需）
- **Remaining arguments**: optional flags in any order / 可选标志，顺序不限

Supported flags:
- `--domain <value>`: geopolitics | tech | health | finance | philosophy | culture | general (default: auto-infer from topic)
- `--depth <value>`: quick | standard | deep (default: standard)
- `--rounds <N>`: number of rounds (default: 3)
- `--mode <value>`: balanced | red_team (default: balanced)
- `--speculation <value>`: conservative | moderate | exploratory (default: moderate)
- `--output <value>`: full_report | executive_summary | decision_matrix (default: full_report)
- `--language <value>`: en | zh | bilingual (default: bilingual)
- `--focus <value>`: comma-separated focus areas (default: none)

Examples:
- `/debate "Bitcoin vs Gold as store of value"` → all defaults, domain auto-inferred as finance
- `/debate "React vs Vue" --domain tech --depth deep --speculation exploratory`
- `/debate "Is remote work productive?" --mode red_team --output executive_summary`
- `/debate "中东局势" --rounds 5 --focus "oil prices,shipping routes"`

**Auto-inference / 自动推断:** If `--domain` is not provided, use LLM to infer the most appropriate domain from the topic text. Include the inferred domain in the config.json passed to the orchestrator.

## Execution / 执行

Launch the `debate-orchestrator` agent to drive the entire workflow:

1. Spawn a `debate-orchestrator` subagent with this prompt:

```
Run a full multi-agent debate.

Topic: <parsed topic>
Rounds: <parsed rounds>
Config: <all parsed config fields as JSON>
Project root: <current working directory>

Write the full config to the workspace config.json before proceeding.

Follow your system prompt to execute all 4 phases:
1. Initialize workspace (run scripts/init-workspace.sh, gather evidence via WebSearch/WebFetch)
2. Run <N> debate rounds (Pro → Con → Judge each round, using Agent tool for each)
3. Generate final synthesis report
4. Offer scheduled refresh setup

Key references:
- Data contracts: .claude/skills/source-ingest/references/data-contracts.md
- Project rules: docs/debate_system_v2.md
- Scripts: scripts/init-workspace.sh, scripts/validate-json.sh, scripts/hash-snippet.sh, scripts/append-audit.sh

Present the final report in a readable, bilingual (Chinese + English) format to the user.
```

2. When the orchestrator completes, present its final report output to the user.

### Mode: `red_team`

When `config.mode = "red_team"`, the debate structure changes:

- **Con agent becomes Red Team**: Instead of opposing a motion, it actively searches for risks, vulnerabilities, failure modes, and blind spots in the topic/plan.
- **Pro agent becomes Blue Team**: Instead of supporting a motion, it defends against Red Team attacks with mitigations, contingency plans, and risk acceptance rationale.
- **Judge agent**: Evaluates the SEVERITY and LIKELIHOOD of each identified risk, and the FEASIBILITY of proposed mitigations.

**Orchestrator prompt adjustment:**
```
Run a Red Team analysis.

Topic: <parsed topic>
Mode: red_team
...

IMPORTANT MODE CHANGE:
- Con agent's role: RED TEAM — find every possible risk, failure mode, vulnerability, and blind spot. Be creative and thorough. Think about edge cases, cascading failures, adversarial scenarios, and black swan events.
- Pro agent's role: BLUE TEAM — for each risk identified by Red Team, propose mitigations, assess residual risk, and provide risk acceptance rationale where mitigation is impractical.
- Judge's role: Assess each risk's severity (critical/high/medium/low) and likelihood (high/medium/low). Evaluate whether Blue Team's mitigations are feasible and sufficient.
```

## Notes / 注意事项

- The debate runs sequentially within each round: Pro → Con → Judge
- Each agent runs as an isolated subagent
- All state is persisted to the workspace directory as JSON files
- The system guarantees real-time information access (can fetch data from last 24 hours)
- Evidence chains may span any timeframe — historical evidence is valid
- No total scores — output uses evidence states (verified, contested, unverified, stale)
