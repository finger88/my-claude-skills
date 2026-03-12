---
name: skill-manager
version: v3.2
description: "Comprehensive skill management system for Claude Code. 14 core functions: list, evaluate, optimize, backup, rollback, log, auto-git-commit, batch-backup, batch-evaluate, version diff, and registry management (register, formalize, remove, trial status). Use when user wants to manage skills or maintain the skills ecosystem. Trigger words: '列出 skills', '评估 XXX', '优化 XXX', '备份 XXX', '回退 XXX', '自动提交', '批量备份', '批量评估', '版本对比', '注册 XXX', '转正 XXX', '删除 XXX', '试用期'."
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
| 7 | **自动 Git 提交** | "自动提交" / "git 提交" | 含 push 后自动更新 README 表格 | [references/functions/git-auto.md](references/functions/git-auto.md) |
| 8 | **批量备份** | "批量备份" / "备份所有 skills" | [references/functions/batch-backup.md](references/functions/batch-backup.md) |
| 9 | **批量评估** | "批量评估" / "检查 skills 质量" | [references/functions/batch-evaluate.md](references/functions/batch-evaluate.md) |
| 10 | **版本 Diff 对比** | "diff 对比" / "版本对比" | [references/functions/diff.md](references/functions/diff.md) |
| 11 | **注册技能** | "注册 xxx" / "新增 skill" | [references/functions/registry.md](references/functions/registry.md) |
| 12 | **转正技能** | "转正 xxx" / "skill 转正" | [references/functions/registry.md](references/functions/registry.md) |
| 13 | **删除技能** | "删除 xxx" / "卸载 xxx" | [references/functions/registry.md](references/functions/registry.md) |
| 14 | **查看试用期** | "试用期" / "试用状态" | [references/functions/registry.md](references/functions/registry.md) |

---

## 目录结构

```
~/my-claude-skills/               # Git 仓库（单一数据源）
├── skill-name/                   # 每个 skill 目录
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── assets/
├── packages/                     # 大包/技能集目录
│   └── package-name/
│       └── README.md
├── registry.json                 # 技能注册表（分类/状态/安装日期）
├── docs/                         # 管理文档
└── README.md

~/.claude/skills/                 # Claude 加载目录（全部为 Junction）
└── skill-name -> my-claude-skills/skill-name  # Windows Junction

D:\my tool\skills log\            # 日志与备份目录
├── backups\                      # 备份目录（独立于 Git）
│   └── YYYYMMDD-skill-name-vX.Y\
├── skills修改日志.md
└── skills迭代计划.md
```

**架构说明**: `~/.claude/skills/` 下所有目录均为 Junction，指向 `~/my-claude-skills/` Git 仓库。编辑任何 skill 文件会直接修改 Git 仓库中的文件。

**Registry**: `registry.json` 记录技能元数据（分类、试用状态、安装日期），由 skill-manager 统一管理，不影响 Claude 加载 skill。

---

## 执行要点

### 功能 1: 列出技能

读取 `~/.claude/skills/` 目录，检查每个 skill 的 SKILL.md、YAML frontmatter、子目录，按来源分类（官方/社区/自建）输出表格。

### 功能 2: 评估技能

基于 5 个维度评估: YAML Frontmatter、渐进式披露、Token 效率（< 150 行）、自动发现（"Use when..."）、输出格式。输出评估报告和改进建议。

### 功能 3: 优化技能

完整工作流: 评估 -> 备份 -> 优化 -> 验证 -> 记录。自动项无需确认（格式修复），半自动项需确认（Token 拆分、Description 增强、本地化定制）。

### 功能 4: 备份技能

1. 从 SKILL.md YAML frontmatter 提取版本号（`version: vX.Y`）
2. 创建备份目录: `backups/YYYYMMDD-skill-name-vX.Y/`
3. 复制 SKILL.md + references/ + scripts/ + assets/
4. 记录到 skills修改日志.md

**版本号提取**: 优先从 frontmatter `version` 字段读取，其次从更新日志匹配 `vX.Y`，均无则自动分配 `1.0.0` 并写入 frontmatter。

### 功能 5: 回退技能

1. 列出该 skill 所有备份，显示版本号供选择
2. 回退前自动备份当前版本（`-pre-rollback` 后缀）
3. 从选定备份恢复，记录日志

### 功能 6: 记录日志

读取 `D:\my tool\skills log\skills修改日志.md`，追加修改记录（类型、内容、验证结果、回退方法）。

### 功能 7: 自动 Git 提交

支持手动触发或配置自动提交。配置 `config.json` 中 `git.autoCommit: true` 后，修改操作完成后自动执行 git commit/push。

**Push 后自动更新 README**: 默认开启（`autoUpdateReadme: true`），push 完成后自动扫描所有 skills，更新 README.md 中的 skills 表格。

### 功能 8: 批量备份

一键备份所有已安装 skills，支持增量检测（跳过无变更技能），生成汇总报告。

### 功能 9: 批量评估

批量评估所有 skills 的 5 个维度质量，生成评分汇总和改进建议，支持导出报告。

### 功能 10: 版本 Diff 对比

对比同一 skill 的两个备份版本或当前版本与历史备份，输出结构化差异报告。

### 功能 11-14: Registry 管理

统一管理 `registry.json` 技能注册表，实现试用追踪和分类管理。

**功能 11: 注册技能**
- 将新安装 skill 添加到 `registry.json`
- 自动提取分类、版本、描述
- 默认状态为 `trial`，记录安装日期
- 支持指定所属包（如 `critical-debater`）

**功能 12: 转正技能**
- 将 skill 状态从 `trial` 改为 `formal`
- 更新 `registry.json` 并自动 git commit
- README 下次 push 后自动更新显示

**功能 13: 删除技能**
- 从 `registry.json` 移除条目
- 可选删除 Git 仓库中的 skill 目录
- 自动清理 Junction 链接

**功能 14: 查看试用期**
- 列出所有 `trial` 状态技能
- 显示试用天数（安装日期至今）
- 提示建议操作（转正/删除）

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

1. **Junction 架构**: `~/.claude/skills/` 下均为 Junction，修改即写入 Git 仓库
2. **备份策略**: 备份到 `skills log\backups\`（独立于 Git），每次修改前自动备份
3. **Git 提交**:
   - 手动模式：备份/回退/优化完成后提醒用户执行 git commit/push
   - 自动模式：配置 `config.json` 中 `git.autoCommit: true` 后自动提交
4. **批量操作**: 批量备份/评估时单个 skill 失败不影响其他 skill
5. **日志格式**: 严格按照模板格式记录，便于后续追溯
6. **路径处理**: Windows 路径使用双反斜杠 `\\` 或正斜杠 `/`
7. **迭代计划**: 详见 `D:\my tool\skills log\skills迭代计划.md`
