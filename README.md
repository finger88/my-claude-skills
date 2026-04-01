# My Claude Skills

个人 Claude Code 技能集合。包含内容提取、深度阅读、知识管理、日程复盘等多领域 skills。

---

## 📊 Skills 概览

<!-- STATS-START -->
| 指标 | 数量 |
|------|------|
| **总计** | 34 |
| **正式使用** | 25 |
| **试用期** | 12 ⏳ |
| **大包** | 1 |
<!-- STATS-END -->

---

## ⏳ 试用期 Skills

以下技能正在试用中，建议在使用 **7-14天** 后决定是否转正或删除：

| Skill | 版本 | 分类 | 用途 | 试用天数 |
|-------|------|------|------|----------|
| **debate** | - | 🎭 辩论系统 | 多Agent辩论入口 | 20天 |
| **source-ingest** | - | 🎭 辩论系统 | 证据收集 | 20天 |
| **freshness-check** | - | 🎭 辩论系统 | 时效验证 | 20天 |
| **evidence-verify** | - | 🎭 辩论系统 | 跨源验证 | 20天 |
| **debate-turn** | - | 🎭 辩论系统 | 辩论回合构建 | 20天 |
| **analogy-safeguard** | - | 🎭 辩论系统 | 类比验证 | 20天 |
| **judge-audit** | - | 🎭 辩论系统 | 裁判审计 | 20天 |
| **claim-ledger-update** | - | 🎭 辩论系统 | 声明管理 | 20天 |
| **final-synthesis** | - | 🎭 辩论系统 | 报告生成 | 20天 |
| **_gym-deep-dive** | - | 🧪 青训营 | 技能试用评估 | 2天 |
| **getnote-mcp** | - | 🔗 集成 | Get笔记MCP集成 | 19天 |
| **web-access** | - | 🔧 工具 | 网页访问与内容提取 | 2天 |

> 📦 [critical-debater 包详情](./packages/critical-debater/README.md)

---

## 🎭 辩论系统

**包**: [critical-debater](./packages/critical-debater/README.md) (9 skills)

多Agent辩论系统，用于深度批判性分析任何话题。

```bash
# 使用示例
claude "/debate Bitcoin will surpass gold as a store of value within 10 years"
claude "/debate --rounds 3 --depth deep --mode red_team Will AI replace most knowledge workers by 2030?"
```

---

## 📚 内容处理

内容提取、深度阅读和知识管理。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **ljg-clip** | - | On-demand内容剪藏 | 社区 |
| **ljg-card** | v1.6.0 | 内容铸卡(长图/信息图) | 社区 |
| **ljg-explain-concept** | - | 概念8维解构 | 社区 |
| **ljg-explain-words** | - | 单词深度解析 | 社区 |
| **ljg-paper** | v2.2.0 | 论文深度阅读 | 社区 |
| **ljg-xray-article** | - | 文章X光解剖 | 社区 |
| **ljg-xray-book** | - | 书籍结构提取 | 社区 |
| **web-content-extraction** | - | 网页内容提取(9层降级) | 自建 |
| **feifei-reading** | - | 飞飞物理共读 | 自建 |
| **touch-reading** | - | 触读法深度阅读 | 自建 |
| **dream-to-video** | - | 梦境素材转视频 | 自建 |
| **video-replication-sop-cy** | - | 视频复刻分镜生产SOP | 自建 |

---

## 📅 生产力

日记、周报、时间管理和记忆系统。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **daily-review** | - | 飞书日历日记生成器 | 自建 |
| **weekly-review** | - | 周报复盘生成器 | 自建 |
| **memory-review** | v1.0 | 周期性记忆校准 | 自建 |
| **pptx-generator** | v1.1 | PPT生成与编辑 | minimax |

---

## 🛠️ 技能管理

技能的创建、安装、备份和评估。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **skill-manager** | v3.1 | 技能管理系统(评估/备份/优化/Git) | 自建 |
| **skill-hub** | v1.1.0 | 技能搜索安装(跨平台) | 自建 |
| **skill-creator** | v2.1.0 | 技能创建与eval测评 | 官方 |

---

## 🔗 集成

第三方服务和工具集成。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **getnote-mcp** | - | Get笔记MCP集成 | 自建 |
| **getnote-openclaw** | - | Get笔记个人知识库 | 自建 |

---

## 🧪 青训营

技能试用评估与测试。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **_gym-deep-dive** | - | 青训营技能评估 | 自建 |

---

## 🔧 工具

天气、时间、电子表格等实用工具。

| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **datetime-tool** | - | 时间日期工具 | 自建 |
| **weather** | - | 天气查询 | 社区 |
| **xlsx** | - | 电子表格处理 | 社区 |
| **web-access** | - | 网页访问与内容提取 | 自建 |

---

## 安装

```bash
# 克隆仓库
git clone https://github.com/finger88/my-claude-skills.git
cd my-claude-skills

# 复制全部 skills 到 Claude 目录
cp -r */ ~/.claude/skills/

# 或只安装单个 skill
cp -r web-content-extraction ~/.claude/skills/
```

---

## 目录结构

```
my-claude-skills/
├── packages/                  # 大包/技能集
│   └── critical-debater/      # 多Agent辩论系统
│       └── README.md
├── registry.json              # 技能注册表(分类/状态/安装日期)
├── skill-name/                # 单个技能目录
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── assets/
├── docs/
│   ├── skills修改日志.md
│   ├── skills迭代计划.md
│   └── skills评估与修改建议.md
└── README.md
```

---

## 管理工具

本仓库配套 **skill-manager** 技能，提供：
- 评估 skill 质量（基于 Anthropic 最佳实践）
- 带版本号的备份（`YYYYMMDD-skill-name-vX.Y`）
- 一键回退到任意历史版本
- 修改日志自动记录
- **push后自动更新 README** skills 表格

---

## 致谢

- ljg 系列 skills 来自 [lijigang](https://github.com/lijigang) 的优秀设计
- critical-debater 来自 [xwxga](https://github.com/xwxga/critical-debater)
- 基于 Anthropic 官方 skill 最佳实践构建

---

## License

MIT
