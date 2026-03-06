# 技能生态系统对比

## 概述

| 特性 | ClawHub | Skills.sh |
|------|---------|-----------|
| **定位** | 技能商店（Shop） | 技能包管理器（Package Manager） |
| **托管方式** | 中心化平台 | GitHub 仓库 |
| **安装命令** | `npx clawhub install <name>` | `npx skills add <owner/repo@skill>` |
| **安装路径** | `~/.claude/skills/` | `~/.agents/skills/` |
| **规模** | ~11,000+ skills | ~100-500 skills |
| **主要来源** | 社区上传 | GitHub 组织/个人 |

---

## ClawHub 详解

### 特点
- **即装即用**: 单命令安装，无需关心来源
- **数量庞大**: 社区活跃，覆盖面广
- **质量参差**: 需要自己甄别
- **Web 界面**: https://clawhub.ai 可浏览

### 使用场景
- 需要快速找到一个功能
- 不确定具体要哪个，想浏览
- 使用 LJG 等社区知名技能

### 已知优质技能
| 技能 | 作者 | 用途 |
|------|------|------|
| ljg-xray-article | @ljg | 文章 X-ray 分析 |
| ljg-clip | @ljg | 内容剪藏 |
| skill-creator | Anthropic | 创建技能 |
| web-content-extraction | @user | 网页提取 |

---

## Skills.sh 详解

### 特点
- **版本控制**: 基于 Git，可回滚
- **代码可见**: 都是 GitHub 公开仓库
- **安全扫描**: 安装时自动检查
- **组织背书**: Vercel Labs、Google Labs 等官方维护

### 使用场景
- 需要高质量、经过验证的技能
- 关心代码安全性和来源
- 需要版本管理和更新

### 已知优质技能
| 技能 | 作者 | 用途 |
|------|------|------|
| vercel-react-best-practices | Vercel Labs | React 最佳实践 |
| gog | @steipete | Google Workspace CLI |
| ontology | @oswalpalash | 知识图谱 |
| datetime-tool | @openakita | 日期时间工具 |

---

## 如何选择

### 选 ClawHub 当：
- 功能需求明确，想快速尝试
- 需要 LJG 等社区知名工具
- 搜索时发现 clawhub 有而 skills.sh 没有

### 选 Skills.sh 当：
- 技能来自可信组织（Vercel、Google）
- 需要代码审查和安全保障
- 技能频繁更新，需要版本管理

### 选 Skill Hub（统一）当：
- 不想关心来源，只想解决问题
- 需要跨生态搜索和比较
- 想要基于任务的智能推荐

---

## 技术细节

### 目录结构对比

```
# ClawHub
~/.claude/skills/
├── ljg-xray-article/
│   ├── SKILL.md
│   └── references/
└── skill-creator/
    ├── SKILL.md
    └── scripts/

# Skills.sh
~/.agents/skills/
├── datetime-tool/
│   ├── SKILL.md
│   └── scripts/
└── ontology/
    ├── SKILL.md
    └── references/
```

### 安装机制对比

| 方面 | ClawHub | Skills.sh |
|------|---------|-----------|
| 下载方式 | 平台 CDN | Git clone |
| 版本管理 | 平台维护 | Git 标签 |
| 更新检查 | `npx clawhub check` | `npx skills check` |
| 卸载 | 删除目录 | `npx skills remove` |

---

## 未来趋势

### 短期
- 两个生态继续独立发展
- Skill Hub 作为统一入口

### 长期可能
- 协议标准化（统一 skill 格式）
- 交叉索引（互相引用）
- 统一注册中心（类似 npm 之于 Node）

---

## 相关链接

- ClawHub: https://clawhub.ai
- Skills.sh: https://skills.sh
- Skill Hub: 本项目统一接口
