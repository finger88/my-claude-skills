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

## Description 触发验证

评估 description 时，不只检查"有没有触发词"，还要生成示例 prompt 供用户判断实际触发效果：

生成 **3-5 个应触发的 prompt** 和 **2-3 个不应触发的 prompt**，展示给用户：

```markdown
### Description 触发验证: skill-name

**应触发（你觉得这些描述会让 Claude 用上这个 skill 吗？）**
1. "帮我评估一下 ljg-paper 这个 skill 写得怎么样"
2. "我想优化 web-content-extraction，先给我看看它现在的质量"
3. "所有 skills 里有没有 Token 超标的？"

**不应触发（这些情况不需要用这个 skill）**
1. "帮我写一个新的 Python 脚本"
2. "解释一下什么是渐进式披露"
```

这一步是轻量人工验证，不需要自动化——让用户凭直觉判断 description 写得准不准，比检查关键词更有效。

## 输出格式

```markdown
## 评估报告: skill-name

| 维度 | 评分 | 说明 |
|------|------|------|
| YAML Frontmatter | OK/WARN/FAIL | ... |
| 渐进式披露 | OK/WARN/FAIL | ... |
| Token 效率 | WARN | 当前 200 行，建议拆分（上限 150 行） |

**改进建议**:
- [ ] P0: 建议 1（原因：...）
- [ ] P1: 建议 2（原因：...）

### Description 触发验证
（见上方示例）
```
