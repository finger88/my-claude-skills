---
name: web-content-extraction
description: 8-layer toolkit for extracting web content from restricted or dynamic domains. Use when WebFetch fails, user needs content from JavaScript-heavy pages, or when dealing with blocked domains. Provides fallback strategies from Brave Summary (L0) → jina.ai (L1) → requests (L2) → curl (L3) → Playwright (L4), plus Brave Search discovery mode. Now includes executable scripts for automated extraction.
---

# Web Content Extraction Skill（网页内容提取技能）

一个完整的网页内容获取方案矩阵，针对不同类型网页提供最优提取策略。新增 **Brave Search** 支持：搜索发现 + 快速摘要。

---

## 🚀 快速开始（推荐）

现在本技能包含**可执行脚本**，无需手动编写代码：

### 方法1：使用 extract.py（自动选择最佳策略）

```bash
# ===== 提取模式（URL → 内容）=====

# 自动提取（智能降级：brave → jina → requests → curl → playwright）
python scripts/extract.py "https://example.com/article"

# 使用 Brave 快速摘要（需 BRAVE_API_KEY，速度最快）
python scripts/extract.py "https://example.com/article" --method brave

# Markdown 输出（保存到 ~/Downloads/，自动根据标题生成文件名）
python scripts/extract.py "https://example.com/article" --format md

# Markdown 输出 + 指定路径
python scripts/extract.py "https://example.com/article" --format md -o ~/Documents/my-article.md

# ===== 搜索模式（关键词 → URL 列表）=====

# Brave Search 搜索发现（需 BRAVE_API_KEY）
python scripts/extract.py --search "Claude Code 最佳实践"

# 搜索并保存结果
python scripts/extract.py --search "AI Agent 架构" -o search_results.json
```

**环境变量配置：**
```bash
# 配置 Brave API Key（用于 L0 摘要和搜索模式）
export BRAVE_API_KEY="your-brave-api-key"
```

**输出格式（JSON）：**
```json
{
  "success": true,
  "method": "requests",
  "title": "文章标题",
  "author": "作者名",
  "content": "正文内容...",
  "url": "最终URL"
}
```

**输出格式（Markdown）：**
```markdown
# 文章标题

**作者**: 作者名 | **来源**: https://example.com/article | **提取方式**: requests

---

正文内容...
```

### 方法2：安装依赖（首次使用）

```bash
bash scripts/setup.sh
```

---

## 📋 使用决策流程

---

## 🔧 可用脚本

| 脚本 | 用途 | 路径 |
|------|------|------|
| `extract.py` | 统一提取接口，自动降级 | `scripts/extract.py` |
| `setup.sh` | 安装依赖 | `scripts/setup.sh` |

---

## 8层提取策略详解

### 各层适用场景与实战指南

| 层级 | 方法 | 核心优势 | 最佳适用场景 | 典型成功案例 | 常见失败场景 |
|:----:|------|---------|-------------|-------------|-------------|
| **L0** | **Brave** | **元信息验证**：速度极快（<1s）、验证 URL 有效性、获取标题 | 热门网页、快速验证 URL 是否存在 | 知乎文章标题获取、链接有效性检查 | 摘要过短（<500字）时自动降级，冷门页面 |
| **L1** | **jina.ai** | **完整内容提取**：免费免 API key、绕过付费墙、能抓 X/Twitter | 微信公众号、付费墙内容、社交媒体、个人博客 | 微信公众号文章、Every.to 付费内容 | 需要登录态的页面、重度 JS 渲染页面 |
| **L2** | **requests** | 结构化提取（标题/作者/正文分离）、可定制化 | 需要提取元信息的页面、标准化网站、微信公众号 | 标准博客、新闻站、公众号 | Cloudflare 拦截、复杂反爬 |
| **L3** | **curl** | 轻量快速、无需 Python 依赖、某些环境唯一选择 | 简单静态页面、服务器环境只有 curl | 简单的 HTML 页面 | 知乎等强反爬站点、JS 渲染页面 |
| **L4** | **Playwright** | 执行 JavaScript、模拟真实浏览器、最后兜底 | React/Vue 单页应用、动态加载内容 | SPA 站点、需要滚动加载的页面 | 验证码拦截、需要登录态、极度复杂的反爬 |
| **搜索** | **Brave Search** | 从关键词到 URL 列表、发现未知内容 | 只有主题没有具体 URL 时 | 论文搜索、资料收集 | - |

### 选择策略

**场景1：你有具体 URL**
- 配置 `BRAVE_API_KEY` → 优先 L0（最快）
- 未配置 → 从 L1 开始自动降级

**场景2：只有主题/关键词**
- 使用 `--search` 搜索发现，获取 URL 后再进入提取流程

**场景3：特定网站**
- 微信公众号 → L1 jina.ai（最强）
- 知乎 → L0 Brave（索引已收录）或 L4 Playwright
- 小红书/抖音 → L4 Playwright（截图+视觉提取）
- 付费内容（Every.to/Substack）→ L1 jina.ai（绕过付费墙）

