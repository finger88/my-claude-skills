#!/usr/bin/env python3
"""
lesson-miner: 经验挖掘器主入口
交互式记录卡点，生成/更新项目级 PITFALLS.md
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

# 配置路径
SKILL_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"
PROJECTS_ROOT = Path("zh-CN/01 你的项目")  # 相对路径，实际使用时转为绝对路径
FOCUS_ZONE = Path("zh-CN/00 专注区")


def detect_context():
    """检测当前工作目录上下文"""
    cwd = Path.cwd()
    cwd_str = str(cwd).replace("\\", "/")

    if "00 专注区" in cwd_str or "00 Focus Zone" in cwd_str:
        return "focus_zone", None
    elif "01 你的项目" in cwd_str or "01 Projects" in cwd_str:
        # 提取项目名
        match = re.search(r'01 [^/]+/([^/]+)', cwd_str)
        if match:
            return "project_zone", match.group(1)
        return "project_zone", None
    else:
        return "other", None


def list_existing_projects(base_path: Path):
    """列出已有项目"""
    if not base_path.exists():
        return []

    projects = []
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            projects.append(item.name)
    return sorted(projects)


def extract_project_from_dialog(dialog_history: list):
    """从对话历史提取项目名关键词"""
    keywords = []

    # 常见技能/工具名映射到项目
    skill_to_project = {
        "web-content-extraction": ["web-content-extraction", "内容提取", "网页提取"],
        "feishu": ["做饭智能体", "chefmind", "飞书"],
        "wechat": ["微信", "公众号", "wechat-publish"],
    }

    for msg in dialog_history[-10:]:  # 最近10条
        content = msg.get("content", "")
        for skill, patterns in skill_to_project.items():
            for pattern in patterns:
                if pattern in content:
                    keywords.append(skill)

    return list(set(keywords))


def interactive_capture():
    """交互式录入卡点"""
    pitfall = {}

    print("\n=== 录入卡点 ===")
    pitfall["title"] = input("卡点标题（简短）: ").strip()
    pitfall["phenomenon"] = input("现象（用户看到了什么）: ").strip()
    pitfall["root_cause"] = input("根因（为什么会这样）: ").strip()
    pitfall["solution"] = input("解决方案（具体怎么做）: ").strip()
    pitfall["detection"] = input("检测信号（如何快速识别）: ").strip()
    pitfall["date"] = datetime.now().strftime("%Y-%m-%d")

    return pitfall


def load_template():
    """加载 PITFALLS.md 模板"""
    template_path = TEMPLATES_DIR / "pitfalls_template.md"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")

    # 默认模板
    return """# {project_name} 踩坑记录

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

---

## 最佳实践

### DO（应该做的）
- [ ]

### DON'T（避免做的）
- ❌

---

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| {date} | 初始版本 |

---

*最后更新: {date}*
"""


def update_pitfalls_doc(project_path: Path, project_name: str, pitfalls: list):
    """更新或创建 PITFALLS.md"""
    doc_path = project_path / "PITFALLS.md"

    if doc_path.exists():
        content = doc_path.read_text(encoding="utf-8")
        # 追加新卡点
        new_section = generate_pitfalls_section(pitfalls)

        # 在 "<!-- 在此追加新卡点 -->" 后插入
        marker = "<!-- 在此追加新卡点 -->"
        if marker in content:
            content = content.replace(marker, marker + "\n" + new_section)
        else:
            # 在 ## 卡点记录 后插入
            content = content.replace("## 卡点记录", "## 卡点记录\n" + new_section)

        # 更新更新日志
        today = datetime.now().strftime("%Y-%m-%d")
        new_log = f"| {today} | 新增 {len(pitfalls)} 个卡点 |"

        # 在更新日志表格中追加
        log_pattern = r"(## 更新日志\s*\n\s*\|[^\n]+\|\s*\n\s*\|[^\n]+\|)"
        if re.search(log_pattern, content):
            content = re.sub(log_pattern, r"\1\n" + new_log, content)

        # 更新最后更新时间
        content = re.sub(r"\*最后更新: [^\*]+\*", f"*最后更新: {today}*", content)

    else:
        # 创建新文档
        template = load_template()
        today = datetime.now().strftime("%Y-%m-%d")
        content = template.format(project_name=project_name, date=today)

        # 添加卡点
        new_section = generate_pitfalls_section(pitfalls)
        content = content.replace("[决策树占位符]", "（暂无决策树，录入多个卡点后自动生成）")
        content = content.replace("<!-- 在此追加新卡点 -->", "<!-- 在此追加新卡点 -->\n" + new_section)

    doc_path.write_text(content, encoding="utf-8")
    return doc_path


def generate_pitfalls_section(pitfalls: list):
    """生成卡点记录 Markdown 片段"""
    sections = []

    for i, p in enumerate(pitfalls, 1):
        section = f"""### {i}. {p['title']}

