# 模具：警示卡片（-a / alert）

**用途**： truth-explorer 等尖锐内容的可视化呈现。当头棒喝的视觉形态。

## 视觉定位

- **气质**：警醒、尖锐、不容回避
- **灵感来源**：警告标志、审讯室灯光、朋克海报、宗教警示牌
- **核心效果**：让用户感觉"被抓住肩膀摇晃"

## 步骤 1：读取模板

Read `~/.claude/skills/ljg-card/assets/warning_template.html`

## 步骤 2：内容预处理

**内容类型识别**：
- **假设/判决书**：核心断言，通常是一句狠话
- **观察与质疑**：成对的"现象+戳破"
- **深入探究**：虚/实双面的关键词与核心关联
- **反思提问**：让人卡住的问题
- **归结**：一记耳光的金句

**提取结构**：
1. **标题**：概念名（如"自由 · 求真"）
2. **假设区块**：核心断言，视觉最突出
3. **解剖区块**：虚/实双面的对比呈现
4. **质问区块**：3-5个反思问题
5. **归结区块**：最终金句

## 步骤 3：色调选择

警示卡片使用**高对比度警示色系**：

| 内容气质 | `{{BG_COLOR}}` | `{{ACCENT_COLOR}}` | `{{TEXT_COLOR}}` |
|----------|---------------|-------------------|-----------------|
| 强烈警告（默认） | `#0A0A0A` | `#FF3B30` | `#FFFFFF` |
| 冷峻审判 | `#1A1A2E` | `#E94560` | `#F5F5F5` |
| 哲学思辨 | `#16213E` | `#E94560` | `#E8E8E8` |
| 危险诱惑 | `#2D0A0A` | `#FF6B6B` | `#FFF5F5` |

默认使用"强烈警告"配色：黑底红字，最高对比度。

## 步骤 4：格式化为 HTML

**特殊元素处理**：

### 假设区块（最突出）
```html
<div class="verdict">
  <span class="verdict-label">假设</span>
  <p class="verdict-text">核心断言内容</p>
</div>
```

### 观察与质疑（成对呈现）
```html
<div class="pair">
  <div class="observation">
    <span class="pair-label">观察</span>
    <p>表面现象</p>
  </div>
  <div class="challenge">
    <span class="pair-label">质疑</span>
    <p>尖锐戳破</p>
  </div>
</div>
```

### 虚/实双面（并排对比）
```html
<div class="dual">
  <div class="void">
    <h3>无形的"虚"</h3>
    <p class="keywords">关键词1、关键词2、关键词3</p>
    <p class="insight">核心关联分析...</p>
  </div>
  <div class="solid">
    <h3>有形的"实"</h3>
    <p class="keywords">关键词1、关键词2、关键词3</p>
    <p class="insight">核心关联分析...</p>
  </div>
</div>
```

### 反思提问（列表形式，带编号）
```html
<div class="questions">
  <h3>反思提问</h3>
  <ol>
    <li>问题1？</li>
    <li>问题2？</li>
  </ol>
</div>
```

### 归结（最终金句，视觉突出）
```html
<div class="conclusion">
  <p>归结金句内容</p>
</div>
```

## 步骤 5：渲染模板

替换模板变量：

| 变量 | 规则 |
|------|------|
| `{{BG_COLOR}}` | 步骤 3 确定的背景色（默认 `#0A0A0A`） |
| `{{ACCENT_COLOR}}` | 步骤 3 确定的强调色（默认 `#FF3B30`） |
| `{{TEXT_COLOR}}` | 步骤 3 确定的文字色（默认 `#FFFFFF`） |
| `{{TITLE}}` | 概念名（如"自由 · 求真"） |
| `{{BODY_HTML}}` | 步骤 4 生成的全部 HTML |
| `{{SOURCE}}` | 来源信息（truth-explorer / 李继刚） |

写入：`/tmp/ljg_cast_warning_{name}.html`

## 步骤 6：截图

```bash
node ~/.claude/skills/ljg-card/assets/capture.js /tmp/ljg_cast_warning_{name}.html ~/Downloads/{name}.png 1080 800 fullpage
```

## 设计原则

1. **不容回避**：高对比度、大字号、强边框
2. **层级分明**：假设最突出，归结次之，细节再次
3. **仪式感**：像一份判决书，像一记耳光
4. **无装饰**：禁渐变、禁阴影、禁圆角——要锋利
