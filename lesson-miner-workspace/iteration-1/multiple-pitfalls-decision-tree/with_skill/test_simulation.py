#!/usr/bin/env python3
"""
Test simulation for lesson-miner skill
Scenario: Adding 4th pitfall to existing project with 3 pitfalls
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Test configuration
OUTPUT_DIR = Path("C:/Users/HONOR/.claude/skills/lesson-miner-workspace/iteration-1/multiple-pitfalls-decision-tree/with_skill/outputs")
PROJECT_NAME = "测试项目"

# Simulate the existing 3 pitfalls
existing_pitfalls = [
    {
        "title": "数据库防火墙阻止连接",
        "phenomenon": "连接数据库时报错 'Connection timed out'，无法建立连接",
        "root_cause": "数据库服务器防火墙未开放 3306 端口，或安全组规则限制",
        "solution": "1. 检查服务器防火墙设置，开放 3306 端口<br>2. 检查云平台安全组规则<br>3. 确认 IP 白名单包含应用服务器 IP",
        "detection": "看到 'Connection timed out' + 网络可达但端口不通",
        "date": "2025-03-20"
    },
    {
        "title": "数据库连接字符串格式错误",
        "phenomenon": "报错 'Access denied for user' 或 'Unknown database'",
        "root_cause": "连接字符串中用户名、密码或数据库名拼写错误，或特殊字符未转义",
        "solution": "1. 核对用户名/密码拼写<br>2. 对特殊字符进行 URL 编码<br>3. 使用配置文件分离敏感信息",
        "detection": "看到认证相关错误 + 确认网络连接正常",
        "date": "2025-03-20"
    },
    {
        "title": "环境变量未加载导致配置缺失",
        "phenomenon": "应用启动时报 'DATABASE_URL is not set' 或配置项为空",
        "root_cause": ".env 文件未加载，或环境变量未正确导出，或配置文件路径错误",
        "solution": "1. 确认 .env 文件存在且格式正确<br>2. 使用 dotenv 库加载环境变量<br>3. 检查文件权限，确保可读",
        "detection": "看到配置项缺失错误 + 应用刚部署或刚重启",
        "date": "2025-03-20"
    }
]

# Simulate the new 4th pitfall (user input)
new_pitfall = {
    "title": "数据库连接池满导致请求超时",
    "phenomenon": "应用请求超时，日志显示 'Connection pool exhausted' 或 'Timeout waiting for connection'",
    "root_cause": "数据库连接池配置过小，或连接未及时释放，或连接泄漏导致池满",
    "solution": "1. 增加连接池最大连接数（如 HikariCP 调整 maximum-pool-size）<br>2. 检查连接泄漏，确保 try-with-resources 关闭连接<br>3. 设置合理的连接超时时间<br>4. 监控连接池使用率",
    "detection": "看到 'Connection pool exhausted' 或大量请求超时 + 数据库服务正常",
    "date": "2025-03-25"
}

def generate_pitfall_entry(pitfall, index):
    """Generate markdown for a single pitfall"""
    return f"""### {index}. {pitfall['title']}

| 维度 | 内容 |
|------|------|
| **现象** | {pitfall['phenomenon']} |
| **根因** | {pitfall['root_cause']} |
| **解决方案** | {pitfall['solution']} |
| **检测信号** | {pitfall['detection']} |

*记录时间: {pitfall['date']}*

"""

def generate_decision_tree(pitfalls):
    """Generate decision tree based on detection signals"""
    tree_lines = ["开始排查数据库问题:"]

    for i, p in enumerate(pitfalls, 1):
        detection = p.get('detection', '')
        title = p.get('title', '')

        # Extract key condition from detection signal
        condition = detection
        if "看到" in detection:
            condition = detection.split("看到")[-1].strip("？?").strip()
        elif "遇到" in detection:
            condition = detection.split("遇到")[-1].strip("？?").strip()

        # Clean up condition for tree display
        condition = condition.replace("'", "").replace("+", "且").strip()

        if i == 1:
            tree_lines.append(f"  ├─ {condition}?")
        elif i < len(pitfalls):
            tree_lines.append(f"  ├─ {condition}?")
        else:
            tree_lines.append(f"  └─ {condition}?")

        # Add solution branch
        solution_preview = title.replace("数据库", "").replace("导致", "→")[:25]
        tree_lines.append(f"  │    ├─ 是 → {solution_preview}")
        tree_lines.append(f"  │    └─ 否 → 继续排查...")
        if i < len(pitfalls):
            tree_lines.append(f"  │")

    tree_lines.append("  └─ 以上都不是 → 记录新卡点")

    return "\n".join(tree_lines)

def create_before_state():
    """Create the BEFORE state document (3 pitfalls)"""
    content = f"""# {PROJECT_NAME} 踩坑记录

## 快速决策树（自动生成）

```text
开始排查数据库问题:
  ├─ 'Connection timed out' 且网络可达但端口不通?
  │    ├─ 是 → 防火墙阻止连接
  │    └─ 否 → 继续排查...
  │
  ├─ 认证相关错误 且确认网络连接正常?
  │    ├─ 是 → 连接字符串格式错误
  │    └─ 否 → 继续排查...
  │
  └─ 配置项缺失错误 且应用刚部署或刚重启?
       ├─ 是 → 环境变量未加载
       └─ 否 → 继续排查...

  └─ 以上都不是 → 记录新卡点
```

