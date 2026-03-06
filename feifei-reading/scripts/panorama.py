#!/usr/bin/env python3
"""飞飞共读 · 全景透镜（动态版）：生成会呼吸的 HTML/SVG 页面。"""
import sys, os, argparse, math, json, webbrowser
import html as H

sys.path.insert(0, os.path.dirname(__file__))
from shared import (
    setup_font, split_sentences, segment, tmp_path,
    score_temperature, score_weight, find_turns,
    _match_lexicon, WARM, COLD, HEAVY, LIGHT,
)


# ── 分析引擎 ─────────────────────────────────────────────
def analyze(text: str) -> dict:
    sentences = split_sentences(text)
    all_words = [segment(s) for s in sentences]
    temps = [score_temperature(w) for w in all_words]
    weights = [score_weight(s, w) for s, w in zip(sentences, all_words)]
    turns_list = [find_turns(w) for w in all_words]

    torques = [0.0]
    for i in range(1, len(sentences)):
        delta = temps[i] - temps[i - 1]
        has_turn = len(turns_list[i]) > 0
        torques.append(abs(delta) * (2.0 if has_turn else 0.5))

    # 力场关键词
    try:
        import jieba.analyse
        kws = jieba.analyse.extract_tags("".join(sentences), topK=14, withWeight=True)
    except ImportError:
        from collections import Counter
        flat = []
        for w in all_words:
            flat.extend(t for t in w if len(t) > 1)
        freq = Counter(flat).most_common(14)
        kws = [(w, c / max(len(flat), 1)) for w, c in freq]

    keywords = []
    for word, weight in kws:
        pos = next((i for i, s in enumerate(sentences) if word in s), 0)
        is_warm = _match_lexicon(word, WARM)
        is_cold = _match_lexicon(word, COLD)
        temp = 1 if is_warm else (-1 if is_cold else 0)
        keywords.append(dict(word=word, weight=weight, pos=pos, temp=temp))

    return dict(
        sentences=sentences, temps=temps, weights=weights,
        turns=turns_list, torques=torques, keywords=keywords,
    )


LENS_TITLES = {
    "all":     ("全景透镜", "用皮肤和重力，看见文字的物理世界"),
    "thermal": ("温度热力图", "逐句冷暖 —— 感受文字划过皮肤的温差"),
    "gravity": ("重力波形", "文字的脉搏 —— 哪里沉、哪里轻、哪里屏住了气"),
    "field":   ("意象力场", "词语的引力与斥力 —— 看见意象怎样聚散"),
    "torque":  ("扭矩标注", "叙事在哪里被扭了一下 —— 隐形的箭头"),
}


# ── HTML 生成 ─────────────────────────────────────────────
def generate_html(data: dict, raw_text: str, lens: str = "all") -> str:
    sentences = data["sentences"]
    temps = data["temps"]
    weights = data["weights"]
    turns = data["turns"]
    torques = data["torques"]
    keywords = data["keywords"]
    n = len(sentences)

    show = set(["thermal", "gravity", "field", "torque"] if lens == "all" else [lens])
    title, subtitle = LENS_TITLES.get(lens, LENS_TITLES["all"])

    # JSON 数据嵌入前端
    js_data = json.dumps(dict(
        sentences=[H.escape(s) for s in sentences],
        temps=temps,
        weights=weights,
        turns=[t for t in turns],
        torques=torques,
        keywords=[dict(word=H.escape(k["word"]), weight=k["weight"],
                       pos=k["pos"], temp=k["temp"]) for k in keywords],
    ), ensure_ascii=False)

    excerpt = H.escape(raw_text[:120] + ("..." if len(raw_text) > 120 else ""))

    # 按需构造 section HTML
    sec_thermal = f"""
  <div class="section" id="sec-thermal">
    <div class="section-title">温度热力图 —— 逐句冷暖</div>
    <div id="thermal-container"></div>
  </div>""" if "thermal" in show else ""

    sec_gravity = f"""
  <div class="section" id="sec-gravity">
    <div class="section-title">重力波形 —— 文字的脉搏</div>
    <svg id="gravity-svg" class="gravity-svg" viewBox="0 0 800 220" preserveAspectRatio="xMidYMid meet" width="100%"></svg>
  </div>""" if "gravity" in show else ""

    sec_field = f"""
  <div class="section" id="sec-field">
    <div class="section-title">意象力场 —— 词语的引力与斥力</div>
    <svg id="field-svg" class="field-svg" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet" width="100%" style="max-width:600px"></svg>
  </div>""" if "field" in show else ""

    sec_torque = f"""
  <div class="section" id="sec-torque">
    <div class="section-title">扭矩标注 —— 叙事在哪里被扭了一下</div>
    <div id="torque-container"></div>
  </div>""" if "torque" in show else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>飞飞共读 · {title}</title>
