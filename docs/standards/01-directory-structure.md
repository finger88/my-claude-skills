# Claude Skills 本地管理标准规范

> **版本**: v1.0
> **生效日期**: 2026-03-30
> **适用范围**: Windows + MSYS2/Git Bash 环境

## 1. 目录架构标准

### 1.1 核心目录定义

```
C:\Users\{USER}\
├── my-claude-skills\              # Git 仓库：skills 源码主库
│   ├── .git\                       # Git 版本控制
│   ├── .skillrc\                   # 【YAML】本地标准配置文件（本文件）
│   ├── README.md                   # 仓库说明
│   ├── registry.json               # Skills 元数据注册表
│   ├── docs\                       # 规范文档
│   │   └── standards\              # 标准规范文档
│   │       ├── 01-directory-structure.md
│   │       ├── 02-junction-management.md
│   │       ├── 03-sync-workflow.md
│   │       └── 04-troubleshooting.md
│   └── {skill-name}\               # 各 skill 目录（N 个）
│       ├── SKILL.md
│       └── ...
│
├── .claude\                        # Claude Code 配置目录
│   └── skills\                     # 【Junction 链接目录】
│       └── {skill-name} -> my-claude-skills/{skill-name}  (Junction)
│
└── .claude-local\                  # 【可选】本地开发 skills（不入库）
    └── skills-dev\                 # 开发中/测试中的 skills
        └── {skill-name}\           # 实际目录
```

### 1.2 目录类型定义

| 类型 | 标识 | 用途 | 同步策略 |
|------|------|------|----------|
| **Git 主库** | `my-claude-skills/` | Skills 源码唯一真源 | 全量提交 GitHub |
| **Junction 链接** | `.claude/skills/*` | Claude 加载入口 | 必须是符号链接 |
| **本地开发** | `.claude-local/skills-dev/` | 实验性 skills | 不入库，仅本地 |

---

## 2. Junction 链接管理标准

### 2.1 创建规则

**Windows Junction 创建命令**:
```bash
# 在 CMD 中（MSYS2 中使用 //c 转义）
mklink /J C:\Users\HONOR\.claude\skills\{skill-name} C:\Users\HONOR\my-claude-skills\{skill-name}

# 在 MSYS2/Git Bash 中
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\{skill-name} C:\Users\HONOR\my-claude-skills\{skill-name}"
```

### 2.2 验证规则

**必须满足的条件**:
1. `.claude/skills/{skill-name}` 必须是 **Junction** 类型（`<JUNCTION>`）
2. 不能是实际目录（`<DIR>`）
3. 不能是文件符号链接（`lrwxrwxrwx` - 这是 MSYS2 模拟的）
4. 链接目标必须指向 `my-claude-skills/` 内的对应目录

**验证命令**:
```bash
# CMD 中查看类型
dir /a C:\Users\HONOR\.claude\skills\

# 预期输出：JUNCTION 类型
# <JUNCTION>     skill-name    [C:\Users\HONOR\my-claude-skills\skill-name]
```

### 2.3 禁止事项

| 禁止行为 | 后果 |
|----------|------|
| 直接复制目录到 `.claude/skills/` | 版本不一致，Git 同步失效 |
| 使用 MSYS2 `ln -s` 创建软链接 | MSYS2 模拟的链接 Windows 不识别为 Junction |
| 手动创建同名文件夹 | 阻断 Junction 创建，技能无法更新 |

---

## 3. 双向同步工作流

### 3.1 标准操作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    日常开发工作流                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     编辑/修改      ┌──────────────┐          │
│  │ my-claude-   │ ─────────────────> │ Git 提交     │          │
│  │ skills/      │                    │ & Push       │          │
│  └──────────────┘                    └──────────────┘          │
│         │                                  │                    │
│         │ Junction 自动同步                │ 推送到远程          │
│         ▼                                  ▼                    │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │ .claude/     │                    │ GitHub       │          │
│  │ skills/      │                    │ Repository   │          │
│  │ (Junction)   │                    │              │          │
│  └──────────────┘                    └──────────────┘          │
│         │                                                        │
│         └────────────────┐                                     │
│                          ▼                                     │
│                   Claude Code 加载                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 新 Skill 添加流程

```yaml
# 步骤 1: 在 my-claude-skills/ 中创建 skill
mkdir my-claude-skills/new-skill
cd my-claude-skills/new-skill
# 创建 SKILL.md 等文件

# 步骤 2: 提交到 Git
git add new-skill/
git commit -m "Add new-skill: xxx"
git push origin main

# 步骤 3: 创建 Junction 链接
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\new-skill C:\Users\HONOR\my-claude-skills\new-skill"

# 步骤 4: 验证
ls -la ~/.claude/skills/new-skill
# 应该显示为链接，而不是目录
```

### 3.3 Skill 更新/删除流程

**更新**:
1. 直接在 `my-claude-skills/{skill}/` 中编辑
2. 提交并推送
3. Junction 自动同步（无需额外操作）

**删除**:
1. 先删除 Junction: `rmdir ~/.claude/skills/{skill}`
2. 再删除源码: `rm -rf ~/my-claude-skills/{skill}`
3. 提交删除: `git add -A && git commit -m "Remove skill"`

---

## 4. 自动化检查机制

### 4.1 预操作检查清单

在任何 skill 相关操作前，必须读取 `my-claude-skills/.skillrc` 并验证：

```yaml
# .skillrc 中定义的检查项
checks:
  - junction_integrity      # Junction 链接完整性
  - git_sync_status         # Git 同步状态
  - duplicate_detection     # 重复检测
  - orphaned_junctions      # 孤儿链接检测
```

### 4.2 定期维护任务

| 频率 | 任务 | 命令 |
|------|------|------|
| 每次启动 | 检查 Junction 状态 | `skill-manager check-junctions` |
| 每日 | 同步 Git 状态 | `cd my-claude-skills && git pull` |
| 每周 | 运行完整性修复 | `fix-junctions.sh` |

---

## 5. 故障排查速查表

### 5.1 常见问题

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| Skill 调用提示 "Unknown skill" | Junction 断裂或指向错误 | 运行 `fix-junctions.sh` |
| 修改 skill 不生效 | 编辑的是 Junction 目标外的副本 | 确认编辑的是 `my-claude-skills/` 中的文件 |
| Git 提交有未跟踪的大文件 | skill 目录被错误复制 | 移动目录到正确位置，重建 Junction |
| Claude 加载 skill 失败 | Junction 类型错误（用了软链接而非 Junction） | 删除后重新用 `mklink /J` 创建 |

---

## 6. 附录

### 6.1 相关文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| 本标准文档 | `docs/standards/` | 完整规范说明 |
| YAML 配置 | `.skillrc` | 自动化读取的配置 |
| 修复脚本 | `fix-junctions.sh` | 修复 Junction 问题 |
| Registry | `registry.json` | Skills 元数据 |

### 6.2 相关命令速查

```bash
# 查看所有 skills 及其类型
ls -la ~/.claude/skills/

# 查看 Junction 详情（CMD）
dir /a C:\Users\HONOR\.claude\skills\

# 强制删除错误创建的目录
rm -rf ~/.claude/skills/{skill-name}

# 创建正确 Junction
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\{skill} C:\Users\HONOR\my-claude-skills\{skill}"

# 验证 Git 状态
cd ~/my-claude-skills && git status

# 全量同步
cd ~/my-claude-skills && git pull && git add -A && git commit -m "Sync" && git push
```
