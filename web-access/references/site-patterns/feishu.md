---
domain: feishu.cn
description: 飞书文档（docx/wiki）内容提取策略与CDP操作模式
aliases: [飞书, Lark, Feishu]
updated: 2026-03-24
---

## 平台特征

### URL 类型区分（关键）

| 类型 | URL 模式 | 防护级别 | 提取策略 |
|------|---------|---------|---------|
| **docx** | `*.feishu.cn/docx/*` | 中等 | CDP + 点击目录法 ✅ |
| **wiki** | `*.feishu.cn/wiki/*` | 严格 | CDP 可能失效，需尝试 jina.ai ⚠️ |

### 技术架构

- **虚拟滚动（Virtual Scrolling）**：只有当前视口内容存在于 DOM，滚动时离开视口的内容会被移除
- **自定义滚动容器**：使用 `.bear-web-x-container`，非 `window`
- **非标准标签**：正文段落使用 `[data-block-type="text"]`，非标准 `<p>` 标签
- **懒加载触发**：基于 Intersection Observer，非传统 scroll 事件

## 有效模式

### 方法1：点击目录法（推荐用于长文档）

逐个点击左侧目录项，每次点击触发对应章节加载。

```javascript
// 适用于 feishu.cn/docx/*
(async () => {
  const allContent = [];
  const tocItems = document.querySelectorAll(".catalogue__list-item");

  for (let item of tocItems) {
    const title = item.innerText?.trim();
    if (!title || title.length > 50) continue; // 过滤非标题项

    item.click();
    await new Promise(r => setTimeout(r, 2500)); // 等待加载

    const blocks = document.querySelectorAll("[data-block-type=\"text\"]");
    let chapterText = "=== " + title + " ===\n\n";
    blocks.forEach(b => {
      const t = b.innerText?.trim();
      if (t) chapterText += t + "\n\n";
    });

    allContent.push(chapterText);
  }

  return allContent.join("\n");
})()
```

**关键参数**：
- 目录选择器：`.catalogue__list-item`
- 正文选择器：`[data-block-type="text"]`
- 等待时间：2500ms（点击后等待内容加载）
- 章节过滤：`length < 50` 排除过长文本（非标题）

### 方法2：逐步滚动法（备用）

适用于短文档或点击目录法失效的情况。

```javascript
(async () => {
  const container = document.querySelector(".bear-web-x-container");
  const allTexts = [];
  const scrollPoints = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000];

  for (let y of scrollPoints) {
    container.scrollTo({top: y, behavior: "instant"});
    await new Promise(r => setTimeout(r, 2000));

    const blocks = document.querySelectorAll("[data-block-type=\"text\"]");
    blocks.forEach(b => {
      const t = b.innerText?.trim();
      if (t && !allTexts.includes(t)) {
        allTexts.push(t);
      }
    });
  }

  return allTexts.join("\n\n");
})()
```

### 方法3：jina.ai 预处理（快速尝试）

部分公开文档可直接提取：

```
https://r.jina.ai/http://example.feishu.cn/docx/xxx
```

**适用场景**：
- 简单 docx 文档
- 无需登录的公开内容
- 快速验证内容可用性

**局限性**：
- 对长文档可能只提取部分内容
- wiki 类型通常无法完整提取
- 内容可能包含 "Failed to load" 占位符

## 已知陷阱

### ❌ 错误做法

| 做法 | 问题 | 原因 |
|------|------|------|
| `window.scrollTo()` | 无效 | 飞书使用自定义滚动容器 |
| `document.querySelectorAll("p")` | 返回空 | 飞书不使用标准 p 标签 |
| 点击第一个目录项触发全量加载 | 部分文档失效 | 防护级别差异 |
| 纯 CSS 高度修改 | 不触发加载 | 只是视觉改变 |

### ⚠️ wiki 类型特殊限制

测试 URL: `https://waytoagi.feishu.cn/wiki/SmL7w8fBdiJ2x5kfgWLcavM4nRe`

- CDP + 点击目录 → 只加载目录，正文为空
- CDP + 渐进滚动 → 正文未加载
- jina.ai → 只获取目录和引言

**可能解法**：需要登录态 Cookie 或更强的浏览器伪装（未验证）

## 文档长度判断

| 长度 | 推荐方法 | 预估时间 |
|------|---------|---------|
| 短文档（<2000px）| 点击第一项 + 滚动 | 1-2分钟 |
| 长文档（>3000px）| **逐个点击目录** | 3-5分钟 |
| 严格懒加载 | 逐个点击目录 | 5-10分钟 |

## 推荐流程

```
1. 先用 jina.ai 尝试（最简单）
   ↓ 如果内容不完整
2. CDP 打开文档
   ↓
3. 判断文档类型：
   - docx → 继续
   - wiki → 告知用户可能无法完整提取
   ↓
4. 判断文档长度：
   - 短文档 → 点击目录第一项 + 滚动提取
   - 长文档 → 逐个点击目录章节提取
```

## CDP API 调用示例

```bash
# 创建标签页
curl -s "http://localhost:3456/new?url=https://xxx.feishu.cn/docx/xxx"

# 点击目录项
curl -s -X POST "http://localhost:3456/click?target=ID" \
  -d '.catalogue__list-item:nth-child(1)'

# 提取内容
curl -s -X POST "http://localhost:3456/eval?target=ID" \
  -d 'Array.from(document.querySelectorAll("[data-block-type=text]")).map(b => b.innerText).join("\n\n")'
```

## 经验沉淀日期

- 2026-03-24: 初始经验整理，docx 类型点击目录法验证成功
