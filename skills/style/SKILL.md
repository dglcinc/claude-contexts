---
name: style
description: Record a writing-style correction into the global prose style guide. Use when David flags AI-slop phrasing, filler, praise, or any tic he wants stopped — e.g. "/style stop saying 'worth noting'" or just "style" after a bad response. Also triggered by "style:" or "that's slop".
---

# /style

Add or tighten a rule in the **### Prose style** section of `~/.claude/CLAUDE.md`.

Usage: `/style <the offending phrase, or a description of the habit>`

If `$ARGS` is empty, look back at your own most recent responses, identify the tic David is
reacting to, and name it explicitly before editing. Do not guess silently.

## Steps

1. **Read** the `### Prose style` section of `~/.claude/CLAUDE.md`.

2. **Check whether an existing rule already covers it.** If it does, the rule is not working —
   do not add a duplicate. Instead make the existing rule harder to miss: add the concrete
   offending phrase to its example list, and if David has now flagged it more than once, mark it
   as a recurring tic to check before sending.

3. **Otherwise add one bullet**, in the same form as the others: an imperative in bold, then the
   banned constructions spelled out in italic. Name actual phrases. Abstract instructions
   ("be concise", "avoid filler") do not change behaviour; a checkable list does.

4. **Quote David's own example verbatim** in the rule when he supplied one. His wording is the
   most reliable trigger for recognising the pattern later.

5. **Check the guide against itself.** The style section is written in the style it describes —
   after editing, re-read it and fix any violation the new rule introduces.

6. **Keep it compact.** The whole section is loaded into every session, so it costs input tokens
   on every turn. Merge near-duplicates rather than letting the list grow. If it exceeds ~20
   bullets, consolidate.

7. **Confirm** with the exact bullet added or changed, and nothing else. No restart is needed —
   `~/.claude/CLAUDE.md` is read at the start of each session, and within the current session the
   edit is already in context.
