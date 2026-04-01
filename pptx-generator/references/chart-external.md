# External Chart Rendering | 外部图表渲染

当 PptxGenJS 原生图表（BAR / LINE / PIE / DOUGHNUT / SCATTER / BUBBLE / RADAR）无法满足视觉需求时，使用 **ECharts + Sharp** 生成高保真 PNG，以 base64 形式嵌入幻灯片。

**适用场景：**
- 复杂热力图、树图、桑基图、旭日图
- 多层雷达、K线、仪表盘、水球图
- 需要渐变纹理或精确标签位置的图表
- 组合图表超出原生 API 表达能力

---

## 准备工作

```bash
npm install -g echarts sharp
```

> `echarts` 用于生成 SVG，`sharp` 用于将 SVG 栅格化为高分辨率 PNG。

---

## 完整脚本：生成 base64 PNG

```javascript
const echarts = require("echarts");
const sharp = require("sharp");

async function renderChartToBase64(option, width = 800, height = 450) {
  // 1. 初始化 echarts 实例（使用 null 容器生成 SVG）
  const chart = echarts.init(null, null, {
    renderer: "svg",
    ssr: true,
    width,
    height
  });

  // 2. 设置图表配置
  chart.setOption(option);

  // 3. 导出 SVG 字符串
  const svgStr = chart.renderToSVGString();

  // 4. Sharp 栅格化（2x 分辨率保证投影清晰）
  const pngBuffer = await sharp(Buffer.from(svgStr))
    .resize(width * 2, height * 2)
    .png()
    .toBuffer();

  // 5. 返回 base64
  return "image/png;base64," + pngBuffer.toString("base64");
}

// 示例：调用
(async () => {
  const option = {
    backgroundColor: "#ffffff",
    color: ["#264653", "#2a9d8f", "#e9c46a"],
    title: { text: "Quarterly Revenue", left: "center", textStyle: { fontSize: 18 } },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: ["Q1", "Q2", "Q3", "Q4"] },
    yAxis: { type: "value" },
    series: [{
      data: [120, 200, 150, 80],
      type: "bar",
      barWidth: "50%",
      itemStyle: { borderRadius: [4, 4, 0, 0] }
    }]
  };

  const base64 = await renderChartToBase64(option, 800, 450);
  console.log(base64); // 粘贴到 PptxGenJS 的 data 字段
})();
```

---

## 与 PptxGenJS 集成

生成的 base64 字符串直接作为 `data` 字段传入 `slide.addImage`：

```javascript
const PptxGenJS = require("pptxgenjs");
const pres = new PptxGenJS();
const slide = pres.addSlide();

// 从外部脚本获取的 base64
const chartBase64 = "image/png;base64,iVBORw0KGgo...";

slide.addImage({
  data: chartBase64,
  x: 0.5,
  y: 1,
  w: 6,
  h: 3.5
});

// 添加标题和结论（仍然用 PptxGenJS 文本保证一致性和可编辑性）
slide.addText("用户增长趋势", { x: 0.5, y: 0.4, w: 6, h: 0.5, fontSize: 24, bold: true, color: theme.primary });
slide.addText("Q3 出现明显回落，需重点关注留存策略", { x: 0.5, y: 4.7, w: 6, h: 0.3, fontSize: 12, color: theme.secondary });

pres.writeFile({ fileName: "output.pptx" });
```

---

## ECharts 配色与主题对接

**必须与当前 PPT 的调色板保持一致**。PptxGenJS 的 theme 对象通常包含 5 个主色，映射到 ECharts `color` 数组即可。

例如使用第 10 套 "Education & Charts"（`#264653`, `#2a9d8f`, `#e9c46a`, `#f4a261`, `#e76f51`）：

```javascript
const theme = {
  primary: "264653",
  secondary: "2a9d8f",
  accent: "e9c46a",
  light: "f4a261",
  bg: "e76f51"
};

const echartsColors = [
  `#${theme.primary}`,
  `#${theme.secondary}`,
  `#${theme.accent}`,
  `#${theme.light}`,
  `#${theme.bg}`
];

// 在 ECharts option 中使用
{
  backgroundColor: "#ffffff",
  color: echartsColors,
  // ...
}
```

**字体匹配建议：**
- 中文正文：`fontFamily: "Microsoft YaHei"`
- 英文标题：`fontFamily: "Arial"`

---

## 推荐图表类型映射

| 数据故事 | PptxGenJS Native | 外部渲染替代 |
|----------|------------------|--------------|
| 简单对比柱状图 | BAR | 柱状图（圆角标签版） |
| 时间趋势 | LINE | 面积图 / 折线+柱状组合 |
| 占比 | PIE / DOUGHNUT | 南丁格尔玫瑰图 / 环形图 |
| 多维度评分 | RADAR | 多层雷达 / 仪表盘组合 |
| 转化率漏斗 | Shape-composed | ECharts 漏斗图 |
| 用户路径/流量 | — | 桑基图 |
| 层级结构 | — | 树图 / 旭日图 |
| 地理分布 | — | 地图热力图 |
| 相关性矩阵 | — | 热力图 |

---

## 输出尺寸建议

为了保持 PPT 中图表的清晰度，建议生成尺寸为显示尺寸的 **2 倍**，再通过 `w` / `h` 控制显示大小。

```javascript
// PPT 显示区域: 6" x 3.5"
// 生成像素: 1200 x 700 (150 DPI 下约为 2x)
const base64 = await renderChartToBase64(option, 800, 450);

