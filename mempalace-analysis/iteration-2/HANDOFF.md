# Handoff: Iteration-2 ralph

You're a fresh Claude Code session on `utilityserver` (Mac Mini). Read this
file first, then `PLAN.md`, then start the driver.

## What's already set up

- Branch `mempalace-analysis-iteration-2` is checked out.
- Open PR against `main` (see `gh pr view`); will accumulate artifacts.
- Ralph driver: `~/github/claude-contexts/ralph.sh`.
- mempalace MCP is stdio-local on this host — no SSH wrapper needed.

## How to start

```
cd ~/github/claude-contexts/mempalace-analysis/iteration-2
../../ralph.sh PLAN.md
```

## Context the prior sessions built

- **Iteration 1 (`baseline/`)** ran the original four facets + synthesis on
  palace drawers. Headline: David is more precise than expected; the real
  friction is Claude over-asking at `AskUserQuestion`/`ExitPlanMode`. See
  `mempalace-analysis/baseline/INSIGHTS.md`.

- **Bowling pass (`bowling/`)** extended Facets 1/3/4 to one project on raw
  `.jsonl` transcripts. Confirmed the over-asking finding and amplified to
  75% for delegated-build mode. Showed transcripts are ~3× the signal of
  drawers. See `mempalace-analysis/bowling/INSIGHTS-bowling.md`.

- **`global.md`** has a `### Asking, planning, and diagnosing` subsection
  (commit `89f2834`) encoding the five validated levers from iteration 1.
  Iteration 2's synthesis revisits whether those levers still hold with
  cross-project evidence.

- **Wing cleanup** complete: only `wing_X` names exist. P2 (raise diary
  `recent:` truncation to 400 chars) and P3 (skip mempalace-analysis
  sessions during mining) are local patches on the Mini, applied 2026-05-30
  — they affect *future* mining only, not existing transcripts.

- **The `mp` CLI helper** is installed for direct palace search if you want
  it. The mempalace MCP tools are the primary interface.

## What to do at the end

After Task 5 writes `INSIGHTS-2.md`, push, update the PR description with a
5-line summary of findings, and surface the PR URL. **Don't merge** — the
user reviews the synthesis first.

## What NOT to do

- Don't re-run iteration 1 or bowling — both are landed on `main`.
- Don't expand the task list beyond the 5 in `PLAN.md` without asking the
  user. The bowling pass added work the user found valuable, but those
  extensions were one project; this iteration is meant to be the
  cross-project breadth.
- Don't merge the PR at the end — the user reviews first.
- If you stumble into transcript content that looks personal (not
  engineering work), redact rather than quote.

## Open question to flag if it comes up

`wing_contexts` (58 drawers, shortened name from prior `--wing` override)
won't merge with `wing_claude_contexts` (full project name) that future
P1-patched fallback mining will produce. User has not decided; both names
are likely to appear in palace queries. Either is a legitimate target; flag
the discrepancy if it materially affects a count, but don't act on it.
