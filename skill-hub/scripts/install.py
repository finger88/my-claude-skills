#!/usr/bin/env python3
"""
统一技能安装脚本 - 自动识别生态系统并安装

用法:
    python install.py <skill-identifier>
    python install.py datetime-tool                              # clawhub
    python install.py openakita/openakita@datetime-tool          # skills.sh
    python install.py https://github.com/user/repo.git           # GitHub (列出可用技能)
    python install.py https://github.com/user/repo.git --skill x # GitHub (指定技能)

支持格式:
    - clawhub: skill-name
    - skills.sh: owner/repo@skill-name
    - github: https://github.com/user/repo.git 或 git@github.com:user/repo.git
"""

import argparse
import subprocess
import sys
import re
import io
import os
import shutil
import tempfile
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 本地技能管理路径
SKILLS_REPO = Path.home() / "my-claude-skills"
SKILLS_LOAD = Path.home() / ".claude" / "skills"


def detect_ecosystem(identifier: str) -> str:
    """识别技能标识符属于哪个生态"""
    # GitHub URL
    if re.match(r'^https?://github\.com/', identifier) or re.match(r'^git@github\.com:', identifier):
        return "github"
    # skills.sh 格式: owner/repo@skill-name
    if re.match(r'^[\w-]+/[\w-]+@[\w-]+$', identifier):
        return "skills.sh"
    # clawhub 格式: skill-name (简单名称)
    elif re.match(r'^[\w-]+$', identifier):
        return "clawhub"
    else:
        return "unknown"


def scan_skills_in_repo(repo_dir: str) -> list:
    """扫描仓库中包含 SKILL.md 的子目录，返回 [(name, description), ...]"""
    skills = []
    for entry in sorted(os.listdir(repo_dir)):
        skill_md = os.path.join(repo_dir, entry, "SKILL.md")
        if os.path.isfile(skill_md):
            desc = ""
            try:
                with open(skill_md, "r", encoding="utf-8") as f:
                    content = f.read()
                # 提取 YAML frontmatter 中的 description
                m = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if m:
                    fm = m.group(1)
                    dm = re.search(r'description:\s*["\']?(.+?)(?:["\']?\s*$|\n)', fm, re.MULTILINE)
                    if dm:
                        desc = dm.group(1).strip().strip('"').strip("'")
                    else:
                        # 多行 description (| 或 >)
                        dm = re.search(r'description:\s*[|>]\s*\n((?:\s+.+\n?)+)', fm)
                        if dm:
                            lines = dm.group(1).strip().split('\n')
                            desc = lines[0].strip()
            except Exception:
                pass
            skills.append((entry, desc))
    return skills


