#!/usr/bin/env python3
"""
统一技能列表脚本 - 显示所有已安装技能（跨生态）

用法:
    python list.py
    python list.py --json

输出: Markdown 表格或 JSON
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Any


def get_clawhub_skills() -> List[Dict[str, Any]]:
    """获取 clawhub 已安装技能"""
    skills = []
    path = os.path.expanduser("~/.claude/skills/")

    if not os.path.exists(path):
        return skills

    for name in os.listdir(path):
        skill_path = os.path.join(path, name)
        if os.path.isdir(skill_path) and not name.startswith('.'):
            # 读取 SKILL.md 获取元数据
            skill_md = os.path.join(skill_path, "SKILL.md")
            metadata = {"name": name, "description": "", "version": ""}

            if os.path.exists(skill_md):
                try:
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 简单解析 YAML frontmatter
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                for line in frontmatter.split('\n'):
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        key = key.strip()
                                        value = value.strip().strip('"\'')
                                        if key in ['name', 'description']:
                                            metadata[key] = value
                except Exception:
                    pass

            # 获取修改时间
            mtime = os.path.getmtime(skill_path)
            metadata["installed_at"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            metadata["ecosystem"] = "clawhub"
            metadata["path"] = skill_path

            skills.append(metadata)

    return skills


def get_skills_sh_skills() -> List[Dict[str, Any]]:
    """获取 skills.sh 已安装技能"""
    skills = []
    path = os.path.expanduser("~/.agents/skills/")

    if not os.path.exists(path):
        return skills

    for name in os.listdir(path):
        skill_path = os.path.join(path, name)
        if os.path.isdir(skill_path) and not name.startswith('.'):
            # 读取 SKILL.md
            skill_md = os.path.join(skill_path, "SKILL.md")
            metadata = {"name": name, "description": "", "version": ""}

            if os.path.exists(skill_md):
                try:
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                frontmatter = parts[1]
                                for line in frontmatter.split('\n'):
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        key = key.strip()
                                        value = value.strip().strip('"\'')
                                        if key in ['name', 'description']:
                                            metadata[key] = value
                except Exception:
                    pass

            mtime = os.path.getmtime(skill_path)
            metadata["installed_at"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            metadata["ecosystem"] = "skills.sh"
            metadata["path"] = skill_path

            skills.append(metadata)

    return skills


def calculate_usage_score(skill: Dict) -> int:
    """计算技能使用评分（基于修改时间）"""
    try:
        installed_date = datetime.strptime(skill.get("installed_at", "2024-01-01"), "%Y-%m-%d")
        days_since_install = (datetime.now() - installed_date).days

        # 获取目录内文件的最新修改时间
        path = skill.get("path", "")
        if os.path.exists(path):
            latest_mtime = max(
                os.path.getmtime(os.path.join(root, f))
                for root, _, files in os.walk(path)
                for f in files
            )
            days_since_use = (datetime.now() - datetime.fromtimestamp(latest_mtime)).days

            if days_since_use < 7:
                return 100  # 最近使用
            elif days_since_use < 30:
                return 50   # 近期使用
            else:
                return 10   # 很少使用
    except Exception:
        pass

    return 0


def format_output(clawhub: List[Dict], skills_sh: List[Dict]) -> str:
    """格式化 Markdown 输出"""
    total = len(clawhub) + len(skills_sh)

    lines = ["## 已安装技能列表", ""]
    lines.append(f"总计: {total} 个技能")
    lines.append(f"- clawhub: {len(clawhub)} 个")
    lines.append(f"- skills.sh: {len(skills_sh)} 个")
    lines.append("")

    if total == 0:
        lines.append("[X] 未安装任何技能")
        lines.append("")
        lines.append("安装技能:")
        lines.append("- clawhub: `npx clawhub install <skill-name>`")
        lines.append("- skills.sh: `npx skills add <owner/repo@skill>`")
        return "\n".join(lines)

    # Clawhub 技能
    if clawhub:
        lines.append("### ClawHub 生态")
        lines.append("")
        lines.append("| 名称 | 描述 | 安装日期 | 使用频率 |")
        lines.append("|------|------|----------|----------|")

        for skill in sorted(clawhub, key=calculate_usage_score, reverse=True):
            score = calculate_usage_score(skill)
            freq = "[HOT]常用" if score >= 100 else "[OCC]偶尔" if score >= 50 else "[LOW]很少"
            desc = skill.get("description", "")[:40] + "..." if len(skill.get("description", "")) > 40 else skill.get("description", "")
            lines.append(f"| {skill['name']} | {desc} | {skill.get('installed_at', '-')} | {freq} |")

        lines.append("")

    # Skills.sh 技能
    if skills_sh:
        lines.append("### Skills.sh 生态")
        lines.append("")
        lines.append("| 名称 | 描述 | 安装日期 | 使用频率 |")
        lines.append("|------|------|----------|----------|")

        for skill in sorted(skills_sh, key=calculate_usage_score, reverse=True):
            score = calculate_usage_score(skill)
            freq = "[HOT]常用" if score >= 100 else "[OCC]偶尔" if score >= 50 else "[LOW]很少"
            desc = skill.get("description", "")[:40] + "..." if len(skill.get("description", "")) > 40 else skill.get("description", "")
            lines.append(f"| {skill['name']} | {desc} | {skill.get('installed_at', '-')} | {freq} |")

        lines.append("")

    # 使用建议
    all_skills = clawhub + skills_sh
    low_usage = [s for s in all_skills if calculate_usage_score(s) < 50]

    if len(low_usage) > 5:
        lines.append("💡 **建议**: 有 {} 个技能很少使用，可考虑清理".format(len(low_usage)))
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="List installed skills")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON format")
    parser.add_argument("--ecosystem", "-e", choices=["clawhub", "skills.sh", "all"],
                        default="all", help="Filter by ecosystem")

    args = parser.parse_args()

    clawhub_skills = get_clawhub_skills()
    skills_sh_skills = get_skills_sh_skills()

    if args.ecosystem == "clawhub":
        skills_sh_skills = []
    elif args.ecosystem == "skills.sh":
        clawhub_skills = []

    if args.json:
        output = {
            "total": len(clawhub_skills) + len(skills_sh_skills),
            "clawhub": clawhub_skills,
            "skills_sh": skills_sh_skills
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_output(clawhub_skills, skills_sh_skills))


if __name__ == "__main__":
    main()
