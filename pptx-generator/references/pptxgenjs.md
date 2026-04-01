# PptxGenJS Tutorial

## Setup & Basic Structure

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';  // or 'LAYOUT_16x10', 'LAYOUT_4x3', 'LAYOUT_WIDE'
pres.author = 'Your Name';
pres.title = 'Presentation Title';

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "Presentation.pptx" });
```

## Layout Dimensions

Slide dimensions (coordinates in inches):
- `LAYOUT_16x9`: 10" x 5.625" (default)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

---

## Text & Formatting

```javascript
// Basic text
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2, fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true, align: "center", valign: "middle"
});

// Character spacing (use charSpacing, not letterSpacing which is silently ignored)
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });

// Rich text arrays
slide.addText([
  { text: "Bold ", options: { bold: true } },
  { text: "Italic ", options: { italic: true } }
], { x: 1, y: 3, w: 8, h: 1 });

// Multi-line text (requires breakLine: true)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }  // Last item doesn't need breakLine
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// Text box margin (internal padding)
slide.addText("Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  margin: 0  // Use 0 when aligning text with other elements like shapes or icons
});
```

**Tip:** Text boxes have internal margin by default. Set `margin: 0` when you need text to align precisely with shapes, lines, or icons at the same x-position.

---

## Lists & Bullets

```javascript
// CORRECT: Multiple bullets
slide.addText([
  { text: "First item", options: { bullet: true, breakLine: true } },
  { text: "Second item", options: { bullet: true, breakLine: true } },
  { text: "Third item", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// WRONG: Never use unicode bullets
slide.addText("* First item", { ... });  // Creates double bullets

// Sub-items and numbered lists
{ text: "Sub-item", options: { bullet: true, indentLevel: 1 } }
{ text: "First", options: { bullet: { type: "number" }, breakLine: true } }
```

---

## Shapes

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" }, line: { color: "000000", width: 2 }
});

slide.addShape(pres.shapes.OVAL, { x: 4, y: 1, w: 2, h: 2, fill: { color: "0000FF" } });

slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0, line: { color: "FF0000", width: 3, dashType: "dash" }
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "0088CC", transparency: 50 }
});

// Rounded rectangle (rectRadius only works with ROUNDED_RECTANGLE, not RECTANGLE)
// Don't pair with rectangular accent overlays -- they won't cover rounded corners. Use RECTANGLE instead.
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// With shadow
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15 }
});
```

Shadow options:

| Property | Type | Range | Notes |
|----------|------|-------|-------|
| `type` | string | `"outer"`, `"inner"` | |
| `color` | string | 6-char hex (e.g. `"000000"`) | No `#` prefix, no 8-char hex -- see Common Pitfalls |
| `blur` | number | 0-100 pt | |
| `offset` | number | 0-200 pt | **Must be non-negative** -- negative values corrupt the file |
| `angle` | number | 0-359 degrees | Direction the shadow falls (135 = bottom-right, 270 = upward) |
| `opacity` | number | 0.0-1.0 | Use this for transparency, never encode in color string |

To cast a shadow upward (e.g. on a footer bar), use `angle: 270` with a positive offset -- do **not** use a negative offset.

**Note**: Gradient fills are not natively supported. Use a gradient image as a background instead.

---

## Images

### Image Sources

```javascript
// From file path
slide.addImage({ path: "images/chart.png", x: 1, y: 1, w: 5, h: 3 });

// From URL
slide.addImage({ path: "https://example.com/image.jpg", x: 1, y: 1, w: 5, h: 3 });

// From base64 (faster, no file I/O)
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });
```

### Image Options

```javascript
slide.addImage({
  path: "image.png",
  x: 1, y: 1, w: 5, h: 3,
  rotate: 45,              // 0-359 degrees
  rounding: true,          // Circular crop
  transparency: 50,        // 0-100
  flipH: true,             // Horizontal flip
  flipV: false,            // Vertical flip
  altText: "Description",  // Accessibility
  hyperlink: { url: "https://example.com" }
});
```

### Image Sizing Modes

```javascript
// Contain - fit inside, preserve ratio
{ sizing: { type: 'contain', w: 4, h: 3 } }

// Cover - fill area, preserve ratio (may crop)
{ sizing: { type: 'cover', w: 4, h: 3 } }

// Crop - cut specific portion
{ sizing: { type: 'crop', x: 0.5, y: 0.5, w: 2, h: 2 } }
```

### Calculate Dimensions (preserve aspect ratio)

```javascript
const origWidth = 1978, origHeight = 923, maxHeight = 3.0;
const calcWidth = maxHeight * (origWidth / origHeight);
const centerX = (10 - calcWidth) / 2;

slide.addImage({ path: "image.png", x: centerX, y: 1.2, w: calcWidth, h: maxHeight });
```

### Supported Formats

- **Standard**: PNG, JPG, GIF (animated GIFs work in Microsoft 365)
- **SVG**: Works in modern PowerPoint/Microsoft 365

---

## Icons

Use react-icons to generate SVG icons, then rasterize to PNG for universal compatibility.

### Setup

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle, FaChartLine } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}
```

### Add Icon to Slide

```javascript
const iconData = await iconToBase64Png(FaCheckCircle, "#4472C4", 256);

slide.addImage({
  data: iconData,
  x: 1, y: 1, w: 0.5, h: 0.5  // Size in inches
});
```

**Note**: Use size 256 or higher for crisp icons. The size parameter controls the rasterization resolution, not the display size on the slide (which is set by `w` and `h` in inches).

### Icon Libraries

Install: `npm install -g react-icons react react-dom sharp`

Popular icon sets in react-icons:
- `react-icons/fa` - Font Awesome
- `react-icons/md` - Material Design
- `react-icons/hi` - Heroicons
- `react-icons/bi` - Bootstrap Icons

---

## Slide Backgrounds

```javascript
// Solid color
slide.background = { color: "F1F1F1" };

// Color with transparency
slide.background = { color: "FF3399", transparency: 50 };

// Image from URL
slide.background = { path: "https://example.com/bg.jpg" };

// Image from base64
slide.background = { data: "image/png;base64,iVBORw0KGgo..." };
```

---

## Tables

```javascript
slide.addTable([
  ["Header 1", "Header 2"],
  ["Cell 1", "Cell 2"]
], {
  x: 1, y: 1, w: 8, h: 2,
  border: { pt: 1, color: "999999" }, fill: { color: "F1F1F1" }
});

// Advanced with merged cells
let tableData = [
  [{ text: "Header", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } }, "Cell"],
  [{ text: "Merged", options: { colspan: 2 } }]
];
slide.addTable(tableData, { x: 1, y: 3.5, w: 8, colW: [4, 4] });
```

---

## Charts

```javascript
// Bar chart
slide.addChart(pres.charts.BAR, [{
  name: "Sales", labels: ["Q1", "Q2", "Q3", "Q4"], values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.6, w: 6, h: 3, barDir: 'col',
  showTitle: true, title: 'Quarterly Sales'
});

// Line chart
slide.addChart(pres.charts.LINE, [{
  name: "Temp", labels: ["Jan", "Feb", "Mar"], values: [32, 35, 42]
}], { x: 0.5, y: 4, w: 6, h: 3, lineSize: 3, lineSmooth: true });

// Pie chart
slide.addChart(pres.charts.PIE, [{
  name: "Share", labels: ["A", "B", "Other"], values: [35, 45, 20]
}], { x: 7, y: 1, w: 5, h: 4, showPercent: true });
```

### Better-Looking Charts

Default charts look dated. Apply these options for a modern, clean appearance:

```javascript
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1, w: 9, h: 4, barDir: "col",

  // Custom colors (match your presentation palette)
  chartColors: ["0D9488", "14B8A6", "5EEAD4"],

  // Clean background
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },

  // Muted axis labels
  catAxisLabelColor: "64748B",
  valAxisLabelColor: "64748B",

  // Subtle grid (value axis only)
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },

  // Data labels on bars
  showValue: true,
  dataLabelPosition: "outEnd",
  dataLabelColor: "1E293B",

  // Hide legend for single series
  showLegend: false,
});
```

**Key styling options:**
- `chartColors: [...]` - hex colors for series/segments
- `chartArea: { fill, border, roundedCorners }` - chart background
- `catGridLine/valGridLine: { color, style, size }` - grid lines (`style: "none"` to hide)
- `lineSmooth: true` - curved lines (line charts)
- `legendPos: "r"` - legend position: "b", "t", "l", "r", "tr"

---

## Slide Masters

```javascript
pres.defineSlideMaster({
  title: 'TITLE_SLIDE', background: { color: '283A5E' },
  objects: [{
    placeholder: { options: { name: 'title', type: 'title', x: 1, y: 2, w: 8, h: 2 } }
  }]
});

