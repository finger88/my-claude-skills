#!/usr/bin/env python3
"""
lesson-miner skill simulation
场景：用户在专注区，记录web-content-extraction的3个踩坑
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = Path("C:/Users/HONOR/.claude/skills/lesson-miner-workspace/iteration-1/focus-zone-new-project/with_skill/outputs")
PROJECT_NAME = "web-content-extraction-practice"
PROJECT_DIR = OUTPUT_DIR / PROJECT_NAME

def simulate_workflow():
    """模拟完整的lesson-miner工作流程"""

    logs = []

    # ========== Step 1: 检测当前位置 ==========
    step1 = """
=== Step 1: 位置检测 ===
检测当前工作目录上下文...
结果: 专注区 (00 专注区/)
位置类型: focus_zone
当前项目: None
"""
    logs.append(step1)
    print(step1)

    # ========== Step 2: 识别目标项目 ==========
    step2 = """
=== Step 2: 项目识别 ===
分析对话内容提取关键词：
- "web-content-extraction" (技能名)
- "微信文章" (应用场景)
- "提取" (动作)

匹配到技能映射: web-content-extraction

用户确认:
[用户] 这个项目属于：
1. web-content-extraction 技能本身（新建项目）
2. 当前探索的课题（新建项目）
3. 其他已有项目
> 1

[用户] 新项目命名？（建议: web-content-extraction-practice）
> web-content-extraction-practice
"""
    logs.append(step2)
    print(step2)

    # 创建项目目录
    project_path = PROJECT_DIR
    project_path.mkdir(parents=True, exist_ok=True)
    logs.append(f"\n[操作] 创建项目目录: {project_path}")

    # ========== Step 3: 交互式录入卡点 ==========
    step3 = """
=== Step 3: 交互式录入卡点 ===
"""
    logs.append(step3)
    print(step3)

    pitfalls = []

    # 卡点 1
    p1 = {
        "title": "Windows路径错误 - Python无法打开文件",
        "phenomenon": "Python报错 `can't open file`，路径显示为 `D:\\c\\Users\\...` 格式，明显路径解析错误",
        "root_cause": "Windows环境下路径分隔符 `\\` 被转义或路径展开时 `~` 符号处理错误，导致路径拼接异常",
        "solution": "使用绝对路径，或将 `\\` 替换为 `/`，或使用 `pathlib.Path` 处理跨平台路径。避免在Windows下使用 `~` 展开为用户目录",
        "detection": "看到 `can't open file` + 路径中有 `\\c\\` 或其他异常片段",
        "date": "2026-03-25"
    }
    pitfalls.append(p1)

    log_p1 = f"""
--- 卡点 1/3 ---
现象: {p1['phenomenon']}
根因: {p1['root_cause']}
方案: {p1['solution']}
检测: {p1['detection']}
"""
    logs.append(log_p1)
    print(log_p1)

    # 卡点 2
    p2 = {
        "title": "WebFetch安全限制无法抓取特定域名",
        "phenomenon": "使用WebFetch工具抓取微信文章等特定域名时返回空内容或安全警告，无法获取页面内容",
        "root_cause": "WebFetch工具有安全沙箱限制，对微信域名(weixin.qq.com等)设置了访问限制，防止恶意抓取",
        "solution": "对于受限制域名，改用web-access MCP工具或手动复制内容。对于微信文章，可先用浏览器打开再复制正文",
        "detection": "WebFetch返回空内容或 `access denied` / `security restriction` 提示",
        "date": "2026-03-25"
    }
    pitfalls.append(p2)

    log_p2 = f"""
--- 卡点 2/3 ---
现象: {p2['phenomenon']}
根因: {p2['root_cause']}
方案: {p2['solution']}
检测: {p2['detection']}
"""
    logs.append(log_p2)
    print(log_p2)

    # 卡点 3
    p3 = {
        "title": "jina.ai触发CAPTCHA返回验证页面",
        "phenomenon": "通过jina.ai API提取文章内容时，返回的是CAPTCHA验证页面HTML而非正文内容",
        "root_cause": "目标网站检测到非人类访问流量，触发反爬机制要求验证。jina.ai作为代理服务无法自动处理CAPTCHA",
        "solution": "1) 减少请求频率，添加延时 2) 更换User-Agent 3) 对于CAPTCHA强制网站，改用人工复制或专用API 4) 考虑使用付费内容提取服务",
        "detection": "返回内容包含 `captcha`、`验证`、`security check` 等关键词，或明显是HTML页面而非正文",
        "date": "2026-03-25"
    }
    pitfalls.append(p3)

    log_p3 = f"""