---

## 快速决策表

### 提取模式（URL → 内容）

| 层级 | 工具 | 类型 | 适用场景 | 特点 | 需 API Key |
|:----:|------|------|---------|------|:----------:|
| L0 | **Brave** | 云服务 | 已知 URL 快速摘要 | 速度最快、有全球 CDN | ✅ |
| L1 | **jina.ai** | 云服务 | 快速提取大多数网页 | 免费、免API key、绕过付费墙 | ❌ |
| L2 | **requests** | 脚本 | 结构化提取（标题/作者/正文） | 最灵活，可定制化 | ❌ |
| L3 | **curl** | 命令行 | 备用方案，绕过部分限制 | 轻量快速 | ❌ |
| L4 | **Playwright** | 脚本 | JavaScript动态渲染页面 | 资源占用高，兜底方案 | ❌ |

### 搜索模式（关键词 → URL 列表）

| 模式 | 工具 | 用途 | 需 API Key |
|------|------|------|:----------:|
| 搜索发现 | **Brave Search** | 从关键词发现相关 URL | ✅ |

### 其他工具

| 工具 | 类型 | 适用场景 | 备注 |
|------|------|---------|------|
| **WebFetch** | 内置工具 | Claude内置提取 | 最简单，但受限于平台 |
| **WebSearch** | 内置工具 | 搜索+获取摘要 | 无法获取全文 |
| **wget** | 命令行 | 整站下载 | 递归下载 |

### 使用顺序建议

**自动模式（配置 BRAVE_API_KEY 后）：**

```
尝试内置工具（WebFetch）
    ↓ 失败或受限
使用 Brave（L0 - 快速摘要，适合热门网页）
    ↓ 未收录或摘要不足
使用 jina.ai（L1 - 免费快速，绕过付费墙）
    ↓ 需要结构化信息（标题/作者/正文分离）
使用 requests（L2 - 本地解析，最灵活）
    ↓ 简单备用方案
使用 curl（L3 - 轻量快速）
    ↓ 需要执行JS
使用 Playwright（L4 - 动态渲染兜底）
```

**未配置 BRAVE_API_KEY：**

```
从 L1 jina.ai 开始自动降级
```

---

## 执行步骤

### Step 1: 尝试 WebFetch（最简单）

如果用户提供 URL，首先尝试 WebFetch 获取内容。

**成功？** → 完成任务
**失败（安全限制）？** → 进入 Step 2

---

### Step 2: 使用 extract.py 脚本（推荐）

直接调用封装好的提取脚本：

```bash
# 自动模式（推荐）- 按 L0→L1→L2→L3 自动降级
python scripts/extract.py "<URL>" -o result.json

# 指定使用 jina.ai（最快，适合大多数网页）
python scripts/extract.py "<URL>" --method jina

# 指定使用 requests（需要结构化信息时）
python scripts/extract.py "<URL>" --method requests
```

**脚本特点：**
- ✅ **8层自动降级**：brave → jina → requests → curl → playwright
- ✅ **L0 Brave 摘要**：配置 API key 后速度最快，适合热门网页
- ✅ **搜索发现模式**：`--search` 关键词直接获取相关 URL 列表
- ✅ **L1 jina.ai**：免费、免 API key、绕过付费墙
- ✅ **双输出格式**：JSON（结构化数据）或 Markdown（可读文档）
- ✅ Markdown 模式自动保存到 `~/Downloads/`（基于文章标题生成文件名）
- ✅ 自动处理编码问题（UTF-8/GBK）
- ✅ 内置多种正文提取策略（含微信公众号优化选择器）

**解析结果：**
```bash
# 读取结果
cat result.json

# 提取标题
python -c "import json; d=json.load(open('result.json')); print(d['title'])"

# 提取正文
python -c "import json; d=json.load(open('result.json')); print(d['content'])"
```

**脚本失败？** → 进入 Step 3 手动处理

---

### Step 3: 手动选择工具（备用方案）

当脚本无法满足需求时，根据网页类型选择工具：

**技术判断：**
- 网页是否需要登录？→ **Python requests + Cookie**
- 内容是否为 JavaScript 动态生成？
  - 源代码中没有 → **Playwright**
  - 源代码中有 → **curl** 或 **Python requests**
- 网页编码是什么？
  - GB2312/GBK → 需要 `iconv -f gb2312 -t utf-8`

具体命令和代码见 [references/toolkit.md](references/toolkit.md)

---

### Step 4: 特殊情况处理

| 问题 | 解决方案 |
|------|---------|
| 编码问题（中文乱码） | extract.py 已内置 UTF-8/GBK 自动检测 |
| IP 被封/频率限制 | 添加延时或使用代理 |
| 需要登录/Cookie | 修改 scripts/extract.py 添加 Session |
| 遇到验证码 | 需人工干预或使用打码平台 |
| 提取内容为空 | 尝试 `--method playwright` |