| 维度 | 内容 |
|------|------|
| **现象** | {p['phenomenon']} |
| **根因** | {p['root_cause']} |
| **解决方案** | {p['solution']} |
| **检测信号** | {p['detection']} |

*记录时间: {p['date']}*

"""
        sections.append(section)

    return "\n".join(sections)


def generate_decision_tree(pitfalls: list):
    """基于卡点生成简单决策树"""
    if len(pitfalls) < 2:
        return "（卡点数量不足，暂不生成决策树）"

    tree_lines = ["开始排查:"]

    for p in pitfalls:
        detection = p.get('detection', '')
        solution = p.get('solution', '')

        # 提取关键条件
        if "看到" in detection or "遇到" in detection:
            condition = detection.split("看到")[-1].split("遇到")[-1].strip("？?")
            tree_lines.append(f"  {condition}?")
            tree_lines.append(f"    └─ 是 → {solution[:30]}...")

    tree_lines.append("  └─ 以上都不是 → 记录新卡点")

    return "\n".join(tree_lines)


def update_decision_tree(project_path: Path, pitfalls: list):
    """更新文档中的决策树"""
    doc_path = project_path / "PITFALLS.md"
    if not doc_path.exists():
        return

    content = doc_path.read_text(encoding="utf-8")
    new_tree = generate_decision_tree(pitfalls)

    # 替换决策树部分
    pattern = r"(## 快速决策树.*?```text\s*).*?(\s*```)"
    replacement = r"\1" + new_tree + r"\2"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    doc_path.write_text(content, encoding="utf-8")


def main():
    """主入口"""
    print("=== lesson-miner: 经验挖掘器 ===\n")

    # 检测上下文
    context, current_project = detect_context()
    print(f"当前位置: {context}" + (f" (项目: {current_project})" if current_project else ""))

    # 确定目标项目
    target_project = None

    if context == "project_zone" and current_project:
        print(f"\n当前在项目 '{current_project}' 下。")
        switch = input("记录到当前项目？还是其他项目？(当前/其他) [当前]: ").strip()
        if not switch or switch in ["当前", "current", "y", "yes"]:
            target_project = current_project

    if not target_project:
        # 列出已有项目
        projects = list_existing_projects(PROJECTS_ROOT)

        if projects:
            print("\n已有项目:")
            for i, p in enumerate(projects, 1):
                print(f"  {i}. {p}")
            print(f"  {len(projects)+1}. [新建项目]")

            choice = input(f"\n选择项目 (1-{len(projects)+1}): ").strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    target_project = projects[idx]
                elif idx == len(projects):
                    target_project = input("新项目命名: ").strip()
            else:
                target_project = choice
        else:
            print("\n暂无项目，创建新项目。")
            target_project = input("项目命名: ").strip()

    if not target_project:
        print("错误: 未指定项目名")
        return 1

    # 确保项目目录存在
    project_path = PROJECTS_ROOT / target_project
    project_path.mkdir(parents=True, exist_ok=True)

    print(f"\n目标项目: {target_project}")
    print(f"项目路径: {project_path}\n")

    # 交互式录入卡点
    pitfalls = []
    while True:
        pitfall = interactive_capture()
        if pitfall["title"]:
            pitfalls.append(pitfall)

        more = input("\n继续录入下一个卡点? (y/n) [n]: ").strip().lower()
        if more not in ["y", "yes", "是"]:
            break

    if not pitfalls:
        print("未录入任何卡点，退出。")
        return 0

    # 更新文档
    doc_path = update_pitfalls_doc(project_path, target_project, pitfalls)
    print(f"\n✓ 已更新: {doc_path}")

    # 询问是否生成决策树
    if len(pitfalls) >= 1:
        gen_tree = input("\n生成/更新决策树? (y/n) [y]: ").strip().lower()
        if not gen_tree or gen_tree in ["y", "yes", "是"]:
            update_decision_tree(project_path, pitfalls)
            print("✓ 决策树已更新")

    print(f"\n完成！共记录 {len(pitfalls)} 个卡点。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