let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("My Title", { placeholder: "title" });
```

---

## Chart Recipes

### Stacked Column Chart

```javascript
slide.addChart(pres.charts.BAR, [
  { name: "Product A", labels: ["Q1", "Q2", "Q3", "Q4"], values: [30, 45, 35, 50] },
  { name: "Product B", labels: ["Q1", "Q2", "Q3", "Q4"], values: [20, 25, 40, 35] },
  { name: "Product C", labels: ["Q1", "Q2", "Q3", "Q4"], values: [15, 20, 25, 30] }
], {
  x: 0.5, y: 1, w: 6, h: 3.5,
  barDir: "col",
  barGrouping: "stacked",
  chartColors: [theme.primary, theme.secondary, theme.accent],
  chartArea: { fill: { color: "FFFFFF" } },
  catGridLine: { style: "none" },
  valGridLine: { color: theme.light, size: 0.5 },
  showValue: false,
  legendPos: "b",
  catAxisLabelColor: theme.primary,
  valAxisLabelColor: theme.primary
});
```

### Smooth Area Line Chart

```javascript
slide.addChart(pres.charts.LINE, [
  { name: "Revenue", labels: ["Jan", "Feb", "Mar", "Apr", "May"], values: [12, 19, 15, 28, 35] }
], {
  x: 0.5, y: 1, w: 6, h: 3.5,
  lineSize: 3,
  lineSmooth: true,
  lineDataSymbol: "circle",
  lineDataSymbolSize: 8,
  chartColors: [theme.accent],
  chartArea: { fill: { color: "FFFFFF" } },
  showLegend: false,
  catGridLine: { style: "none" },
  valGridLine: { color: theme.light, size: 0.5 },
  dataLabelPosition: "top",
  showValue: true,
  dataLabelColor: theme.primary,
  dataLabelFontSize: 10
});
```

### Doughnut Chart with Center Label

```javascript
slide.addChart(pres.charts.DOUGHNUT, [
  { name: "Share", labels: ["A", "B", "C"], values: [55, 30, 15] }
], {
  x: 0.5, y: 1, w: 4, h: 4,
  chartColors: [theme.primary, theme.secondary, theme.light],
  showPercent: true,
  dataLabelColor: "FFFFFF",
  dataLabelFontSize: 11,
  legendPos: "r",
  holeSize: 60  // percent
});

