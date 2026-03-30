# 故障排查手册

> **版本**: v1.0
> **关联配置**: `.skillrc` -> `troubleshooting`

## 1. 快速诊断流程

```
遇到问题？
   │
   ▼
┌─────────────────┐
│ 1. 运行标准检查  │
│ python tools/   │
│   check-standard.py │
└─────────────────┘
   │
   ├──► 发现问题？──► 按提示修复
   │
   └──► 检查通过？──► 查看下方具体问题
```

## 2. Skill 调用问题

### 2.1 "Unknown skill" 错误

**症状**: 调用 skill 时 Claude 提示 `Unknown skill: xxx`

**可能原因**:
1. Junction 链接不存在
2. Junction 链接断裂
3. Junction 链接指向错误位置
4. Skill 文件损坏或不完整

**诊断**:
```bash
# 1. 检查 Junction 是否存在
ls -la ~/.claude/skills/skill-name

# 2. 检查是否是 Junction（CMD）
cmd /c "dir /a C:\Users\HONOR\.claude\skills\" | findstr skill-name

# 3. 检查目标是否存在
ls -la ~/my-claude-skills/skill-name

# 4. 检查 SKILL.md 是否存在
ls ~/my-claude-skills/skill-name/SKILL.md
```

**修复**:
```bash
# 如果 Junction 不存在或错误
rmdir ~/.claude/skills/skill-name 2>/dev/null
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"

# 如果 skill 不存在于 Git 仓库
# 从其他位置复制或重新克隆
```

### 2.2 Skill 加载但无响应

**症状**: Skill 被识别但执行后无输出

**可能原因**:
1. SKILL.md 格式错误
2. 权限问题
3. 依赖缺失

**诊断**:
```bash
# 检查 SKILL.md
head -50 ~/my-claude-skills/skill-name/SKILL.md

# 检查权限
ls -la ~/my-claude-skills/skill-name/
```

## 3. Junction 链接问题

### 3.1 创建了目录而非 Junction

**症状**: 编辑 `.claude/skills/skill/` 的文件但 `my-claude-skills/` 中的文件未更新

**诊断**:
```cmd
dir /a C:\Users\HONOR\.claude\skills\

# 错误输出（<DIR> 而非 <JUNCTION>）:
2026-03-30  12:00    <DIR>          skill-name
```

**修复**:
```bash
# 1. 保存目录内容（如果有重要修改）
cp -r ~/.claude/skills/skill-name ~/tmp/skill-name-backup

# 2. 删除错误的目录
rm -rf ~/.claude/skills/skill-name

# 3. 重新创建 Junction
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"

# 4. 如果有备份的修改，合并回 my-claude-skills/
```

### 3.2 Junction 指向错误目标

**症状**: 修改 A skill 但 B skill 的内容变了

**诊断**:
```cmd
dir /a C:\Users\HONOR\.claude\skills\
# 检查 Junction 指向的目标路径
```

**修复**:
```bash
# 删除并重新创建
rmdir ~/.claude/skills/wrong-skill
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"
```

### 3.3 孤儿 Junction（目标已删除）

**症状**: Junction 存在但指向的目录不存在

**诊断**:
```bash
# 尝试访问 Junction
cd ~/.claude/skills/skill-name
# 会报错：No such file or directory
```

**修复**:
```bash
# 删除孤儿 Junction
rmdir ~/.claude/skills/skill-name

# 如果 skill 还应该存在，从 Git 恢复
cd ~/my-claude-skills
git checkout skill-name/

# 然后重新创建 Junction
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"
```

## 4. Git 同步问题

### 4.1 本地修改未提交

**症状**: `git status` 显示有未跟踪文件或修改

**修复**:
```bash
cd ~/my-claude-skills

# 查看修改内容
git diff

# 如果修改是故意的，提交
git add -A
git commit -m "Update: xxx"
git push

# 如果修改是无意的，放弃
git checkout -- .
git clean -fd
```

### 4.2 远程有更新未拉取

**症状**: `git status` 显示分支落后

**修复**:
```bash
cd ~/my-claude-skills

# 拉取更新
git pull

# 如果拉取后出现新的 skills，创建 Junction
./fix-junctions.sh
```

### 4.3 合并冲突

**症状**: `git pull` 后显示冲突

**修复**:
```bash
# 查看冲突文件
git status

# 手动解决冲突（编辑冲突文件）
vim conflicted-file

# 标记为已解决
git add conflicted-file
git commit -m "Merge: resolve conflicts"
```

## 5. 批量修复

### 5.1 运行自动修复脚本

```bash
# 修复所有 Junction 问题
cd ~/my-claude-skills
./fix-junctions.sh

# 运行标准检查
python tools/check-standard.py --fix
```

### 5.2 手动重建所有 Junction

```bash
# 1. 备份当前的 Junction 列表
ls ~/.claude/skills/ > ~/junctions-backup.txt

# 2. 删除所有 Junction（保留实际目录）
for dir in ~/.claude/skills/*/; do
    if [ -d "$dir" ]; then
        name=$(basename "$dir")
        # 检查是否是 Junction
        if cmd /c "dir /a C:\Users\HONOR\.claude\skills\" 2>/dev/null | grep -q "<JUNCTION>.*$name"; then
            rmdir "$dir"
        fi
    fi
done

# 3. 重新创建所有 Junction
./fix-junctions.sh
```

## 6. 预防性维护

### 6.1 每日检查

```bash
# 添加到 ~/.bashrc 或作为定时任务
alias skill-check='cd ~/my-claude-skills && python tools/check-standard.py'
```

### 6.2 备份策略

```bash
# 在重大修改前创建备份
skill-manager backup skill-name

# 或手动备份整个仓库
cd ~
tar czf my-claude-skills-backup-$(date +%Y%m%d).tar.gz my-claude-skills/
```

### 6.3 监控 Junction 健康

```bash
# 创建监控脚本
#!/bin/bash
# save as ~/bin/check-skills-health.sh

cd ~/my-claude-skills
result=$(python tools/check-standard.py 2>&1)

if [ $? -ne 0 ]; then
    echo "Skills 检查失败:"
    echo "$result"
    # 可以添加邮件通知或其他告警
fi
```

## 7. 获取帮助

### 7.1 收集诊断信息

```bash
# 收集系统信息用于问题报告
{
    echo "=== 目录结构 ==="
    ls -la ~/my-claude-skills/
    echo ""
    echo "=== Junction 状态 ==="
    cmd /c "dir /a C:\Users\HONOR\.claude\skills\" 2>/dev/null
    echo ""
    echo "=== Git 状态 ==="
    cd ~/my-claude-skills && git status
    echo ""
    echo "=== 标准检查结果 ==="
    python tools/check-standard.py 2>&1
} > ~/skill-issue-report.txt
```

### 7.2 标准文档参考

遇到问题时的查阅顺序：

1. 本故障排查手册
2. `.skillrc` 配置文件
3. `docs/standards/02-junction-management.md`
4. `docs/standards/03-sync-workflow.md`
