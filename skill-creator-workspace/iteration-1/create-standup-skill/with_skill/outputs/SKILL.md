---
name: standup-formatter
version: "1.0.0"
description: Formats raw bullet-point standup notes into a clean Yesterday / Today / Blockers message. Use when user mentions 'standup', 'daily update', 'scrum notes', 'daily sync', or pastes bullet points asking for standup format. Also trigger when user says 'format my notes' or 'help me write my standup' — even without mentioning the word standup explicitly.
---

# standup-formatter

Takes freeform notes and shapes them into a three-section standup message. The goal is to save the user from the small daily friction of reformatting — they paste their raw thoughts, you return something ready to post.

## Output structure

Always produce exactly three sections. Keep the total under ~100 words.

**Yesterday**
- [what was completed]

**Today**
- [what's planned]

**Blockers**
- [blockers, or "None" if not mentioned]

## How to handle the input

Infer which bullets belong to Yesterday vs Today from tense and phrasing — past tense → Yesterday, future/present intent → Today. If something is ambiguous, make a reasonable call rather than asking. If input is genuinely too sparse to infer sections, ask one focused question.

Merge closely related items. Don't invent content that isn't there.

## Example

Input:
```
- finished the auth PR review
- pair programmed with Jamie on the cache layer
- writing tests for the new API endpoint today
- blocked on getting staging access
```

Output:
**Yesterday**
- Finished auth PR review
- Pair programmed with Jamie on cache layer

**Today**
- Write tests for new API endpoint

**Blockers**
- Waiting on staging environment access