<style>
/* ── 基础 ────────────────────── */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: #fafaf5;
  color: #333;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;
  line-height: 1.7;
  overflow-x: hidden;
}}
.container {{ max-width: 900px; margin: 0 auto; padding: 60px 24px 100px; }}

/* ── 标题 ────────────────────── */
header {{
  text-align: center;
  margin-bottom: 50px;
  animation: fadeDown 1s ease;
}}
header h1 {{
  font-size: 28px;
  font-weight: 300;
  letter-spacing: 4px;
  color: #444;
}}
header .sub {{
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
}}
.excerpt {{
  font-size: 13px; color: #888;
  background: #f0f0ea; padding: 14px 18px;
  border-radius: 6px; border-left: 3px solid #ccc;
  margin-bottom: 56px; line-height: 1.8;
  animation: fadeIn 1.2s ease 0.3s both;
}}

/* ── 节标题 ───────────────────── */
.section {{ margin-bottom: 64px; }}
.section-title {{
  font-size: 14px; font-weight: 600; color: #777;
  letter-spacing: 2px; text-transform: uppercase;
  padding-bottom: 10px; border-bottom: 1px solid #e0e0d8;
  margin-bottom: 24px;
}}

/* ── 温度热力图 ───────────────── */
.thermal-row {{
  display: flex; align-items: center;
  margin-bottom: 5px; border-radius: 5px;
  padding: 8px 14px; position: relative;
  opacity: 0; transform: translateX(-20px);
  transition: box-shadow 0.3s;
  cursor: default;
}}
.thermal-row.visible {{
  animation: slideIn 0.5s ease forwards;
}}
.thermal-row:hover {{
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transform: scale(1.005);
}}
.thermal-text {{ flex: 1; font-size: 13px; color: #333; }}
.thermal-score {{
  font-size: 12px; font-weight: bold; min-width: 50px;
  text-align: right; font-family: monospace;
}}
/* 冷暖呼吸动画 */
.thermal-row.warm {{ animation: slideIn 0.5s ease forwards, breatheWarm 3s ease-in-out infinite 1s; }}
.thermal-row.cold {{ animation: slideIn 0.5s ease forwards, breatheCold 3s ease-in-out infinite 1s; }}

/* ── 重力波形 ─────────────────── */
.gravity-svg {{ display: block; margin: 0 auto; }}
.gravity-line {{
  fill: none; stroke: #555; stroke-width: 2.5;
  stroke-linecap: round; stroke-linejoin: round;
  stroke-dasharray: 2000; stroke-dashoffset: 2000;
}}
.gravity-line.draw {{ animation: drawLine 2.5s ease forwards; }}
.gravity-fill {{ opacity: 0; }}
.gravity-fill.show {{ animation: fadeIn 1s ease 2.2s forwards; }}
.gravity-dot {{
  opacity: 0; transition: opacity 0.3s;
}}
.gravity-dot.show {{ animation: popIn 0.4s ease forwards; }}
.gravity-label {{ font-size: 11px; opacity: 0; }}
.gravity-label.show {{ animation: fadeIn 0.5s ease 2.8s forwards; }}

/* ── 力场图 ───────────────────── */
.field-svg {{ display: block; margin: 0 auto; }}
.field-node {{
  opacity: 0;
  transform-origin: center;
}}
.field-node.show {{
  animation: nodeAppear 0.6s ease forwards;
}}
.field-node-circle {{
  transition: r 0.3s, filter 0.3s;
}}
.field-node:hover .field-node-circle {{
  filter: brightness(1.2) drop-shadow(0 0 8px currentColor);
}}
.field-link {{
  opacity: 0;
  stroke-dasharray: 4 4;
}}
.field-link.show {{
  animation: linkDraw 0.8s ease forwards;
}}
/* 浮动动画 */
@keyframes floatA {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(3px,-5px); }} }}
@keyframes floatB {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(-4px,3px); }} }}
@keyframes floatC {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(5px,4px); }} }}

