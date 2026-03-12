# Description Optimization for ljg-paper

## 10 Trigger Eval Queries

```json
[
  {"query": "Can you read this paper for me? https://arxiv.org/abs/2401.12345 — it's about RAG improvements", "should_trigger": true},
  {"query": "just dropped an arxiv link in chat — https://arxiv.org/abs/2312.00001 — can you go through it", "should_trigger": true},
  {"query": "读论文 https://arxiv.org/abs/2310.12345", "should_trigger": true},
  {"query": "here's a pdf from neurips, mind taking a look and telling me if it's worth reading? [attached]", "should_trigger": true},
  {"query": "分析论文：可解释AI在医疗图像中的应用，这是链接 https://arxiv.org/abs/2405.00001", "should_trigger": true},
  {"query": "I need to evaluate whether this paper is worth citing in my thesis. Can you deep-read it? https://arxiv.org/abs/2311.09232", "should_trigger": true},
  {"query": "can you help me write a related work section? I need to summarize 5 papers", "should_trigger": false},
  {"query": "what are the best papers on attention mechanisms from 2023?", "should_trigger": false},
  {"query": "I'm writing a paper and need feedback on my methodology section", "should_trigger": false},
  {"query": "can you search arxiv for papers about diffusion models published this year", "should_trigger": false}
]
```

## Failure Analysis (why current description under-triggers)

The current description has two English trigger words: `'paper'` and `'deep read'`. Casual queries use: "read this," "take a look," "go through," "check out," "worth reading," "what does this say" — none of which match.

Additionally: an arxiv URL alone should be sufficient to trigger (combined with any reading-intent verb), but the current description has no URL-based heuristic.

## Improved Description

Paper deep-reader. Trigger when a user shares an academic paper — arxiv URL, PDF, DOI, or uploaded file — and wants it read, analyzed, summarized, reviewed, critiqued, or explained, including casual English phrasings like "can you read this paper for me," "take a look at this arxiv link," "go through this for me," "is this paper worth reading," "what does this say," or "check out this PDF." Also trigger on Chinese: '读论文', '分析论文', '深度解读', '帮我看看这篇论文'. Runs the atom pipeline (split→squeeze→plain→feynman→博导审稿): identifies the research gap, extracts the core contribution, and delivers a seasoned-advisor judgment on whether the work holds up. Output: Markdown report, default ~/Downloads/.

Do NOT trigger for: paper writing help, paper search/recommendation, or general conceptual questions where no specific paper is provided.