**扩展 extract.py：**
如需添加新的提取策略，编辑 `scripts/extract.py`：
- 添加新方法函数（如 `extract_with_new_method`）
- 在 `extract_url()` 的 methods 列表中加入新方法
- 测试并提交更新

详细处理方案见 [references/toolkit.md](references/toolkit.md)

---

## 工具选择速查

### 提取场景（URL → 内容）

| 如果你需要... | 使用工具 | 备选工具 | 需 API Key |
|-------------|---------|---------|:----------:|
| 已知 URL 快速摘要（最快） | **Brave** (L0) | jina.ai | ✅ |
| 绕过付费墙/抓推特 | **jina.ai** (L1) | requests | ❌ |
| 提取结构化信息（标题/作者/正文） | **requests** (L2) | jina.ai | ❌ |
| 绕过简单反爬 | **curl** (L3) | requests | ❌ |
| JavaScript 动态页面 | **Playwright** (L4) | - | ❌ |

### 搜索场景（关键词 → URL）

| 如果你需要... | 使用工具 | 需 API Key |
|-------------|---------|:----------:|
| 从关键词发现相关文章 | **Brave Search** (`--search`) | ✅ |

### 其他工具

| 如果你需要... | 使用工具 | 备选工具 |
|-------------|---------|---------|
| 快速获取单个网页全文 | **WebFetch** | jina.ai |
| 搜索信息 | **WebSearch** | Brave Search |
| 整站备份 | **wget** | Python+requests |

---

## 失败处理流程

### 自动流程（使用 extract.py）

**提取模式（URL → 内容）：**

```
WebFetch 失败
    ↓
python scripts/extract.py "URL" --method auto
    ↓
├── brave 尝试 ──→ 成功 ✅ （L0：快速摘要，需 BRAVE_API_KEY）
│
├── jina.ai 尝试 ──→ 成功 ✅ （L1：免费快速，适合大多数网页）
│
├── requests 尝试 ──→ 成功 ✅ （L2：结构化提取，需作者/标题信息时）
│
├── curl 尝试 ──→ 成功 ✅ （L3：备用方案）
│
├── playwright 尝试 ──→ 成功 ✅ （L4：JS动态页面，兜底方案）
│
└── 全部失败 ──→ 返回错误信息 ❌
```

**搜索模式（关键词 → URL 列表）：**

```
python scripts/extract.py --search "关键词"
    ↓
└── Brave Search API ──→ 返回搜索结果列表 ✅
```

### 手动流程（extract.py 失败时）

```
extract.py 失败
    ↓
查看 result.json 中的 error 详情
    ↓
根据错误类型选择：
    - 编码问题 → 修改 extract.py 的 encoding 处理
    - 需要登录 → 添加 Cookie/Session
    - JS 渲染失败 → 调整 Playwright 等待时间
    - 反爬机制 → 添加代理/延时
```

---

## 参考资源

- **详细工具手册**: [references/toolkit.md](references/toolkit.md) - 包含 curl、Python、Playwright、wget 的完整命令和代码示例
- **实战案例**: 见原技能文档 `skills/web-content-extraction-cases.md`（如存在）

---

## 更新日志

- **2026-02-03 v1.0**: 初始版本，整合 curl/Python/Playwright/wget 方案
- **2026-02-03 v1.1**: 添加内置工具和 MCP 工具，形成完整 7 层工具矩阵
- **2026-02-09 v1.2**: 重构为渐进式披露结构，拆分详细内容到 references/
- **2026-02-15 v2.0**: 🎉 **重大更新 - 增加可执行脚本层**
  - 新增 `scripts/extract.py`: 统一提取接口，自动策略降级
  - 新增 `scripts/setup.sh`: 一键安装依赖
  - 内置编码自动检测（UTF-8/GBK）
  - JSON 结构化输出，便于其他 skills 调用
  - 支持微信公众号等受限域名提取
- **2026-02-26 v2.1**: 🚀 **添加 jina.ai L0 层**
  - 将 jina.ai Reader 作为第 0 层快速提取方案
  - 自动降级顺序：jina → requests → curl → playwright
  - 免费、免 API key、绕过付费墙、返回干净 Markdown
  - 对标 OpenClaw 中推荐的 jina.ai 配置方案
- **2026-02-26 v2.2**: 📝 **添加 Markdown 输出模式**
  - 新增 `--format md` 参数，支持输出可读 Markdown 文件
  - 自动生成文件名（基于文章标题或域名）
  - Markdown 格式包含标题、元信息、正文，适合直接阅读
- **2026-02-26 v3.0**: 🔍 **集成 Brave Search API**
  - 新增 L0 层 **Brave 快速摘要**：配置 API key 后速度最快
  - 新增 **搜索发现模式**：`--search` 参数从关键词获取 URL 列表
  - 自动降级链更新：brave → jina → requests → curl → playwright
  - 通过 `BRAVE_API_KEY` 环境变量配置
