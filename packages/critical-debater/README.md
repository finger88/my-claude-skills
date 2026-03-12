# 🎭 critical-debater | 多Agent辩论系统

来源: https://github.com/xwxga/critical-debater

## 简介

一个结构化的多Agent辩论系统，通过正反方对抗和独立裁判机制，对任何话题进行深度批判性分析。

## 核心特点

- **5要素推理链**: 观察事实 → 机制 → 场景 → 触发条件 → 可证伪性检验
- **实时证据验证**: 自动搜索和交叉验证证据
- **历史类比保护**: 验证类比的结构合规性
- **独立裁判**: Judge Agent 独立审计，不受辩论双方影响

## 使用方式

```bash
# 基础辩论
claude "/debate Bitcoin will surpass gold as a store of value within 10 years"

# 高级配置
claude "/debate --rounds 3 --depth deep --mode red_team Will AI replace most knowledge workers by 2030?"
```

## 包含技能 (9个)

| 技能 | 角色 | 功能 |
|------|------|------|
| **debate** | 入口 | 解析参数，启动编排器 |
| **source-ingest** | 证据收集 | 网络搜索 → 证据标准化 |
| **freshness-check** | 时效验证 | 证据时效标记 |
| **evidence-verify** | 交叉验证 | 跨源验证 + Twitter交叉验证 |
| **debate-turn** | 辩手 | 构建5要素推理链论证 |
| **analogy-safeguard** | 类比审计 | 历史类比结构验证 |
| **judge-audit** | 裁判 | 独立验证 + 因果审计 |
| **claim-ledger-update** | 状态管理 | 声明状态机 |
| **final-synthesis** | 报告生成 | 最终报告 + 24h观察清单 |

## 输出

生成结构化 Markdown 报告，包含：
- 已验证事实
- 可能结论（置信度分级）
- 争议点
- 场景展望
- 24小时观察清单

## 试用期状态

⏳ **试用期中** (自 2026-03-12)

建议试用场景：
- 投资决策前的多角度分析
- 技术方案的红蓝对抗评估
- 热点事件的深度追踪

转正标准：
- [ ] 完成3次以上实际辩论
- [ ] 验证证据质量符合预期
- [ ] 报告输出满足需求
