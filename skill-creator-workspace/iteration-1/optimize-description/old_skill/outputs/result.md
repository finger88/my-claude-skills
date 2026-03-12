# Description Optimization for ljg-paper

## 10 Trigger Eval Queries

| # | Query | should_trigger | Rationale |
|---|-------|---------------|-----------|
| 1 | "Can you read this paper for me? https://arxiv.org/abs/2401.12345" | true | Exact reported failure — "read this paper for me" + arxiv URL |
| 2 | "Analyze this arxiv link: https://arxiv.org/abs/2312.00001" | true | Exact reported failure — "analyze this arxiv link" |
| 3 | "I found this ML paper, can you take a look? [PDF attached]" | true | "take a look" + paper + PDF — casual phrasing not in current triggers |
| 4 | "深度解读这篇论文：https://arxiv.org/abs/2401.99999" | true | "深度解读" not listed in current Chinese triggers |
| 5 | "读论文 https://arxiv.org/abs/2310.12345" | true | Direct use of existing trigger — baseline positive |
| 6 | "Here's a research paper I need summarized and critiqued: [URL]" | true | "summarize and critique" a "research paper" — not in current triggers |
| 7 | "Can you recommend papers on transformer architectures?" | false | Discovery/recommendation, no specific paper shared |
| 8 | "What is the difference between a CNN and a Transformer?" | false | General knowledge question, no paper involved |
| 9 | "I'm writing a paper, help me improve the introduction" | false | Writing assistance, not reading/analyzing an existing paper |
| 10 | "Can you search arxiv for recent diffusion model papers?" | false | Search task, no specific paper provided |

## Failure Analysis

Current description fails on casual English because:
1. Only `'paper'` and `'deep read'` cover English — missing "read," "analyze," "summarize," "take a look," "walk me through"
2. No URL-detection heuristic (an arxiv URL alone should trigger)
3. Chinese triggers dominate visually, biasing toward Chinese queries

## Improved Description

Academic paper deep-reader. Trigger when a user shares an academic paper (arxiv URL, PDF link, uploaded PDF, or DOI) and asks you to read, analyze, summarize, review, critique, explain, or walk through it — including casual phrasings like "can you read this paper for me," "take a look at this arxiv link," "analyze this paper," "go through this for me," "what does this paper say," or "check out this PDF." Also trigger on Chinese requests: '读论文', '分析论文', '深度解读', '帮我看看这篇文章'. Runs the atom pipeline (split→squeeze→plain→feynman→博导审稿) to produce a structured analysis: research gap, key contributions, methodology critique, and a seasoned-advisor judgment. Outputs a Markdown report (default: ~/Downloads/).

Do NOT trigger for: paper writing assistance, paper search/recommendation requests, or general questions where no specific paper is provided.
