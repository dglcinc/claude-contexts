# MemPalace Behavioral Analysis — Synthesis & Recommendations

> **Executive summary (5 lines).**
> 1. The "terse imperative operator" stereotype is **wrong**: 74% of David's directives open with a question/ack/proper-noun, the median is ~11 words, and only 13% are ≤3 words.
> 2. The "iOS work interrupts 5-10× more" hypothesis is **refuted** quantitatively; only a weak ~1.3× lean survives, and the raw metric was an artifact of mining duplication + the analysis mining itself.
> 3. David's diagnostics skew **precise 2.2:1**; true vagueness is rare (~4.5% of messages) and is an *escalation signal* that the current fix approach has failed, not a habit.
> 4. The dominant friction is **not code bugs — it's interaction mismatch**: 47% of interrupts land on Claude *asking* (`AskUserQuestion`) or *proposing* (`ExitPlanMode`) when it already had enough to act or read.
> 5. The mining pipeline systematically **destroys the highest-signal data** (interrupt→correction adjacency, turn segmentation) and **contaminates itself** by mining its own analysis sessions — both are fixable.

Sources: `01-directives.md`, `02-interrupts.md`, `03-diagnostics.md`, `04-corrections.md`.
Corpus: ~2 weeks of work (2026-05-25 → 2026-05-30), 2805 drawers, four project wings
(`wing_wilhelm` = WilhelmSK iOS, `wing_docs` = SignalK doc-plugin/npm, `wing_contexts` =
claude-contexts infra/memory, `wing_pivac`/`wing_code` = minor).

---

## 1. What the data CONFIRMED

- **Work type predicts communication register, cleanly and consistently across all four
  facets.** The same three-way split recurs everywhere:
  - *iOS/UI (`wing_wilhelm`)* — longest directives (mean 10.7 words), nearly all diagnostics
    (24 of 32), the most genuine interrupts (4 of ~7), and where vague-escalation lives.
    Visual, hands-on, iterative work generates explanatory prose and symptom reports.
  - *Docs/npm (`wing_docs`)* — similar to wilhelm but slightly vaguer on visual polish and
    his own file-state (the two areas where *David himself* is uncertain).
  - *Infra/memory (`wing_contexts`)* — the terse exception (mean 6.9 words), **zero**
    diagnostics, **zero** genuine interrupts. Infra work is *directed* ("add the rule",
    "remodel"), never *diagnosed* — there is nothing visual to point at.
- **Short barked commands are real but narrow.** They cluster tightly around git/publish
  mechanics: "merge it", "push it", "commit this", "publish 0.1.3". This is the only place
  the terse-operator stereotype holds, and it is a minority register (Facet 1b/1d).
- **The qualitative spirit of the interrupt hypothesis survives even though the number
  fails.** Hands-on iOS/UI work *does* carry the most genuine interrupts and the most
  over-confident-diagnosis corrections (Facet 2e, Facet 4 Theme B) — just at ~1.3×, not
  5-10×, and on single-digit counts.
- **Vague reports and interrupts co-locate in time.** The serif-font saga (sessions
  `6c0209bd`, `a79f4e6d`) is simultaneously Facet 3's canonical vague-escalation case and
  Facet 4's canonical over-confident-diagnosis case. When fixes stop landing, the user's
  language degrades to affect *and* the interrupt rate rises — the same underlying event
  surfaces in both facets.

## 2. What the data REFUTED or surprised on

- **REFUTED — "most directives are ≤3 words" (Facet 1f).** Only 12.8% are ≤3 words; the
  modal bucket is 8-15 words (44.5%) and the median is ~11. Truncation in the mining hook
  (~80 chars) makes long directives look *shorter* than they are, so the true distribution
  refutes the hypothesis even harder.
- **REFUTED — "iOS/UI has 5-10× the interrupt density of infra/docs" (Facet 2f).** Raw
  density actually ranks `wing_contexts` (11.9/100) and `wing_docs` (11.1) *above*
  `wing_wilhelm` (9.8) — the opposite direction. And the raw metric is meaningless: its top
  rows are produced by diary rolling-window duplication and the analysis mining its own
  sessions, not by user behavior.
- **SURPRISE — the corpus observes and contaminates itself.** 9 of 26 interrupt-marker
  drawers were the mempalace-analysis planning/execution sessions quoting the marker *as
  data* (Facet 2c). Any keyword census of this palace measures the analysis unless
  meta-sessions are filtered out first.
