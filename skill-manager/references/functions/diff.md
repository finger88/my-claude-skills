# 功能 10: 版本 Diff 对比

**触发条件**: 用户说 "diff 对比" / "版本对比" / "对比 xxx 版本" / "查看 xxx 变化"

## 执行步骤

### 1. 选择对比模式

**模式 A: 指定两个备份版本对比**
```
对比 skill-manager v2.1 和 v2.2
```

**模式 B: 当前版本与指定备份对比**
```
对比 skill-manager 与 v2.1 备份
```

**模式 C: 当前版本与 Git HEAD 对比**
```
对比 skill-manager 与 git HEAD
```

### 2. 列出可用版本

如用户未指定版本号，列出该 skill 所有备份:

```markdown
### skill-manager 可用版本

| 序号 | 备份目录 | 版本 | 日期 | 大小 |
|------|---------|------|------|------|
| 1 | 20260306-skill-manager-v2.2 | v2.2 | 2026-03-06 | 3.2 KB |
| 2 | 20260305-skill-manager-v2.1 | v2.1 | 2026-03-05 | 3.0 KB |
| 3 | 20260305-skill-manager-v2.0 | v2.0 | 2026-03-05 | 2.8 KB |
| 4 | 20260303-skill-manager-v1.1 | v1.1 | 2026-03-03 | 2.5 KB |
| 5 | 20260303-skill-manager-v1.0 | v1.0 | 2026-03-03 | 2.2 KB |
```

### 3. 执行 Diff

对选定的两个版本进行文件对比:

```bash
# 获取备份路径
BACKUP1="D:/my tool/skills log/backups/20260305-skill-manager-v2.1/"
BACKUP2="D:/my tool/skills log/backups/20260306-skill-manager-v2.2/"
CURRENT="C:/Users/HONOR/my-claude-skills/skill-manager/"

# 文件级对比
diff -rq BACKUP1 BACKUP2

# 内容级对比 (SKILL.md)
diff -u BACKUP1/SKILL.md BACKUP2/SKILL.md

# 或 Git 对比 (如对比当前与 HEAD)
cd ~/my-claude-skills && git diff HEAD -- skill-manager/
```

### 4. 生成对比报告

输出结构化差异报告。

## 输出格式

```markdown
## 版本对比报告：skill-manager

**对比**: v2.1 → v2.2
**日期**: 2026-03-06

### 文件变更汇总

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| SKILL.md | 修改 | +4 行 -2 行 |
| references/functions/backup.md | 修改 | +10 行 -5 行 |
| references/functions/git-auto.md | 新增 | 新增文件 |

### 详细 Diff

#### SKILL.md

```diff
--- v2.1
+++ v2.2
@@ -1,6 +1,6 @@
 ---
 name: skill-manager
-version: v2.1
+version: v2.2
 description: Comprehensive skill management system...

 ## 核心功能
@@ -18,6 +18,7 @@
 | 4 | **备份技能** | "备份 xxx" | ... |
 | 5 | **回退技能** | "回退 xxx" | ... |
 | 6 | **记录日志** | "记录修改了 xxx" | ... |
+| 7 | **自动 Git 提交** | "自动提交" | ... |
```

#### references/functions/backup.md

```diff
--- v2.1
+++ v2.2
@@ -10,6 +10,8 @@
 5. 记录到 skills 修改日志.md
 6. 记录备份操作
 7. 输出备份成功信息
+8. 如启用自动提交，执行 git commit
```

#### references/functions/git-auto.md (新增)

```
新文件，共 85 行
功能：自动 Git 提交
```

### 变更统计

| 指标 | 数值 |
|------|------|
| 修改文件 | 2 |
| 新增文件 | 1 |
| 删除文件 | 0 |
| 新增行数 | +95 |
| 删除行数 | -7 |
| 净变化 | +88 行 |
```

## Diff 可视化

### 简易模式

只显示变更摘要:

```markdown
skill-manager v2.1 → v2.2
  M  SKILL.md (+4 -2)
  M  references/functions/backup.md (+10 -5)
  A  references/functions/git-auto.md (new)
```

### 详细模式

显示完整 diff 输出（适合审查代码变更）。

### 统计模式

只显示统计数据:

```markdown
skill-manager v2.1 → v2.2
  3 files changed, 95 insertions(+), 7 deletions(-)
```

## 高级选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--stat` | 只显示统计 | `diff skill-manager --stat` |
| `--name-only` | 只显示文件名 | `diff skill-manager --name-only` |
| `--brief` | 精简输出 | `diff skill-manager --brief` |
| `--output` | 导出到文件 | `diff skill-manager --output changes.md` |

## 跨版本对比

支持跳跃多个版本对比:

```
对比 skill-manager v1.0 和 v2.0  # 大版本跨越对比
```

## Git Diff 集成

如技能在 Git 仓库中，可使用 Git 的原生 diff 能力:

```bash
# 对比当前与指定 tag
git diff v2.1 -- skill-manager/

# 对比两个 tag
git diff v2.1..v2.2 -- skill-manager/

# 显示变更统计
git diff --stat v2.1..v2.2 -- skill-manager/
```

## 注意事项

1. **备份存在性**: 确保对比的备份版本存在
2. **文件编码**: 处理 UTF-8 编码，避免中文乱码
3. **大文件处理**: 如 diff 过大，自动切换到精简模式
4. **二进制文件**: 跳过二进制文件对比（如 assets/ 中的图片）
