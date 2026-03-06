#!/usr/bin/env python3
"""
统一技能搜索脚本 - 跨 clawhub 和 skills.sh 搜索

用法:
    python search.py <关键词>
    python search.py datetime
    python search.py "web scraping"

输出: JSON 格式合并结果
"""

import argparse
import json
import subprocess
import sys
import re
import concurrent.futures
from typing import List, Dict, Any

# Windows 编码修复
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def search_skills_sh(query: str) -> List[Dict[str, Any]]:
    """搜索 skills.sh 生态"""
    results = []
    try:
        result = subprocess.run(
            ["npx", "skills", "find", query],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # 解析输出格式：
            # owner/repo@skill-name  [安装量]
            # └ https://skills.sh/...
            lines = result.stdout.strip().split('\n')
            current_skill = None

            for line in lines:
                line = line.strip()
                # 匹配技能行 (去除 ANSI 颜色码)
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)

                if '@' in clean_line and 'install' not in clean_line.lower():
                    # 提取 skill 标识
                    match = re.search(r'([\w-]+/[\w-]+@[\w-]+)', clean_line)
                    if match:
                        skill_id = match.group(1)
                        # 提取安装量
                        install_match = re.search(r'(\d+(?:\.\d+)?[Kk]?)\s*install', clean_line)
                        installs = install_match.group(1) if install_match else "0"

                        current_skill = {
                            "id": skill_id,
                            "ecosystem": "skills.sh",
                            "installs": installs,
                            "description": "",  # skills.sh find 不返回描述
                            "url": f"https://skills.sh/{skill_id.replace('@', '/')}"
                        }
                elif current_skill and line.startswith('└'):
                    # URL 行，跳过
                    results.append(current_skill)
                    current_skill = None
                elif current_skill and line and not line.startswith('─'):
                    # 可能是描述
                    current_skill["description"] = clean_line[:100]

    except subprocess.TimeoutExpired:
        return [{"error": "skills.sh search timeout", "ecosystem": "skills.sh"}]
    except FileNotFoundError:
        return [{"error": "skills CLI not found", "ecosystem": "skills.sh"}]
    except Exception as e:
        return [{"error": str(e), "ecosystem": "skills.sh"}]

    return results


