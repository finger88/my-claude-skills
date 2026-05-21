const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const skillDir = [
  process.env.LJG_CARD_SKILL_DIR,
  path.resolve(__dirname, "..", "..", "ljg-card"),
  "C:\\Users\\HONOR\\my-claude-skills\\ljg-card",
].filter(Boolean).find((dir) => fs.existsSync(path.join(dir, "assets", "capture.js")));

if (!skillDir) {
  throw new Error("Cannot find ljg-card. Set LJG_CARD_SKILL_DIR or place ljg-card beside see-me-card.");
}

const capturePath = path.join(skillDir, "assets", "capture.js");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function lines(value) {
  return escapeHtml(value).replace(/\n/g, "<br>");
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function html(spec) {
  const nodes = (spec.nodes || []).slice(0, 5);
  const sourceEcho = spec.sourceEcho || spec.rawThought || spec.originalThought || "";
  const nodeHtml = nodes.map((node, index) => `
      <article class="node node-${index + 1}">
        <span class="node-number">${escapeHtml(node.number || String(index + 1).padStart(2, "0"))}</span>
        <h2>${escapeHtml(node.title)}</h2>
        <p>${escapeHtml(node.body)}</p>
      </article>`).join("");
  const sourceEchoHtml = sourceEcho
    ? `<div class="source-echo" aria-hidden="true">${lines(sourceEcho)}</div>`
    : "";

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080, initial-scale=1.0">
<title>${escapeHtml(spec.fileBase || "see-me-card")}</title>
<style>
  :root {
    --paper: ${spec.paper || "#F5F7F1"};
    --paper-deep: ${spec.paperDeep || "#E9EFE7"};
    --ink: ${spec.ink || "#232820"};
    --ink-soft: ${spec.inkSoft || "#586158"};
    --ink-faint: ${spec.inkFaint || "#8C9488"};
    --accent: ${spec.accent || "#426F62"};
    --rule: rgba(66, 111, 98, 0.28);
    --rule-soft: rgba(66, 111, 98, 0.14);
    --font-serif: "Noto Serif SC", "Source Han Serif SC", "Songti SC", "SimSun", serif;
    --font-sans: "Geist", "Satoshi", "Microsoft YaHei", system-ui, sans-serif;
  }

  * { box-sizing: border-box; }
  html, body {
    width: 1080px;
    height: 1440px;
    margin: 0;
    overflow: hidden;
    background: var(--paper);
  }
  body {
    color: var(--ink);
    font-family: var(--font-serif);
  }
  .card {
    position: relative;
    width: 1080px;
    height: 1440px;
    padding: 78px 82px 58px;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.46), rgba(255, 255, 255, 0) 38%),
      repeating-linear-gradient(90deg, rgba(35, 40, 32, 0.018) 0, rgba(35, 40, 32, 0.018) 1px, transparent 1px, transparent 9px),
      linear-gradient(135deg, var(--paper) 0%, var(--paper-deep) 100%);
  }
  .spine {
    position: absolute;
    left: 82px;
    top: 80px;
    bottom: 62px;
    width: 2px;
    background: linear-gradient(180deg, var(--accent), rgba(66, 111, 98, 0.04));
  }
  .source-echo {
    position: absolute;
    left: 126px;
    top: 430px;
    width: 820px;
    color: rgba(66, 111, 98, 0.105);
    font: 700 58px/1.5 var(--font-serif);
    letter-spacing: 0;
    white-space: pre-wrap;
    transform: rotate(-2deg);
    transform-origin: 20% 20%;
    z-index: 0;
  }
  .spine,
  .meta,
  .index,
  .title-block,
  .side-formula,
  .quote,
  .map,
  .closing,
  .footer {
    z-index: 1;
  }
  .meta {
    position: absolute;
    left: 132px;
    top: 80px;
    display: flex;
    align-items: center;
    gap: 18px;
    font: 500 21px/1.4 var(--font-sans);
    color: var(--ink-faint);
  }
  .meta .dot {
    width: 7px;
    height: 7px;
    background: var(--accent);
    transform: rotate(45deg);
  }
  .index {
    position: absolute;
    right: 82px;
    top: 72px;
    font: 600 118px/0.9 var(--font-sans);
    color: rgba(66, 111, 98, 0.12);
  }
  .title-block {
    position: absolute;
    left: 132px;
    top: 134px;
    width: 620px;
  }
  h1 {
    margin: 0;
    font: 700 82px/1.08 var(--font-serif);
    color: var(--ink);
    letter-spacing: 0;
  }
  .title-note {
    margin: 24px 0 0;
    width: 445px;
    font: 400 27px/1.72 var(--font-serif);
    color: var(--ink-soft);
  }
  .side-formula {
    position: absolute;
    right: 82px;
    top: 314px;
    width: 218px;
    padding-top: 18px;
    border-top: 2px solid var(--rule);
    font: 500 24px/1.62 var(--font-serif);
    color: var(--accent);
  }
  .quote {
    position: absolute;
    left: 132px;
    top: 520px;
    width: 790px;
    padding: 34px 0 34px 34px;
    border-left: 4px solid var(--accent);
  }
  .quote p {
    margin: 0;
    font: 600 41px/1.56 var(--font-serif);
    color: var(--ink);
  }
  .quote .thin {
    margin-top: 18px;
    font: 400 25px/1.72 var(--font-serif);
    color: var(--ink-soft);
  }
  .map {
    position: absolute;
    left: 164px;
    right: 82px;
    top: 790px;
    display: grid;
    grid-template-columns: 1.12fr 0.88fr;
    column-gap: 48px;
    row-gap: 28px;
  }
  .node {
    position: relative;
    min-height: 148px;
    padding-top: 22px;
    border-top: 1px solid var(--rule);
  }
  .node-2 { margin-top: 44px; }
  .node-3 { margin-left: 58px; }
  .node-number {
    display: block;
    margin-bottom: 8px;
    font: 600 20px/1 var(--font-sans);
    color: var(--accent);
  }
  .node h2 {
    margin: 0 0 10px;
    font: 700 33px/1.28 var(--font-serif);
    color: var(--ink);
    letter-spacing: 0;
  }
  .node p {
    margin: 0;
    font: 400 24px/1.62 var(--font-serif);
    color: var(--ink-soft);
  }
  .closing {
    position: absolute;
    left: 132px;
    right: 82px;
    bottom: 112px;
    display: grid;
    grid-template-columns: 1.6fr 0.6fr;
    column-gap: 54px;
    align-items: end;
    padding-top: 25px;
    border-top: 1px solid var(--rule-soft);
  }
  .closing-main {
    margin: 0;
    font: 500 30px/1.58 var(--font-serif);
    color: var(--ink);
  }
  .closing-main strong {
    color: var(--accent);
    font-weight: 700;
  }
  .stamp {
    margin: 0;
    text-align: right;
    font: 500 18px/1.6 var(--font-sans);
    color: var(--ink-faint);
  }
  .footer {
    position: absolute;
    left: 132px;
    right: 82px;
    bottom: 58px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font: 400 18px/1.4 var(--font-sans);
    color: var(--ink-faint);
  }