// Add center label manually
slide.addText("55%", {
  x: 1.25, y: 2.6, w: 1.5, h: 0.6,
  fontSize: 28, bold: true, color: theme.primary,
  align: "center", valign: "middle"
});
```

### Radar Chart (Competency / Dimension)

```javascript
slide.addChart(pres.charts.RADAR, [
  { name: "Current", labels: ["Speed", "Quality", "Cost", "Service", "Innovation"], values: [80, 70, 90, 65, 75] },
  { name: "Target", labels: ["Speed", "Quality", "Cost", "Service", "Innovation"], values: [90, 90, 85, 85, 90] }
], {
  x: 0.5, y: 1, w: 5, h: 4,
  chartColors: [theme.accent, theme.light],
  lineSize: 2,
  showLegend: true,
  legendPos: "b",
  radarStyle: "filled"
});
```

---

## Shape-Composed Infographics

When native charts are too plain or don't support the desired shape, build infographics from basic shapes. These render flawlessly and are fully palette-controllable.

### Progress Ring (Completion / OKR)

```javascript
const cx = 2.5, cy = 2.8, r = 1.5, stroke = 0.25;
const pct = 0.72;

// Background ring
slide.addShape(pres.shapes.OVAL, {
  x: cx - r, y: cy - r, w: r * 2, h: r * 2,
  fill: { color: "FFFFFF" },
  line: { color: theme.light, width: stroke * 72 }
});

// Progress arc (simulate with a partial arc shape or overlay blocks)
// For precise arcs, generate an SVG path and add as image (see External Chart Rendering)

// Center text
slide.addText("72%", {
  x: cx - 0.8, y: cy - 0.3, w: 1.6, h: 0.6,
  fontSize: 36, bold: true, color: theme.primary,
  align: "center", valign: "middle"
});
```

### Funnel (Conversion Stages)

```javascript
const stages = [
  { label: "Visitors", value: 10000, color: theme.primary },
  { label: "Leads", value: 6000, color: theme.secondary },
  { label: "Customers", value: 2500, color: theme.accent },
  { label: "Repeat", value: 800, color: theme.light }
];

let y = 1.0;
stages.forEach((s, i) => {
  const maxW = 6;
  const h = 0.7;
  const w = maxW * (s.value / stages[0].value);
  const x = 0.5 + (maxW - w) / 2;

  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: s.color },
    rectRadius: 0.05
  });

  slide.addText(`${s.label}: ${s.value.toLocaleString()}`, {
    x, y, w, h,
    color: "FFFFFF", fontSize: 14, align: "center", valign: "middle"
  });

  y += h + 0.15;
});
```

### Pictogram Bar (Repeated Icons)

```javascript
// Each icon = 1 unit. 8 icons = value of 8.
const rows = 3;
const cols = 10;
const iconW = 0.35;
const iconH = 0.35;
const gap = 0.08;
const values = [7, 5, 9];
const labels = ["Team A", "Team B", "Team C"];

