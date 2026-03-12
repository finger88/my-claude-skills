# My Claude Skills

个人 Claude Code 技能集合。包含内容提取、深度阅读、知识管理、日程复盘等多领域 skills。

## Skills 列表

<!-- SKILLS-TABLE-START -->
| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **analogy-safeguard** | - | Validates historical and classical analogies in debate arguments | 自建 |
| **claim-ledger-update** | - | Manages the claim state machine for a multi-agent debate system | 自建 |
| **daily-review** | - | 飞书日历日记生成器 | 自建 |
| **datetime-tool** | - | 获取当前时间、格式化日期、计算日期差值、时区转换 | 自建 |
| **debate** | - | Launches a multi-agent debate on any topic with real-time evidence verification | 自建 |
| **debate-turn** | - | Constructs a complete structured debate turn with 5-element reasoning chains | 自建 |
| **evidence-verify** | - | Performs cross-source verification and credibility validation for debate evidence | 自建 |
| **feifei-reading** | - | 沉浸式物理共读搭子 | 自建 |
| **final-synthesis** | - | Generates the final debate report with verified facts and watchlists | 自建 |
| **freshness-check** | - | Validates evidence timeliness and tags freshness status | 自建 |
| **judge-audit** | - | Performs independent verification and causal chain audit for debate rounds | 自建 |
| **ljg-card** | v1.6.0 | Content caster (铸). Transforms content into PNG visuals | 社区 |
| **ljg-clip** | - | On-demand content clipper for L1 intake | 社区 |
| **ljg-explain-concept** | - | Deep concept anatomist that deconstructs any concept | 社区 |
| **ljg-explain-words** | - | A deep-dive word mastery tool that deconstructs English words | 社区 |
| **ljg-paper** | v2.2.0 | Paper deep reader with atom pipeline | 社区 |
| **ljg-xray-article** | - | X-ray scans articles to extract wisdom cores using a 4-layer funnel | 社区 |
| **ljg-xray-book** | - | Deep structure extraction from books using the Epiplexity principle | 社区 |
| **memory-review** | v1.0 | 周期性记忆校准 | 自建 |
| **skill-creator** | v2.1.0 | Create new skills, modify and improve existing skills | 官方 |
| **skill-hub** | v1.1.0 | 统一技能管理器，整合 clawhub.ai、skills.sh 和 GitHub 仓库 | 自建 |
| **skill-manager** | v3.1 | Comprehensive skill management system for Claude Code | 自建 |
| **source-ingest** | - | Searches, fetches, and normalizes web sources for debate evidence | 自建 |
| **weather** | - | Get current weather and forecasts | 社区 |
| **web-content-extraction** | - | 9-layer toolkit for extracting web content from restricted domains | 自建 |
| **weekly-review** | - | 周报复盘生成器 | 自建 |
| **xlsx** | - | Use this skill any time a spreadsheet file is the primary input | 社区 |
<!-- SKILLS-TABLE-END -->

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

## 目录结构

```
my-claude-skills/
├── skill-name/
│   ├── SKILL.md              # 核心配置（< 150 行）
│   ├── references/            # 参考资料（按需加载）
│   ├── scripts/               # 可执行脚本
│   └── assets/                # 资源文件
├── docs/
│   ├── skills修改日志.md       # 修改历史
│   ├── skills迭代计划.md       # 迭代路线图
│   └── skills评估与修改建议.md  # 评估报告
└── README.md
```

## 管理工具

本仓库配套 **skill-manager** 技能，提供：
- 评估 skill 质量（基于 Anthropic 最佳实践）
- 带版本号的备份（`YYYYMMDD-skill-name-vX.Y`）
- 一键回退到任意历史版本
- 修改日志自动记录

## 致谢

- ljg 系列 skills 来自 [lijigang](https://github.com/lijigang) 的优秀设计
- 基于 Anthropic 官方 skill 最佳实践构建

## License

MIT