// 在 slide 中显示
slide.addImage({ data: base64, x: 0.5, y: 1, w: 6, h: 3.5 });
```

> 过大（>2000px）会导致 PPT 文件体积暴涨；过小（<600px）会出现锯齿。

---

## 限制与陷阱

### 陷阱 1：SVG 中的外部资源
ECharts SVG 默认不内嵌字体。如果使用了特殊字体，Sharp 栅格化时可能 fallback 到系统默认字体。解决方式：
- 使用系统自带字体（Microsoft YaHei / Arial）
- 或将文字导出为路径（ECharts 不支持，需改用 Canvas + 字体预加载）

### 陷阱 2：透明背景
如果希望图表背景透明，ECharts 中设置 `backgroundColor: "transparent"`，Sharp 会正确保留 PNG 的 alpha 通道。但 PPT 中某些版本对透明 PNG 渲染有差异，**建议显式设置与幻灯片一致的背景色**。

### 陷阱 3：异步脚本与 compile.js
外部渲染脚本是 `async` 的，但 `pptxgenjs.md` 明确禁止 `createSlide` 使用 async。正确做法：
1. **预渲染**：在 compile.js 执行前，先用 Node 脚本生成所有 chart PNG 到 `slides/imgs/chart-01.png`
2. **同步嵌入**：`slide.addImage({ path: "slides/imgs/chart-01.png", ... })`

```javascript
// 预渲染脚本（可独立运行）
node scripts/prerender-charts.js

// compile.js 中同步读取图片路径
slide.addImage({ path: "imgs/chart-01.png", x: 0.5, y: 1, w: 6, h: 3.5 });
```

### 陷阱 4：颜色带 `#`
与 PptxGenJS 不同，**ECharts 中颜色必须带 `#`**。在传入 PptxGenJS 的 theme 前要注意区分：
- ECharts: `#264653`
- PptxGenJS: `264653`

### 陷阱 5：base64 字符串过长
超长 base64 直接写入 `.js` 文件会影响可读性。当单张图 base64 > 50KB 时，**优先写入文件**而不是内联字符串。

---

## Workflow 建议

### 方案 A：内联 base64（少量图表 < 3 张）
```
1. 运行 render script 获取 base64
2. 复制粘贴到 slide-XX.js
3. slide.addImage({ data: base64, ... })
```

### 方案 B：文件引用（推荐，图表 >= 3 张 或 团队协作）
```
slides/
├── slide-01.js
├── slide-02.js
├── imgs/
│   ├── chart-revenue.png      ← 预渲染输出
│   └── chart-funnel.png
└── scripts/
│   └── prerender-charts.js    ← 统一渲染入口
└── output/
    └── presentation.pptx
```

**compile.js 中只保留同步的图片加载：**
```javascript
slide.addImage({ path: "imgs/chart-revenue.png", x: 0.5, y: 1, w: 6, h: 3.5 });
```

---

## QA 检查清单

- [ ] 图表 PNG 已正确生成，无白边/截断
- [ ] 图表颜色与当前 PPT 调色板一致
- [ ] 文字在 PPT 中打开后清晰可读（无模糊）
- [ ] 文件体积未异常膨胀（单张 PNG < 300KB 为佳）
- [ ] `markitdown` 提取后，图表旁边的结论文字完整无 placeholder
- [ ] 若使用预渲染文件，`imgs/` 目录已随 `.pptx` 一并交付或说明运行方式

---

## 示例：预渲染脚本

```javascript
// slides/scripts/prerender-charts.js
const fs = require("fs");
const path = require("path");
const echarts = require("echarts");
const sharp = require("sharp");

const OUT_DIR = path.join(__dirname, "../imgs");
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

async function saveChart(filename, option, width = 800, height = 450) {
  const chart = echarts.init(null, null, { renderer: "svg", ssr: true, width, height });
  chart.setOption(option);
  const svg = chart.renderToSVGString();
  const png = await sharp(Buffer.from(svg)).resize(width * 2, height * 2).png().toBuffer();
  fs.writeFileSync(path.join(OUT_DIR, filename), png);
  console.log("Saved:", filename);
}

(async () => {
  await saveChart("chart-bar.png", {
    backgroundColor: "#ffffff",
    color: ["#264653", "#2a9d8f", "#e9c46a"],
    xAxis: { type: "category", data: ["A", "B", "C"] },
    yAxis: { type: "value" },
    series: [{ data: [120, 200, 150], type: "bar" }]
  });
})();
```

运行：
```bash
node slides/scripts/prerender-charts.js
```

---

> **设计原则**：外部渲染是 PptxGenJS 原生的增强层，不是替代层。能用原生图表讲清楚的故事，优先用原生以保持文件轻量和可编辑性；原生确实不足时，再用外部渲染兜底。
