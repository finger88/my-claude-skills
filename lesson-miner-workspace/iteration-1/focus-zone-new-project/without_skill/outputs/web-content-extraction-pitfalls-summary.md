# Web Content Extraction 踩坑记录

**记录时间**: 2026-03-25
**记录人**: AI Assistant
**场景**: 使用 web-content-extraction 技能提取微信文章时遇到的技术问题

---

## 问题概述

刚才尝试使用 web-content-extraction 技能提取微信文章内容时，连续遇到3个技术卡点，形成了一条完整的「失败链」。

---

## 问题 1: Windows 路径错误

### 现象
Python 脚本执行时报告文件找不到：
```
can't open file 'D:\c\Users\HONOR\...'
```

### 根因
Windows 环境下 `~` 路径展开后被错误解析，添加了多余的 `\c` 前缀。

### 解决方案
- 使用绝对路径调用脚本
- 或切换到脚本所在目录后执行

---

## 问题 2: WebFetch 安全限制

### 现象
WebFetch 工具返回安全验证错误：
```
Unable to verify if domain mp.weixin.qq.com is safe to fetch
```

### 根因
微信公众号域名（mp.weixin.qq.com）在 WebFetch 的安全黑名单中，无法直接抓取。

### 解决方案
- 立即降级到 jina.ai 或 Playwright MCP
- 对于微信公众号，直接使用 Playwright MCP

---

## 问题 3: jina.ai 触发 CAPTCHA

### 现象
jina.ai Reader API 返回验证页面：
```
当前环境异常，完成验证后即可继续访问
```

### 根因
微信、知乎等平台对 jina.ai 的 IP 地址做了风控，返回 CAPTCHA 验证页面而非真实内容。

### 解决方案
- 对于反爬严格的站点（微信、小红书），直接使用 Playwright MCP
- Playwright 模拟真实浏览器行为，成功率最高

---

## 经验总结

### 快速决策树

```
URL 是微信公众号？
  ├─ 是 → 直接使用 Playwright MCP
  └─ 否 → 尝试 jina.ai → 失败 → Playwright MCP
```

### 工具选择优先级

| 网站类型 | 首选工具 | 说明 |
|---------|---------|------|
| 微信公众号 | Playwright MCP | 唯一可靠方案 |
| 知乎 | jina.ai / Brave | 备选 Playwright |
| 小红书 | Playwright MCP | 反爬严格 |
| 普通网页 | jina.ai | 快速、免费 |

### 核心教训

1. **不要在一个工具上死磕** - 遇到限制立即降级
2. **微信文章直接上 Playwright** - 跳过前面所有层
3. **Windows 路径问题** - 使用绝对路径避免歧义

---

## 后续行动

- [ ] 更新 web-content-extraction 技能的文档，加入这些坑点
- [ ] 在 skill 的代码中加入智能路由，自动识别域名选择最佳工具
- [ ] 考虑封装 Playwright MCP 的专用微信提取流程

---

*记录状态: 已完成*
*关联文件: web-content-extraction-pitfalls.md (专注区)*
