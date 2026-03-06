# 功能 8: 批量备份 Skills

**触发条件**: 用户说 "批量备份" / "备份所有 skills" / "全部备份"

## 执行步骤

### 1. 扫描已安装的 Skills

读取 `~/.claude/skills/` 目录，获取所有 skill 名称列表。

### 2. 过滤技能

- **排除项**:
  - `skills` 子目录（如有）
  - 不包含 `SKILL.md` 的目录
  - Junction 断开的目录
- **可选项**: 用户可指定只备份特定前缀的 skills（如 `ljg-*`）

### 3. 逐个备份

对每个 skill 执行标准备份流程:

1. 读取 `SKILL.md` YAML frontmatter 提取版本号
2. 创建备份目录：`backups/YYYYMMDD-skill-name-vX.Y/`
3. 复制 `SKILL.md` + `references/` + `scripts/` + `assets/`
4. 记录到 `skills 修改日志.md`

### 4. 生成汇总报告

输出批量备份结果表格。

## 输出格式

```markdown
## 批量备份完成

**备份时间**: YYYY-MM-DD HH:MM
**成功**: 15 / **失败**: 0 / **跳过**: 1

| # | Skill | 版本 | 备份路径 | 状态 |
|---|-------|------|---------|------|
| 1 | skill-manager | v2.2 | 20260306-skill-manager-v2.2 | ✅ |
| 2 | ljg-paper | v2.0 | 20260306-ljg-paper-v2.0 | ✅ |
| 3 | daily-review | - | 20260306-daily-review | ✅ |
| 4 | broken-link | - | (Junction 断开) | ❌ |

**总大小**: 2.5 MB
**日志**: skills 修改日志.md 已追加 15 条记录
```

## 增量备份优化

如检测到某 skill 自上次备份后无变更:

- 比对 `SKILL.md` 文件大小/修改时间
- 或使用 `git diff --quiet skill-name/` 检查
- 跳过未变更的 skill，在报告中标记为「跳过」

```markdown
| 5 | weather | - | (无变更，跳过) | ⏭️ |
```

## 高级选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--prefix` | 只备份指定前缀 | `批量备份 ljg-*` |
| `--exclude` | 排除指定 skills | `批量备份 排除 skill-manager` |
| `--force` | 强制备份即使无变更 | `批量备份 --force` |

## 注意事项

1. **备份位置**: 所有备份保存到 `D:\my tool\skills log\backups\`
2. **Git 提醒**: 批量备份完成后，提醒用户执行 `git commit/push`（如未启用自动提交）
3. **错误处理**: 单个 skill 备份失败不影响其他 skill
4. **权限检查**: 确保有目标目录写权限
