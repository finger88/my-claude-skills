# 功能 11-14: Registry 管理

**触发条件**:
- "注册 xxx" / "新增 skill" / "登记 xxx"
- "转正 xxx" / "skill 转正" / "正式使用 xxx"
- "删除 xxx" / "卸载 xxx" / "移除 xxx"
- "试用期" / "试用状态" / "查看试用"

**依赖文件**: `~/my-claude-skills/registry.json`

---

## 功能 11: 注册技能

将新安装的 skill 添加到注册表，启用试用追踪。

**执行步骤**:

1. 读取 `~/my-claude-skills/registry.json`
2. 检查 skill 是否已存在：
   - 如存在，提示用户（可选择更新信息）
   - 如不存在，继续注册
3. 解析 skill 的 SKILL.md 获取元数据：
   - `name` - 从 frontmatter
   - `version` - 从 frontmatter
   - `description` - 从 frontmatter 第一句
4. 交互确认或填写：
   - **分类** (`category`): content / productivity / management / utility / debate
   - **所属包** (`package`): 如属于大包（如 `critical-debater`）
   - 如无包，留空或填 "standalone"
5. 生成注册条目：
   ```json
   {
     "skill-name": {
       "category": "content",
       "status": "trial",
       "installedAt": "2026-03-12",
       "package": "",
       "description": "用途说明"
     }
   }
   ```
6. 保存 `registry.json`
7. 如配置 `autoCommit: true`，自动 git commit

**输出格式**:

```markdown
### 技能注册完成

| 项目 | 内容 |
|------|------|
| Skill | skill-name |
| 分类 | 内容处理 |
| 状态 | ⏳ 试用期 |
| 安装日期 | 2026-03-12 |
| 建议 | 7-14天后运行 "转正 xxx" 或 "删除 xxx" |
```

---

## 功能 12: 转正技能

将试用期 skill 转为正式使用状态。

**执行步骤**:

1. 读取 `registry.json`
2. 查找指定 skill：
   - 如不存在，报错并提示先注册
   - 如状态已是 `formal`，提示无需操作
3. 确认转正（自动项，无需确认）
4. 更新状态：`"status": "formal"`
5. 可选：添加 `formalizedAt` 日期
6. 保存 `registry.json`
7. 如 `autoCommit: true`：
   ```bash
   git add registry.json
   git commit -m "chore(skills): formalize skill-name"
   git push
   ```
8. 提示：README 将在下次 push 后自动更新

**输出格式**:

```markdown
### 技能转正完成

| 项目 | 内容 |
|------|------|
| Skill | skill-name |
| 原状态 | ⏳ 试用期 (12天) |
| 新状态 | ✅ 正式使用 |
| Git | 已提交并推送 |
```

---

## 功能 13: 删除技能

从注册表移除 skill，可选删除文件。

**执行步骤**:

1. 读取 `registry.json`
2. 查找指定 skill：
   - 如不存在，报错
3. 确认删除方式（二选一）：
   - **仅从注册表移除**（保留文件，仅不再追踪）
   - **完全删除**（移除注册表条目 + 删除 skill 目录）
4. 执行操作：
   - 更新 `registry.json`
   - 如选择完全删除：
     ```bash
     # 删除 Git 仓库中的 skill 目录
     rm -rf ~/my-claude-skills/skill-name
     # Junction 链接会自动失效（下次重启后清理）
     ```
5. 保存 `registry.json`
6. 如 `autoCommit: true`，自动 git commit

**输出格式**:

```markdown
### 技能删除完成

| 项目 | 内容 |
|------|------|
| Skill | skill-name |
| 操作 | 完全删除 / 仅从注册表移除 |
| 文件 | 已删除 / 保留 |
| Git | 已提交 |
```

**注意事项**:
- 完全删除后，Junction 链接在 `~/.claude/skills/` 中会变成死链接
- 建议手动清理：`rmdir ~/.claude/skills/skill-name`

---

## 功能 14: 查看试用期

列出所有试用期技能，显示天数和建议操作。

**执行步骤**:

1. 读取 `registry.json`
2. 筛选 `status: "trial"` 的技能
3. 计算每个 skill 的试用天数：
   ```python
   from datetime import datetime
   days = (today - installedAt).days
   ```
4. 按试用天数排序（最早的在前）
5. 生成建议：
   - `< 7天`: 继续试用
   - `7-14天`: 建议决定转正或删除
   - `> 14天`: 强烈建议处理

**输出格式**:

```markdown
### 试用期 Skills (共 9 个)

| Skill | 分类 | 试用天数 | 建议 |
|-------|------|----------|------|
| debate | 🎭 辩论系统 | 0天 | 继续试用 |
| source-ingest | 🎭 辩论系统 | 0天 | 继续试用 |
| freshness-check | 🎭 辩论系统 | 0天 | 继续试用 |
| ... | ... | ... | ... |

### 操作建议

```bash
# 转正技能
claude "转正 debate"

# 删除技能
claude "删除 debate"
```
```

---

## registry.json 格式参考

```json
{
  "version": "1.0",
  "lastUpdated": "2026-03-12",
  "skills": {
    "skill-name": {
      "category": "content|productivity|management|utility|debate",
      "status": "trial|formal|deprecated",
      "installedAt": "2026-03-12",
      "formalizedAt": "2026-03-20",
      "package": "critical-debater",
      "description": "用途说明"
    }
  },
  "categories": {
    "content": { "name": "内容处理", "icon": "📚" },
    "productivity": { "name": "生产力", "icon": "📅" },
    "management": { "name": "技能管理", "icon": "🛠️" },
    "utility": { "name": "工具", "icon": "🔧" },
    "debate": { "name": "辩论系统", "icon": "🎭" }
  },
  "packages": {
    "critical-debater": {
      "name": "critical-debater",
      "description": "多Agent辩论系统",
      "installedAt": "2026-03-12",
      "status": "trial",
      "skills": ["debate", "source-ingest", ...],
      "source": "https://github.com/xwxga/critical-debater"
    }
  }
}
```

---

## 典型工作流

### 安装新 Skill

```bash
# 1. 安装 skill（通过 skill-hub 或手动）
claude "install skill from https://github.com/xxx/yyy"

# 2. 注册到 registry（启用试用追踪）
claude "注册 yyy"

# 3. 试用期间正常使用...

# 4. 查看试用期状态
claude "试用期"

# 5. 决定转正或删除
claude "转正 yyy"    # 或
claude "删除 yyy"
```

### 批量注册已有 Skills

```bash
# 为所有未注册的 skills 创建 registry 条目
claude "批量注册 skills"
```

---

## 注意事项

1. **Git 提交**: 修改 registry.json 后建议立即 commit，便于追踪变更
2. **分类规范**: 使用预定义分类（content/productivity/management/utility/debate）
3. **包管理**: 属于大包的 skill 应填写 `package` 字段，便于统一管理
4. **试用期**: 建议 7-14 天内决定是否转正，避免长期堆积试用 skill
