# Facet 2 — Interrupt density per wing

**Source & method.** A literal census of every drawer whose stored document
contains the substring `[Request interrupted by user` (covers both marker
variants: `[Request interrupted by user]` and `…by user for tool use]`).
Semantic `mempalace_search` proved unreliable for this — its hybrid ranker
caps the candidate pool (`total_before_filter` capped at 300) and the top-100
is dominated by semantic false-positives (`<local-command-caveat>`,
`Login interrupted`, AskUserQuestion rejections), surfacing only ~15 of the
real matches. Because this analysis runs **on the Mini where the palace lives**,
the census was instead run directly against ChromaDB's SQLite
(`~/.mempalace/palace/chroma.sqlite3`, key `chroma:document`), a read-only
exact scan of all **2805** drawers. Per-wing totals from that scan match
`mempalace_status` exactly (sessions 2536, wing_wilhelm 133, wing_contexts 59,
wing_pivac 55, wing_docs 18, wing_code 3, wing_analysis 1).

## (a) Raw literal-marker density per wing

| Wing | interrupt drawers | total drawers | per-100 |
|------|------:|------:|------:|
| wing_contexts | 7 | 59 | **11.86** |
| wing_docs | 2 | 18 | **11.11** |
| wing_wilhelm | 13 | 133 | **9.77** |
| sessions | 4 | 2536 | 0.16 |
| wing_pivac | 0 | 55 | 0.00 |
| wing_code | 0 | 3 | 0.00 |
| wing_analysis | 0 | 1 | 0.00 |

Total literal-match drawers: **26** (11 contain the plain marker, 17 the
`for tool use` variant; 2 contain both).

**On its face this REFUTES the hypothesis** — iOS/UI work (`wing_wilhelm`) does
not lead; it sits *below* both `wing_contexts` (infra/memory) and `wing_docs`.
But the raw number is an artifact of the mining pipeline, not a behavioral
signal. Two distortions, dissected below, account for almost the entire table.

## (b) Distortion 1 — diary rolling-window duplication

Every `wing_wilhelm` (13) and `wing_docs` (2) match is a **diary CHECKPOINT**
drawer, not an interrupt event. Diary checkpoints are overlapping rolling
windows of the recent user-message stream, so a single interrupt is echoed
across every checkpoint whose window still contains it. Deduping by
`session` + distinct marker snippet in the `recent:` field collapses 15 diary
drawers to **5 genuine interrupt events across 4 sessions**:

| Session | wing | checkpoint drawers | distinct interrupt events |
|---------|------|------:|------:|
| `a79f4e6d` | wing_wilhelm | 6 | 2 |
| `6c0209bd` | wing_wilhelm | 4 | 1 |
| `bd1c1597` | wing_wilhelm | 3 | 1 |
| `2172308c` | wing_docs | 2 | 1 |

Sample diary drawers (rolling-window echoes of the **same** event):
- `diary_wing_wilhelm_20260525_161256379756_d06694e919da` and
  `diary_wing_wilhelm_20260525_164607115835_de1f502f9525` — the font/styling
  saga (`6c0209bd`): `…no it's still not styled, on both my ipad and simulator |[Request interrupted by user]| …`
- `diary_wing_wilhelm_20260529_194719723485_d90bc5ef49eb` and
  `…_20260529_203154906549_12867c5f8cd2` — the restEndpoint/architecture
  session (`a79f4e6d`): two distinct interrupts in one session.
- `diary_wing_docs_20260526_220050305825_6ea2d1542903` /
  `…_221122797603_0bc00ad4bc27` — custom-signalk-paths verification (`2172308c`).

## (c) Distortion 2 — self-referential contamination

All **7 `wing_contexts` matches** and **2 of the 4 `sessions` matches** are not
interrupts — they are drawers that *quote the marker as data* because they are
mined transcripts of the very sessions that planned/ran this interrupt
analysis. Provenance is unambiguous:

