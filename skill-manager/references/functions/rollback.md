# 功能 5: 回退 Skill

**触发条件**: 用户说 "回退 xxx" / "恢复 xxx" / "还原 xxx"

## 执行步骤

1. 列出所有该 skill 的备份:
   ```bash
   ls "D:\my tool\skills log\backups\" | grep skill-name
   ```
2. 显示备份列表供用户选择（或选择最新）
3. 确认回退操作
4. 备份当前版本到 `YYYYMMDD-skill-name-vX.Y-pre-rollback/`（防止误操作）
5. 从选定备份恢复文件到 `~/.claude/skills/skill-name/`
   - 注意: 通过 Junction 写入会直接修改 Git 仓库中的文件
6. 在 skills修改日志.md 中记录回退操作
7. 输出回退成功信息
8. **提醒用户**: 建议在 `~/my-claude-skills/` 执行 git commit/push 记录回退

## Junction 注意事项

回退操作通过 Junction 直接修改 Git 仓库文件。如果需要完全撤销回退：
- 方案 A: 从 `-pre-rollback` 备份重新恢复
- 方案 B: 在 Git 仓库中 `git checkout -- skill-name/` 恢复到最后一次 commit

## 输出格式

```markdown
回退操作确认
- Skill: skill-name
- 从: backups/20240209-skill-name-v1.2/
- 到: ~/.claude/skills/skill-name/ (Junction -> my-claude-skills/)
- 当前版本将先备份到: backups/YYYYMMDD-skill-name-vX.Y-pre-rollback/

确认回退? (是/否)
```

回退完成后:
```markdown
回退成功
- 已恢复到: v1.2
- 当前版本已备份到: backups/YYYYMMDD-skill-name-vX.Y-pre-rollback/
- Git: 建议执行 `cd ~/my-claude-skills && git add . && git commit -m "rollback skill-name to vX.Y"`
```
