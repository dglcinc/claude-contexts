# Handoff to a fresh Mini session

You're a new Claude Code session on `utilityserver` (Mac Mini). Your job is to
run the ralph defined in `mempalace-analysis/PLAN.md` to completion. Read this
file first, then PLAN.md, then start the driver.

## What's already set up

- Branch `mempalace-analysis` is checked out.
- Open PR against `main` carries this PLAN.md (see `gh pr view`).
- The ralph driver lives at `~/github/claude-contexts/ralph.sh`.
- mempalace MCP is stdio-local on this host (no SSH wrapper needed here —
  that's why we moved the work to the Mini).

## How to start

```
cd ~/github/claude-contexts/mempalace-analysis
../ralph.sh PLAN.md
```

Each iteration spawns a fresh sclaude with the next unchecked task's text as
its prompt. That sub-Claude is expected to: produce the named artifact,
`git add` it, `git commit` with a clear message, `git push` to the
`mempalace-analysis` branch, then mark the task done in PLAN.md.

## Context the previous session built (M2)

- Wing cleanup complete (2026-05-30). All wings are clean `wing_X` form:
  `wing_wilhelm` 133, `wing_pivac` 55, `wing_contexts` 58, `wing_docs` 18,
  `wing_code` 3, `sessions` 2469. No path-style wings should remain — if any
  appear, surface them but don't fix in this analysis pass.
- Local patch to `convo_miner.py` prevents new path-style wings; reapply
  script at `~/bin/mempalace-reapply-patch.py`; launchd job
  `com.dglc.mempalace-patch` runs daily at 04:00.
- The diary room (77 entries) is the densest user-message-only corpus.
  The `recent:` field is pipe-delimited and chronological — Facet 1 and
  Facet 3 lean on this heavily.
- Past `mempalace_search` queries with `limit=100` returned cleanly. Use
  `mempalace_list_drawers` for paginated full enumeration.

## What NOT to do

- Don't re-run the wing cleanup — it's done.
- Don't expand the facet list beyond the 5 in PLAN.md without asking the user.
- Don't merge the PR at the end — that's the user's call after reviewing
  `INSIGHTS.md`.
- If you stumble into a drawer that looks personal (not engineering work),
  redact rather than quote.

## When you're done

After Facet 5 writes `INSIGHTS.md`, push, refresh the PR description with
a summary of findings, and surface the PR URL to the user. Stop. Don't merge.
