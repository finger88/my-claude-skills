# 功能 1: 列出所有 Skills

**触发条件**: 用户说 "列出所有 skills" / "显示已安装 skills" / "skills 列表"

## 执行步骤

1. 读取 `~/.claude/skills/` 目录
2. 对每个 skill 检查:
   - 是否为 Junction（指向 `~/my-claude-skills/`）
   - SKILL.md 是否存在
   - YAML frontmatter 是否完整（name, version, description）
   - 是否有 references/ / scripts/ / assets/
3. 分类标记来源:
   - 官方: skill-creator
   - 社区: ljg-*
   - 自建: web-content-extraction 等
4. 输出 Markdown 表格

## 输出格式

```markdown
| # | Skill | 来源 | 版本 | refs | scripts | assets | 状态 |
|---|-------|------|------|------|---------|--------|------|
| 1 | skill-manager | 自建 | v2.2 | Y | - | - | Junction |
| 2 | ljg-paper | 社区 | v2.2.0 | Y | - | - | Junction |
| 3 | weather | 社区 | - | - | - | - | Junction |
```

**状态说明**:
- `Junction`: 通过 Junction 指向 Git 仓库（正常状态）
- `本地`: 独立目录，未纳入 Git 管理
- `断开`: Junction 目标不存在