- **SURPRISE — David is more precise than the folk model assumes (Facet 3).** Diagnostics
  skew **2.2 precise : 1 vague**, and his hedges ("I think", "still not") are mostly
  *politeness wrappers around precise reports*, not real vagueness — a keyword classifier
  mislabels them half the time (Facet 3e). The actionable lever is **not** "ask David to be
  more precise."
- **SURPRISE — the single most-interrupted Claude action is Claude pausing to ask
  (Facet 4).** 47% of corrected interrupts hit an `AskUserQuestion`/`ExitPlanMode` dialog.
  The mistake category that dominates is interaction, not computation.

## 3. Revised facet list for a future analysis pass

The four facets were bottlenecked by one structural fact: **mined drawers are not
turn-segmented and the diary is the only clean user-message source.** Three of four facets
hit this wall (Facet 2, 3, 4 all fell back to diary `recent:` or raw `.jsonl`). A better
pass would:

- **F-A (replaces 2/4): Mine the raw `.jsonl` transcripts directly for interrupt→correction
  pairs.** Facet 4 got 17 corrected pairs from transcripts vs Facet 2's ~5 from drawers —
  3× the signal. Transcripts, not drawers, are the right grain for any behavioral facet.
- **F-B: In-flight-action taxonomy at interrupt time.** Facet 4 found `AskUserQuestion`/
  `ExitPlanMode` dominate; quantify this across *all* transcripts (not just the 20 sampled)
  and correlate with whether the answer was discoverable (file present, prior-session
  proposal exists).
- **F-C: Precise→vague escalation as a convergence-failure detector.** Facet 3 found vague
  language is a lagging signal of a wrong fix approach. Build a per-session timeline:
  count turns-to-resolution after the first vague message vs after a precise one.
- **F-D: De-duplicated, meta-filtered per-wing rates.** Re-run any density metric only
  after (a) collapsing diary rolling-windows by `session`+snippet and (b) excluding
  `source_file`s that are mempalace-analysis/claude-contexts meta-sessions. Facet 2g.
