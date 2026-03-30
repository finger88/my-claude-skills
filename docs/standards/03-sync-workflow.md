# 双向同步工作流规范

> **版本**: v1.0
> **关联配置**: `.skillrc` -> `sync_workflow`

## 1. 工作流概述

```
┌─────────────────────────────────────────────────────────────────┐
│                     双向同步架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    本地开发环境                           云端仓库               │
│    ═══════════════                       ════════════           │
│                                                                 │
│   my-claude-skills/                      GitHub                 │
│   ┌──────────────┐                      ┌──────────────┐       │
│   │ skill-a/     │◄────────────────────►│ skill-a/     │       │
│   │ skill-b/     │    git push/pull     │ skill-b/     │       │
│   └──────────────┘                      └──────────────┘       │
│          │                                                      │
│          │  Junction 链接（自动同步）                             │
│          ▼                                                      │
│   .claude/skills/                                               │
│   ┌──────────────┐                                              │
│   │ skill-a/     │───► Claude Code 加载                        │
│   │ skill-b/     │                                              │
│   └──────────────┘                                              │
│                                                                 │
│   .claude-local/skills-dev/  (可选，不入库)                      │
│   ┌──────────────┐                                              │
│   │ skill-x/     │───► 开发中/实验性 skills                      │
│   └──────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 标准操作流程

### 2.1 新增 Skill 流程

#### 步骤 1: 准备（每次操作前必做）

```bash
# 1. 读取标准配置（自动化）
cat ~/my-claude-skills/.skillrc

# 2. 运行标准检查
python ~/my-claude-skills/tools/check-standard.py
```

#### 步骤 2: 创建 Skill 目录

```bash
# 在 Git 主库中创建
cd ~/my-claude-skills
mkdir new-skill-name
cd new-skill-name

# 创建标准文件结构
touch SKILL.md
# 编辑 SKILL.md 添加元数据和指令
```

#### 步骤 3: 本地测试

```bash
# 在测试通过前，可以先放到本地开发目录
mkdir -p ~/.claude-local/skills-dev/new-skill-name
cp -r * ~/.claude-local/skills-dev/new-skill-name/

# 测试调用（Claude 需要配置加载此目录）
# 测试通过后，再移到主库
```

#### 步骤 4: 提交到 Git

```bash
cd ~/my-claude-skills

# 添加新 skill
git add new-skill-name/

# 提交（使用规范提交信息）
git commit -m "Add skill: new-skill-name

- 功能描述: xxx
- 用途: yyy
- 关联: zzz

Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送到远程
git push origin main
```

#### 步骤 5: 创建 Junction

```bash
# 使用标准命令创建 Junction
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\new-skill-name C:\Users\HONOR\my-claude-skills\new-skill-name"

# 验证
ls -la ~/.claude/skills/new-skill-name
```

#### 步骤 6: 更新 Registry

```bash
# 在 registry.json 中添加 skill 元数据
python ~/my-claude-skills/tools/update-registry.py

# 提交 registry 更新
git add registry.json
git commit -m "Update registry: add new-skill-name"
git push
```

### 2.2 修改 Skill 流程

```bash
# 1. 确保从最新代码开始
cd ~/my-claude-skills
git pull

# 2. 直接编辑 Git 主库中的文件
# 推荐: 使用 skill-manager 的备份功能
skill-manager backup skill-name

# 3. 编辑文件
vim skill-name/SKILL.md

# 4. 测试修改
# 通过 .claude/skills/ 的 Junction 自动生效

# 5. 提交修改
git add skill-name/
git commit -m "Update skill-name: 修改描述

- 修改点 1
- 修改点 2

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### 2.3 删除 Skill 流程

```bash
# 1. 备份（可选）
cp -r ~/my-claude-skills/old-skill ~/backups/

# 2. 删除 Junction（重要！先删 Junction）
rmdir ~/.claude/skills/old-skill

# 3. 删除源码
cd ~/my-claude-skills
rm -rf old-skill

# 4. 提交删除
git add -A
git commit -m "Remove skill: old-skill

原因: xxx

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### 2.4 同步远程更新流程

```bash
# 1. 拉取远程更新
cd ~/my-claude-skills
git pull

# 2. 检查是否有新增的 skills
# 对比 Git 仓库和 Junction 目录
diff <(ls ~/my-claude-skills | grep -v "^\\.") <(ls ~/.claude/skills/)

# 3. 为新 skills 创建 Junction
./fix-junctions.sh

# 4. 运行标准检查
python tools/check-standard.py
```

## 3. 自动化检查点

### 3.1 预操作检查清单

在任何 skill 相关操作前，必须确认：

```yaml
checklist:
  - [ ] 已读取 .skillrc 配置
  - [ ] 已运行 check-standard.py
  - [ ] Git 工作区干净或有计划的修改
  - [ ] 知道当前操作的 skill 名称
  - [ ] 如果是删除操作，已确认备份
```

### 3.2 提交前检查

```bash
# 自动执行的检查
python tools/check-standard.py

# 手动确认
# - [ ] 修改的文件是正确的
# - [ ] 提交信息符合规范
# - [ ] 没有包含敏感信息
```

## 4. 提交信息规范

### 4.1 标准格式

```
<类型>: <简短描述>

- 详细变更点 1
- 详细变更点 2

关联: #issue 或其他上下文

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 4.2 类型定义

| 类型 | 用途 | 示例 |
|------|------|------|
| `Add` | 新增 skill | `Add skill: web-crawler` |
| `Update` | 修改现有 skill | `Update skill-name: 增加错误处理` |
| `Fix` | 修复问题 | `Fix debate: 修复角色切换逻辑` |
| `Remove` | 删除 skill | `Remove old-skill: 功能已合并` |
| `Docs` | 仅文档修改 | `Docs: 更新 README` |
| `Refactor` | 重构 | `Refactor skill-manager: 优化目录结构` |

## 5. 本地开发 Skills 管理

### 5.1 何时使用本地开发目录

适合放入 `.claude-local/skills-dev/` 的 skill：

- 实验性功能
- 正在开发中，尚未稳定
- 仅个人使用，不适合分享
- 临时测试用的 skill

### 5.2 开发完成后迁移

```bash
# 从开发目录迁移到主库
mv ~/.claude-local/skills-dev/my-skill ~/my-claude-skills/

# 按标准流程提交和创建 Junction
cd ~/my-claude-skills
git add my-skill/
git commit -m "Add skill: my-skill"
git push

MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\my-skill C:\Users\HONOR\my-claude-skills\my-skill"
```

## 6. 紧急修复流程

### 6.1 发现 Junction 损坏

```bash
# 立即运行修复脚本
./fix-junctions.sh

# 验证修复
python tools/check-standard.py
```

### 6.2 发现版本不一致

```bash
# 1. 确认 Git 状态
cd ~/my-claude-skills
git status

# 2. 如果有本地修改，决定保留或放弃
git diff

# 3. 同步远程
git pull

# 4. 重新创建所有 Junction（保险起见）
./fix-junctions.sh
```
