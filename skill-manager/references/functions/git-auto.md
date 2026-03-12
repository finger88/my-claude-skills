# 功能 7: 自动 Git 提交

**触发条件**: 用户说 "自动提交" / "git 提交" / "提交修改" / "保存并提交"

## 配置选项

在 `~/.claude/skills/skill-manager/config.json` 中添加配置（如不存在则创建）:

```json
{
  "git": {
    "autoCommit": false,        // 是否启用自动提交
    "autoPush": false,          // 提交后是否自动 push
    "autoUpdateReadme": true,   // push 后是否自动更新 README skills 表格（默认开启）
    "commitTemplate": "chore(skills): {message}",  // 提交模板，{message}为占位符
    "alwaysSignoff": false      // 是否添加 Signed-off-by
  }
}
```

## 执行步骤

### 模式 A: 手动触发单次提交

1. 检查 `~/my-claude-skills/` 是否为 Git 仓库
2. 运行 `git status` 获取变更文件列表
3. 如有未提交变更，显示变更摘要供用户确认
4. 生成提交信息（基于变更内容或用户提供）
5. 执行 `git add .` 和 `git commit -m "message"`
6. 如配置了 `autoPush: true`，执行 `git push`
7. **Push 后自动更新 README**: 如 `autoUpdateReadme: true`（默认），自动更新 README skills 表格并再次 push
8. 输出提交结果

### 模式 B: 配置自动提交

1. 检查/创建 `config.json` 配置文件
2. 设置 `autoCommit: true` 和 `autoPush: true`
3. 此后所有修改操作（备份/回退/优化）完成后自动执行 Git 提交和 push
4. **Push 后自动更新 README**: 如 `autoUpdateReadme: true`（默认），push 后自动更新 README skills 表格并再次 push
5. 提交信息格式：`chore(skills): {操作类型} {skill-name}`

## Git 命令参考

```bash
# 检查仓库状态
cd ~/my-claude-skills && git status --short

# 暂存所有变更
git add .

# 提交（使用模板）
git commit -m "chore(skills): backup skill-name to vX.Y"

# 可选：添加 Signed-off-by
git commit -m "chore(skills): ..." --signoff

# 推送（如配置）
git push
```

## 提交信息规范

采用 Conventional Commits 格式:

| 操作类型 | 提交前缀 | 示例 |
|---------|---------|------|
| 备份 | `chore(skills)` | `chore(skills): backup skill-manager to v2.2` |
| 回退 | `fix(skills)` | `fix(skills): rollback ljg-paper to v1.5` |
| 优化 | `refactor(skills)` | `refactor(skills): optimize skill-manager token efficiency` |
| 新增 | `feat(skills)` | `feat(skills): add new skill weather` |
| 修复 | `fix(skills)` | `fix(skills): fix ljg-clip path handling` |

## 输出格式

```markdown
### Git 提交完成

| 项目 | 内容 |
|------|------|
| 仓库 | ~/my-claude-skills/ |
| 变更文件 | 3 个文件 |
| 提交信息 | chore(skills): backup skill-manager to v2.2 |
| Commit | a1b2c3d |
| Push | 已完成 / 跳过 |
```

## 注意事项

1. **权限检查**: 确保有 Git 仓库写权限
2. **钩子检查**: 不跳过 pre-commit hooks（除非用户明确要求）
3. **冲突处理**: 如有冲突，提示用户手动解决
4. **远程检查**: push 前检查是否有远程分支

---

## 模式 C: README 自动更新（push 后固定执行）

**说明**: push 完成后自动执行，无需额外配置。如要禁用，设置 `config.json` 中 `git.autoUpdateReadme: false`

**依赖文件**: `registry.json` - 技能注册表，记录分类、状态、安装日期等元数据

**README 结构**（按分类分组显示）：
- 概览统计（总数/试用期/正式使用）
- 试用期 Skills（顶部突出显示）
- 按分类分组：辩论系统、内容处理、生产力、技能管理、工具

**执行步骤**:

1. push 完成后，检查 `config.json` 中 `autoUpdateReadme`（默认为 `true`）
2. 读取 `registry.json` 获取技能元数据（分类、状态、安装日期）
3. 扫描 `~/my-claude-skills/*/SKILL.md` 解析版本号
4. 更新 `registry.json` 中的版本信息
5. 更新 README 中的统计区域（`<!-- STATS-START -->` 到 `<!-- STATS-END -->`）
6. 更新试用期表格（计算安装日期至今的天数）
7. 如有变更：
   ```bash
   git add README.md registry.json
   git commit -m "docs: update README skills table"
   git push
   ```
8. 如无变更，跳过（README 已是最新）

**输出格式**:

```markdown
### README 更新完成

| 项目 | 内容 |
|------|------|
| Skills 总数 | 27 |
| 试用期 | 9 ⏳ |
| 正式使用 | 18 ✅ |
| 新增 | debate, source-ingest, ... |
| Commit | b2c3d4e |
```

---

## 附录: registry.json 格式

```json
{
  "version": "1.0",
  "skills": {
    "skill-name": {
      "category": "content",
      "status": "trial|formal|deprecated",
      "installedAt": "2026-03-12",
      "package": "critical-debater",
      "description": "用途说明"
    }
  },
  "categories": {
    "content": { "name": "内容处理", "icon": "📚" }
  },
  "packages": {
    "critical-debater": {
      "name": "critical-debater",
      "skills": ["debate", "source-ingest", ...],
      "source": "https://github.com/xwxga/critical-debater"
    }
  }
}
```
