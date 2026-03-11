---
name: skill-creator
version: "2.1.0"
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating and iteratively improving Claude Code skills.

Your job is to figure out where the user is in the process and jump in. Maybe they have an idea — help refine it, draft the skill, test it, iterate. Maybe they already have a draft — go straight to eval. Maybe they want to vibe without evals — do that too.

**Be flexible.** Always adapt to where the user actually is.

## Communication style

Users range from non-technical to expert. Read context cues:
- "evaluation" and "benchmark" are fine for most users
- Explain "JSON" and "assertion" unless the user clearly knows them

---

## Phase 1: Creating a skill

### Capture Intent

Start by understanding the user's intent. The conversation might already contain a workflow to capture — extract answers from history first.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with verifiable outputs (file transforms, code gen, fixed workflows) benefit from them. Subjective skills (writing style, art) often don't.

### Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, dependencies. Wait to write test prompts until this is ironed out. Check available MCPs for research if useful.

### Write the SKILL.md

Key components:

- **name**: Skill identifier
- **description**: The primary triggering mechanism. Include both what the skill does AND when to use it — all "when to use" goes here, not in the body. Make descriptions a little "pushy": instead of "Build a dashboard", write "Build a dashboard. Use this skill whenever the user mentions dashboards, data visualization, or wants to display company data, even if they don't explicitly ask for a dashboard."
- **the rest of the skill**

**Anatomy:**
```
skill-name/
+-- SKILL.md (required, <500 lines ideal)
+-- Bundled Resources (optional)
    +-- scripts/    - Executable code for deterministic tasks
    +-- references/ - Docs loaded into context as needed
    +-- assets/     - Templates, icons, fonts
```

Keep SKILL.md under 500 lines. If approaching this limit, add hierarchy with clear pointers to reference files. Prefer imperative form. Explain the **why** behind instructions — LLMs respond better to understanding than rigid rules. If you find yourself writing ALWAYS/NEVER in all caps, reframe as reasoning instead.

### Test Cases

Write 2-3 realistic test prompts. Share with the user first. Save to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {"id": 1, "prompt": "User's task prompt", "expected_output": "Description of success", "files": []}
  ]
}
```

---

## Phase 2-3: Running and evaluating test cases

This is one continuous sequence — don't stop partway. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory, organized by `iteration-N/` then by eval name.

### Step 1: Spawn all runs in the same turn

For each test case, spawn **both** runs simultaneously — with-skill AND baseline. Don't do with-skill first and baseline later.

**With-skill run prompt:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Save outputs to: <workspace>/iteration-<N>/<eval-name>/with_skill/outputs/
```

**Baseline:** new skill → `without_skill/` (no skill). Improving existing skill → snapshot old version first (`cp -r <skill-path> <workspace>/skill-snapshot/`), point baseline at snapshot → `old_skill/`.

Write `eval_metadata.json` for each eval with a descriptive name (not "eval-0"):
```json
{"eval_id": 0, "eval_name": "descriptive-name", "prompt": "...", "assertions": []}
```

### Step 2: Draft assertions while runs are in progress

Good assertions are objectively verifiable. Subjective skills need human judgment — don't force assertions on them. Update `eval_metadata.json` and `evals/evals.json` with assertions once drafted.

### Step 3: Capture timing data as runs complete

When each subagent completes, save immediately to `timing.json` — this is the only opportunity:
```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

### Step 4: Grade, aggregate, launch viewer

1. **Grade** — spawn a grader subagent reading `agents/grader.md`. Save to `grading.json`. Use fields `text`, `passed`, `evidence` (not `name`/`met`/`details`).

2. **Aggregate** — from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Analyst pass** — read benchmark data, surface patterns. See `agents/analyzer.md`.

4. **Launch viewer:**
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+: add `--previous-workspace <workspace>/iteration-<N-1>`.
   Headless/Cowork: use `--static <output_path>` instead.

   **GENERATE THE VIEWER before evaluating outputs yourself** — get results in front of the human first.

5. Tell the user: "Results are open in your browser — 'Outputs' tab to review and leave feedback, 'Benchmark' tab for quantitative comparison. Come back when you're done."

### Step 5: Read the feedback

Read `feedback.json` when done. Empty = fine. Focus improvements on cases with specific complaints. Kill the viewer: `kill $VIEWER_PID 2>/dev/null`

---

## Phase 4: Improving the skill

1. **Generalize from feedback.** You're building something used a million times, not just these examples. Avoid over-fit changes. If something is stubbornly wrong, try a different metaphor or approach.

2. **Keep it lean.** Read the transcripts, not just the final outputs — cut parts causing unproductive steps.

3. **Explain the why.** Transmit understanding, not rules. More humane and more effective.

4. **Bundle repeated work.** If multiple test cases independently wrote the same helper script, it belongs in `scripts/`.

After improving: rerun into `iteration-<N+1>/`, launch reviewer with `--previous-workspace`, wait for feedback, repeat until happy or no longer making progress.

**Blind comparison** (optional): read `agents/comparator.md` and `agents/analyzer.md`.

---

## Phase 5: Description optimization

See `references/description-optimization.md` for the full 4-step loop (trigger eval generation, user review, `run_loop.py`, apply result).

Offer this after skill quality is solid. Requires the `claude` CLI tool (`claude -p`) — skip on Claude.ai.

---

## Platform notes

**Claude.ai / Cowork / headless**: mechanics change. Read `references/platform-notes.md` before starting if you're in one of these environments.

---

## Reference files

| File | When to read |
|------|-------------|
| `references/description-optimization.md` | Phase 5: optimizing the description |
| `references/platform-notes.md` | Claude.ai, Cowork, or headless environments |
| `references/schemas.md` | JSON schemas for evals.json, grading.json, benchmark.json |
| `agents/grader.md` | When spawning a grader subagent |
| `agents/comparator.md` | When doing blind A/B comparison |
| `agents/analyzer.md` | When analyzing benchmark results |
