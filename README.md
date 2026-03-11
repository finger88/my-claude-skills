# My Claude Skills

个人 Claude Code 技能集合。包含内容提取、深度阅读、知识管理、日程复盘等多领域 skills。

## Skills 列表

<!-- SKILLS-TABLE-START -->
| Skill | 版本 | 用途 | 来源 |
|-------|------|------|------|
| **daily-review** | - | 飞书日历日记生成器 | 自建 |
| **datetime-tool** | - | 获取当前时间、格式化日期、计算日期差值、时区转换 | 自建 |
| **feifei-reading** | - | 沉浸式物理共读搭子 | 自建 |
| **ljg-clip** | - | 内容剪藏到 inbox.org | 社区改 |
| **ljg-explain-concept** | - | 概念 8 维解构 | 社区 |
| **ljg-explain-words** | - | 英文单词深度解析 + HTML 卡片 | 社区 |
| **ljg-paper** | v2.2.0 | 论文深度阅读（原子管线） | 社区 |
| **ljg-xray-article** | - | 文章深度解剖（4 层漏斗） | 社区 |
| **ljg-xray-book** | - | 书籍核心结构提取（Epiplexity） | 社区 |
| **memory-review** | - | 周期性记忆校准 | 自建 |
| **skill-creator** | v2.1.0 | Skill 创建、迭代与 eval 测评（官方最新） | 官方 |
| **skill-hub** | - | 跨平台技能搜索安装 | 自建 |
| **skill-manager** | v3.1 | Skills 生态管理（评估/备份/优化/回退/Git 自动提交） | 自建 |
| **weather** | - | 天气查询 | 社区 |
| **web-content-extraction** | - | 9 层网页内容提取工具，自动降级 | 自建 |
| **weekly-review** | - | 周报复盘生成器 | 自建 |
| **xlsx** | - | 电子表格处理 | 社区 |
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
