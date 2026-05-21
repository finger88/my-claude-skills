# Card Spec

`scripts/render_card.js` 接收一个 JSON 文件，生成同名 HTML、PNG 和 `cards_manifest.md`。

## 最小示例

```json
{
  "outputDir": "D:\\my tool\\memory-work\\02 你的阅读\\书籍\\剑来\\card\\20260521_不被吞没_see_me_card",
  "fileBase": "20260521--不被吞没",
  "kicker": "阅读区显影",
  "subject": "微信读书 / 剑来",
  "index": "01",
  "title": "别让世界\n只剩下应付",
  "subtitle": "今天看见的是那个仍想保有感受力、创造力和选择感的你。",
  "sideNote": "真实证据先于解释，解释最后才成为卡片。",
  "sourceEcho": "我的原文想法可以放在这里，作为半透明背景显影。",
  "mainText": "你的自由，不是逃离责任，而是在责任仍然存在时，不把自己交给吞没。",
  "subText": "这只是今天的小样本理解，不是最终结论。",
  "nodes": [
    {"number": "01", "title": "证据", "body": "保留一条微信读书原文想法或触发原文。"},
    {"number": "02", "title": "压力", "body": "指出这条想法背后的现实约束。"},
    {"number": "03", "title": "保护", "body": "说明这个想法在保护哪个自我。"},
    {"number": "04", "title": "显影", "body": "给出今天对用户的阶段性理解。"}
  ],
  "closingLead": "今天先看见：",
  "closingStrong": "那个不想被压扁的自己。",
  "stampDate": "2026.05.21",
  "footerLeft": "证据来自微信读书想法"
}
```

## 字段

- `outputDir`：必填。HTML/PNG/manifest 输出目录。
- `fileBase`：必填。文件基础名，不含扩展名。
- `kicker`：左上角短标签。
- `subject`：来源，如 `微信读书 / 剑来`。
- `index`：右上角淡色编号，默认 `01`。
- `title`：标题，允许用 `\n` 手动断行。
- `subtitle`：标题下解释。
- `sideNote`：右侧短句。
- `sourceEcho`：建议填写用户的一条原始想法。脚本会用半透明大字放在背景里，作为显影源头。
- `mainText`：主文眼。
- `subText`：主文眼下的证据/限定。
- `nodes`：3-5 个节点；每个节点含 `number`、`title`、`body`。
- `closingLead` + `closingStrong`：底部收束句。
- `stampDate`：日期。
- `footerLeft`：底部来源说明。

## 文案长度

- `title`：建议 8-16 个汉字，手动分 2 行。
- `mainText`：建议 36-70 个汉字。
- `sourceEcho`：建议 18-48 个汉字；太长时取最能触发回忆的原句。
- `nodes[].body`：每条 20-38 个汉字，最多 5 条。
- 若使用真实想法原文较长，先压成短引，不要把卡片变成笔记正文。
