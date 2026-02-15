# Web Content Extraction Toolkit | 详细工具手册

本文件包含 7 层工具提取策略的详细说明和代码示例。
仅在需要具体工具命令时加载此文件。

---

## 1. curl（静态页面，最轻量）

### 基础获取
```bash
curl -sL "http://example.com/page.html"
```

### 处理 GB2312 编码（中文老网站常用）
```bash
curl -sL "http://example.com/page.html" | iconv -f gb2312 -t utf-8
```

### 带 User-Agent（部分网站需要）
```bash
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "http://example.com"
```

### 提取正文（去除 HTML 标签）
```bash
curl -sL "URL" | \
  sed 's/<br\s*\/?>/\n/gi' | \
  sed 's/<[^>]*>//g' | \
  sed 's/&nbsp;/ /g' | \
  sed 's/^[[:space:]]*//' | \
  grep -v "^[[:space:]]*$"
```

---

## 2. Python + BeautifulSoup（结构化提取）

### 基础模板
```python
import requests
from bs4 import BeautifulSoup

def extract_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding  # 自动检测编码

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        text = soup.get_text(separator='\n', strip=True)

        return {'title': title, 'text': text}
    except Exception as e:
        return {'error': str(e)}
```

### 提取特定元素
```python
# 按 class 提取
content = soup.find('div', class_='article-content')

# 按 id 提取
content = soup.find('div', id='post-content')

# 提取所有段落
texts = [p.get_text() for p in soup.find_all('p')]
```

---

## 3. Python + Playwright（动态页面神器）

### 基础模板
```python
from playwright.sync_api import sync_playwright

def extract_dynamic_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=30000, wait_until='networkidle')

        # 等待特定元素加载（如有需要）
        # page.wait_for_selector('.content', timeout=10000)

        title = page.title()
        text = page.inner_text('body')

        browser.close()

        return {'title': title, 'text': text}
```

### 模拟用户操作
```python
# 点击按钮
page.click('button.load-more')

# 填写表单
page.fill('input[name="username"]', 'myuser')
page.click('button[type="submit"]')

# 滚动页面
page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
```

---

## 4. wget（整站下载）

### 递归下载整站
```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent http://example.com/

# 简写
wget -mkEpnp http://example.com/
```

### 限制递归深度
```bash
wget --mirror --level=2 http://example.com/
```

---

## 特殊情况处理

### 编码问题（中文乱码）
```python
# 方法1: 自动检测
response.encoding = response.apparent_encoding

# 方法2: 手动指定
response.encoding = 'utf-8'      # 现代网站
response.encoding = 'gb2312'     # 老网站
response.encoding = 'gbk'        # 老网站
response.encoding = 'big5'       # 台湾网站
```

### IP 被封/频率限制
```python
import time
import random

# 添加延时
time.sleep(random.uniform(1, 3))

# 使用代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
response = requests.get(url, proxies=proxies)
```

### 需要登录/Cookie
```python
import requests

headers = {
    'User-Agent': 'Mozilla/5.0...',
    'Cookie': 'sessionid=xxx; userid=yyy'
}

# 或使用 session 保持登录
session = requests.Session()
session.post('http://example.com/login', data={'user': 'xxx', 'pass': 'yyy'})
response = session.get('http://example.com/protected-page')
```

---

## 工具选择速查

| 场景 | 首选工具 | 备选工具 |
|-----|---------|---------|
| 快速获取单个网页全文 | **WebFetch** | curl |
| 受限域名/需全文 | **curl** | Python+requests |
| 需要解析 HTML 结构 | **Python+BeautifulSoup** | Playwright |
| JavaScript 动态页面 | **Playwright** | - |
| 整站备份 | **wget** | Python+requests |

---

## 失败处理流程

```
WebFetch 失败
    ↓
尝试 curl / Python requests（绕过安全限制）
    ↓
内容是动态生成？
    ↓
使用 Playwright（执行 JavaScript）
    ↓
有反爬机制？
    ↓
添加 headers/proxy/延时
```
