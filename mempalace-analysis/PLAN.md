# MemPalace Behavioral-Analysis Plan

Goal: facet the palace's drawer content to surface behavioral patterns in how
David directs work, then synthesize updated insight recommendations.
Each `- [ ]` task below is one ralph iteration — a fresh sclaude reads the task,
executes it against the palace via the `mempalace_*` MCP tools, writes the named
artifact, and marks the task done.

## Conventions for every facet task

- Source data lives in the palace. Use `mempalace_search`, `mempalace_list_drawers`,
  `mempalace_get_drawer`, `mempalace_status`, `mempalace_kg_query` as needed.
- Wings are unified `wing_X` names (post-2026-05-30 cleanup). No path-style
  wings should remain; if you see one, flag it but don't bail.
- Save artifacts to `mempalace-analysis/<file>` in this repo.
- Cap each artifact at ~300 lines. Numbers + small sample tables. The synthesis
  task will narrativize — keep facet artifacts data-dense, not prose-dense.
- Cite sample drawer IDs (or session UUIDs from diary CHECKPOINTs) so claims
  are auditable.
- Verbatim quoted user messages are OK; this corpus is engineering work, not
  personal content. Keep quotes short.
- The diary room's `recent:` field is the highest-signal source for
  user-message-only patterns — it's already pipe-delimited and chronological.

## Tasks

- [x] **Facet 1 — Imperative-verb histogram + directive length distribution.**
  Source: the `recent:` field of every diary-room drawer (room=diary, all wings).
  Extract pipe-delimited user-message snippets; drop drawer/session boilerplate
  ("Base directory for this skill:" etc.). Output:
  `mempalace-analysis/01-directives.md` with (a) top 30 leading verbs by
  frequency across all directives, (b) word-count histogram with buckets
  1, 2-3, 4-7, 8-15, 16+ words, (c) 10 representative directives at each
  bucket, (d) per-wing breakdown of mean word count, (e) one-paragraph
  observation. Evaluate the hypothesis: "most directives are <=3 words."

- [x] **Facet 2 — Interrupt density per wing.**
  Source: drawers whose content matches `[Request interrupted by user]` or
  `[Request interrupted by user for tool use]` across all wings/rooms (use
  `mempalace_search` with high limit + content scan). Output:
  `mempalace-analysis/02-interrupts.md` with a table per wing (raw interrupt
  count, total drawers in wing, density per 100 drawers). Rank wings by
  density. Cite 2-3 sample interrupt drawers per wing for the top 3.
  Evaluate the hypothesis: "iOS/UI work (`wing_wilhelm`) has 5-10x the
  interrupt density of infra/docs work."

- [ ] **Facet 3 — Vague-vs-precise diagnostic ratio.**
  Source: the `recent:` field of diary drawers + a 200-message sample of
  user-message drawers from `room=problems`. Classify each diagnostic-style
  user message as VAGUE (patterns: "something is", "I think", "doesn't look",
  "still not", "not working", "feels off", "weird") or PRECISE (file:line
  citation, exact error text, named symptom with location). Skip non-diagnostic
  messages (pure directives like "merge it"). Output:
  `mempalace-analysis/03-diagnostics.md` with (a) overall vague/precise
  ratio, (b) ratio per wing, (c) 10 vague examples + 10 precise examples
  with drawer IDs, (d) brief observation on which projects favor which mode.

- [ ] **Facet 4 — Correction-after-interrupt labeled corpus.**
  Source: for each interrupt drawer surfaced in Facet 2, find the next user
  message in the same session (match on `source_file` metadata and
  chronological order). Output: `mempalace-analysis/04-corrections.md` with
  20-30 `(interrupt-context, correction-message)` pairs. Group by theme
  (e.g. wrong file, wrong scope, wrong tool choice, wrong analysis,
  too-confident assertion). Each pair: 2-line context + the correction
  verbatim. This is the labeled corpus the synthesis task draws on for
  "what kinds of mistakes happen most often."

- [ ] **Facet 5 — Synthesis: updated insights and recommendations.**
  Read all four facet artifacts. Cross-reference. Output:
  `mempalace-analysis/INSIGHTS.md` with sections: (1) what the data
  CONFIRMED about the original hypotheses, (2) what it REFUTED or
  surprised on, (3) revised facet list for any future analysis pass,
  (4) actionable improvements David could make to reduce friction
  (cite specific drawers from Facet 4), (5) actionable improvements to
  the mempalace mining pipeline itself (tagging, room re-classification,
  drawer-level metadata). Cap at 400 lines. Begin with a 5-line executive
  summary at the top.

## How to run

From this directory on the Mini:

```
cd ~/github/claude-contexts/mempalace-analysis
../ralph.sh PLAN.md
```

The driver picks the next unchecked task, spawns a fresh sclaude with the
task description as its prompt, waits for it to finish + commit + push the
artifact, then marks the task done and loops.

## Where this lives

Branch: `mempalace-analysis` (open PR against `main`). Artifacts stay on
the branch until synthesis is reviewed and merged.