- **Drop as written:** raw drawer-count density (meaningless), and keyword-based
  vague/precise classification (Facet 3e showed it's wrong ~50% of the time).

## 4. Actionable improvements for David (reduce friction)

These target the *interaction mismatch* that Facet 4 shows is the real cost — but most are
levers on **Claude's** behavior that David can encode once in CLAUDE.md, not habits David
must change. (His diagnostics are already precise; "be clearer" is not the fix.)

1. **Suppress premature `AskUserQuestion`/`ExitPlanMode` — read the obvious source first.**
   The largest interrupt category (Facet 4 Theme A, 8 pairs). In `64edd6be`:73 Claude asked
   whether to read config files that were right there; the correction was "you should. Read
   the claude config files in the claude-contexts folder" (Facet 4 #1/#13). In `bd1c1597`:177
   Claude asked instead of retrieving a prior-session proposal: "in a prior session, you had
   proposed a way to do the context-sensitive integration… Are you finding that?" (#3).
   **Lever:** a CLAUDE.md rule — *before asking or presenting a plan, exhaust the readable
   sources (repo files, claude-contexts, prior session/palace); only ask when the answer is
   genuinely a user preference.* This already partly exists in the global working-style
   ("execute without repeated check-ins") but isn't landing on the ask/plan dialogs.

2. **When presenting a plan, fold in the obvious adjacent scope rather than offering a
   narrow one.** Facet 4 #5/#6: approved plans got scope grafted on by interrupt ("I would
   also like to add a voice option…", "would it make sense to re-package this so it runs in
   a ralph loop?"). **Lever:** plan-mode prompting that explicitly enumerates likely
   extensions and asks once, instead of presenting a minimal plan that invites a redirect.

3. **Treat "no…" as a hard stop and re-derive the symptom from scratch.** Every Theme-B
   correction opens by negating a confident assertion (Facet 4 #9, #10, #12). In `a79f4e6d`:585
   Claude verified a "wrong anchor" fix that wasn't the bug: "no the problem scott is
   reporting is not wrong anchor; the ? is appearing on the wrong screen…". In `6c0209bd`:1280
   Claude wrote a multi-clause HSTS-pin theory and the page was simply still broken: "no it's
   still not styled, on both my ipad and simulator." **Lever:** when a fix is asserted,
   state the *expected observable* and ask David to confirm the observable — don't narrate a
   causal theory as fact before it's verified.

4. **Verify world-state facts instead of assuming the harder path (Facet 4 Theme D).**
   `6d867d45`:498 — "you should have root or nasadmin passwordless access… so you should be
   able to rsync directly"; `a79f4e6d`:228 — "check and make sure you have the latest version
   of WilhelmSKLibrary." Claude assumed missing access / stale deps it could have checked.
   **Lever:** a pre-flight check for dependency currency and existing access before choosing
   an implementation path. (`6d867d45`:510, "nas was powered off," is the one genuinely
   un-knowable case — not actionable.)

5. **Watch the precise→vague transition as a "change tack" trigger (Facet 3d).** When
   David's language collapses from named symptoms to affect ("something else is going on",
   "seems completely screwed up") it means the current approach has failed across retries.
   **Lever:** on the 2nd-or-3rd failed fix in a session, stop iterating on the same theory
   and re-investigate from the symptom — this is exactly where the interrupt-dense sessions
   went wrong.

## 5. Actionable improvements to the mempalace mining pipeline

The analysis surfaced concrete, fixable defects in how the palace is built. Ranked by
signal recovered.

1. **Mine the interrupt→correction *pair*, not the isolated marker (Facet 4 closing).**
   The richest behavioral data in the corpus — what mistake triggered a user interrupt and
   how they corrected it — is almost entirely dropped: the pipeline isolates the marker line
   only twice in 2805 drawers (Facet 2d) and never preserves the next-message adjacency.
   **Fix:** a transcript-aware extractor that, on seeing an interrupt marker, emits one
   drawer containing `(in-flight assistant action, interrupt, next user message)` with
   `source_file`+line metadata. This single change would have made Facet 4 a drawer query
   instead of a raw-`.jsonl` scan.

2. **Tag drawers with turn structure / `extract_mode` so user-message facets are queryable.**
   Three of four facets had to fall back to the diary `recent:` field because `room=problems`
   drawers are `extract_mode=exchange` content windows with no isolable user turn (Facet 3
   caveat: 200 drawers → 0 usable diagnostics). **Fix:** segment drawers by speaker turn, or
   at minimum add a `has_user_turn` / `user_turn_count` metadata field so a query can target
   user prose without scanning prose for `>`-quotes.

3. **Exclude meta/analysis sessions from mining, or tag them `meta=true`.** 9 of 26 interrupt
   matches (35%) were the palace mining its own analysis sessions (Facet 2c). The CLAUDE.md
   already forbids project-mode mining of curated repos, but *convo* mining still ingests
   claude-contexts/mempalace-analysis transcripts and they quote palace internals as data.
   **Fix:** the auto-capture hook should skip (or flag) transcripts whose `cwd`/`source_file`
   is a claude-contexts or mempalace-analysis session, so the palace doesn't measure itself.

4. **Stop counting diary checkpoints as events — or store a stable event ID.** Diary
   rolling-windows echo a single user message across 3-6 overlapping checkpoints (Facet 2b,
   collapsing 15 drawers → 5 events; Facet 1/3 both had to dedup longest-prefix). **Fix:**
   either de-duplicate at mine time (one drawer per distinct message, first-seen wins) or
   stamp each message with a stable `(session, message_index)` ID so downstream dedup is
   exact instead of prefix-heuristic.

5. **Raise or remove the snippet truncation in the diary `recent:` field.** Messages are
   stored truncated at ~80 chars, often mid-word (Facet 1 caveat). This corrupts every
   word-count/length metric and clips the locator out of otherwise-precise diagnostics
   ("the font that shows in the simulator is a serif…" cut off). **Fix:** store the full
   user message (or a much higher cap) in `recent:`; it is the single most-used field for
   behavioral analysis and the only clean user-message source.

6. **`sessions` is a 90%-of-everything catch-all, not a behavioral wing (Facet 2g).**
   Interrupts and diagnostics from wilhelm/contexts work land in `sessions` as raw transcript
   chunks, so per-project-wing rates undercount. **Fix:** classify `sessions` drawers to
   their originating project wing using `source_file`/`cwd` at mine time, so per-wing metrics
   are meaningful instead of dominated by an undifferentiated bucket.

---

*All claims above cite specific drawer IDs or `session:idx` transcript references in the
four facet artifacts, which are auditable against the palace and `~/.claude/projects/`.*
