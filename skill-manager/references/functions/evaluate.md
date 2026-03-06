# 功能 2: 评估 Skill 质量

**触发条件**: 用户说 "评估 xxx" / "检查 xxx 质量" / "xxx 是否符合最佳实践"

## 评估维度

1. **YAML Frontmatter**: name, description 是否完整
2. **渐进式披露**: 是否使用了 references/ 拆分内容
3. **Token 效率**: SKILL.md 行数是否 < 150 行
4. **自动发现**: description 是否包含 "Use when..."
5. **输出格式**: 是否统一、实用

## 层级结构检查

| 层级 | 检查项 | 标准 |
|------|--------|------|
| 元信息层 | name, description | 完整且包含触发条件 |
| 指令层 | SKILL.md body | < 150 行 |
| 资源层 | references/ | 详细内容已拆分 |

## 输出格式

```markdown
## 评估报告: skill-name

| 维度 | 评分 | 说明 |
|------|------|------|
| YAML Frontmatter | OK/WARN/FAIL | ... |
| 渐进式披露 | OK/WARN/FAIL | ... |
| Token 效率 | 3/5 | 当前 200 行，建议拆分 |

**改进建议**:
- [ ] P0: 建议 1
- [ ] P1: 建议 2
```
