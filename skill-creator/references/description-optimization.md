# Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

## Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic — concrete and specific with detail (file paths, personal context, column names, company names, URLs, a little backstory). Some might be lowercase or contain abbreviations or typos or casual speech. Mix different lengths, and focus on edge cases rather than clear-cut cases.

**Bad**: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

**Good**: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

**Should-trigger queries (8-10)**: Cover different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't explicitly name the skill or file type but clearly needs it. Include uncommon use cases and cases where this skill competes with another but should win.

**Should-not-trigger queries (8-10)**: The most valuable ones are near-misses — queries that share keywords or concepts with the skill but actually need something different. Think adjacent domains, ambiguous phrasing, and cases where the query touches on something the skill does but in a context where another tool is more appropriate. Don't make them obviously irrelevant — "Write a fibonacci function" as a negative test for a PDF skill is too easy.

## Step 2: Review with user

Present the eval set to the user for review using the HTML template:

1. Read the template from `assets/eval_review.html`
2. Replace the placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array of eval items (no quotes — it's a JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write to `/tmp/eval_review_<skill-name>.html` and open it: `open /tmp/eval_review_<skill-name>.html`
4. The user can edit queries, toggle should-trigger, add/remove entries, then click "Export Eval Set"
5. Check `~/Downloads/` for the most recent `eval_set.json` (might be `eval_set (1).json`, etc.)

This step matters — bad eval queries lead to bad descriptions.

## Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt so the triggering test matches what the user actually experiences. Periodically tail the output to give updates on iteration progress and scores.

This handles the full optimization loop automatically: splits the eval set into 60% train / 40% held-out test, evaluates the current description (running each query 3 times for reliability), then calls Claude to propose improvements based on what failed. Re-evaluates each new description on both train and test, iterating up to 5 times. Returns JSON with `best_description` — selected by test score to avoid overfitting.

### How skill triggering works

Skills appear in Claude's `available_skills` list with their name + description. Claude only consults skills for tasks it can't easily handle on its own — simple one-step queries may not trigger a skill even if the description matches, because Claude can handle them directly. Complex, multi-step, or specialized queries reliably trigger skills when the description matches. So make eval queries substantive enough that Claude would actually benefit from consulting a skill.

## Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.

---

## Package and Present

(Only if the `present_files` tool is available — skip otherwise.)

Package the skill and present the `.skill` file to the user:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Direct the user to the resulting `.skill` file path so they can install it.
