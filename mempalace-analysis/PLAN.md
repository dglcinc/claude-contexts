# MemPalace Behavioral Analysis — Pass 2: bowling-league-tracker (raw transcripts)

Goal: analyze how David directed the **bowling-league-tracker** build — the largest
single collaboration in the corpus (570 sessions, 2026-04-30 → 2026-05-07) — and **diff it
against the cross-project baseline** in `baseline/INSIGHTS.md`.

Why raw transcripts, not the palace: the baseline analysis established that the mining
pipeline drops the highest-signal data (interrupt→correction adjacency, speaker turns), and
`wing_bowling` has **zero diary-room drawers** — the field every baseline facet relied on.
So this pass goes to the raw `.jsonl`, the grain baseline Facet 4 proved gives ~3× the
signal. Each `- [ ]` task is one ralph iteration: a fresh sclaude reads the task, parses the
raw transcripts (write a script — don't eyeball 570 files), writes the named artifact,
commits, pushes, and checks its box.

## Conventions for every task

- **Source:** raw Claude Code session transcripts at
  `~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker/`.
  Process ONLY uuid-named `*.jsonl` (the 570 main-thread sessions). **EXCLUDE**
  `agent-*.jsonl` (subagent transcripts — they contain no David messages) and any `*.md`.
- **This is raw JSONL, NOT the palace — do NOT use `mempalace_*` tools.** Write a small
  Python/jq script. Each line is a JSON object. David's messages are the lines where
  `type == "user"` and `message.role == "user"` and the content is human text. **Exclude**:
  `tool_result` content blocks, lines whose text is wrapped in `<system-reminder>` /
  `<command-name>` / `<command-message>` / "Caveat:" boilerplate, and pure tool plumbing.
  Interrupt markers are content containing `[Request interrupted by user`.
- For the heavy parse/scan, spawn a subagent (general-purpose) with the script and work from
  its summary rather than loading 26 MB into your own context.
- Save artifacts to `mempalace-analysis/bowling/<file>`. Cap ~300 lines. Numbers + small
  sample tables; the synthesis task narrativizes.
- Cite samples as `<session-uuid>:<line>` so claims are auditable.
- Short verbatim quoted David messages are OK — this is engineering work (his own app
  build), not personal content. Keep quotes short. If a message is clearly personal
  (not engineering), redact rather than quote.
- **Every facet that has a baseline analogue MUST include a comparison row/section vs the
  baseline number** (read `baseline/INSIGHTS.md` and the relevant `baseline/0N-*.md`).

## Tasks

- [x] **B1 — Directive histogram (bowling) + diff vs baseline.**
  Same methodology as baseline Facet 1, over raw bowling David-messages. Output
  `bowling/B1-directives.md` with (a) top 30 leading verbs by frequency, (b) word-count
  histogram (buckets 1, 2-3, 4-7, 8-15, 16+), (c) 10 representative directives per bucket,
  (d) mean/median word count, (e) **comparison table vs baseline** (median words, %≤3-word,
  modal bucket, top verbs) + one paragraph on how directing an intense single-product build
  differs from the cross-project baseline. Re-evaluate the baseline's refuted hypothesis
  ("most directives ≤3 words") on this corpus.

- [ ] **B2 — Vague-vs-precise diagnostics (bowling) + diff vs baseline.**
  Classify diagnostic-style David messages VAGUE vs PRECISE (baseline Facet 3 criteria:
  PRECISE = concrete locator/error text/named symptom+location; VAGUE = symptom carried only
  by hedge/affect — "seems", "weird", "still not", "doesn't look"). Skip non-diagnostic
  directives. Output `bowling/B2-diagnostics.md` with (a) overall vague:precise ratio and %
  of messages that are diagnostics, (b) 10 vague + 10 precise examples with citations,
  (c) **comparison vs baseline 2.2:1 precise / ~14% diagnostic-rate**, (d) observation —
  bowling is hands-on product work, so test whether it skews precise like the product wings
  did, and whether vague spikes cluster where a fix failed across retries.

- [ ] **B3 — Interrupt + correction corpus (bowling, full 570-session scan).**
  Scan ALL 570 transcripts for `[Request interrupted` markers; for each, capture the
  in-flight assistant action (what Claude was doing — tool call / ask / plan / assertion)
  and the next genuine David message in the same session (chronological by line). Output
  `bowling/B3-corrections.md` with (a) total interrupts + density per 100 David-messages,
  (b) theme grouping with counts (over-asking / wrong-analysis-overconfident /
  wrong-scope / wrong-tool / stale-state / mid-flight-redirect), (c) 20-30 verbatim
  (context, correction) pairs with citations, (d) **comparison vs baseline's 47%
  over-asking + 24% over-confidence split** — does the densest single build match the
  cross-project mix? This is the richest facet; a week of intense building is the best
  correction corpus available.

- [ ] **B4 — Synthesis & diff vs baseline.**
  Read B1-B3 and `baseline/INSIGHTS.md`. Output `bowling/INSIGHTS-bowling.md` (cap 300
  lines, 5-line exec summary first) with: (1) where bowling **CONFIRMS** the baseline
  patterns, (2) where it **DIVERGES** and why (intense single-product build vs the
  post-2026-05-25 cross-project mix), (3) what bowling reveals the baseline **couldn't**
  (it predates the palace; it's the largest single collaboration), (4) updated, specific
  recommendations for David/Claude tuned to intense build sessions — cite B3 pairs,
  (5) methodology limits of the raw-transcript approach.

## How to run

```
cd ~/github/claude-contexts/mempalace-analysis
../ralph.sh PLAN.md
```

Picks the next unchecked task, spawns a fresh sclaude, waits for it to finish + commit +
push, marks the box, loops. Says `DONE` when no unchecked tasks remain.

## Where this lives

Branch `mempalace-analysis` (PR #11 → `main`). Baseline pass is preserved under
`baseline/`; this pass writes to `bowling/`. Do **not** merge — the user reviews both
passes first.
