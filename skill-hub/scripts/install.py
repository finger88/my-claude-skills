#!/usr/bin/env python3
"""
统一技能安装脚本 - 自动识别生态系统并安装

用法:
    python install.py <skill-identifier>
    python install.py datetime-tool              # clawhub
    python install.py openakita/openakita@datetime-tool  # skills.sh

支持格式:
    - clawhub: skill-name
    - skills.sh: owner/repo@skill-name
"""

import argparse
import subprocess
import sys
import re
import io

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def detect_ecosystem(identifier: str) -> str:
    """识别技能标识符属于哪个生态"""
    # skills.sh 格式: owner/repo@skill-name
    if re.match(r'^[\w-]+/[\w-]+@[\w-]+$', identifier):
        return "skills.sh"
    # clawhub 格式: skill-name (简单名称)
    elif re.match(r'^[\w-]+$', identifier):
        return "clawhub"
    else:
        return "unknown"


def install_clawhub(skill_name: str) -> bool:
    """安装 clawhub 技能"""
    print(f"📦 安装 clawhub 技能: {skill_name}")
    print(f"   命令: npx clawhub install {skill_name}")
    print()

    try:
        result = subprocess.run(
            ["npx", "clawhub", "install", skill_name],
            capture_output=False,  # 显示实时输出
            text=True,
            timeout=120
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ 安装超时")
        return False
    except FileNotFoundError:
        print("❌ 未找到 clawhub CLI")
        print("   请确保已安装: npm install -g clawhub")
        return False
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False


def install_skills_sh(skill_id: str) -> bool:
    """安装 skills.sh 技能"""
    print(f"📦 安装 skills.sh 技能: {skill_id}")
    print(f"   命令: npx skills add {skill_id} -g -y")
    print()

    try:
        result = subprocess.run(
            ["npx", "skills", "add", skill_id, "-g", "-y"],
            capture_output=False,
            text=True,
            timeout=120
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ 安装超时")
        return False
    except FileNotFoundError:
        print("❌ 未找到 skills CLI")
        print("   请确保 Node.js 和 npm 已安装")
        return False
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Unified Skill Installer")
    parser.add_argument("identifier", help="Skill identifier (name or owner/repo@skill)")
    parser.add_argument("--ecosystem", "-e", choices=["clawhub", "skills.sh", "auto"],
                        default="auto", help="Ecosystem (auto-detect by default)")

    args = parser.parse_args()

    # 检测生态
    if args.ecosystem == "auto":
        ecosystem = detect_ecosystem(args.identifier)
        if ecosystem == "unknown":
            print(f"❌ 无法识别技能标识符格式: {args.identifier}")
            print()
            print("支持的格式:")
            print("  - clawhub: skill-name (如: datetime-tool)")
            print("  - skills.sh: owner/repo@skill-name (如: openakita/openakita@datetime-tool)")
            sys.exit(1)
    else:
        ecosystem = args.ecosystem

    print(f"🔍 检测到生态系统: {ecosystem}")
    print()

    # 执行安装
    if ecosystem == "clawhub":
        success = install_clawhub(args.identifier)
    else:
        success = install_skills_sh(args.identifier)

    if success:
        print()
        print(f"✅ 技能安装成功: {args.identifier}")
        print()
        print("使用技能:")
        print("  1. 直接说出技能相关的请求")
        print("  2. 或运行: python ~/.claude/skills/skill-hub/scripts/list.py")
    else:
        print()
        print(f"❌ 技能安装失败: {args.identifier}")
        sys.exit(1)


if __name__ == "__main__":
    main()
