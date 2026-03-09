# 功能 4: 备份 Skill

**触发条件**: 用户说 "备份 xxx" / "保存 xxx 副本"

## 执行步骤

1. 检查 skill 是否存在于 `~/.claude/skills/skill-name/`（通过 Junction 实际读取 Git 仓库）
2. 从 SKILL.md YAML frontmatter 提取版本号（`version: vX.Y`）
3. 创建备份目录: `D:\my tool\skills log\backups\YYYYMMDD-skill-name-vX.Y\`
   - 版本号确保备份目录名体现迭代顺序
   - 若无法提取版本号，回退为 `YYYYMMDD-skill-name\`
4. 复制 SKILL.md 到备份目录
5. 如有 references/ scripts/ assets/ 一并复制
6. 在 skills修改日志.md 中记录备份操作
7. 输出备份成功信息
8. **提醒用户**: 如果修改了 skill 文件，建议在 `~/my-claude-skills/` 执行 git commit/push

## 版本号提取规则

优先级从高到低:
1. YAML frontmatter 的 `version` 字段（推荐）
2. 更新日志最后一条匹配 `vX.Y` 或 `vX.Y.Z`（兼容旧格式）
3. 均无则**自动分配 `1.0.0`**，写入 SKILL.md frontmatter 的 `version` 字段，然后用此版本号备份

### 自动分配版本号

当 SKILL.md 的 YAML frontmatter 中没有 `version` 字段时：
1. 在 frontmatter 中添加 `version: "1.0.0"`（插入在 `description:` 之前）
2. 使用 `1.0.0` 作为备份目录名中的版本号
3. 在日志中标注"版本号由系统自动分配"

## 备份说明

备份目录 `D:\my tool\skills log\backups\` 独立于 Git 仓库，用于快速回退和误操作恢复。Git 仓库本身也保留完整版本历史，两者互补。

## 输出格式

```markdown
备份成功
- Skill: skill-name
- 版本: vX.Y
- 时间: YYYY-MM-DD HH:MM
- 路径: backups/YYYYMMDD-skill-name-vX.Y/
- 文件: SKILL.md (+ 3 个 references 文件)
- Git: 建议执行 `cd ~/my-claude-skills && git add . && git commit`
```
