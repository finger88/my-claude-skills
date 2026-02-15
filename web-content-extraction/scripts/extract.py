#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Content Extraction Script
统一网页内容提取脚本，支持多种策略自动降级

Usage:
    python extract.py <URL> [options]

Options:
    --method    指定提取方法 (auto|requests|curl|playwright)
    --output    输出文件路径 (默认: stdout)
    --timeout   请求超时时间 (默认: 30s)
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
    """
    methods = []

    if method == 'auto':
        # 智能选择方法顺序
        methods = ['requests', 'curl', 'playwright']
    else:
        methods = [method]

    errors = []

    for m in methods:
        if m == 'requests':
            result, error = extract_with_requests(url, timeout)
        elif m == 'curl':
            result, error = extract_with_curl(url, timeout)
        elif m == 'playwright':
            result, error = extract_with_playwright(url, timeout)
        else:
            continue

        if result and result.get('success') and result.get('content'):
            return result

        if error:
            errors.append(f"{m}: {error}")

    # 所有方法都失败
    return {
        'success': False,
        'error': '所有提取方法均失败',
        'details': errors,
        'url': url
    }


def main():
    parser = argparse.ArgumentParser(description='网页内容提取工具')
    parser.add_argument('url', help='要提取的 URL')
    parser.add_argument('--method', default='auto',
                        choices=['auto', 'requests', 'curl', 'playwright'],
                        help='提取方法 (默认: auto)')
    parser.add_argument('--output', '-o', help='输出文件路径 (默认: stdout)')
    parser.add_argument('--timeout', type=int, default=30, help='超时时间(秒)')

    args = parser.parse_args()

    # 执行提取
    result = extract_url(args.url, args.method, args.timeout)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)

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