/* ── 扭矩标注 ─────────────────── */
.torque-row {{
  display: flex; gap: 12px; align-items: stretch;
  margin-bottom: 4px; opacity: 0;
}}
.torque-row.visible {{ animation: fadeIn 0.4s ease forwards; }}
.torque-text-col {{
  flex: 3; padding: 8px 14px; border-radius: 5px;
  font-size: 13px; position: relative;
  transition: transform 0.3s;
}}
.torque-text-col:hover {{ transform: scale(1.005); }}
.torque-bar-col {{
  flex: 1; display: flex; align-items: center;
}}
.torque-bar {{
  height: 16px; border-radius: 3px;
  width: 0; transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
}}
.torque-turn-tag {{
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  font-size: 10px; color: #b91c1c; font-style: italic;
}}
/* 高扭矩句子的扭动 */
.torque-text-col.twist {{
  animation: twistPulse 0.8s ease 0.5s;
}}

/* ── 动画定义 ─────────────────── */
@keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes fadeDown {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes slideIn {{ from {{ opacity: 0; transform: translateX(-20px); }} to {{ opacity: 1; transform: translateX(0); }} }}
@keyframes breatheWarm {{
  0%,100% {{ box-shadow: inset 0 0 0 rgba(239,68,68,0); }}
  50% {{ box-shadow: inset 0 0 20px rgba(239,68,68,0.06); }}
}}
@keyframes breatheCold {{
  0%,100% {{ box-shadow: inset 0 0 0 rgba(59,130,246,0); }}
  50% {{ box-shadow: inset 0 0 20px rgba(59,130,246,0.06); }}
}}
@keyframes drawLine {{
  to {{ stroke-dashoffset: 0; }}
}}
@keyframes popIn {{
  from {{ opacity: 0; transform: scale(0); }}
  to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes nodeAppear {{
  from {{ opacity: 0; transform: scale(0) rotate(-30deg); }}
  to {{ opacity: 1; transform: scale(1) rotate(0deg); }}
}}
@keyframes linkDraw {{
  from {{ opacity: 0; stroke-dashoffset: 50; }}
  to {{ opacity: 0.4; stroke-dashoffset: 0; }}
}}
@keyframes twistPulse {{
  0% {{ transform: rotate(0deg); }}
  25% {{ transform: rotate(0.8deg); }}
  50% {{ transform: rotate(-0.8deg); }}
  75% {{ transform: rotate(0.4deg); }}
  100% {{ transform: rotate(0deg); }}
}}

/* ── 尾 ──────────────────────── */
.footer {{
  text-align: center; font-size: 11px; color: #ccc;
  margin-top: 80px; letter-spacing: 1px;
}}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>飞飞共读 · {title}</h1>
    <p class="sub">{subtitle}</p>
  </header>
  <div class="excerpt">{excerpt}</div>
  {sec_thermal}{sec_gravity}{sec_field}{sec_torque}

  <div class="footer">飞飞共读 · 触感透镜</div>
</div>

<script>
const D = {js_data};

// ── 工具 ──
function tempColor(t) {{
  // -1=蓝 0=米 1=红
  if (t <= 0) {{
    let p = (t + 1); // 0..1  (0=full blue, 1=neutral)
    let r = Math.round(59 + p * (230 - 59));
    let g = Math.round(130 + p * (228 - 130));
    let b = Math.round(246 + p * (225 - 246));
    return `rgb(${{r}},${{g}},${{b}})`;
  }} else {{
    let p = t; // 0..1  (0=neutral, 1=full red)
    let r = Math.round(230 + p * (239 - 230));
    let g = Math.round(228 + p * (100 - 228));
    let b = Math.round(225 + p * (100 - 225));
    return `rgb(${{r}},${{g}},${{b}})`;
  }}
}}

// ── Intersection Observer ──
function onVisible(el, cb, threshold = 0.15) {{
  const obs = new IntersectionObserver((entries) => {{
    entries.forEach(e => {{ if (e.isIntersecting) {{ cb(e.target); obs.unobserve(e.target); }} }});
  }}, {{ threshold }});
  obs.observe(el);
}}

// ── 温度热力图 ──
(function() {{
  const c = document.getElementById('thermal-container');
  if (!c) return;
  D.sentences.forEach((s, i) => {{
    const row = document.createElement('div');
    row.className = 'thermal-row' + (D.temps[i] > 0.1 ? ' warm' : D.temps[i] < -0.1 ? ' cold' : '');
    row.style.background = tempColor(D.temps[i]);
    row.style.animationDelay = (i * 0.08) + 's, 1s';
    row.innerHTML = `<span class="thermal-text">${{s}}</span><span class="thermal-score" style="color:${{Math.abs(D.temps[i]) > 0.3 ? '#fff' : '#666'}}">${{D.temps[i] > 0 ? '+' : ''}}${{D.temps[i].toFixed(2)}}</span>`;
    c.appendChild(row);
    onVisible(row, el => el.classList.add('visible'));
  }});
}})();

// ── 重力波形 ──
(function() {{
  const svg = document.getElementById('gravity-svg');
  if (!svg) return;
  const n = D.weights.length;
  const padX = 60, padY = 40, W = 800, H = 220;
  const plotW = W - 2 * padX, plotH = H - 2 * padY;

  let pts = D.weights.map((w, i) => {{
    let x = padX + (i / Math.max(n - 1, 1)) * plotW;
    let y = padY + plotH * (1 - w);
    return [x, y];
  }});

  // 平滑
  if (pts.length >= 3) {{
    let smooth = pts.map(p => [...p]);
    for (let i = 1; i < pts.length - 1; i++) {{
      smooth[i][1] = pts[i-1][1] * 0.2 + pts[i][1] * 0.6 + pts[i+1][1] * 0.2;
    }}
    pts = smooth;
  }}

  let linePath = 'M ' + pts.map(p => p[0] + ',' + p[1]).join(' L ');
  let fillPath = linePath + ` L ${{pts[pts.length-1][0]}},${{padY+plotH}} L ${{pts[0][0]}},${{padY+plotH}} Z`;

  // 轴线
  svg.innerHTML += `<line x1="${{padX}}" y1="${{padY+plotH}}" x2="${{padX+plotW}}" y2="${{padY+plotH}}" stroke="#ddd" stroke-width="1"/>`;
  svg.innerHTML += `<text x="${{W/2}}" y="${{H-5}}" text-anchor="middle" fill="#bbb" font-size="11">句序</text>`;
  svg.innerHTML += `<text x="${{padX-8}}" y="${{padY+plotH/2}}" text-anchor="middle" fill="#bbb" font-size="11" transform="rotate(-90,${{padX-8}},${{padY+plotH/2}})">重力</text>`;

  // 填充
  svg.innerHTML += `<path d="${{fillPath}}" fill="#333" class="gravity-fill" opacity="0.08"/>`;
  // 线
  svg.innerHTML += `<path d="${{linePath}}" class="gravity-line"/>`;

  // 标注最重/最轻
  let iMax = D.weights.indexOf(Math.max(...D.weights));
  let iMin = D.weights.indexOf(Math.min(...D.weights));

  let [mx, my] = pts[iMax];
  let [nx, ny] = pts[iMin];
  let maxLabel = D.sentences[iMax].substring(0, 10) + '...';
  let minLabel = D.sentences[iMin].substring(0, 10) + '...';

  svg.innerHTML += `<circle cx="${{mx}}" cy="${{my}}" r="5" fill="#333" class="gravity-dot"/>`;
  svg.innerHTML += `<text x="${{mx}}" y="${{my-12}}" text-anchor="middle" fill="#333" class="gravity-label" font-size="11" font-weight="bold">▼ ${{maxLabel}}</text>`;
  svg.innerHTML += `<circle cx="${{nx}}" cy="${{ny}}" r="5" fill="#aaa" class="gravity-dot"/>`;
  svg.innerHTML += `<text x="${{nx}}" y="${{Math.min(ny+20, padY+plotH-5)}}" text-anchor="middle" fill="#999" class="gravity-label" font-size="11">△ ${{minLabel}}</text>`;

  onVisible(svg, el => {{
    el.querySelector('.gravity-line').classList.add('draw');
    el.querySelector('.gravity-fill').classList.add('show');
    el.querySelectorAll('.gravity-dot').forEach((d, i) => {{
      d.style.animationDelay = (2.5 + i * 0.2) + 's';
      d.classList.add('show');
    }});
    el.querySelectorAll('.gravity-label').forEach(l => l.classList.add('show'));
  }});
}})();

// ── 力场图 ──
(function() {{
  const svg = document.getElementById('field-svg');
  if (!svg) return;
  const kws = D.keywords;
  const n = kws.length;
  if (!n) return;

  const cx0 = 300, cy0 = 300, maxR = 220;
  const maxPos = Math.max(...kws.map(k => k.pos)) || 1;
  const maxW = Math.max(...kws.map(k => k.weight)) || 1;
  const floatAnims = ['floatA', 'floatB', 'floatC'];

  let coords = kws.map((k, i) => {{
    let angle = (k.pos / maxPos) * Math.PI * 1.7 + 0.3;
    let r = 60 + (k.weight / maxW) * maxR * 0.6;
    return [cx0 + r * Math.cos(angle), cy0 + r * Math.sin(angle)];
  }});

  // 连线
  for (let i = 0; i < n; i++) {{
    for (let j = i + 1; j < n; j++) {{
      if (Math.abs(kws[i].pos - kws[j].pos) > 2) continue;
      let samePole = kws[i].temp === kws[j].temp && kws[i].temp !== 0;
      let diffPole = kws[i].temp * kws[j].temp < 0;
      if (!samePole && !diffPole) continue;
      let color = samePole ? '#888' : '#c44';
      let style = samePole ? '' : 'stroke-dasharray:6 4';
      svg.innerHTML += `<line x1="${{coords[i][0]}}" y1="${{coords[i][1]}}" x2="${{coords[j][0]}}" y2="${{coords[j][1]}}" stroke="${{color}}" stroke-width="1" class="field-link" style="${{style}};animation-delay:${{0.5 + j * 0.1}}s"/>`;
    }}
  }}

  // 节点
  kws.forEach((k, i) => {{
    let [x, y] = coords[i];
    let r = 18 + (k.weight / maxW) * 22;
    let fill = k.temp > 0 ? '#ef4444' : k.temp < 0 ? '#3b82f6' : '#999';
    let anim = floatAnims[i % 3];
    let dur = (3 + (i % 3)).toFixed(1);
    let delay = (0.3 + i * 0.12).toFixed(2);

    svg.innerHTML += `<g class="field-node" style="animation-delay:${{delay}}s">
      <circle class="field-node-circle" cx="${{x}}" cy="${{y}}" r="${{r}}" fill="${{fill}}" opacity="0.8"
        style="animation:${{anim}} ${{dur}}s ease-in-out infinite; color:${{fill}}"/>
      <text x="${{x}}" y="${{y+4}}" text-anchor="middle" fill="white" font-size="12" font-weight="bold"
        style="animation:${{anim}} ${{dur}}s ease-in-out infinite; pointer-events:none">${{k.word}}</text>
    </g>`;
  }});

  // 图例
  svg.innerHTML += `<circle cx="520" cy="30" r="8" fill="#ef4444" opacity="0.8"/><text x="535" y="34" fill="#888" font-size="11">暖</text>`;
  svg.innerHTML += `<circle cx="520" cy="52" r="8" fill="#3b82f6" opacity="0.8"/><text x="535" y="56" fill="#888" font-size="11">冷</text>`;
  svg.innerHTML += `<circle cx="520" cy="74" r="8" fill="#999" opacity="0.8"/><text x="535" y="78" fill="#888" font-size="11">中性</text>`;

  onVisible(svg, el => {{
    el.querySelectorAll('.field-node').forEach(n => n.classList.add('show'));
    el.querySelectorAll('.field-link').forEach(l => l.classList.add('show'));
  }});
}})();

// ── 扭矩标注 ──
(function() {{
  const c = document.getElementById('torque-container');
  if (!c) return;
  const maxT = Math.max(...D.torques) || 1;

  D.sentences.forEach((s, i) => {{
    const row = document.createElement('div');
    row.className = 'torque-row';
    row.style.animationDelay = (i * 0.06) + 's';

    let bg = D.temps[i] > 0.1 ? '#fde8e8' : D.temps[i] < -0.1 ? '#dbeafe' : '#f5f5f0';
    let barColor = i === 0 ? '#ddd' : (D.temps[i] - D.temps[i-1]) > 0 ? '#ef4444' : (D.temps[i] - D.temps[i-1]) < 0 ? '#3b82f6' : '#ddd';
    let barW = (D.torques[i] / maxT) * 100;
    let isHighTorque = D.torques[i] > maxT * 0.6;

    let turnTag = D.turns[i].length ? `<span class="torque-turn-tag">&gt;&gt; ${{D.turns[i].join(' ')}}</span>` : '';

    row.innerHTML = `
      <div class="torque-text-col${{isHighTorque ? ' twist' : ''}}" style="background:${{bg}}">
        ${{s}}${{turnTag}}
      </div>
      <div class="torque-bar-col">
        <div class="torque-bar" style="background:${{barColor}}" data-width="${{barW}}%"></div>
      </div>`;
    c.appendChild(row);

    onVisible(row, el => {{
      el.classList.add('visible');
      const bar = el.querySelector('.torque-bar');
      requestAnimationFrame(() => {{
        bar.style.width = bar.dataset.width;
      }});
    }});
  }});
}})();
</script>
</body>
</html>"""


def panorama(text: str, output: str, lens: str = "all"):
    data = analyze(text)
    if not data["sentences"]:
        print("没有可分析的句子。")
        return

    html = generate_html(data, text, lens=lens)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    title = LENS_TITLES.get(lens, LENS_TITLES["all"])[0]
    print(f"{title}已保存 → {output}")
    abs_path = os.path.abspath(output).replace("\\", "/")
    webbrowser.open(f"file:///{abs_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="飞飞共读 · 触感透镜（动态版）")
    parser.add_argument("--text", type=str, help="待分析文本")
    parser.add_argument("--file", type=str, help="从文件读取文本")
    parser.add_argument("--lens", type=str, default="all",
                        choices=["all", "thermal", "gravity", "field", "torque"],
                        help="选择透镜: thermal|gravity|field|torque|all")
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()

    if args.output is None:
        name = "panorama" if args.lens == "all" else args.lens
        args.output = tmp_path(name, ".html")

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    panorama(text, args.output, lens=args.lens)
