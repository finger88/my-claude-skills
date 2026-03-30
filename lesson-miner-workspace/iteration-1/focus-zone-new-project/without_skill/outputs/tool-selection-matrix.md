# 工具选择决策矩阵

**用途**: 快速判断针对不同网站应使用哪种提取工具

---

## 问题类型速查

| 错误信息 | 问题类型 | 立即降级到 |
|---------|---------|-----------|
| `can't open file 'D:\c\Users\...'` | Windows 路径错误 | 使用绝对路径 |
| `Unable to verify if domain is safe` | WebFetch 安全限制 | jina.ai / Playwright |
| `当前环境异常，完成验证后即可继续访问` | CAPTCHA 拦截 | Playwright MCP |
| `403 Forbidden` | 访问被拒绝 | Playwright MCP |
| `Timeout` | 请求超时 | 检查网络或换工具 |

---

## 网站类型 → 工具映射

### 微信公众号 (mp.weixin.qq.com)
**特征**: WebFetch 安全限制 + jina.ai CAPTCHA
**唯一方案**: Playwright MCP
**示例代码**:
```python
# 导航到文章
await browser_navigate(url="https://mp.weixin.qq.com/s/...")

# 获取快照
snapshot = await browser_snapshot()

# 提取正文（在 js_content div 中）
content = snapshot.text
```

### 知乎 (zhihu.com)
**特征**: jina.ai 有时可用，有时触发 CAPTCHA
**推荐**: 先尝试 jina.ai，失败再降级到 Playwright
**注意**: 知乎专栏文章比问答页面更容易提取

### 小红书 (xiaohongshu.com)
**特征**: 强反爬，需要登录态
**方案**: Playwright MCP + 可能需要登录
**限制**: 部分内容可能无法提取

### GitHub (github.com)
**特征**: 结构化数据，有 API
**推荐**: defuddle 或直接使用 GitHub API
**避免**: Playwright（过度杀伤）

### 付费内容 (Every.to / Substack)
**特征**: 有付费墙，但 jina.ai 可绕过
**推荐**: jina.ai（免费且有效）
**备选**: Playwright（如果已订阅）

---

## 工具特性对比

| 工具 | 速度 | 成功率 | 反爬能力 | 适用场景 |
|------|------|--------|----------|----------|
| WebFetch | ⚡ 最快 | 低 | 无 | 简单静态页 |
| jina.ai | 快 | 中 | 低 | 通用网页 |
| defuddle | 中等 | 高 | 中 | GitHub/Reddit/YouTube |
| Playwright | 慢 | 最高 | 强 | 反爬严格站点 |

---

## Windows 路径问题专项

### 错误示例
```bash
# 错误 - 使用 ~ 展开
python ~/.claude/skills/web-content-extraction/scripts/extract.py "<URL>"
```

### 正确做法
```bash
# 正确 - 使用绝对路径
python "C:\Users\HONOR\.claude\skills\web-content-extraction\scripts\extract.py" "<URL>"

# 或切换到目录后执行
cd "C:\Users\HONOR\.claude\skills\web-content-extraction\scripts"
python extract.py "<URL>"
```

---

## 实战流程图

```
开始提取
    │
    ▼
检查 URL 域名
    │
    ├── 微信公众号 ──→ 直接使用 Playwright
    │
    ├── 小红书 ──────→ 直接使用 Playwright
    │
    ├── 知乎 ────────→ 尝试 jina.ai ──→ 失败 ──→ Playwright
    │
    ├── GitHub ──────→ 使用 defuddle
    │
    └── 其他 ────────→ 尝试 jina.ai ──→ 失败 ──→ WebFetch ──→ 失败 ──→ Playwright
```

---

*最后更新: 2026-03-25*
