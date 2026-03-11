# Platform-Specific Notes

## Claude.ai

Core workflow is the same (draft → test → review → improve → repeat), but no subagents means some mechanics change:

**Running test cases**: No parallel execution. For each test case, read the skill's SKILL.md and follow its instructions to accomplish the test prompt yourself. Do them one at a time. Less rigorous than independent subagents (you wrote the skill and you're also running it), but a useful sanity check — human review compensates. Skip baseline runs.

**Reviewing results**: If you can't open a browser, skip the browser reviewer entirely. Present results directly in the conversation: show the prompt and output for each test case. If the output is a file (like .docx or .xlsx), save it to the filesystem and tell them where it is so they can download and inspect it. Ask for feedback inline: "How does this look? Anything you'd change?"

**Benchmarking**: Skip quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback.

**The iteration loop**: Same — improve the skill, rerun test cases, ask for feedback — just without the browser reviewer in the middle.

**Description optimization**: Requires `claude -p` CLI tool, only available in Claude Code. Skip it if on Claude.ai.

**Blind comparison**: Requires subagents. Skip it.

**Packaging**: `package_skill.py` works anywhere with Python and a filesystem. The user can download the resulting `.skill` file.

**Updating an existing skill**:
- Preserve the original name — use the same directory name and `name` frontmatter field unchanged
- Copy to a writeable location before editing: `cp -r <skill-path> /tmp/skill-name/`, edit there, package from the copy
- If packaging manually, stage in `/tmp/` first — direct writes may fail due to permissions

---

## Cowork

You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. If you run into severe timeout problems, it's OK to run test prompts in series rather than parallel.

**No display**: When generating the eval viewer, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Provide the file path so the user can click to open it in their browser.

**CRITICAL**: After running tests, GENERATE THE EVAL VIEWER before evaluating inputs yourself. You want to get results in front of the human ASAP. Use `generate_review.py` — not custom HTML.

**Feedback**: Since there's no running server, "Submit All Reviews" downloads `feedback.json` as a file. Read it from there (you may need to request access first).

**Packaging**: `package_skill.py` just needs Python and a filesystem — works fine.

**Description optimization**: `run_loop.py` / `run_eval.py` use `claude -p` via subprocess, not a browser — works fine in Cowork. Save until the skill is fully finished and the user agrees it's in good shape.

**Updating an existing skill**: Follow the update guidance from the Claude.ai section above.