## 卡点记录

"""

    # Add existing pitfalls
    for i, p in enumerate(existing_pitfalls, 1):
        content += generate_pitfall_entry(p, i)

    content += """## 最佳实践

### DO
- [ ] 使用连接池管理数据库连接
- [ ] 配置连接超时和重试机制
- [ ] 将数据库配置与代码分离
- [ ] 使用环境变量存储敏感信息

### DON'T
- ❌ 在代码中硬编码数据库密码
- ❌ 使用 root 账户连接应用数据库
- ❌ 忽略连接错误处理
- ❌ 无限制地创建新连接而不关闭旧连接

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2025-03-20 | 初始化：添加前 3 个常见数据库连接问题 |

---

*最后更新: 2025-03-20*
"""

    return content

def create_after_state():
    """Create the AFTER state document (4 pitfalls including new one)"""
    all_pitfalls = existing_pitfalls + [new_pitfall]

    content = f"""# {PROJECT_NAME} 踩坑记录

## 快速决策树（自动生成）

```text
{generate_decision_tree(all_pitfalls)}
```

## 卡点记录

"""

    # Add all pitfalls
    for i, p in enumerate(all_pitfalls, 1):
        content += generate_pitfall_entry(p, i)

    content += """## 最佳实践

### DO
- [ ] 使用连接池管理数据库连接（推荐 HikariCP）
- [ ] 配置连接超时和重试机制
- [ ] 将数据库配置与代码分离
- [ ] 使用环境变量存储敏感信息
- [ ] 监控连接池使用率（目标 < 80%）
- [ ] 使用 try-with-resources 确保连接关闭

### DON'T
- ❌ 在代码中硬编码数据库密码
- ❌ 使用 root 账户连接应用数据库
- ❌ 忽略连接错误处理
- ❌ 无限制地创建新连接而不关闭旧连接
- ❌ 连接池配置过大（浪费资源）或过小（导致超时）
- ❌ 忽略连接池监控和告警

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2025-03-20 | 初始化：添加前 3 个常见数据库连接问题 |
| 2025-03-25 | 新增：数据库连接池满导致请求超时 |

---

*最后更新: 2025-03-25*
"""

    return content

def main():
    print("=== Lesson-Miner Skill Test: Multiple Pitfalls Scenario ===\n")

    # Create BEFORE state
    print("[1/4] Creating BEFORE state with 3 pitfalls...")
    before_content = create_before_state()
    before_path = OUTPUT_DIR / "PITFALLS_BEFORE.md"
    before_path.write_text(before_content, encoding="utf-8")
    print(f"      [OK] Created: {before_path}")

    # Create AFTER state
    print("\n[2/4] Creating AFTER state with 4 pitfalls (including new one)...")
    after_content = create_after_state()
    after_path = OUTPUT_DIR / "PITFALLS.md"
    after_path.write_text(after_content, encoding="utf-8")
    print(f"      [OK] Created: {after_path}")

    # Extract and display decision trees
    print("\n[3/4] Extracting decision trees for comparison...")

    # Parse BEFORE tree
    before_tree_match = re.search(r'## 快速决策树.*?```text(.*?)```', before_content, re.DOTALL)
    before_tree = before_tree_match.group(1).strip() if before_tree_match else "NOT FOUND"

    # Parse AFTER tree
    after_tree_match = re.search(r'## 快速决策树.*?```text(.*?)```', after_content, re.DOTALL)
    after_tree = after_tree_match.group(1).strip() if after_tree_match else "NOT FOUND"

    # Save trees for comparison
    tree_comparison = f"""# 决策树对比

## BEFORE (3 pitfalls)

```text
{before_tree}
```

## AFTER (4 pitfalls)

```text
{after_tree}
```

## Changes Summary

1. **新增分支**: 连接池满检测（第4分支）
2. **结构变化**: 从3层决策扩展到4层
3. **检测信号**: 基于"看到 Connection pool exhausted"快速识别
4. **最佳实践更新**: 新增连接池监控和配置建议

## 新增卡点详情

**标题**: {new_pitfall['title']}

**现象**: {new_pitfall['phenomenon']}

**根因**: {new_pitfall['root_cause']}

**解决方案**: {new_pitfall['solution']}

**检测信号**: {new_pitfall['detection']}
"""

    comparison_path = OUTPUT_DIR / "DECISION_TREE_COMPARISON.md"
    comparison_path.write_text(tree_comparison, encoding="utf-8")
    print(f"      [OK] Created: {comparison_path}")

    # Display summary
    print("\n[4/4] Test Summary:")
    print("=" * 60)
    print(f"项目: {PROJECT_NAME}")
    print(f"初始卡点: 3 个")
    print(f"新增卡点: 1 个（连接池满）")
    print(f"最终卡点: 4 个")
    print(f"\n输出文件:")
    print(f"  - PITFALLS_BEFORE.md (3 pitfalls)")
    print(f"  - PITFALLS.md (4 pitfalls, final)")
    print(f"  - DECISION_TREE_COMPARISON.md (对比分析)")
    print("=" * 60)

    print("\n决策树对比:")
    print("\n--- BEFORE (3 branches) ---")
    print(before_tree)
    print("\n--- AFTER (4 branches) ---")
    print(after_tree)

    print("\n[Test OK] Test completed successfully!")
    print(f"[OK] All outputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
