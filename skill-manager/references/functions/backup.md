# 功能 4: 备份 Skill

**触发条件**: 用户说 "备份 xxx" / "保存 xxx 副本"

## 执行步骤

1. 检查 skill 是否存在于 `~/.claude/skills/skill-name/`
2. 从 SKILL.md 更新日志中提取当前版本号（匹配最后一条 `vX.Y` 或 `vX.Y.Z`）
3. 创建备份目录: `D:\my tool\skills log\backups\YYYYMMDD-skill-name-vX.Y\`
   - 版本号从更新日志自动提取，确保备份目录名体现迭代顺序
   - 若无法提取版本号，回退为 `YYYYMMDD-skill-name\`
4. 复制 SKILL.md 到备份目录
5. 如有 references/ scripts/ assets/ 一并复制
6. 在 skills修改日志.md 中记录备份操作
7. 输出备份成功信息

## 版本号提取规则

- 优先从更新日志最后一条匹配: `**YYYY-MM-DD vX.Y**` 或 `vX.Y.Z`
- 备选从 YAML frontmatter 的 description 中匹配
- 示例: 更新日志写 `2026-02-26 v3.0` -> 备份目录为 `20260226-skill-name-v3.0`

## 输出格式

```markdown
备份成功
- Skill: skill-name
- 版本: vX.Y
- 时间: YYYY-MM-DD HH:MM
- 路径: backups/YYYYMMDD-skill-name-vX.Y/
- 文件: SKILL.md (+ 3 个 references 文件)
```