def install_github(url: str, skill_name: str = None) -> bool:
    """从 GitHub 仓库安装技能到本地 Git 仓库"""
    print(f"📦 从 GitHub 安装技能: {url}")
    print()

    # 1. Clone 到临时目录
    tmp_dir = tempfile.mkdtemp(prefix="skill-github-")
    try:
        print("⏳ 克隆仓库...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, tmp_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"❌ 克隆失败: {result.stderr.strip()}")
            return False

        # 2. 扫描可用技能
        available = scan_skills_in_repo(tmp_dir)
        if not available:
            print("❌ 仓库中未找到包含 SKILL.md 的技能目录")
            return False

        # 3. 选择要安装的技能
        if skill_name:
            # 指定了技能名
            matches = [s for s in available if s[0] == skill_name]
            if not matches:
                print(f"❌ 未找到技能: {skill_name}")
                print(f"   可用技能: {', '.join(s[0] for s in available)}")
                return False
            to_install = [matches[0]]
        else:
            # 未指定，列出所有可用技能供选择
            print(f"📋 仓库中共 {len(available)} 个可用技能:\n")
            already_installed = []
            for i, (name, desc) in enumerate(available, 1):
                installed_mark = ""
                if (SKILLS_REPO / name).exists():
                    installed_mark = " ★ 已安装"
                    already_installed.append(name)
                print(f"  {i}. {name}{installed_mark}")
                if desc:
                    print(f"     {desc}")
            print()
            # 脚本模式下列出后退出，让调用方（Claude）决定
            print("💡 使用 --skill <name> 指定要安装的技能")
            print(f"   例: python install.py {url} --skill {available[0][0]}")
            return True  # 列出成功，非错误

        # 4. 执行安装
        for (name, desc) in to_install:
            print(f"📥 安装技能: {name}")

            src = os.path.join(tmp_dir, name)
            dst = SKILLS_REPO / name
            link = SKILLS_LOAD / name

            # 检查是否已安装
            if dst.exists():
                print(f"   ⚠️ 已存在，将覆盖: {dst}")
                shutil.rmtree(dst)

            # 复制到 Git 仓库
            shutil.copytree(src, dst)
            print(f"   ✅ 复制到仓库: {dst}")

            # npm install (如有 package.json)
            pkg_json = dst / "package.json"
            if pkg_json.exists():
                print("   ⏳ 安装 npm 依赖...")
                npm_result = subprocess.run(
                    "npm install",
                    cwd=str(dst), shell=True,
                    capture_output=True, text=True, timeout=120
                )
                if npm_result.returncode == 0:
                    print("   ✅ npm 依赖已安装")
                    # 检查是否需要 playwright chromium
                    try:
                        with open(pkg_json, "r", encoding="utf-8") as f:
                            if "playwright" in f.read():
                                print("   ⏳ 安装 Playwright Chromium...")
                                pw_result = subprocess.run(
                                    "npx playwright install chromium",
                                    cwd=str(dst), shell=True,
                                    capture_output=True, text=True, timeout=300
                                )
                                if pw_result.returncode == 0:
                                    print("   ✅ Playwright Chromium 已安装")
                                else:
                                    print(f"   ⚠️ Playwright 安装失败: {pw_result.stderr.strip()[:100]}")
                    except Exception:
                        pass
                else:
                    print(f"   ⚠️ npm install 失败: {npm_result.stderr.strip()[:100]}")

            # 创建 junction (Windows 不需要管理员权限，与现有技能一致)
            if link.exists() or link.is_symlink():
                if link.is_dir() and not link.is_symlink():
                    shutil.rmtree(link)
                else:
                    link.unlink()
            if sys.platform == 'win32':
                subprocess.run(
                    ['cmd', '/c', 'mklink', '/J', str(link), str(dst)],
                    capture_output=True, text=True
                )
            else:
                os.symlink(str(dst), str(link))
            print(f"   ✅ 创建链接: {link} -> {dst}")

        # 5. Git commit + push
        print()
        print("⏳ 提交到 Git 仓库...")
        names = [n for n, _ in to_install]
        subprocess.run(["git", "add"] + names, cwd=str(SKILLS_REPO),
                       capture_output=True, text=True)
        commit_msg = f"Add skill: {', '.join(names)} (from GitHub)"
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(SKILLS_REPO), capture_output=True, text=True
        )
        if commit_result.returncode == 0:
            print(f"   ✅ Git commit: {commit_msg}")
            push_result = subprocess.run(
                ["git", "push"], cwd=str(SKILLS_REPO),
                capture_output=True, text=True, timeout=30
            )
            if push_result.returncode == 0:
                print("   ✅ Git push 成功")
            else:
                print(f"   ⚠️ Git push 失败: {push_result.stderr.strip()[:100]}")
        else:
            print(f"   ⚠️ Git commit 跳过（无变更或失败）")

        return True

    except subprocess.TimeoutExpired:
        print("❌ 操作超时")
        return False
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


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
    parser.add_argument("identifier", help="Skill identifier (name, owner/repo@skill, or GitHub URL)")
    parser.add_argument("--ecosystem", "-e", choices=["clawhub", "skills.sh", "github", "auto"],
                        default="auto", help="Ecosystem (auto-detect by default)")
    parser.add_argument("--skill", "-s", default=None,
                        help="Skill name to install (for GitHub repos with multiple skills)")

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
            print("  - github: https://github.com/user/repo.git")
            sys.exit(1)
    else:
        ecosystem = args.ecosystem

    print(f"🔍 检测到生态系统: {ecosystem}")
    print()

    # 执行安装
    if ecosystem == "github":
        success = install_github(args.identifier, args.skill)
    elif ecosystem == "clawhub":
        success = install_clawhub(args.identifier)
    else:
        success = install_skills_sh(args.identifier)

    if success:
        print()
        print(f"✅ 操作完成: {args.identifier}")
    else:
        print()
        print(f"❌ 操作失败: {args.identifier}")
        sys.exit(1)


if __name__ == "__main__":
    main()
