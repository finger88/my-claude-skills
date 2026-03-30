# Claude Skills 管理标准规范

> **版本**: v1.0
> **最后更新**: 2026-03-30
> **适用环境**: Windows + MSYS2/Git Bash

## 概述

本文档定义了 Claude Skills 本地管理的标准规范，确保：

- ✅ 所有 skills 通过 Git 版本控制
- ✅ 本地开发环境与 Claude Code 加载点同步
- ✅ 双向同步机制可靠运行
- ✅ 问题可快速诊断和修复

## 快速开始

### 1. 读取标准配置

```bash
# 每次操作前读取此配置
cat ~/my-claude-skills/.skillrc
```

### 2. 运行标准检查

```bash
# 检查当前环境是否符合标准
python ~/my-claude-skills/tools/check-standard.py
```

### 3. 修复 Junction 问题

```bash
# 自动修复所有 Junction 链接问题
cd ~/my-claude-skills
./fix-junctions.sh
```

## 文档索引

| 文档 | 内容 | 何时查阅 |
|------|------|----------|
| [01-目录结构标准](01-directory-structure.md) | 完整的目录架构和定义 | 初次设置、理解整体设计 |
| [02-Junction 管理](02-junction-management.md) | Junction 链接的创建、验证、修复 | 创建新 skill、Junction 问题 |
| [03-同步工作流](03-sync-workflow.md) | 新增/修改/删除 skill 的标准流程 | 日常操作 |
| [04-故障排查](04-troubleshooting.md) | 常见问题和解决方案 | 遇到问题 |

## 核心原则

### 1. 单一真源原则

所有 skills 的**唯一真源**是 `~/my-claude-skills/` Git 仓库。

```
❌ 错误：在多个位置保存 skill 副本
✅ 正确：所有修改都在 my-claude-skills/ 中进行
```

### 2. Junction 唯一原则

`~/.claude/skills/` 中的所有 skill 必须是 **Junction 链接**，不能是实际目录。

```
❌ 错误：cp -r skill ~/.claude/skills/
✅ 正确：MSYS_NO_PATHCONV=1 cmd /c "mklink /J ..."
```

### 3. 先检查再操作原则

任何 skill 相关操作前，先运行标准检查：

```bash
python tools/check-standard.py
```

## 目录结构速览

```
C:\Users\HONOR\
├── my-claude-skills\          # 【Git 仓库】Skills 唯一真源
│   ├── .skillrc               # 【YAML】标准配置文件
│   ├── docs/standards/        # 规范文档
│   ├── tools/                 # 工具脚本
│   │   └── check-standard.py  # 标准检查工具
│   ├── fix-junctions.sh       # Junction 修复脚本
│   ├── registry.json          # Skills 注册表
│   └── {skill-name}/          # 各 skill 目录
│
├── .claude\                   # Claude Code 配置
│   └── skills\                # 【Junction 容器】
│       └── {skill-name} -> my-claude-skills/{skill-name}
│
└── .claude-local\             # 【可选】本地开发
    └── skills-dev/            # 实验性 skills（不入库）
```

## 配置详解

### .skillrc 配置项

```yaml
# 版本信息
metadata:
  version: "1.0"

# 目录结构
directory_structure:
  git_repository: { path: "~/my-claude-skills" }
  junction_target: { path: "~/.claude/skills" }

# Junction 规则
junction_rules:
  create_command: { msys_bash: "..." }
  validation: { must_be_junction: true }

# 同步工作流
sync_workflow:
  add_skill_steps: [...]
  remove_skill_steps: [...]

# 自动化检查
checks:
  pre_operation: [...]

# 故障排查提示
troubleshooting:
  unknown_skill: { cause: "...", solution: "..." }
```

## 工具脚本

| 脚本 | 用途 | 用法 |
|------|------|------|
| `tools/check-standard.py` | 运行标准检查 | `python tools/check-standard.py` |
| `tools/check-standard.py --fix` | 检查并尝试修复 | `python tools/check-standard.py --fix` |
| `fix-junctions.sh` | 批量修复 Junction | `./fix-junctions.sh` |

## 变更日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-30 | 初始版本，建立完整标准规范 |

## 相关资源

- 主仓库: `https://github.com/finger88/my-claude-skills`
- 配置文件: `~/my-claude-skills/.skillrc`
- 检查工具: `~/my-claude-skills/tools/check-standard.py`
