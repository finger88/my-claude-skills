#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Content Extraction Script
统一网页内容提取脚本，支持多种策略自动降级

9层提取策略（按优先级排序）：
    L0: brave      - 快速摘要（需 API key），适合已知 URL 的快速提取
    L1: jina.ai    - 免费快速，适合大多数网页
    L2: defuddle   - 智能正文识别 + 站点专用提取器（GitHub/Reddit/YouTube 等）
    L3: requests   - 本地解析，提取结构化信息（标题、作者等）
    L4: curl       - 备用方案，绕过部分限制
    L5: playwright - 动态渲染页面，执行 JavaScript

搜索模式：
    --search    使用 Brave Search 从关键词发现 URL

Usage:
    python extract.py <URL> [options]
    python extract.py --search "query" [options]

Options:
    --method    指定提取方法 (auto|brave|jina|requests|curl|playwright)
    --search    搜索关键词（发现模式，而非提取模式）
    --output    输出文件路径 (默认: stdout; Markdown 格式未指定时保存到 ~/Downloads/)
    --timeout   请求超时时间 (默认: 30s)

Environment:
    BRAVE_API_KEY   Brave Search API Key（用于 L0 摘要和搜索模式）
"""

import sys
import os
import re
import json
import argparse
import subprocess
import html
from urllib.parse import urlparse

# 确保输出编码正确
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='ignore', buffering=1)
sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', errors='ignore', buffering=1)


def get_brave_api_key():
    """
    获取 Brave API Key
    优先级：1. 环境变量 2. USER.md Secrets 区块
    """
    # 1. 优先从环境变量获取
    key = os.environ.get('BRAVE_API_KEY', '')
    if key:
        return key

    # 2. 从 USER.md 解析（fallback）
    try:
        # 可能的 USER.md 路径（中英文环境）
        possible_paths = [
            os.path.expanduser("~/.claude/projects/memory-work/USER.md"),
            os.path.expanduser("~/.claude/projects/memory-work/zh-CN/USER.md"),
            os.path.expanduser("~/memory-work/USER.md"),
            os.path.expanduser("~/memory-work/zh-CN/USER.md"),
            "D:/my tool/memory-work/USER.md",
            "D:/my tool/memory-work/zh-CN/USER.md",
        ]

        user_md_content = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    user_md_content = f.read()
                break

        if user_md_content:
            # 在 Secrets & API Keys 区块中查找 Brave Search API key
            import re
            # 直接在整个文件中搜索 Brave Search 行（更可靠）
            # 格式: | Brave Search | `key` | usage |
            brave_match = re.search(
                r'\|\s*Brave\s*Search\s*\|\s*`?([^`\n|]+)`?\s*\|',
                user_md_content,
                re.IGNORECASE
            )
            if brave_match:
                key = brave_match.group(1).strip()
                if key and key not in ('待添加', '-', ''):
                    return key
    except Exception:
        pass

    return ''


def search_with_brave(query, api_key=None, timeout=30, count=5):
    """
    使用 Brave Search API 搜索发现（搜索模式）
    返回搜索结果列表
    """
    if not api_key:
        api_key = get_brave_api_key()

    if not api_key:
        return None, "未配置 BRAVE_API_KEY 环境变量"

    try:
        import requests
    except ImportError:
        return None, "requests 未安装"

    headers = {
        'X-Subscription-Token': api_key,
        'Accept': 'application/json'
    }

    params = {
        'q': query,
        'count': count,
        'offset': 0,
        'mkt': 'zh-CN',
        'safesearch': 'moderate',
        'freshness': 'all',
        'text_decorations': False,
        'text_format': 'Raw'
    }

    try:
        resp = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params,
            timeout=timeout
        )

        if resp.status_code != 200:
            return None, f"Brave Search API 返回错误: {resp.status_code} - {resp.text}"

        data = resp.json()
        results = []

        # 提取网页搜索结果
        web_results = data.get('web', {}).get('results', [])
        for item in web_results[:count]:
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'description': item.get('description', ''),
                'age': item.get('age', ''),
                'source': 'web'
            })

        return {
            'success': True,
            'method': 'brave_search',
            'query': query,
            'results': results,
            'total': len(results)
        }, None

    except Exception as e:
        return None, str(e)


def extract_with_brave(url, api_key=None, timeout=30):
    """
    使用 Brave Search API 获取 URL 摘要（L0 层 - 快速摘要）
    特点：速度快、有 Brave 全球 CDN 加速、可能已有缓存
    适合：热门网页、新闻文章等已被 Brave 索引的内容
    """
    if not api_key:
        api_key = get_brave_api_key()

    if not api_key:
        return None, "未配置 BRAVE_API_KEY 环境变量"

    try:
        import requests
    except ImportError:
        return None, "requests 未安装"

    headers = {
        'X-Subscription-Token': api_key,
        'Accept': 'application/json'
    }

    # 方法1：尝试直接搜索该 URL，看能否获取摘要
    params = {
        'q': f"url:{url}",
        'count': 1,
        'offset': 0,
        'text_decorations': False,
        'text_format': 'Raw'
    }

    try:
        resp = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params,
            timeout=timeout
        )

        if resp.status_code == 200:
            data = resp.json()
            web_results = data.get('web', {}).get('results', [])

            if web_results:
                item = web_results[0]
                # 如果找到的结果 URL 匹配或相似
                if url in item.get('url', '') or item.get('url', '') in url:
                    return {
                        'success': True,
                        'method': 'brave',
                        'title': item.get('title', ''),
                        'author': '',  # Brave 不提供作者信息
                        'content': item.get('description', ''),
                        'url': item.get('url', url),
                        'age': item.get('age', '')
                    }, None

        # 方法2：将该 URL 作为搜索词，看能否找到相关信息
        params2 = {
            'q': url,
            'count': 3,
            'offset': 0,
            'text_decorations': False,
            'text_format': 'Raw'
        }

        resp2 = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers,
            params=params2,
            timeout=timeout
        )

        if resp2.status_code == 200:
            data2 = resp2.json()
            web_results2 = data2.get('web', {}).get('results', [])

            for item in web_results2:
                result_url = item.get('url', '')
                # 检查 URL 是否匹配（去掉协议和 www 后比较）
                clean_input = url.replace('https://', '').replace('http://', '').replace('www.', '')
                clean_result = result_url.replace('https://', '').replace('http://', '').replace('www.', '')

                if clean_input in clean_result or clean_result in clean_input:
                    return {
                        'success': True,
                        'method': 'brave',
                        'title': item.get('title', ''),
                        'author': '',
                        'content': item.get('description', ''),
                        'url': result_url,
                        'age': item.get('age', '')
                    }, None

        return None, "Brave 未索引该 URL 或无法获取摘要"

    except Exception as e:
        return None, str(e)


def extract_with_jina(url, timeout=30):
    """
    使用 jina.ai Reader 提取（第 1 层 - 快速方案）
    特点：免费、免 API key、绕过付费墙、返回干净 Markdown
    适合：大多数普通网页、微信公众号、博客等
    """
    try:
        import requests
    except ImportError:
        return None, "requests 未安装"

    jina_url = f"https://r.jina.ai/http://{url}" if not url.startswith('http') else f"https://r.jina.ai/{url}"

    try:
        resp = requests.get(jina_url, timeout=timeout)

        if resp.status_code != 200:
            return None, f"jina.ai 返回状态码: {resp.status_code}"

        content = resp.text

        # jina.ai 返回格式：第一行是标题，后面是正文
        lines = content.split('\n')
        title = lines[0].strip() if lines else ''
        # 去掉标题行，剩余为正文
        body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else content

        # 清理 jina.ai 的标记
        body = re.sub(r'\[\d+\]\s*https?://\S+', '', body)  # 移除引用标记如 [1] http://...

        return {
            'success': True,
            'method': 'jina',
            'title': title,
            'author': '',  # jina.ai 不返回作者信息
            'content': body,
            'url': url
        }, None

    except Exception as e:
        return None, str(e)


def extract_with_defuddle(url, timeout=30):
    """
    使用 defuddle (npm CLI) 提取 — L2 智能正文识别
    优势：评分算法识别正文 + 站点专用提取器（GitHub/Reddit/Twitter/YouTube 等）
    限制：无法处理 JS 动态渲染的 SPA 页面
    """
    try:
        # Windows 上 npm 全局命令需要通过 shell 调用（.cmd 包装）
        cmd = f'defuddle parse "{url}" -j -m'
        # 继承当前环境变量（含代理设置），确保 JSDOM 请求能走代理
        env = os.environ.copy()
        # 如果未设置代理但本机有常用代理端口，自动配置
        if not env.get('https_proxy') and not env.get('HTTPS_PROXY'):
            proxy = 'http://127.0.0.1:6789'
            env['http_proxy'] = proxy
            env['https_proxy'] = proxy
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True,
            encoding='utf-8', errors='ignore',
            timeout=timeout + 5,
            env=env
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if 'not recognized' in stderr or 'not found' in stderr or 'command not found' in stderr:
                return None, "defuddle 未安装，运行: npm install -g defuddle jsdom"
            return None, f"defuddle failed: {stderr}"

        data = json.loads(result.stdout)
        content = data.get('content', '').strip()

        if not content or len(content) < 50:
            return None, f"defuddle: content too short ({len(content or '')} chars)"

        return {
            'success': True,
            'method': 'defuddle',
            'title': data.get('title', ''),
            'author': data.get('author', ''),
            'content': content,
            'url': url,
            'description': data.get('description', ''),
            'published': data.get('published', ''),
            'wordCount': data.get('wordCount', 0),
            'domain': data.get('domain', ''),
            'image': data.get('image', ''),
            'site': data.get('site', ''),
        }, None

    except subprocess.TimeoutExpired:
        return None, "defuddle: timeout"
    except json.JSONDecodeError as e:
        return None, f"defuddle: invalid JSON: {e}"
    except FileNotFoundError:
        return None, "defuddle 未安装，运行: npm install -g defuddle jsdom"
    except Exception as e:
        return None, str(e)


def extract_with_requests(url, timeout=30):
    """
    使用 requests + BeautifulSoup 提取
    适合：静态页面，需要解析 HTML 结构
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return None, "requests 或 beautifulsoup4 未安装"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        # 自动检测编码
        if resp.encoding == 'ISO-8859-1':
            resp.encoding = resp.apparent_encoding

        html_content = resp.text

        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除 script 和 style
        for elem in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            elem.decompose()

        # 提取标题
        title = None
        for selector in ['h1.rich_media_title', 'h2.rich_media_title', 'h1.post-title',
                         'h1.entry-title', 'h1.article-title', 'h1', 'title']:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                break

        # 提取作者
        author = None
        for selector in ['a#js_name', 'span.profile_nickname', '.author', '.byline',
                         '[rel="author"]', '.post-author']:
            elem = soup.select_one(selector)
            if elem:
                author = elem.get_text(strip=True)
                break

        # 提取正文
        content = None
        for selector in ['div#js_content', 'div.rich_media_content', 'article',
                         'div.post-content', 'div.entry-content', 'div.article-content',
                         'main', '[role="main"]']:
            elem = soup.select_one(selector)
            if elem:
                # 清理图片
                for img in elem.find_all('img'):
                    img.replace_with('[图片]')

                content = elem.get_text(separator='\n', strip=True)
                content = re.sub(r'\n{3,}', '\n\n', content)
                break

        # 如果都没找到，尝试正文最长段落
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])

        return {
            'success': True,
            'method': 'requests',
            'title': title or '',
            'author': author or '',
            'content': content or '',
            'url': resp.url
        }, None

    except Exception as e:
        return None, str(e)


