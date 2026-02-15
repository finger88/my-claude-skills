---
name: web-content-extraction
description: 7-layer toolkit for extracting web content from restricted or dynamic domains. Use when WebFetch fails, user needs content from JavaScript-heavy pages, or when dealing with blocked domains. Provides fallback strategies from WebFetch to Playwright. Now includes executable scripts for automated extraction.
---

# Web Content Extraction Skill（网页内容提取技能）

一个完整的网页内容获取方案矩阵，针对不同类型网页提供最优提取策略。

---

## 🚀 快速开始（推荐）

现在本技能包含**可执行脚本**，无需手动编写代码：

### 方法1：使用 extract.py（自动选择最佳策略）

```bash
# 自动提取（智能降级：requests → curl → playwright）
python scripts/extract.py "https://example.com/article"

# 输出到文件
python scripts/extract.py "https://example.com/article" -o result.json

# 指定方法
python scripts/extract.py "https://example.com/article" --method requests
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

## 快速决策表

| 优先级 | 工具 | 类型 | 适用场景 | 备注 |
|:------:|------|------|---------|------|
| 1 | **WebFetch** | 内置工具 | 单个网页全文提取 | 最简单，首选 |
| 2 | **WebSearch** | 内置工具 | 搜索+获取摘要 | 无法获取全文 |
| 3 | **Brave MCP** | MCP工具 | 搜索+隐私保护 | 需配置 |
| 4 | **curl** | 命令行 | 静态页面/快速测试 | 需处理编码 |
| 5 | **Python requests** | 脚本 | 结构化提取 | 最灵活 |
| 6 | **Playwright** | 脚本 | 动态SPA页面 | 资源占用高 |
| 7 | **wget** | 命令行 | 整站下载 | 递归下载 |

### 使用顺序建议

```
尝试内置工具（WebFetch）
    ↓ 失败或受限
尝试 MCP 工具（Brave Search）
    ↓ 需要全文
使用 curl（静态页面）
    ↓ 需要解析结构
使用 Python requests
    ↓ 需要执行JS
使用 Playwright
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
python scripts/extract.py "<URL>" -o result.json
```

**脚本特点：**
- ✅ 自动选择最佳方法（requests → curl → playwright）
- ✅ 自动处理编码问题（UTF-8/GBK）
- ✅ 结构化输出（JSON格式）
- ✅ 内置多种正文提取策略

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

| 如果你需要... | 使用工具 | 备选工具 |
|-------------|---------|---------|
| 快速获取单个网页全文 | **WebFetch** | curl |
| 搜索信息 | **WebSearch** | Brave MCP |
| 受限域名/需全文 | **curl** | Python+requests |
| 解析 HTML 结构 | **Python+BeautifulSoup** | Playwright |
| JavaScript 动态页面 | **Playwright** | - |
| 整站备份 | **wget** | Python+requests |

---

## 失败处理流程

### 自动流程（使用 extract.py）

```
WebFetch 失败
    ↓
python scripts/extract.py "URL" --method auto
    ↓
├── requests 尝试 ──→ 成功 ✅
│
├── curl 尝试 ──→ 成功 ✅
│
├── playwright 尝试 ──→ 成功 ✅
│
└── 全部失败 ──→ 返回错误信息 ❌
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
