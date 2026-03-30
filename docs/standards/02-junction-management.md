# Junction 链接管理规范

> **版本**: v1.0
> **关联配置**: `.skillrc` -> `junction_rules`

## 1. 什么是 Junction 链接

Junction 链接是 Windows 特有的一种目录链接（Directory Junction），它允许一个目录指向另一个目录，而不占用额外磁盘空间。

### 1.1 Junction vs 其他链接类型

| 类型 | Windows 支持 | MSYS2 显示 | 用途 |
|------|-------------|-----------|------|
| **Junction** | ✅ CMD 原生 | `<JUNCTION>` | 目录链接（推荐）|
| 符号链接 (Symlink) | ✅ 需要管理员 | `lrwxrwxrwx` | 文件/目录链接 |
| MSYS2 软链接 | ❌ 模拟 | `lrwxrwxrwx` | **Claude 不识别** |
| 快捷方式 (.lnk) | ✅ 资源管理器 | `.lnk` 文件 | 仅资源管理器有效 |

### 1.2 为什么必须用 Junction

Claude Code 在 Windows 上运行时：
- ✅ 能正确识别 Windows Junction
- ❌ 不能识别 MSYS2 `ln -s` 创建的软链接
- ❌ 直接复制目录会导致版本不一致

## 2. 创建 Junction 的标准方法

### 2.1 在 CMD 中创建

```cmd
mklink /J "C:\Users\HONOR\.claude\skills\skill-name" "C:\Users\HONOR\my-claude-skills\skill-name"
```

### 2.2 在 MSYS2/Git Bash 中创建

```bash
# 方法 1: 使用 MSYS_NO_PATHCONV
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"

# 方法 2: 使用 Windows 路径格式
MSYS_NO_PATHCONV=1 cmd //c "mklink /J C:\\Users\\HONOR\\.claude\\skills\\skill-name C:\\Users\\HONOR\\my-claude-skills\\skill-name"
```

### 2.3 使用 fix-junctions.sh 脚本

```bash
# 自动为所有 Git 仓库中的 skills 创建 Junction
./fix-junctions.sh
```

## 3. 验证 Junction

### 3.1 CMD 验证（推荐）

```cmd
dir /a C:\Users\HONOR\.claude\skills\
```

**正确输出示例**:
```
2026-03-30  12:00    <JUNCTION>     skill-name [C:\Users\HONOR\my-claude-skills\skill-name]
```

### 3.2 MSYS2 验证（不推荐作为主要验证方式）

```bash
ls -la ~/.claude/skills/
```

**注意**: MSYS2 会将 Junction 显示为 `lrwxrwxrwx`，但这不代表它是软链接！

## 4. 常见问题与修复

### 4.1 问题：创建了普通目录而非 Junction

**症状**:
```cmd
# dir /a 显示
2026-03-30  12:00    <DIR>          skill-name
```

**修复**:
```bash
# 1. 删除错误创建的目录
rm -rf ~/.claude/skills/skill-name

# 2. 重新创建 Junction
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"
```

### 4.2 问题：Junction 指向错误目标

**修复**:
```bash
# 1. 删除错误的 Junction
rmdir ~/.claude/skills/skill-name

# 2. 重新创建
MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\Users\HONOR\.claude\skills\skill-name C:\Users\HONOR\my-claude-skills\skill-name"
```

### 4.3 问题：Junction 断裂（目标被删除）

**症状**: Junction 存在但指向的目录已不存在

**修复**:
```bash
# 删除断裂的 Junction
rmdir ~/.claude/skills/skill-name

# 如果 skill 还应该存在，重新创建目标目录
# 如果 skill 已废弃，完成删除
```

## 5. 最佳实践

### 5.1 永远不要

- ❌ 用 `cp -r` 复制 skill 到 `.claude/skills/`
- ❌ 用 `ln -s` 在 MSYS2 中创建链接
- ❌ 在 `.claude/skills/` 中直接编辑文件
- ❌ 手动创建与 skill 同名的文件夹

### 5.2 总是要

- ✅ 编辑 `my-claude-skills/` 中的文件
- ✅ 使用 `fix-junctions.sh` 或标准命令创建 Junction
- ✅ 定期运行 `check-standard.py` 检查完整性
- ✅ 提交前确认 Junction 状态正确

## 6. 工具命令速查

| 操作 | 命令 |
|------|------|
| 创建 Junction | `MSYS_NO_PATHCONV=1 cmd /c "mklink /J TARGET SOURCE"` |
| 删除 Junction | `rmdir TARGET`（仅删除链接，不删源文件）|
| 验证类型 | `cmd /c "dir /a TARGET_PARENT"` |
| 批量修复 | `./fix-junctions.sh` |
| 标准检查 | `python tools/check-standard.py` |
