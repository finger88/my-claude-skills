# Running and Evaluating Test Cases

This is one continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, by test case (`eval-0/`, `eval-1/`, etc.). Don't create all directories upfront — create them as you go.

---

## Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn. Don't spawn with-skill runs first and come back for baselines later — launch everything at once so it all finishes around the same time.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, baseline depends on context):
- **New skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving existing skill**: snapshot the old version first (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

---

## Step 2: While runs are in progress, draft assertions

Don't just wait — use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update `eval_metadata.json` files and `evals/evals.json` with assertions once drafted. Also explain to the user what they'll see in the viewer.

---

## Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere.

---

## Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

**1. Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use fields `text`, `passed`, and `evidence` (not `name`/`met`/`details`) — the viewer depends on these exact field names.

**2. Aggregate into benchmark** — run from the skill-creator directory:
```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```
This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration. Put each with_skill version before its baseline counterpart. See `references/schemas.md` for manual benchmark.json schema.

**3. Analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for: non-discriminating assertions, high-variance evals, time/token tradeoffs.

**4. Launch the viewer:**
```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```
For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

**Cowork / headless**: use `--static <output_path>` to write a standalone HTML file instead of starting a server.

**Note**: use `generate_review.py` to create the viewer — no need to write custom HTML.

**5. Tell the user**: "I've opened the results in your browser. 'Outputs' tab lets you click through each test case and leave feedback; 'Benchmark' tab shows the quantitative comparison. When you're done, come back and let me know."

### What the user sees in the viewer

- **Prompt**: the task that was given
- **Output**: files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades**: collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time

Navigation via prev/next buttons or arrow keys. "Submit All Reviews" saves all feedback to `feedback.json`.

---

## Step 5: Read the feedback

When the user says they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on test cases where the user had specific complaints.

Kill the viewer server when done:
```bash
kill $VIEWER_PID 2>/dev/null
```