values.forEach((val, r) => {
  const y = 1.5 + r * (iconH + gap + 0.3);
  slide.addText(labels[r], { x: 0.5, y: y - 0.25, w: 1.2, h: 0.2, fontSize: 12, bold: true, color: theme.primary });

  for (let c = 0; c < cols; c++) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 1.8 + c * (iconW + gap),
      y,
      w: iconW,
      h: iconH,
      fill: { color: c < val ? theme.accent : theme.light },
      rectRadius: 0.03
    });
  }
});
```

### Horizontal Progress Bars

```javascript
const items = [
  { label: "Design", val: 85 },
  { label: "Engineering", val: 62 },
  { label: "Marketing", val: 95 }
];

let y = 1.5;
items.forEach(item => {
  const maxW = 5;
  const h = 0.25;

  // Track
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2, y, w: maxW, h,
    fill: { color: theme.light },
    rectRadius: h / 2
  });

  // Fill
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2, y, w: maxW * (item.val / 100), h,
    fill: { color: theme.accent },
    rectRadius: h / 2
  });

  slide.addText(item.label, { x: 0.5, y: y - 0.02, w: 1.4, h: 0.3, fontSize: 12, color: theme.primary });
  slide.addText(item.val + "%", { x: 7.2, y: y - 0.02, w: 0.8, h: 0.3, fontSize: 12, bold: true, color: theme.primary });

  y += 0.55;
});
```

---

## External Chart Rendering

For charts that exceed PptxGenJS native capabilities (Sankey, Sunburst, Heatmap, advanced Radar, 3DBar, gradient-rich charts), render externally and embed as PNG.

See: [`references/chart-external.md`](./chart-external.md) for the complete ECharts → Sharp → Base64 workflow.

Quick pattern:

```javascript
// 1. Generate chart as PNG base64 (via Node script using ECharts + Sharp)
// 2. Embed into slide
slide.addImage({
  data: pngBase64String,
  x: 0.5, y: 1, w: 6, h: 3.5
});
```

**When to use external rendering:**
- Complex categorical heatmaps
- Hierarchical visuals (treemap, sunburst)
- Flow diagrams (sankey, graph)
- Gradient/texture charts where shapes can't substitute
- Precise arc/pie segments with custom labels

---

## Common Pitfalls

These issues cause file corruption, visual bugs, or broken output. Avoid them.

1. **NEVER use "#" with hex colors** - causes file corruption
   ```javascript
   color: "FF0000"      // CORRECT
   color: "#FF0000"     // WRONG
   ```

2. **NEVER encode opacity in hex color strings** - 8-char colors (e.g., `"00000020"`) corrupt the file. Use the `opacity` property instead.
   ```javascript
   shadow: { type: "outer", blur: 6, offset: 2, color: "00000020" }          // CORRUPTS FILE
   shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.12 }  // CORRECT
   ```

3. **Use `bullet: true`** - NEVER unicode symbols like "o" (creates double bullets)

4. **Use `breakLine: true`** between array items or text runs together

5. **Avoid `lineSpacing` with bullets** - causes excessive gaps; use `paraSpaceAfter` instead

6. **Each presentation needs fresh instance** - don't reuse `pptxgen()` objects

7. **NEVER reuse option objects across calls** - PptxGenJS mutates objects in-place (e.g. converting shadow values to EMU). Sharing one object between multiple calls corrupts the second shape.
   ```javascript
   const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });  // second call gets already-converted values
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });

   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });  // fresh object each time
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
   ```

8. **Don't use `ROUNDED_RECTANGLE` with accent borders** - rectangular overlay bars won't cover rounded corners. Use `RECTANGLE` instead.
   ```javascript
   // WRONG: Accent bar doesn't cover rounded corners
   slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 1, y: 1, w: 3, h: 1.5, fill: { color: "FFFFFF" } });
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 0.08, h: 1.5, fill: { color: "0891B2" } });

   // CORRECT: Use RECTANGLE for clean alignment
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 3, h: 1.5, fill: { color: "FFFFFF" } });
   slide.addShape(pres.shapes.RECTANGLE, { x: 1, y: 1, w: 0.08, h: 1.5, fill: { color: "0891B2" } });
   ```

---

## Quick Reference

- **Shapes**: RECTANGLE, OVAL, LINE, ROUNDED_RECTANGLE
- **Charts**: BAR, LINE, PIE, DOUGHNUT, SCATTER, BUBBLE, RADAR
- **Layouts**: LAYOUT_16x9 (10"x5.625"), LAYOUT_16x10, LAYOUT_4x3, LAYOUT_WIDE
- **Alignment**: "left", "center", "right"
- **Chart data labels**: "outEnd", "inEnd", "center"
