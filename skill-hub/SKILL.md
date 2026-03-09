---
name: skill-hub
version: "1.1.0"
description: |
  统一技能管理器，整合 clawhub.ai、skills.sh 和 GitHub 仓库三个来源。
  提供跨平台搜索、安装、列表和智能推荐功能。
  当用户想要查找技能、安装技能、管理已安装技能，或说"帮我找个做 X 的技能"时使用此技能。
  关键词：找技能、搜索技能、安装技能、技能列表、skill search、skill install、clone、GitHub
---

# Skill Hub | 统一技能管理器

跨生态系统的技能管理工具。不关心技能来自 clawhub、skills.sh 还是 GitHub，只给你最好的匹配。

## 生态系统

| 生态 | 安装路径 | CLI 命令 | 规模 |
|------|----------|----------|------|
| **clawhub** | `~/.claude/skills/` | `npx clawhub install <name>` | ~11,000+ skills |
| **skills.sh** | `~/.agents/skills/` | `npx skills add <owner/repo@skill>` | ~100-500 skills |
| **GitHub** | `~/my-claude-skills/` | `python scripts/install.py <url>` | 任意仓库 |

## 核心功能

### 1. 统一搜索

搜索两个生态系统，合并结果按相关性排序：

```bash
python scripts/search.py <关键词>
```

示例：
```bash
python scripts/search.py datetime
python scripts/search.py pdf
python scripts/search.py "web scraping"
```

### 2. 统一安装

自动识别生态系统，执行正确安装命令：

```bash
python scripts/install.py <skill-identifier>
```

支持格式：
- clawhub: `skill-name`
- skills.sh: `owner/repo@skill-name`
- github: `https://github.com/user/repo.git`

GitHub 安装示例：
```bash
# 列出仓库中所有可用技能
python scripts/install.py https://github.com/user/repo.git

# 指定安装某个技能
python scripts/install.py https://github.com/user/repo.git --skill skill-name
```

GitHub 安装流程：clone → 扫描 SKILL.md → 复制到 `~/my-claude-skills/` → 创建 symlink → npm install（如需要）→ git commit+push。

### 3. 统一列表

查看所有已安装技能（两个生态合并）：

```bash
python scripts/list.py
```

### 4. 智能推荐

基于当前任务和使用历史推荐技能：

```bash
python scripts/recommend.py
```

## 搜索实现

### clawhub 搜索

使用网页抓取（WebFetch 或 curl）：
- URL: `https://clawhub.ai/skills?search={query}`
- 解析结果提取技能名称、描述、安装量

### skills.sh 搜索

使用官方 CLI：
- 命令: `npx skills find {query}`
- 解析文本输出

### 结果合并策略

1. 两个生态分别搜索（并行）
2. 去重（同名技能优先展示两个来源）
3. 排序：
   - 精确匹配 > 部分匹配
   - 高安装量 > 低安装量
   - 已安装的技能标记 ★

## 推荐实现

### 数据来源 A：当前任务内容

从 `_本周.md` 提取：
- 任务关键词（标书、角色工程、Prompt）
- 当前项目（用海监管、亲子创作）
- 阻塞问题（需要技能解决）

### 数据来源 B：使用历史

从技能目录统计：
- 高频使用技能（近期修改时间）
- 从未使用技能（可清理）
- 技能组合模式（用 A 时经常也用 B）

### 推荐规则

```python
if "标书" in tasks and "文档解析" not in installed:
    recommend("document-parser")

if "角色工程" in tasks and "prompt" not in installed:
    recommend("prompt-optimizer")
```

## 输出格式

### 搜索结果

```markdown
找到 8 个技能（clawhub: 5, skills.sh: 3）

1. datetime-tool (skills.sh) ★★★★★ 已安装
   获取当前时间、格式化日期、时区转换
   安装: npx skills add openakita/openakita@datetime-tool

2. date-utils (clawhub)
   日期处理工具
   安装: npx clawhub install date-utils
```

### 推荐结果

```markdown
基于你的本周任务（标书智能体、角色工程）：

🔍 你可能需要:
1. document-parser — 解析标书模板
   理由: 任务中提到"标书"，此技能可提取文档结构

2. prompt-optimizer — 优化角色 Prompt
   理由: "角色工程"任务，需要迭代测试 Prompt
```

## 错误处理

| 错误场景 | 处理 |
|----------|------|
| clawhub 搜索超时 | 仅返回 skills.sh 结果，标记 ⚠️ |
| skills.sh 未安装 | 仅返回 clawhub 结果，提示安装 CLI |
| 网络中断 | 返回本地已安装技能列表 |
| 无匹配结果 | 建议修改关键词或创建自定义技能 |

## 相关文件

- [生态对比](references/ecosystems.md) — clawhub vs skills.sh 详细对比
- [搜索脚本](scripts/search.py) — 统一搜索实现
- [安装脚本](scripts/install.py) — 统一安装实现
- [列表脚本](scripts/list.py) — 已安装技能汇总
- [推荐脚本](scripts/recommend.py) — 智能推荐实现
