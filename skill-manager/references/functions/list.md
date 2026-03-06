# 功能 1: 列出所有 Skills

**触发条件**: 用户说 "列出所有 skills" / "显示已安装 skills" / "skills 列表"

## 执行步骤

1. 读取 `~/.claude/skills/` 目录
2. 对每个 skill 检查:
   - SKILL.md 是否存在
   - YAML frontmatter 是否完整
   - 是否有 references/ / scripts/ / assets/
3. 分类标记来源:
   - 官方: skill-creator
   - 社区: ljg-*
   - 自建: web-content-extraction 等
4. 输出 Markdown 表格

## 输出格式

```markdown
| # | Skill | 来源 | 状态 | 质量 | 备注 |
|---|-------|------|------|------|------|
| 1 | skill-creator | 官方 | OK | 5/5 | 无需修改 |
| 2 | ljg-xray-paper | 社区 | OK | 5/5 | 参考模板 |
```
