# Improving the Skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

## How to think about improvements

**1. Generalize from the feedback.**
The goal is a skill that works across a million different prompts, not just these test cases. You and the user are iterating on a few examples because it's fast — but a skill that only works for those examples is useless. Rather than making fiddly over-fit changes, try to understand the underlying need. If something is stubbornly wrong, try branching out with different metaphors or different working patterns.

**2. Keep the prompt lean.**
Remove things that aren't pulling their weight. Read the transcripts, not just the final outputs — if the skill is making the model spend time on unproductive steps, cut the parts causing that and see what happens.

**3. Explain the why.**
Try hard to explain the reasoning behind what you're asking the model to do. LLMs are smart — when given a good harness and clear reasoning, they go beyond rote instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — reframe as reasoning instead. It's a more humane, powerful, and effective approach.

**4. Look for repeated work across test cases.**
Read transcripts and notice if subagents independently wrote similar helper scripts or took the same multi-step approach. If all 3 test cases resulted in the subagent writing a `create_docx.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it.

Take your time here. Write a draft revision, then look at it with fresh eyes and improve it. Really get into the head of the user.

## The iteration loop

After improving the skill:

1. Apply improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs
   - **New skill**: baseline is always `without_skill` — stays constant across iterations
   - **Improving existing skill**: use judgment — baseline the original or the previous iteration
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

## Advanced: Blind comparison

For a more rigorous comparison between two versions (e.g., "is the new version actually better?"), there's a blind comparison system. Read `agents/comparator.md` and `agents/analyzer.md` for the details. The idea: give two outputs to an independent agent without telling it which is which, let it judge quality, then analyze why the winner won.

This is optional and most users won't need it. The human review loop is usually sufficient.