--- 卡点 3/3 ---
现象: {p3['phenomenon']}
根因: {p3['root_cause']}
方案: {p3['solution']}
检测: {p3['detection']}
"""
    logs.append(log_p3)
    print(log_p3)

    # ========== Step 4: 生成PITFALLS.md ==========
    step4 = """
=== Step 4: 创建/更新 PITFALLS.md ===
"""
    logs.append(step4)
    print(step4)

    pitfalls_md = generate_pitfalls_md(PROJECT_NAME, pitfalls)
    pitfalls_path = project_path / "PITFALLS.md"
    pitfalls_path.write_text(pitfalls_md, encoding="utf-8")

    logs.append(f"[操作] 写入文件: {pitfalls_path}")
    logs.append(f"[操作] 文件大小: {len(pitfalls_md)} 字符")
    print(f"已创建: {pitfalls_path}")

    # ========== Step 5: 生成决策树 ==========
    step5 = """
=== Step 5: 生成决策树 ===
"""
    logs.append(step5)
    print(step5)

    decision_tree = generate_decision_tree(pitfalls)

    # 更新文档中的决策树
    content = pitfalls_path.read_text(encoding="utf-8")
    content = content.replace(
        "[决策树占位符]",
        decision_tree
    )
    pitfalls_path.write_text(content, encoding="utf-8")

    logs.append(f"[操作] 生成决策树，长度: {len(decision_tree)} 字符")
    print(f"决策树已生成，长度: {len(decision_tree)} 字符")

    # ========== Step 6: 保存执行日志 ==========
    step6 = """
=== Step 6: 保存执行日志 ===
"""
    logs.append(step6)
    print(step6)

    log_content = "\\n".join(logs)
    log_path = OUTPUT_DIR / "execution_log.txt"
    log_path.write_text(log_content, encoding="utf-8")

    print(f"\\n=== 执行完成 ===")
    print(f"项目路径: {project_path}")
    print(f"文档路径: {pitfalls_path}")
    print(f"日志路径: {log_path}")
    print(f"共记录 {len(pitfalls)} 个卡点")

    return pitfalls

def generate_pitfalls_md(project_name, pitfalls):
    """生成PITFALLS.md内容"""

    today = datetime.now().strftime("%Y-%m-%d")

    md = f"""# {project_name} 踩坑记录

> 记录本项目开发/使用过程中遇到的问题及解决方案。
> 每次踩坑后更新，保持文档活性。

---

## 快速决策树

<!-- 由 lesson-miner 自动生成 -->

```text
[决策树占位符]
```

---

## 卡点记录

<!-- 在此追加新卡点 -->
"""

    for i, p in enumerate(pitfalls, 1):
        section = f"""
### {i}. {p['title']}

| 维度 | 内容 |
|------|------|
| **现象** | {p['phenomenon']} |
| **根因** | {p['root_cause']} |
| **解决方案** | {p['solution']} |
| **检测信号** | {p['detection']} |

*记录时间: {p['date']}*

"""
        md += section

    md += f"""
---

## 最佳实践

### DO（应该做的）
- [x] 使用 `pathlib.Path` 处理跨平台路径问题
- [x] 遇到WebFetch限制时，及时切换替代方案
- [x] 对于高频请求，添加延时和重试机制
- [x] 保存原始错误信息便于后续分析

### DON'T（避免做的）
- ❌ 在Windows下直接使用 `~` 作为用户目录缩写
- ❌ 对受保护域名（如微信）强行使用WebFetch
- ❌ 忽略CAPTCHA信号继续重试（可能触发封禁）
- ❌ 混用 `\\\\` 和 `/` 作为路径分隔符

---

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| {today} | 初始版本，记录3个web-content-extraction踩坑 |

---

*最后更新: {today}*
"""

    return md

def generate_decision_tree(pitfalls):
    """生成决策树文本"""

    tree = """开始排查:

看到 `can't open file` + 路径中有异常片段（如 `\\\\c\\\\`）?
  ├─ 是 → Windows路径错误。使用绝对路径，或用 `pathlib.Path` 处理
  └─ 否 → 继续判断

WebFetch返回空内容或 `security restriction` 提示?
  ├─ 是 → 遇到安全限制。改用web-access MCP或手动复制
  └─ 否 → 继续判断

返回内容包含 `captcha`、`验证`、`security check`?
  ├─ 是 → 触发反爬机制。降低频率、更换UA，或改用人工/付费服务
  └─ 否 → 可能是新类型问题，记录卡点并更新本文档

以上都不是?
  └─ 查看具体错误信息，搜索相关解决方案，记录到本文档
"""

    return tree

if __name__ == "__main__":
    simulate_workflow()
