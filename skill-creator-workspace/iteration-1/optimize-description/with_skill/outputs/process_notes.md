# Process Notes (with_skill / new 64-line version)

## Reference files read
1. SKILL.md (64 lines) — identified this as Phase 5 (description optimization), directed to references/description-optimization.md
2. references/description-optimization.md — read for:
   - Eval query design: "focus on edge cases," negative cases should be "near-misses not obviously irrelevant"
   - should-trigger query guidance: "include cases where user doesn't explicitly name the skill or file type"
   - JSON format for the eval set

## What the reference file added
- Explicit guidance on near-miss negative cases → "I'm writing a paper" (writing not reading) and "search arxiv" (discovery not reading) are good negative cases precisely because they share vocabulary
- The "casual backstory" guidance → added "just dropped an arxiv link in chat" phrasing to eval queries
- JSON format → output as proper JSON array with should_trigger boolean field
