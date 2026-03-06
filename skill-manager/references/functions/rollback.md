# 功能 5: 回退 Skill

**触发条件**: 用户说 "回退 xxx" / "恢复 xxx" / "还原 xxx"

## 执行步骤

1. 列出所有该 skill 的备份:
   ```bash
   ls "D:\my tool\skills log\backups\" | grep skill-name
   ```
2. 显示备份列表供用户选择（或选择最新）
3. 确认回退操作
4. 备份当前版本（防止误操作）
5. 从选定备份恢复 SKILL.md
6. 在 skills修改日志.md 中记录回退操作
7. 输出回退成功信息

## 输出格式

```markdown
回退操作确认
- Skill: skill-name
- 从: backups/20240209-skill-name-v1.2/
- 到: ~/.claude/skills/skill-name/
- 当前版本将先备份到: backups/YYYYMMDD-skill-name-vX.Y-pre-rollback/

确认回退? (是/否)
```
