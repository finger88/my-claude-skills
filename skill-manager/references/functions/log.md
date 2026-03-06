# 功能 6: 记录日志

**触发条件**: 用户说 "记录今天修改了 xxx" / "在日志中添加 xxx"

## 执行步骤

1. 读取 `D:\my tool\skills log\skills修改日志.md`
2. 在文件末尾追加记录
3. 保存文件
4. 输出记录成功信息

## 日志格式模板

```markdown
### YYYY-MM-DD HH:MM | skill-name

| 项目 | 内容 |
|------|------|
| 修改类型 | 优化 / 修复 / 新增 / 备份 |
| 影响范围 | SKILL.md, references/ |
| 版本变化 | vX.Y -> vX.Z |

**修改内容**:
- [x] 修改点 1
- [x] 修改点 2

**验证结果**: 全部通过 / 部分通过 / 失败

**回退方法**:
- 从 `backups/YYYYMMDD-skill-name-vX.Y/` 恢复
- Git: `cd ~/my-claude-skills && git checkout -- skill-name/`
```
