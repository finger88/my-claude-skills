# My Claude Skills

个人 Claude Code 技能集合，基于 [lijigang/ljg-skill-clip](https://github.com/lijigang/ljg-skill-clip) 修改和扩展。

## Skills 列表

### 1. ljg-clip

内容剪藏工具，用于快速保存 URL 或文本到统一的收件箱。

**修改内容：**
- ✅ 存档路径改为 `D:\my tool\clip\inbox.org`
- ✅ 集成 web-content-extraction 作为 fallback，支持微信公众号等受限网站

**使用方法：**
```
clip https://example.com/article
剪藏 https://mp.weixin.qq.com/s/xxx
```

### 2. web-content-extraction

网页内容提取工具，支持多种提取策略自动降级。

**修改内容：**
- ✅ 新增 `scripts/extract.py`：统一提取接口，自动策略降级
- ✅ 新增 `scripts/setup.sh`：一键安装依赖
- ✅ 内置编码自动检测（UTF-8/GBK）
- ✅ 支持微信公众号等受限域名提取

**使用方法：**
```bash
python scripts/extract.py "https://example.com" -o result.json
```

**提取策略（自动降级）：**
1. WebFetch（内置）
2. Python requests + BeautifulSoup
3. curl
4. Playwright（动态页面）

## 安装

1. 克隆仓库到本地：
```bash
git clone https://github.com/YOUR_USERNAME/my-claude-skills.git
cd my-claude-skills
```

2. 安装依赖（针对 web-content-extraction）：
```bash
bash web-content-extraction/scripts/setup.sh
```

3. 将 skills 复制到 Claude 目录：
```bash
cp -r ljg-clip ~/.claude/skills/
cp -r web-content-extraction ~/.claude/skills/
```

## 更新日志

### 2026-02-15
- 🎉 创建个人 skills 仓库
- 修改 `ljg-clip`：自定义存档路径，添加 fallback 机制
- 升级 `web-content-extraction`：添加可执行脚本层

## 致谢

- 原始 skills 来自 [lijigang/ljg-skill-clip](https://github.com/lijigang/ljg-skill-clip)
- 感谢 lijigang 的优秀设计

## License

参考原始仓库许可证
