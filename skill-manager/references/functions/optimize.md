# 功能 3: 优化 Skill

**触发条件**: 用户说 "优化 xxx" / "优化这个 skill" / "让 xxx 更适配本地"

**核心理念**: 将外部 skills 或新建 skills 优化成更适配本地需求的版本，形成完整工作流：评估 -> 备份 -> 优化 -> 记录

## 执行步骤

### 1. 评估阶段
调用功能 2 评估 skill 质量:
- 检查 YAML frontmatter 完整性
- 检查渐进式披露（是否需要拆分到 references/）
- 检查 Token 效率（SKILL.md 行数）
- 检查自动发现（description 是否包含 "Use when..."）
- 生成评估报告和改进建议

### 2. 备份阶段
自动调用功能 4 备份原始版本:
- 创建带版本号的时间戳备份目录
- 保存原始 SKILL.md 和所有资源文件
- 防止优化失败时无法恢复

### 3. 优化阶段

**自动优化项**（无需确认）:
- 补充缺失的 YAML frontmatter 字段
- 修复格式问题（缩进、空行）
- 统一路径格式（Windows 路径处理）

**半自动优化项**（需用户确认，每条建议附上原因）:
- **Token 优化**: 如 SKILL.md > 150 行，提议拆分到 references/
  - 说明原因，例如："这部分内容只在特定子任务时需要，放 references/ 可以避免每次都占用 context window"
- **Description 增强**: 如缺少 "Use when..."，根据内容生成触发条件
  - 说明原因，例如："description 是 Claude 决定是否调用此 skill 的唯一依据，触发条件越明确，误触发和漏触发越少"
- **本地化定制**: 路径适配、工具适配、输出格式适配
- **代码优化**（如有 scripts/）: 提示用户手动审查，可使用 `/simplify` 辅助

> 建议格式：先说"建议做什么"，再说"为什么这样做更好"，让用户能判断是否接受，而不是盲目执行。

### 4. Before/After 对比

优化完成后，对比优化前后的评估分数，输出变化报告：

```markdown
### 优化效果对比

| 维度 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| YAML Frontmatter | WARN | OK | ✅ 已修复 |
| Token 效率 | FAIL (220 行) | OK (98 行) | ✅ ↓55% |
| 自动发现 | WARN | OK | ✅ 已修复 |
| 渐进式披露 | OK | OK | — |
| 输出格式 | OK | OK | — |
```

这一步的价值在于让用户看到"改了什么带来了什么"，而不只是"改了什么"。

### 5. 验证阶段
- 检查 YAML frontmatter 语法
- 验证文件引用路径正确
- 测试 skill 是否能被 Claude 自动发现

### 5. 记录阶段
调用功能 6 记录优化操作

### 6. Git 提醒
提醒用户在 `~/my-claude-skills/` 执行 git commit/push 保存优化结果

## 输出格式

```markdown
## 优化报告: skill-name

### 评估结果
| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| YAML Frontmatter | WARN 缺少 description | OK 已补充 |
| Token 效率 | FAIL 200 行 | OK 120 行（拆分到 references/） |

### 优化内容
- [x] 补充 description 中的 "Use when..." 触发条件
- [x] 拆分详细内容到 references/toolkit.md（80 行）

### 备份信息
- 原始版本已备份到: backups/YYYYMMDD-skill-name-vX.Y/
- 可随时回退: 使用功能 5 回退

### 验证结果
- [x] YAML 语法检查通过
- [x] 文件引用路径正确
- [x] Skill 可被自动发现
```
