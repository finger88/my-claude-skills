---
name: skill-manager
description: Comprehensive skill management system for Claude Code. Lists installed skills, evaluates quality against Anthropic best practices, backs up skills with timestamps, restores from backups, and logs modification history. Use when user wants to manage skills (list, evaluate, backup, restore, log changes), check skill quality, optimize skills, or maintain the skills ecosystem. Trigger words: '列出 skills', '评估 XXX', '优化 XXX', '备份 XXX', '回退 XXX', 'skills 管理'.
---

# Skill Manager | 技能管理器

专门用于管理 Claude Code skills 的元工具。

## 核心功能

| # | 功能 | 触发词 | 详细说明 |
|---|------|--------|---------|
| 1 | **列出技能** | "列出所有 skills" | [references/functions/list.md](references/functions/list.md) |
| 2 | **评估技能** | "评估 xxx" | [references/functions/evaluate.md](references/functions/evaluate.md) |
| 3 | **优化技能** | "优化 xxx" | [references/functions/optimize.md](references/functions/optimize.md) |
| 4 | **备份技能** | "备份 xxx" | [references/functions/backup.md](references/functions/backup.md) |
| 5 | **回退技能** | "回退 xxx" | [references/functions/rollback.md](references/functions/rollback.md) |
| 6 | **记录日志** | "记录修改了 xxx" | [references/functions/log.md](references/functions/log.md) |

---

## 目录结构

```
~/.claude/skills/                 # Skills 安装目录
D:\my tool\skills log\            # 日志目录
├── backups\                      # 备份目录
│   └── YYYYMMDD-skill-name-vX.Y\ # 带时间戳+版本号的备份
│       └── SKILL.md
├── skills评估与修改建议.md        # 评估报告
├── skills修改日志.md              # 修改记录
└── skills迭代计划.md              # 迭代路线图
```

---

## 执行要点

### 功能 1: 列出技能

读取 `~/.claude/skills/` 目录，检查每个 skill 的 SKILL.md、YAML frontmatter、子目录，按来源分类（官方/社区/自建）输出表格。

### 功能 2: 评估技能

基于 5 个维度评估: YAML Frontmatter、渐进式披露、Token 效率（< 150 行）、自动发现（"Use when..."）、输出格式。输出评估报告和改进建议。

### 功能 3: 优化技能

完整工作流: 评估 -> 备份 -> 优化 -> 验证 -> 记录。自动项无需确认（格式修复），半自动项需确认（Token 拆分、Description 增强、本地化定制）。

### 功能 4: 备份技能

1. 从 SKILL.md 更新日志提取版本号（匹配最后一条 `vX.Y`）
2. 创建备份目录: `backups/YYYYMMDD-skill-name-vX.Y/`
3. 复制 SKILL.md + references/ + scripts/ + assets/
4. 记录到 skills修改日志.md

**版本号提取**: 优先从更新日志匹配 `vX.Y`，无法提取则回退为无版本号目录名。

### 功能 5: 回退技能

1. 列出该 skill 所有备份，显示版本号供选择
2. 回退前自动备份当前版本（`-pre-rollback` 后缀）
3. 从选定备份恢复，记录日志

### 功能 6: 记录日志

读取 `D:\my tool\skills log\skills修改日志.md`，追加修改记录（类型、内容、验证结果、回退方法）。

---

## 三层渐进式披露原则

Skill 应遵循的核心结构:

```
元信息层（始终加载）    -> YAML frontmatter: name + description
    ↓ 触发时加载
指令层（按需加载）      -> SKILL.md body: 执行步骤（< 150 行）
    ↓ 任务需要时加载
资源层（条件加载）      -> references/ + scripts/ + assets/
```

评估和优化时以此为标准。

---

## 注意事项

1. **备份策略**: 每次修改前自动备份，回退前再次备份当前版本
2. **日志格式**: 严格按照模板格式记录，便于后续追溯
3. **路径处理**: Windows 路径使用双反斜杠 `\\` 或正斜杠 `/`
4. **权限检查**: 操作前检查文件读写权限
5. **迭代计划**: 详见 `D:\my tool\skills log\skills迭代计划.md`

---

## 更新日志

- **2026-03-03 v1.0**: 初始版本，含列出/评估/备份/回退/记录 5 个功能 + 优化功能
- **2026-03-05 v1.1**: 备份目录支持版本号自动提取（`YYYYMMDD-skill-name-vX.Y`）
- **2026-03-05 v2.0**: 渐进式披露重构，拆分 6 个功能详解到 references/functions/，SKILL.md 从 297 行精简至当前
