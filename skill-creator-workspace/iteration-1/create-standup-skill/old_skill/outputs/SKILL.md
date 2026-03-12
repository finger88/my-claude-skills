# Skill: standup-formatter

## Overview
Transforms freeform bullet-point notes into a clean, concise daily standup message with three standard sections: Yesterday, Today, and Blockers.

## Trigger Conditions
Activate this skill when the user:
- Mentions the words "standup", "daily update", "scrum notes", or "format my notes"
- Pastes bullet points and asks for standup formatting
- Asks to structure or clean up their daily status notes

## Input
Freeform bullet points describing work done, work planned, and any blockers.

## Output Format
A formatted standup message under three headings, kept to approximately 100 words total.

**Yesterday**
- <concise summary of completed work>

**Today**
- <concise summary of planned work>

**Blockers**
- <blockers, or "None" if none are mentioned>

## Behavior Rules
1. Infer categories (Yesterday/Today/Blockers) from the user's phrasing and context.
2. If a category is unclear, make a reasonable inference and note it briefly.
3. Keep total output to ~100 words. Merge closely related bullets.
4. Do not invent content not present in the user's notes.
5. Use professional, neutral language.
6. Always include a Blockers section; use "None" if none are mentioned.
7. If input is too ambiguous, ask one clarifying question before formatting.

## Example
Input: standup notes — merged auth PR, paired with Sam, going to finish error handling today, waiting on design approval

Output:
**Yesterday**
- Merged the auth refactor PR
- Paired with Sam on data pipeline work

**Today**
- Finish error handling implementation

**Blockers**
- Waiting on design approval for dashboard mockup
