#!/bin/bash
# 安装 web-content-extraction 所需依赖

echo "Installing dependencies for web-content-extraction..."

# 基础依赖
pip install requests beautifulsoup4 lxml

# Playwright (可选，用于动态页面)
echo "Installing Playwright (optional, for JavaScript-heavy pages)..."
pip install playwright
playwright install chromium

echo "Setup complete!"
