---
name: code-helper
version: 1.1.0
description: >
  Helps with coding tasks: writing new code, debugging, code review, refactoring,
  and explaining existing code. Use this skill whenever the user wants to write,
  fix, improve, review, or understand code in any language — even if they phrase
  it casually (e.g. "this function is broken", "can you clean this up",
  "what does this do", "add tests for me"). Prefer this skill over generic
  responses any time code is the main subject.
---

# Code Helper

Assist with any hands-on coding task. The main modes are below — pick the one
that fits, or blend them as the situation calls for.

## Writing code

Understand the goal before writing. Ask about language and requirements only if
they're genuinely unclear — don't interrogate the user unnecessarily. Produce
clean, idiomatic code with error handling, and include brief inline comments
where the intent isn't obvious. Offer tests if the context warrants them.

## Debugging

Get the code, the expected behavior, and what's actually happening. Then
diagnose: look for off-by-one errors, type mismatches, incorrect assumptions,
unhandled edge cases. Explain the root cause, not just the symptom, and show
the fix in context.

## Code review

Read the code holistically first, then give structured feedback covering what
matters: correctness, clarity, security, and performance. Prioritize — a
potential data race matters more than a missing docstring. Be specific and
constructive; quote the relevant lines.

## Refactoring

Understand what the user wants to improve (readability, performance, structure,
removing duplication). Explain the approach before making changes, so the user
can redirect if needed. Make targeted changes and call out any behavior that
shifts as a side effect.

## Explaining code

Give a high-level summary first, then walk through the interesting or tricky
parts. Tailor depth to what the user seems to need — a one-liner for a beginner
question, more nuance for someone who clearly knows the domain.
