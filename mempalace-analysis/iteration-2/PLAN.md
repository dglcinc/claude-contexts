# MemPalace Behavioral Analysis — Iteration 2 (F-A + F-C across projects)

Goal: extend the iteration-1 + bowling findings to a multi-project pass using
*raw `.jsonl` transcripts*, not palace drawers. Each `- [ ]` task is one ralph
iteration — fresh sclaude reads the task, runs it, writes the named artifact,
commits, pushes, marks the task done.

## Why iteration 2

`baseline/INSIGHTS.md` §3 recommended four refined facets (F-A, F-B, F-C, F-D)
to replace the original four, because three of the original four bottlenecked
on one structural fact: **mined drawers are not turn-segmented and the diary
is the only clean user-message source.** The `bowling/` pass already proved
the approach on one project — raw transcripts gave Facet 4 17 corrected
pairs vs the drawer-based Facet 2's 5, ~3× signal. Iteration 2 extends that to
the remaining three behavioral wings.

The two local mempalace patches just landed (P2 `recent:` truncation 80→400,
P3 meta-analysis filter) will only affect *future* drawer mining; existing
transcripts are unchanged, so raw-`.jsonl` is still the right grain for this
pass. Iteration 3 (later) re-runs everything against the cleaner post-patch
drawers to see if the cheaper drawer-based approach is now viable.

## Conventions

- Source data: raw `.jsonl` transcripts under `~/.claude/projects/-*/` and
  `~/.mempalace/incoming/-*/` on the Mini. Not palace drawers.
- Save artifacts to `mempalace-analysis/iteration-2/<file>` in this repo.
- Cite specific `(session_uuid, turn_index)` references for every claim.
- Drop the keyword-based vague/precise classifier — `baseline/INSIGHTS.md`
  §3e showed it's wrong ~50% of the time on David's politeness-wrapped
  reports. Classify by judgment, list per-message in the artifact.
- Skip the raw-drawer-density metric — `baseline/INSIGHTS.md` §3 marked it
  meaningless (contaminated by mining duplication + meta-sessions).
- Cap each artifact at ~300 lines. Data-dense, not prose-dense; the
  synthesis task narrativizes.
- Verbatim user-message quotes are OK (engineering content, not personal).
  Keep them short.
- Helper extraction scripts (the `bowling/` precedent: `_b1_extract.py`
  etc.) are welcome under `iteration-2/<wing>/_*.py` — gitignored
  `_*_dump.txt` if you produce raw dumps, per the existing repo `.gitignore`
  pattern.

## Tasks

- [x] **Task 1 — Corpus inventory.** Enumerate raw `.jsonl` transcripts on
  the Mini from both `~/.claude/projects/-*/` and `~/.mempalace/incoming/-*/`.
  Map each transcript path to a wing (using the source-cwd encoding rules).
  Output: `mempalace-analysis/iteration-2/00-inventory.md` with one row per
  `(wing, transcript-path-prefix, session-count, date-range, total-size)`.
  Skip wings with <50 KB total (signal too thin). This grounds the per-wing
  tasks below — they reference its enumerated paths.

- [x] **Task 2 — F-A + F-C on `wing_wilhelm`.** Highest-signal target per
  baseline (iOS/UI work, where interrupts and over-confident diagnoses
  concentrate). **F-A:** extract 20-30
  `(in-flight assistant action, interrupt marker, next user message)`
  triples from the raw transcripts; group by theme (wrong file, wrong scope,
  wrong tool choice, wrong analysis, too-confident assertion). **F-C:** per
  multi-turn diagnostic session, build a timeline of precise/vague messages
  with turns-to-resolution after the first vague vs precise message. Output:
  `mempalace-analysis/iteration-2/wilhelm/F-A.md` (corpus + theme grouping)
  and `mempalace-analysis/iteration-2/wilhelm/F-C.md` (timelines + a one-paragraph
  evaluation of the baseline hypothesis: "vague language is a lagging signal
  of a wrong fix approach").

- [x] **Task 3 — F-A + F-C on `wing_contexts`.** Same shape as Task 2 but
  for claude-contexts infrastructure work. Baseline §1 said `wing_contexts`
  had **zero** genuine interrupts and **zero** diagnostics — infra work is
  directed, not diagnosed. Test that against raw transcripts: do interrupts
  exist at all? If yes, what category dominates? F-C: expect zero or near-zero
  convergence-failure sessions. Output:
  `mempalace-analysis/iteration-2/contexts/F-A.md` and `F-C.md`. State
  explicitly whether the baseline "zero" finding holds in raw transcripts or
  was an artifact of drawer mining.

- [ ] **Task 4 — F-A + F-C on `wing_docs`.** Same shape but for
  signalk-wilhelmsk-docs work. Baseline placed this between wilhelm (high
  diagnostic) and contexts (zero diagnostic). The relevant question: does the
  over-asking-on-`AskUserQuestion`/`ExitPlanMode` pattern hold here too, or
  does the publishing-workflow nature of this project surface a different
  failure mode (e.g. "wrong version published", "wrong file built")? Output:
  `mempalace-analysis/iteration-2/docs/F-A.md` and `F-C.md`.

- [ ] **Task 5 — Iteration-2 synthesis.** Read all per-wing F-A and F-C
  artifacts plus `baseline/INSIGHTS.md` and `bowling/INSIGHTS-bowling.md`.
  Output: `mempalace-analysis/iteration-2/INSIGHTS-2.md` with sections:
  1. **Cross-project pattern.** Where the over-asking/over-planning
     interrupt dominates, where it doesn't, what drives the variation.
  2. **Per-project convergence-failure profile** from F-C. Which projects
     produce convergence failures, what their fingerprints are, and whether
     the precise→vague tripwire is durable across work types.
  3. **Bowling delta.** What the delegated-build mode showed that the
     attended multi-project work confirms or diverges from. The bowling pass
     is one operating mode; this pass is multiple work types in the *other*
     mode.
  4. **Revised CLAUDE.md / global.md recommendations.** The five validated
     levers in `global.md` came from one analysis pass; iteration 2 either
     confirms, refines, or adds to them. Be specific about what to keep,
     edit, or drop.
  5. **What iteration 3 should do differently.** With P2/P3 landed,
     evaluate whether iteration 3 can run on cleaner drawers instead of raw
     transcripts (cheaper, faster); identify which iteration-2 findings
     would need the still-unaddressed mining-pipeline fixes (P1/P4/P6 from
     INSIGHTS §5) before they're answerable.

  Cap 400 lines. Begin with a 5-line executive summary.

## How to run

From this directory on the Mini:

```
cd ~/github/claude-contexts/mempalace-analysis/iteration-2
../../ralph.sh PLAN.md
```

Each iteration spawns a fresh sclaude with the next unchecked task as its
prompt. Tasks 2-4 can run in parallel in principle, but the ralph driver is
sequential — let it just walk the list. Task 5 depends on 1-4 being done.

## Where this lives

Branch: `mempalace-analysis-iteration-2` (open PR against `main`). Artifacts
stay on the branch until synthesis is reviewed and merged.