| Drawer (embedding_id) | wing | source session | what it actually is |
|---|---|---|---|
| `drawer__users…claude_contexts_problems_f6cb049f…` (+6 more) | wing_contexts | `11d224a2…` (claude-contexts, filed 2026-05-30 11:33) | the mempalace-analysis planning chat — quotes search hits & the PLAN line "Interrupt density per project" |
| `drawer_sessions_technical_ca93f57c…` | sessions | `addcc1d5…mempalace-analysis.jsonl` (2026-05-30) | **this** Facet session's own transcript (the PLAN.md prompt) |
| `drawer_sessions_technical_2b11deca…` | sessions | `addcc1d5…/subagents/agent-a404…` (2026-05-30) | the Facet-1 subagent transcript |

Removing these 9 drains `wing_contexts` to **0 genuine interrupts** and
`sessions` to its 2 real records. The infra wing's table-topping 11.86/100 was
entirely the analysis observing itself.

## (d) Distortion 3 — genuine primary records barely exist

Only **2 drawers** are standalone primary interrupt records — the isolated
line `> [Request interrupted by user for tool use]` mined as its own drawer:

- `drawer_sessions_technical_9faa5c33e124bf269b2dc585` — src `6d867d45…jsonl`
  (claude-contexts mempalace-deployment session, 2026-05-25)
- `drawer_sessions_technical_046f4d216249fc4fa99dc7f0` — src `d37841b1…jsonl`
  (claude-contexts session, 2026-05-25)

The pipeline mostly does **not** isolate the interrupt line as a drawer; it gets
absorbed into a larger technical chunk or survives only as a diary echo. So a
drawer-level interrupt census is structurally a lower bound on true events.

## (e) De-distorted picture — genuine interrupt events by work type

| Work type (wing) | genuine interrupt events | distinct sessions | source |
|------|------:|------:|--------|
| iOS/UI — wing_wilhelm | 4 | 3 | diary dedup (b) |
| infra/contexts — claude-contexts | 2 | 2 | standalone records (d) |
| docs — wing_docs | 1 | 1 | diary dedup (b) |
| wing_pivac / wing_code | 0 | 0 | — |

(The 2 infra events live physically in the `sessions` wing because raw
claude-contexts transcripts mine there; `wing_contexts` proper has 0 genuine.)

## (f) Hypothesis: "iOS/UI (wing_wilhelm) has 5-10x the interrupt density of infra/docs"

**REFUTED.**

1. **Raw density refutes it directly:** wing_wilhelm 9.77/100 is *lower* than
   wing_contexts (11.86) and wing_docs (11.11) — the opposite of a 5-10x lead.
2. **The raw metric is meaningless anyway** — its top three rows are produced
   by diary rolling-window duplication (b) and analysis self-contamination (c),
   not by user behavior.
3. **On de-distorted genuine events**, iOS/UI does carry the *most* interrupts
   (4), vs docs 1 and infra 2 — directionally consistent with the *spirit* of
   the hypothesis (UI/simulator work interrupts more than docs/infra). But
   4 vs 3 is ≈1.3x, nowhere near 5-10x, and at single-digit counts over a
   ~2-week corpus the ratio is statistically empty.

**Verdict:** the quantitative claim is refuted; only a weak qualitative lean
("hands-on iOS work generates somewhat more interrupts") survives, and even
that rests on ~5 events.

## (g) Methodological takeaways (feed Facet 5)

- **Drawer counts ≠ event counts.** Diary checkpoints inflate any per-wing
  content tally 3-6x via rolling-window overlap; always dedup by
  `session` + snippet before computing per-wing rates.
- **The corpus contaminates itself.** Sessions that *analyze* the palace get
  mined back into it (here, 9 of 26 matches). Any keyword census must filter
  drawers whose `source_file` is a mempalace-analysis / claude-contexts
  meta-session, or it measures the analysis, not the work.
- **`sessions` is a cross-project catch-all** (90% of all drawers) and is not a
  "wing" in the behavioral sense — interrupts from wilhelm/contexts work land
  there as raw transcript chunks, so per-wing density on the project wings
  undercounts. True interrupt density needs the raw `.jsonl` transcripts, not
  the mined drawers. This is the single biggest limit on this facet.
