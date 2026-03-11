# 功能 9: 批量评估 Skills

**触发条件**: 用户说 "批量评估" / "评估所有 skills" / "检查 skills 质量" / "skills 评分"

## 执行步骤

### 1. 扫描已安装的 Skills

读取 `~/.claude/skills/` 目录，获取所有 skill 名称列表。

### 2. 逐技能评估

对每个 skill 执行 5 维度评估:

| 维度 | 检查项 | 评分标准 |
|------|--------|---------|
| **YAML Frontmatter** | name, description, version | 完整=OK, 缺 1=warn, 缺 2+=FAIL |
| **渐进式披露** | 有 references/ 拆分 | 已拆分=OK, 无拆分=warn |
| **Token 效率** | SKILL.md 行数 | <150 行=OK, 150-300=warn, >300=FAIL |
| **自动发现** | description 含 "Use when..." | 有=OK, 无=warn |
| **输出格式** | 有明确输出模板 | 有=OK, 无=warn |

### 3. 生成汇总报告

输出整体评分和每个 skill 的详细评估。

### 4. 分析师视角

汇总完成后，额外做一次模式分析，找出单看个别 skill 不容易发现的问题：

**① 哪些维度永远通过（区分度不足）**

如果某个评估维度所有 skill 都是 OK，说明这个标准可能太宽松，或当前 skills 已普遍达标，可以考虑收紧：

```markdown
⚠️ 区分度分析：
- "输出格式" 维度：18/18 个 skill 全 OK → 标准可能过于宽松
- "YAML Frontmatter" 维度：17/18 通过 → 标准合理
```

**② 哪些 skill 反复出现同类问题**

横向比较，找出集中出现的问题类型，帮助判断是否需要系统性修复：

```markdown
📊 共性问题：
- 9 个 skill 缺少 references/ 拆分（渐进式披露 WARN）
  → 建议统一排期优化，而不是逐个处理
- 5 个 skill Token 超标（>150 行）
  → 其中 3 个是同类型 skill，可参考同一模板拆分
```

**③ 高优先级行动建议**

基于以上分析，给出 1-3 条最值得立即行动的建议（而不是列出所有问题）：

```markdown
🎯 建议优先处理：
1. skill-hub（Token 280 行）：拆分收益最大，且影响每次调用
2. 统一修复 9 个缺少 references/ 的 skill：工作量可控，整体质量提升明显
```

## 输出格式

```markdown
## Skills 批量评估报告

**评估时间**: YYYY-MM-DD HH:MM
**Skills 总数**: 18

### 整体评分

| 评级 | 数量 | Skills |
|------|------|--------|
| 🟢 优秀 (全 OK) | 5 | skill-manager, ljg-paper, ... |
| 🟡 良好 (1-2 个 WARN) | 10 | daily-review, weather, ... |
| 🟠 待改进 (3+ WARN) | 2 | skill-hub, xlsx |
| 🔴 需重构 (有 FAIL) | 1 | broken-skill |

### 详细评估

| # | Skill | YAML | 披露 | Token | 发现 | 格式 | 综合 |
|---|-------|------|------|-------|------|------|------|
| 1 | skill-manager | OK | OK | OK (108 行) | OK | OK | 🟢 |
| 2 | ljg-paper | OK | OK | OK (95 行) | OK | OK | 🟢 |
| 3 | daily-review | OK | WARN | OK (80 行) | OK | OK | 🟡 |
| 4 | skill-hub | WARN | WARN | WARN (280 行) | OK | OK | 🟠 |
| 5 | broken-skill | FAIL | FAIL | FAIL (500 行) | FAIL | FAIL | 🔴 |

### 改进建议汇总

**高优先级 (FAIL 项)**:
- [ ] broken-skill: 需重构，SKILL.md 超过 500 行，建议拆分到 references/

**中优先级 (WARN 项)**:
- [ ] skill-hub: Token 效率低 (280 行)，建议拆分详细内容
- [ ] daily-review: 缺少 references/ 目录
- [ ] weather: 缺少 "Use when..." 触发条件
```

## 评估详情输出

对每个 skill 输出简要评估:

```markdown
### skill-manager (🟢 优秀)

| 维度 | 状态 | 说明 |
|------|------|------|
| YAML Frontmatter | OK | name, version, description 完整 |
| 渐进式披露 | OK | 6 个功能拆分到 references/functions/ |
| Token 效率 | OK (108 行) | < 150 行，优秀 |
| 自动发现 | OK | description 含清晰 "Use when..." |
| 输出格式 | OK | 有明确表格和模板 |

**无改进建议** ✅
```

## 评分计算

```
综合评分 = (OK 数量 × 100 + WARN 数量 × 50 + FAIL 数量 × 0) / 5

🟢 优秀：500 分 (全 OK)
🟡 良好：300-499 分
🟠 待改进：100-299 分
🔴 需重构：0-99 分
```

## 高级选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--detail` | 输出每个 skill 详细评估 | `批量评估 --detail` |
| `--prefix` | 只评估指定前缀 | `批量评估 ljg-*` |
| `--focus` | 只评估特定维度 | `批量评估 --focus token` |

## 导出功能

可将评估结果导出为 Markdown 报告:

```
导出路径：D:\my tool\skills log\skills 评估报告-YYYYMMDD.md
```

## 注意事项

1. **评估标准**: 基于 Anthropic Skill 最佳实践
2. **非破坏性**: 评估不修改任何文件
3. **可追溯**: 评估报告保存到日志目录
4. **后续操作**: 可结合「功能 3: 优化技能」进行改进
