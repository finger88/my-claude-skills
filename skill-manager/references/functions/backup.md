# 功能 4: 备份 Skill

**触发条件**: 用户说 "备份 xxx" / "保存 xxx 副本"

## 执行步骤

1. 检查 skill 是否存在于 `~/.claude/skills/skill-name/`
2. 从 SKILL.md YAML frontmatter 提取版本号（`version: vX.Y`）
3. 创建备份目录: `D:\my tool\skills log\backups\YYYYMMDD-skill-name-vX.Y\`
   - 版本号确保备份目录名体现迭代顺序
   - 若无法提取版本号，回退为 `YYYYMMDD-skill-name\`
4. 复制 SKILL.md 到备份目录
5. 如有 references/ scripts/ assets/ 一并复制
6. 在 skills修改日志.md 中记录备份操作
7. 输出备份成功信息

## 版本号提取规则

优先级从高到低:
1. YAML frontmatter 的 `version` 字段（推荐）
2. 更新日志最后一条匹配 `vX.Y` 或 `vX.Y.Z`（兼容旧格式）
3. 均无则回退为无版本号目录名

## 输出格式

```markdown
备份成功
- Skill: skill-name
- 版本: vX.Y
- 时间: YYYY-MM-DD HH:MM
- 路径: backups/YYYYMMDD-skill-name-vX.Y/
- 文件: SKILL.md (+ 3 个 references 文件)
```