def extract_with_curl(url, timeout=30):
    """
    使用 curl 提取
    适合：快速获取原始 HTML，绕过部分限制
    """
    try:
        cmd = [
            'curl', '-s', '-L', '--max-time', str(timeout),
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--compressed',
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

        if result.returncode != 0:
            return None, f"curl failed: {result.stderr}"

        html_content = result.stdout

        # 简单的正则提取
        # 提取标题
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = html.unescape(title_match.group(1).strip()) if title_match else ''

        # 尝试提取正文（简化版）
        content = ''
        for pattern in [r'<article[^>]*>(.*?)</article>', r'<main[^>]*>(.*?)</main>',
                        r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>']:
            match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                content = re.sub(r'<[^>]+>', '\n', content)
                content = html.unescape(content)
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                content = '\n'.join(lines)
                break

        return {
            'success': True,
            'method': 'curl',
            'title': title,
            'author': '',
            'content': content,
            'url': url
        }, None

    except Exception as e:
        return None, str(e)


def extract_with_playwright(url, timeout=30):
    """
    使用 Playwright 提取（最后手段）
    适合：JavaScript 动态渲染页面
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright 未安装，运行: pip install playwright && playwright install"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            page.goto(url, wait_until='networkidle', timeout=timeout*1000)

            # 等待页面加载
            page.wait_for_timeout(2000)

            # 提取标题
            title = page.title()

            # 尝试提取正文
            content_selectors = [
                'div#js_content',
                'div.rich_media_content',
                'article',
                'div.post-content',
                'div.entry-content',
                'main'
            ]

            content = ''
            for selector in content_selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        content = elem.inner_text()
                        break
                except:
                    continue

            browser.close()

            return {
                'success': True,
                'method': 'playwright',
                'title': title,
                'author': '',
                'content': content,
                'url': page.url
            }, None

    except Exception as e:
        return None, str(e)


def extract_url(url, method='auto', timeout=30):
    """
    统一提取接口，支持自动降级

    降级顺序：
    L0: brave       - 快速摘要（需 BRAVE_API_KEY），适合已知 URL 的快速提取
    L1: jina.ai     - 免费快速，适合大多数网页
    L2: defuddle    - 智能正文识别 + 站点专用提取器
    L3: requests    - 本地解析，适合需要提取结构化信息的页面
    L4: curl        - 备用方案
    L5: playwright  - 动态渲染页面
    """
    methods = []

    if method == 'auto':
        # 智能选择方法顺序：如果有 Brave API key，优先尝试
        if get_brave_api_key():
            methods = ['brave', 'jina', 'defuddle', 'requests', 'curl', 'playwright']
        else:
            methods = ['jina', 'defuddle', 'requests', 'curl', 'playwright']
    else:
        methods = [method]

    errors = []

    # 用于保存 Brave 的元信息（标题），供后续方法使用
    brave_title = None
    brave_content = None

    for m in methods:
        if m == 'brave':
            result, error = extract_with_brave(url, timeout=timeout)
            # Brave 特殊处理：只作为元信息层，摘要过短时继续降级
            if result and result.get('success'):
                brave_title = result.get('title')
                brave_content = result.get('content', '')
                # 如果 Brave 返回的内容足够长（>= 500 字符），直接返回
                # 否则继续尝试下一层获取完整内容
                if len(brave_content) >= 500:
                    return result
                else:
                    # 记录信息，继续降级
                    errors.append(f"brave: 仅获取到摘要（{len(brave_content)} 字符），继续获取完整内容...")
                    continue
        elif m == 'jina':
            result, error = extract_with_jina(url, timeout)
        elif m == 'defuddle':
            result, error = extract_with_defuddle(url, timeout)
        elif m == 'requests':
            result, error = extract_with_requests(url, timeout)
        elif m == 'curl':
            result, error = extract_with_curl(url, timeout)
        elif m == 'playwright':
            result, error = extract_with_playwright(url, timeout)
        else:
            continue

        if result and result.get('success') and result.get('content'):
            # 如果之前有 Brave 的标题但当前方法没有标题，合并使用
            if brave_title and not result.get('title'):
                result['title'] = brave_title
            return result

        if error:
            errors.append(f"{m}: {error}")

    # 如果所有完整提取方法都失败，但 Brave 有内容，返回 Brave 的摘要作为 fallback
    if brave_content:
        return {
            'success': True,
            'method': 'brave',
            'title': brave_title or '',
            'author': '',
            'content': brave_content,
            'url': url,
            'note': '仅获取到摘要（完整内容提取失败）'
        }

    # 所有方法都失败
    return {
        'success': False,
        'error': '所有提取方法均失败',
        'details': errors,
        'url': url
    }


def generate_markdown(result):
    """
    将提取结果转换为 Markdown 格式
    """
    if not result or not result.get('success'):
        return None

    title = result.get('title', '')
    author = result.get('author', '')
    content = result.get('content', '')
    url = result.get('url', '')
    method = result.get('method', '')

    md_lines = []

    # 标题
    if title:
        md_lines.append(f"# {title}")
        md_lines.append("")

    # 元信息
    meta_info = []
    if author:
        meta_info.append(f"**作者**: {author}")
    if url:
        meta_info.append(f"**来源**: {url}")
    if method:
        meta_info.append(f"**提取方式**: {method}")

    if meta_info:
        md_lines.append(" | ".join(meta_info))
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # 正文内容
    if content:
        # 清理内容中的多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        md_lines.append(content)

    return '\n'.join(md_lines)


def main():
    parser = argparse.ArgumentParser(description='网页内容提取工具 - 9层降级策略 (含 Brave Search + defuddle)')
    parser.add_argument('url', nargs='?', help='要提取的 URL')
    parser.add_argument('--search', '-s', help='搜索关键词（发现模式，需 BRAVE_API_KEY）')
    parser.add_argument('--method', default='auto',
                        choices=['auto', 'brave', 'jina', 'defuddle', 'requests', 'curl', 'playwright'],
                        help='提取方法: brave(快速摘要需API), jina(免费快速), defuddle(智能正文识别), requests(本地解析), curl(备用), playwright(动态渲染) (默认: auto)')
    parser.add_argument('--output', '-o', help='输出文件路径 (默认: stdout; Markdown 格式未指定时保存到 ~/Downloads/)')
    parser.add_argument('--format', '-f', default='json',
                        choices=['json', 'md', 'markdown'],
                        help='输出格式: json(结构化数据), md/markdown(可读文档，默认保存到 ~/Downloads/) (默认: json)')
    parser.add_argument('--timeout', type=int, default=30, help='超时时间(秒)')

    args = parser.parse_args()

    # 搜索模式
    if args.search:
        result, error = search_with_brave(args.search, timeout=args.timeout)
        if error:
            print(json.dumps({
                'success': False,
                'error': error,
                'query': args.search
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        output = json.dumps(result, ensure_ascii=False, indent=2)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到: {args.output}", file=sys.stderr)
        else:
            print(output)
        sys.exit(0)

    # 提取模式 - 必须提供 URL
    if not args.url:
        parser.print_help()
        print("\n错误: 请提供 URL 或使用 --search 进行搜索", file=sys.stderr)
        sys.exit(1)

    # 执行提取
    result = extract_url(args.url, args.method, args.timeout)

    # 根据格式生成输出
    if args.format in ('md', 'markdown'):
        output = generate_markdown(result)
        if output is None:
            print("提取失败，无法生成 Markdown", file=sys.stderr)
            sys.exit(1)
        # 如果未指定输出路径，保存到 ~/Downloads/
        if not args.output:
            # 使用标题或 URL 生成文件名
            title = result.get('title', '') if result else ''
            if title:
                # 清理文件名中的非法字符
                safe_title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]
                filename = f"{safe_title}.md"
            else:
                # 使用 URL 的域名部分
                parsed = urlparse(args.url)
                domain = parsed.netloc.replace('.', '_')
                filename = f"{domain}_extract.md"
            # 保存到下载目录
            downloads_dir = os.path.expanduser("~/Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            args.output = os.path.join(downloads_dir, filename)
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)

    # 返回码
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
