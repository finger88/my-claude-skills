#!/usr/bin/env python3
"""
智能技能推荐脚本 - 基于任务和使用历史推荐技能

用法:
    python recommend.py
    python recommend.py --from-task "标书智能体"

推荐逻辑:
    - 分析 _本周.md 提取当前任务关键词
    - 分析已安装技能的使用频率
    - 匹配任务需求与可用技能
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


# 任务关键词到技能的映射
TASK_SKILL_MAPPING = {
    # 文档处理
    "标书": ["document-parser", "pdf-extractor", "docx-generator"],
    "文档": ["document-parser", "file-converter"],
    "pdf": ["pdf-extractor", "pdf-editor", "pdf-rotate"],
    "docx": ["docx-generator", "document-parser"],
    "word": ["docx-generator", "document-parser"],

    # AI/Prompt
    "角色": ["prompt-optimizer", "character-designer"],
    "prompt": ["prompt-optimizer", "prompt-template"],
    "智能体": ["agent-builder", "workflow-designer"],
    "agent": ["agent-builder", "workflow-designer"],

    # 数据分析
    "数据": ["data-analyzer", "csv-processor", "excel-tools"],
    "分析": ["data-analyzer", "chart-generator"],
    "可视化": ["chart-generator", "plot-tools"],

    # Web/内容
    "网页": ["web-content-extraction", "html-parser"],
    "爬虫": ["web-content-extraction", "scraping-tools"],
    "提取": ["web-content-extraction", "data-extractor"],

    # 代码
    "代码": ["code-reviewer", "refactor-tools"],
    "重构": ["refactor-tools", "code-reviewer"],
    "测试": ["test-generator", "testing-tools"],

    # 创意
    "ppt": ["ppt-maker", "slide-generator"],
    "演示": ["ppt-maker", "presentation-tools"],
    "图表": ["chart-generator", "mermaid-tools"],

    # 效率
    "剪藏": ["ljg-clip", "content-clipper"],
    "保存": ["ljg-clip", "bookmark-manager"],
    "阅读": ["ljg-xray-article", "article-summarizer"],
}


def extract_tasks_from_weekly(weekly_path: str) -> Dict[str, Any]:
    """从 _本周.md 提取任务信息"""
    tasks = {
        "keywords": [],
        "projects": [],
        "blockers": []
    }

    if not os.path.exists(weekly_path):
        return tasks

    try:
        with open(weekly_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取原始口述中的关键词
        oral_section = re.search(r'## 原始口述(.*?)(?=##|\Z)', content, re.DOTALL)
        if oral_section:
            oral_text = oral_section.group(1)
            # 提取粗体作为重点项目
            bold_items = re.findall(r'\*\*(.+?)\*\*', oral_text)
            tasks["projects"].extend(bold_items)

        # 提取任务清单
        task_section = re.search(r'### 本周任务(.*?)##', content, re.DOTALL)
        if task_section:
            task_text = task_section.group(1)
            # 提取 [项目名] 格式
            projects = re.findall(r'\[([^\]]+)\]', task_text)
            tasks["projects"].extend(projects)

        # 提取阻塞项
        blocker_section = re.search(r'- 阻塞：(.+?)(?=\n|$)', content)
        if blocker_section:
            blocker_text = blocker_section.group(1)
            if blocker_text.strip() and blocker_text.strip() != "无":
                tasks["blockers"].append(blocker_text.strip())

        # 关键词提取（简单匹配）
        all_text = content.lower()
        for keyword in TASK_SKILL_MAPPING.keys():
            if keyword in all_text:
                tasks["keywords"].append(keyword)

    except Exception as e:
        print(f"Warning: 无法解析周文件: {e}", file=__import__('sys').stderr)

    return tasks


def get_skill_usage_stats() -> Dict[str, Any]:
    """获取技能使用统计"""
    stats = {
        "clawhub": {},
        "skills_sh": {},
        "high_usage": [],
        "low_usage": [],
        "never_used": []
    }

    # 检查 clawhub 技能
    clawhub_path = os.path.expanduser("~/.claude/skills/")
    if os.path.exists(clawhub_path):
        for name in os.listdir(clawhub_path):
            skill_path = os.path.join(clawhub_path, name)
            if os.path.isdir(skill_path) and not name.startswith('.'):
                try:
                    mtime = os.path.getmtime(skill_path)
                    days_since = (datetime.now() - datetime.fromtimestamp(mtime)).days

                    stats["clawhub"][name] = {
                        "days_since_modified": days_since,
                        "category": categorize_skill(name)
                    }

                    if days_since < 7:
                        stats["high_usage"].append(("clawhub", name))
                    elif days_since > 60:
                        stats["low_usage"].append(("clawhub", name))
                except Exception:
                    pass

    # 检查 skills.sh 技能
    agents_path = os.path.expanduser("~/.agents/skills/")
    if os.path.exists(agents_path):
        for name in os.listdir(agents_path):
            skill_path = os.path.join(agents_path, name)
            if os.path.isdir(skill_path) and not name.startswith('.'):
                try:
                    mtime = os.path.getmtime(skill_path)
                    days_since = (datetime.now() - datetime.fromtimestamp(mtime)).days

                    stats["skills_sh"][name] = {
                        "days_since_modified": days_since,
                        "category": categorize_skill(name)
                    }

                    if days_since < 7:
                        stats["high_usage"].append(("skills.sh", name))
                    elif days_since > 60:
                        stats["low_usage"].append(("skills.sh", name))
                except Exception:
                    pass

    return stats


def categorize_skill(name: str) -> str:
    """根据名称分类技能"""
    name_lower = name.lower()

    categories = {
        "xray": "分析",
        "explain": "解释",
        "clip": "剪藏",
        "extract": "提取",
        "parser": "解析",
        "generator": "生成",
        "creator": "创建",
        "manager": "管理",
    }

    for key, cat in categories.items():
        if key in name_lower:
            return cat

    return "其他"


def generate_recommendations(tasks: Dict, usage_stats: Dict) -> List[Dict]:
    """生成推荐列表"""
    recommendations = []
    installed_clawhub = set(usage_stats["clawhub"].keys())
    installed_skills_sh = set(usage_stats["skills_sh"].keys())
    all_installed = installed_clawhub.union(installed_skills_sh)

    # 基于任务关键词推荐
    for keyword in tasks.get("keywords", []):
        if keyword in TASK_SKILL_MAPPING:
            for skill_name in TASK_SKILL_MAPPING[keyword]:
                if skill_name not in all_installed:
                    recommendations.append({
                        "skill": skill_name,
                        "reason": f"任务中提到 '{keyword}'，此技能可提供专业支持",
                        "source": "task_analysis",
                        "priority": 1
                    })

    # 基于项目推荐
    for project in tasks.get("projects", []):
        project_lower = project.lower()
        for keyword, skills in TASK_SKILL_MAPPING.items():
            if keyword in project_lower:
                for skill_name in skills:
                    if skill_name not in all_installed:
                        rec = {
                            "skill": skill_name,
                            "reason": f"项目 '{project}' 可能需要此技能",
                            "source": "project_analysis",
                            "priority": 2
                        }
                        if rec not in recommendations:
                            recommendations.append(rec)

    # 基于使用模式推荐
    # 如果常用 X-ray 系列，推荐同类分析工具
    xray_used = any("xray" in name for name in installed_clawhub)
    if xray_used:
        for skill in ["deep-analyzer", "content-parser"]:
            if skill not in all_installed:
                recommendations.append({
                    "skill": skill,
                    "reason": "你常用内容分析类技能，此工具可扩展能力",
                    "source": "usage_pattern",
                    "priority": 3
                })

    # 去重并排序
    seen = set()
    unique_recs = []
    for rec in sorted(recommendations, key=lambda x: x["priority"]):
        if rec["skill"] not in seen:
            seen.add(rec["skill"])
            unique_recs.append(rec)

    return unique_recs[:5]  # 最多5个


def format_output(recommendations: List[Dict], tasks: Dict, usage_stats: Dict) -> str:
    """格式化输出"""
    lines = ["## 技能智能推荐", ""]

    # 分析摘要
    lines.append("### 分析依据")
    lines.append("")
    if tasks.get("keywords"):
        lines.append(f"- 检测到的任务关键词: {', '.join(set(tasks['keywords']))}")
    if tasks.get("projects"):
        lines.append(f"- 当前项目: {', '.join(set(tasks['projects']))}")
    lines.append(f"- 已安装技能: {len(usage_stats['clawhub'])} (clawhub) + {len(usage_stats['skills_sh'])} (skills.sh)")
    lines.append("")

    if not recommendations:
        lines.append("✅ **暂无推荐**")
        lines.append("")
        lines.append("原因:")
        lines.append("- 当前任务已有足够技能支持")
        lines.append("- 或任务类型不在推荐数据库中")
        lines.append("")
        lines.append("建议:")
        lines.append("- 手动搜索: `python scripts/search.py <关键词>`")
        return "\n".join(lines)

    lines.append(f"### 推荐技能 ({len(recommendations)}个)")
    lines.append("")

    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. **{rec['skill']}**")
        lines.append(f"   💡 {rec['reason']}")

        # 尝试猜测生态
        if "ljg-" in rec['skill']:
            eco = "clawhub"
            cmd = f"npx clawhub install {rec['skill']}"
        else:
            eco = "skills.sh"
            cmd = f"npx skills search {rec['skill']}"

        lines.append(f"   搜索: `{cmd}`")
        lines.append("")

    lines.append("### 下一步")
    lines.append("")
    lines.append("1. 搜索技能详情:")
    lines.append("   ```bash")
    lines.append("   python scripts/search.py <关键词>")
    lines.append("   ```")
    lines.append("")
    lines.append("2. 安装推荐技能:")
    lines.append("   ```bash")
    lines.append("   python scripts/install.py <skill-name>")
    lines.append("   ```")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Smart skill recommendation")
    parser.add_argument("--from-task", help="Specify current task context")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    parser.add_argument("--weekly-path", default="zh-CN/00 专注区/_本周.md",
                        help="Path to weekly file")

    args = parser.parse_args()

    # 解析周文件
    weekly_full_path = os.path.expanduser(args.weekly_path)
    if not os.path.exists(weekly_full_path):
        # 尝试相对路径
        weekly_full_path = args.weekly_path

    tasks = extract_tasks_from_weekly(weekly_full_path)
    if args.from_task:
        tasks["projects"].append(args.from_task)

    # 获取使用统计
    usage_stats = get_skill_usage_stats()

    # 生成推荐
    recommendations = generate_recommendations(tasks, usage_stats)

    if args.json:
        output = {
            "tasks": tasks,
            "usage_stats": usage_stats,
            "recommendations": recommendations
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_output(recommendations, tasks, usage_stats))


if __name__ == "__main__":
    main()