</style>
</head>
<body>
  <main class="card">
    <div class="spine"></div>
    ${sourceEchoHtml}
    <div class="meta">
      <span>${escapeHtml(spec.kicker || "阅读区显影")}</span>
      <span class="dot"></span>
      <span>${escapeHtml(spec.subject || "微信读书")}</span>
    </div>
    <div class="index">${escapeHtml(spec.index || "01")}</div>
    <section class="title-block">
      <h1>${lines(spec.title || "看见我")}</h1>
      <p class="title-note">${escapeHtml(spec.subtitle || "")}</p>
    </section>
    <aside class="side-formula">${lines(spec.sideNote || "")}</aside>
    <section class="quote">
      <p>${escapeHtml(spec.mainText || "")}</p>
      <p class="thin">${escapeHtml(spec.subText || "")}</p>
    </section>
    <section class="map" aria-label="今日显影结构">
${nodeHtml}
    </section>
    <section class="closing">
      <p class="closing-main">${escapeHtml(spec.closingLead || "")}<strong>${escapeHtml(spec.closingStrong || "")}</strong></p>
      <p class="stamp">${escapeHtml(spec.stampDate || "")}<br>see-me-card / 铸</p>
    </section>
    <footer class="footer">
      <span>${escapeHtml(spec.footerLeft || "由微信读书想法提炼")}</span>
      <span>1080 × 1440</span>
    </footer>
  </main>
</body>
</html>`;
}

function main() {
  const specPath = process.argv[2];
  if (!specPath) {
    console.error("Usage: node render_card.js <card_spec.json>");
    process.exit(1);
  }

  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  if (!spec.outputDir || !spec.fileBase) {
    console.error("card_spec.json requires outputDir and fileBase");
    process.exit(1);
  }
  if (!fs.existsSync(capturePath)) {
    console.error(`ljg-card capture.js not found: ${capturePath}`);
    process.exit(1);
  }

  ensureDir(spec.outputDir);
  const htmlPath = path.join(spec.outputDir, `${spec.fileBase}.html`);
  const pngPath = path.join(spec.outputDir, `${spec.fileBase}.png`);
  const downloadsDir = path.join(process.env.USERPROFILE || process.env.HOME, "Downloads");
  const downloadPath = path.join(downloadsDir, `${spec.fileBase}.png`);

  fs.writeFileSync(htmlPath, html(spec), "utf8");

  const result = spawnSync(process.execPath, [capturePath, htmlPath, pngPath, "1080", "1440"], {
    cwd: skillDir,
    encoding: "utf8"
  });

  if (result.status !== 0) {
    process.stderr.write(result.stdout || "");
    process.stderr.write(result.stderr || "");
    process.exit(result.status || 1);
  }

  fs.copyFileSync(pngPath, downloadPath);
  fs.writeFileSync(path.join(spec.outputDir, "cards_manifest.md"), [
    `# ${spec.fileBase}`,
    "",
    `- theme: ${spec.theme || ""}`,
    `- source: ${spec.subject || ""}`,
    `- html: ${path.basename(htmlPath)}`,
    `- png: ${path.basename(pngPath)}`,
    `- downloads: ${downloadPath}`,
    ""
  ].join("\n"), "utf8");

  process.stdout.write(`OK: ${pngPath}\n`);
  process.stdout.write(`Copied: ${downloadPath}\n`);
}

main();