def search_clawhub(query: str) -> List[Dict[str, Any]]:
    """搜索 clawhub 生态（使用 web-content-extraction）"""
    results = []
    try:
        # 尝试使用 extract.py
        import tempfile
        import os

        temp_file = tempfile.mktemp(suffix='.json')

        result = subprocess.run(
            ["python", os.path.expanduser("~/.claude/skills/web-content-extraction/scripts/extract.py"),
             f"https://clawhub.ai/skills?search={query}",
             "-o", temp_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('success'):
                    # 解析 content 中的技能列表
                    content = data.get('content', '')
                    # 简单解析：寻找技能名称和安装量
                    # 格式通常: skill-name [安装量]
                    lines = content.split('\n')
                    for line in lines:
                        if '└' in line or '├' in line:
                            continue
                        # 提取可能的技能名
                        match = re.search(r'^([\w-]+)\s+\[?([\d.]+[Kk]?)\s*(?:install|下载)?\]?', line, re.I)
                        if match:
                            skill_name = match.group(1)
                            installs = match.group(2) if match.group(2) else "0"
                            results.append({
                                "id": skill_name,
                                "ecosystem": "clawhub",
                                "installs": installs,
                                "description": "",
                                "url": f"https://clawhub.ai/skills/{skill_name}"
                            })

            os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        return [{"error": "clawhub search timeout", "ecosystem": "clawhub"}]
    except FileNotFoundError:
        # web-content-extraction 未安装，返回错误
        return [{"error": "web-content-extraction not installed", "ecosystem": "clawhub"}]
    except Exception as e:
        return [{"error": str(e), "ecosystem": "clawhub"}]

    return results


def get_installed_skills() -> Dict[str, List[str]]:
    """获取已安装技能列表"""
    installed = {"clawhub": [], "skills.sh": []}

    # clawhub skills
    import os
    import glob
    clawhub_path = os.path.expanduser("~/.claude/skills/")
    if os.path.exists(clawhub_path):
        for item in os.listdir(clawhub_path):
            item_path = os.path.join(clawhub_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                installed["clawhub"].append(item)

    # skills.sh skills
    agents_path = os.path.expanduser("~/.agents/skills/")
    if os.path.exists(agents_path):
        for item in os.listdir(agents_path):
            item_path = os.path.join(agents_path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                installed["skills.sh"].append(item)

    return installed


def merge_results(skills_sh_results: List[Dict], clawhub_results: List[Dict],
                  installed: Dict[str, List[str]]) -> Dict[str, Any]:
    """合并搜索结果，标记已安装"""

    # 标记已安装
    for skill in skills_sh_results:
        if "error" not in skill:
            skill_name = skill["id"].split("@")[-1]
            skill["installed"] = skill_name in installed["skills.sh"]

    for skill in clawhub_results:
        if "error" not in skill:
            skill["installed"] = skill["id"] in installed["clawhub"]

    # 合并
    all_results = skills_sh_results + clawhub_results

    # 排序：已安装 > 有安装量 > 无安装量
    def sort_key(skill):
        if "error" in skill:
            return (2, 0, "")
        installed_flag = 0 if skill.get("installed") else 1

        # 解析安装量
        installs = skill.get("installs", "0")
        if isinstance(installs, str):
            installs = installs.lower().replace('k', '000').replace('.', '')
            try:
                installs = int(installs)
            except:
                installs = 0

        return (installed_flag, -installs, skill.get("id", ""))

    all_results.sort(key=sort_key)

    return {
        "query": None,  # 填充在外层
        "total": len([r for r in all_results if "error" not in r]),
        "errors": [r for r in all_results if "error" in r],
        "clawhub_count": len([r for r in clawhub_results if "error" not in r]),
        "skills_sh_count": len([r for r in skills_sh_results if "error" not in r]),
        "results": [r for r in all_results if "error" not in r][:20]  # 最多20个
    }


def format_output(data: Dict[str, Any], query: str) -> str:
    """格式化输出为 Markdown"""
    lines = [f"## 技能搜索结果: '{query}'"]
    lines.append("")
    lines.append(f"找到 {data['total']} 个技能")
    lines.append(f"- clawhub: {data['clawhub_count']} 个")
    lines.append(f"- skills.sh: {data['skills_sh_count']} 个")
    lines.append("")

    if data["errors"]:
        lines.append("⚠️ **搜索警告**:")
        for err in data["errors"]:
            lines.append(f"- {err['ecosystem']}: {err.get('error', 'Unknown error')}")
        lines.append("")

    if not data["results"]:
        lines.append("❌ 未找到匹配的技能")
        lines.append("")
        lines.append("建议:")
        lines.append("- 尝试更通用的关键词")
        lines.append("- 检查拼写")
        lines.append("- 或创建自定义技能")
        return "\n".join(lines)

    lines.append("### 结果列表")
    lines.append("")

    for i, skill in enumerate(data["results"], 1):
        installed_mark = " ★已安装" if skill.get("installed") else ""
        installs = skill.get("installs", "0")
        if installs and installs != "0":
            install_info = f" [{installs} 安装]"
        else:
            install_info = ""

        lines.append(f"{i}. **{skill['id']}** ({skill['ecosystem']}){installed_mark}{install_info}")

        if skill.get("description"):
            lines.append(f"   > {skill['description']}")

        # 安装命令
        if skill["ecosystem"] == "clawhub":
            lines.append(f"   安装: `npx clawhub install {skill['id']}`")
        else:
            lines.append(f"   安装: `npx skills add {skill['id']}`")

        if skill.get("url"):
            lines.append(f"   详情: {skill['url']}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Unified Skill Search")
    parser.add_argument("query", help="Search keyword")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON format")
    parser.add_argument("--max-results", "-n", type=int, default=20, help="Max results")

    args = parser.parse_args()

    print(f"🔍 搜索 '{args.query}'...", file=sys.stderr)

    # 并行搜索两个生态
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_sh = executor.submit(search_skills_sh, args.query)
        future_clawhub = executor.submit(search_clawhub, args.query)

        skills_sh_results = future_sh.result()
        clawhub_results = future_clawhub.result()

    # 获取已安装列表
    installed = get_installed_skills()

    # 合并结果
    data = merge_results(skills_sh_results, clawhub_results, installed)
    data["query"] = args.query

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_output(data, args.query))


if __name__ == "__main__":
    main()
