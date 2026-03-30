#!/usr/bin/env python3
"""
Claude Skills 标准检查工具
每次操作前读取 .skillrc 并执行必要检查

用法:
    python check-standard.py              # 执行所有检查
    python check-standard.py --fix        # 尝试修复发现的问题
    python check-standard.py --pre-op     # 仅执行预操作检查
"""

import yaml
import json
import os
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fixable: bool = False
    fix_command: Optional[str] = None


class SkillStandardChecker:
    """Claude Skills 标准检查器"""

    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or os.path.expanduser("~/my-claude-skills"))
        self.config_path = self.repo_path / ".skillrc"
        self.config = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_config(self) -> bool:
        """加载 .skillrc 配置文件"""
        if not self.config_path.exists():
            self.errors.append(f"配置文件不存在: {self.config_path}")
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✓ 已加载配置文件: {self.config_path}")
            print(f"  版本: {self.config.get('metadata', {}).get('version', 'unknown')}")
            return True
        except Exception as e:
            self.errors.append(f"加载配置文件失败: {e}")
            return False

    def get_junction_target(self) -> Path:
        """获取 Junction 目标目录"""
        path = self.config['directory_structure']['junction_target']['path']
        return Path(os.path.expanduser(path.replace('~', str(Path.home()))))

    def get_git_repo(self) -> Path:
        """获取 Git 仓库目录"""
        path = self.config['directory_structure']['git_repository']['path']
        return Path(os.path.expanduser(path.replace('~', str(Path.home()))))

    def is_junction(self, path: Path) -> bool:
        """检查路径是否是 Windows Junction（仅在 CMD 中有效）"""
        try:
            result = subprocess.run(
                ['cmd', '/c', 'dir', '/a', str(path.parent)],
                capture_output=True,
                text=True
            )
            # 在输出中查找 <JUNCTION>
            for line in result.stdout.split('\n'):
                if path.name in line and '<JUNCTION>' in line:
                    return True
            return False
        except Exception:
            return False

    def check_junction_integrity(self) -> List[CheckResult]:
        """检查 Junction 链接完整性"""
        results = []
        junction_dir = self.get_junction_target()
        git_repo = self.get_git_repo()

        print(f"\n[检查] Junction 链接完整性")
        print(f"  Junction 目录: {junction_dir}")
        print(f"  Git 仓库: {git_repo}")

        if not junction_dir.exists():
            results.append(CheckResult(
                name="junction_dir_exists",
                passed=False,
                message=f"Junction 目录不存在: {junction_dir}",
                fixable=False
            ))
            return results

        # 获取 Git 仓库中的 skills
        git_skills = set()
        if git_repo.exists():
            for item in git_repo.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name != 'docs':
                    # 检查是否是 skill（有 SKILL.md）
                    if (item / "SKILL.md").exists() or (item / "skill.yaml").exists():
                        git_skills.add(item.name)

        # 获取 Junction 目录中的内容
        junction_items = {}
        if junction_dir.exists():
            for item in junction_dir.iterdir():
                junction_items[item.name] = item

        # 检查 1: 所有 Git 中的 skill 都应该有 Junction
        for skill in git_skills:
            if skill not in junction_items:
                results.append(CheckResult(
                    name=f"junction_exists_{skill}",
                    passed=False,
                    message=f"Skill '{skill}' 在 Git 仓库中，但缺少 Junction 链接",
                    fixable=True,
                    fix_command=f'MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\\Users\\HONOR\\.claude\\skills\\{skill} C:\\Users\\HONOR\\my-claude-skills\\{skill}"'
                ))
            else:
                # 检查是否是 Junction
                is_junc = self.is_junction(junction_items[skill])
                if not is_junc:
                    results.append(CheckResult(
                        name=f"junction_type_{skill}",
                        passed=False,
                        message=f"'{skill}' 是普通目录而非 Junction 链接",
                        fixable=True,
                        fix_command=f'rm -rf ~/.claude/skills/{skill} && MSYS_NO_PATHCONV=1 cmd /c "mklink /J C:\\Users\\HONOR\\.claude\\skills\\{skill} C:\\Users\\HONOR\\my-claude-skills\\{skill}"'
                    ))
                else:
                    results.append(CheckResult(
                        name=f"junction_type_{skill}",
                        passed=True,
                        message=f"'{skill}' Junction 链接正确"
                    ))

        # 检查 2: Junction 目录中不应该有 Git 外的项目（除了已知的本地 skills）
        for name, path in junction_items.items():
            if name not in git_skills:
                # 检查是否是本地开发 skill
                if name in ['lesson-miner-workspace', 'skill-creator-workspace']:
                    self.warnings.append(f"'{name}' 是开发工作区，不计入标准检查")
                else:
                    results.append(CheckResult(
                        name=f"orphaned_junction_{name}",
                        passed=False,
                        message=f"'{name}' 在 Junction 目录中但不在 Git 仓库（可能是孤儿链接或本地 skill）",
                        fixable=True,
                        fix_command=f'rmdir ~/.claude/skills/{name}'
                    ))

        return results

    def check_git_sync_status(self) -> List[CheckResult]:
        """检查 Git 同步状态"""
        results = []
        git_repo = self.get_git_repo()

        print(f"\n[检查] Git 同步状态")

        try:
            # 检查是否有未提交的修改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=git_repo,
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                changes = result.stdout.strip().split('\n')
                results.append(CheckResult(
                    name="git_uncommitted",
                    passed=False,
                    message=f"有 {len(changes)} 个未提交的修改",
                    fixable=True,
                    fix_command="cd ~/my-claude-skills && git add -A && git commit -m 'Sync changes'"
                ))
            else:
                results.append(CheckResult(
                    name="git_uncommitted",
                    passed=True,
                    message="Git 工作区干净"
                ))

            # 检查远程更新
            subprocess.run(['git', 'fetch'], cwd=git_repo, capture_output=True)
            result = subprocess.run(
                ['git', 'log', 'HEAD..origin/main', '--oneline'],
                cwd=git_repo,
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                commits = result.stdout.strip().split('\n')
                results.append(CheckResult(
                    name="git_remote_updates",
                    passed=False,
                    message=f"远程有 {len(commits)} 个提交需要拉取",
                    fixable=True,
                    fix_command="cd ~/my-claude-skills && git pull"
                ))
            else:
                results.append(CheckResult(
                    name="git_remote_updates",
                    passed=True,
                    message="已与远程同步"
                ))

        except Exception as e:
            results.append(CheckResult(
                name="git_check",
                passed=False,
                message=f"Git 检查失败: {e}",
                fixable=False
            ))

        return results

    def print_summary(self, results: List[CheckResult]):
        """打印检查结果摘要"""
        print("\n" + "=" * 60)
        print("检查结果摘要")
        print("=" * 60)

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        fixable = sum(1 for r in results if not r.passed and r.fixable)

        print(f"总计: {len(results)} 项检查")
        print(f"通过: {passed} ✓")
        print(f"失败: {failed} ✗")
        if fixable > 0:
            print(f"可修复: {fixable} ⚡")

        if failed > 0:
            print("\n失败项详情:")
            for r in results:
                if not r.passed:
                    print(f"  ✗ {r.name}: {r.message}")
                    if r.fixable and r.fix_command:
                        print(f"    修复命令: {r.fix_command}")

        if self.warnings:
            print("\n警告:")
            for w in self.warnings:
                print(f"  ⚠ {w}")

        return failed == 0

    def run_all_checks(self, pre_op_only: bool = False) -> bool:
        """运行所有检查"""
        print("=" * 60)
        print("Claude Skills 标准检查")
        print("=" * 60)

        if not self.load_config():
            return False

        all_results = []

        # 预操作检查
        if pre_op_only or True:  # 默认总是执行
            all_results.extend(self.check_junction_integrity())
            all_results.extend(self.check_git_sync_status())

        return self.print_summary(all_results)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Claude Skills 标准检查工具")
    parser.add_argument("--fix", action="store_true", help="尝试修复发现的问题")
    parser.add_argument("--pre-op", action="store_true", help="仅执行预操作检查")
    parser.add_argument("--repo", type=str, help="Git 仓库路径（默认 ~/my-claude-skills）")
    args = parser.parse_args()

    checker = SkillStandardChecker(repo_path=args.repo)
    success = checker.run_all_checks(pre_op_only=args.pre_op)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
