# MemPalace Behavioral Analysis — Pass 2 Synthesis: bowling-league-tracker

> **Executive summary (5 lines).**
> 1. **Operating mode, not personality, drives the metrics.** Bowling was itself a ralph loop: 561 of 570 sessions (98.4%) contain *zero* human input, so David's live channel collapsed to two registers — terse approvals and spec-level steering — with the conversational middle gone.
> 2. **Bowling CONFIRMS every load-bearing baseline finding and amplifies them:** precision tracks how nameable the broken artifact is (82% precise here, the corpus high); over-asking/planning is the #1 interrupt surface (75% of corrections vs baseline's 47%); the precise→vague collapse is the abandonment tripwire (fired twice, both correct).
> 3. **It DIVERGES on proportion, not structure:** the ≤3-word share doubles (24%), the diagnostic rate doubles (28%), the interrupt long tail (stale-state, mid-flight redirect) vanishes, and a new *operational* interrupt appears (killing a ralph iteration at launch).
> 4. **What baseline couldn't see:** the full uncapped directive tail, a delegated build's true interrupt surface (it collapses onto the `ExitPlanMode` gate), and that David's substantive thinking migrates *out* of the turn-by-turn channel into the up-front `PLAN.md`.
> 5. **The single highest-leverage move for intense builds: get the plan right on the first presentation** — fold in adjacent scope, surface assumed scope boundaries, never silently re-present a killed plan — because once the plan settles, a week-long autonomous build runs with near-zero corrective interrupts.

Sources: `bowling/B1-directives.md`, `bowling/B2-diagnostics.md`, `bowling/B3-corrections.md`;
baseline `baseline/INSIGHTS.md` + facets. Corpus: 570 uuid-named main-thread `*.jsonl`
sessions, bowling-league-tracker, 2026-04-30 → 2026-05-07 — the largest single
collaboration in the palace. Live human corpus after filtering the ralph harness prompt:
**79 directives, 22 diagnostics, 8 interrupts.**

---

## 1. Where bowling CONFIRMS the baseline

- **Precision tracks how nameable the broken artifact is — confirmed and pushed to a new
  high.** Baseline's central diagnostic thesis was that diagnostic precision rises with how
  pointable the defect is: infra (nothing to point at) = 0 diagnostics, iOS/UI (visible
  artifact) = 71% precise. Bowling is *all* product work and its hardest surface — the
  AI-stats-query engine — emits **quotable text**, the most reproducible bug class possible.
  Result: **81.8% precise (B2a)**, above even baseline's visible-UI high-water mark. David
  pasted the exact question and the exact wrong answer every time (`d9e08746:473` "Who has
  the most career strikes" → wrong "707"; `:534` audio drops the last letter; `:558`
  "worthless" + repro). The thesis extends cleanly: *reproducible-output features beat
  visible-UI bugs for diagnostic precision.*

- **Hedges are politeness wrappers, not vagueness — confirmed, "almost a law" (B2c).**
  Baseline flagged that a keyword classifier keying on "seems"/"I think" mislabels ~50% of
  David's reports. Bowling makes it nearly absolute: *every* "seem(s)" in the corpus
  (`:473 :534 :558 :783 :796`) is immediately followed by a verbatim reproduction. A regex
  keying on "seems unreliable / seems worthless" would misclassify five of the most precise
  messages in the build. **The lever "ask David to be more precise" remains wrong.**

- **The precise→vague collapse is the abandonment tripwire — confirmed, fired twice (B2d).**
  Baseline's canonical case was the serif-font saga: language degraded from named symptoms
  to pure affect exactly when fixes stopped converging. Bowling reproduces this *twice*. The
  llama-engine saga (`d9e08746`) ran a chain of precise reports (`:473 → :534 → :558 → :783
  → :796`) that never made the feature good, then collapsed to the session's one vague
  message `:629` ("I'm not sure how useful it will be…"), and one message later David
  changed tack entirely: `:634` "prepare for me to ask to remove all the llama
  infrastructure." The ultra-plan round-trip (`f1e54751`) did the same: precise sync attempts
  (`:82 :90 :111`) failed, ending on the vague `:126` "looks like things got messed up on the
  plan side, let's just leave it the way it is." Both times the vague message signaled *the
  approach is wrong*, not *debug this once more* — and both times David abandoned the
  approach within one or two messages.

- **Over-asking / plan-proposing is the #1 interrupt surface — confirmed (B3c/d).** Baseline
  Facet 4's headline: 47% of corrected interrupts land on Claude *asking* or *proposing*
  rather than acting. Bowling confirms the direction and the mechanism — the single
  most-interrupted action is Claude presenting a plan (`ExitPlanMode` = 62.5% of all markers).

- **Over-confidence is caught at the same rate and the same way (~24–25%, B3d).** Baseline
  caught confident-but-wrong scope/analysis claims *before* they became edits at ~24%.
  Bowling's lone analysis correction is `d9e08746:818` — "wait you are saying remove fun
  stats from the LLM surface, that's just your tool not the page in the app right?" — David
  interrupting *mid-thinking* to confirm a scope boundary before it turned into a deletion.
  This is the twin of baseline's `:816` "your tool not the page" catch (same session-id
  family, same instinct).

- **`merge` is the most stable terse command across every project — confirmed (B1e).**
  `merge` is the #1 leading verb in *both* corpora ("merge it" / "merge and deploy" ×6).
  Git/publish mechanics are the one register where the terse-operator stereotype holds.

## 2. Where bowling DIVERGES — and why

The divergences are all downstream of one fact: **bowling was a delegated ralph-loop build,
while the baseline was post-2026-05-25 hands-on, turn-by-turn cross-project collaboration.**
Delegation strips out the conversational middle, so the surviving signal *concentrates*.

| Metric | Baseline | Bowling | Direction |
|---|---|---|---|
| ≤3-word directives | 12.8% | **24.1%** | doubles |
| Modal word bucket | 8-15 (44.5%) | **16+ (34.2%)** | shifts up; bimodal |
| Verb-leading openers | 26.1% | **15.2%** | drops |
| Diagnostic rate | 14% | **27.8%** (product-only 22.8%) | doubles |
| Vague : precise | 0.45 | **0.22** | halves (more precise) |
| Over-asking interrupt share | 47% | **75%** | amplifies |
| Stale-state + mid-flight-redirect | 30% | **0%** | vanishes |
| Human-input density | message-by-message | **9 / 570 sessions** | 98.4% autonomous |

- **The directive distribution goes bimodal, and the conversational middle hollows out
  (B1b).** Live directives split into a doubled ≤3-word spike (terse approvals: "merge and
  deploy", "do it", "yes keep going") and a fat 16+ tail (feature specs + multi-symptom
  diagnostics). The 4-7 trough is the casualty: the step-by-step middle was being done by the
  loop, not typed by David. He shows up to **gate** and to **steer at the spec level**, little
  in between.

- **The diagnostic rate doubles but for a delegation reason, not a behavior change (B2a).**
  With the non-diagnostic middle gone, diagnostics are simply a larger slice of the little
  David types. One session, `d9e08746`, holds 13/22 = 59% of all diagnostics — the
  non-converging AI-query feature — exactly as baseline's diagnostics concentrated in the
  non-converging WilhelmSK serif sessions.

- **The interrupt long tail vanishes and a new operational category appears (B3d).**
  Baseline's stale-state (18%) and mid-flight-redirect (12%) categories are **empty** here:
  you cannot interrupt a build on stale facts you are not watching proceed. In their place are
  three **terminal/operational** interrupts — two of them David killing a ralph iteration *at
  launch* (`4583c448:12`, `d8cdcf9a:7`), an interrupt *of the harness* the attended baseline
  never produced. The interrupt surface collapsed onto the one moment David is still in the
  loop: the plan-approval gate.

- **The "no…"-opened root-cause reversal does not occur.** Baseline's canonical
  over-confidence tell (Claude narrates a wrong causal theory, David opens with "no it's still
  not styled…") is **absent** from bowling. Because the hard feature emitted quotable defects,
  David's corrections arrived as *new precise directives in the next session* (the B2 stream),
  not as interrupts of a wrong fix mid-flight.

## 3. What bowling reveals that the baseline couldn't

- **The true, uncapped directive tail.** Baseline ran on palace diary drawers truncated at
  ~80 chars, so its 16+ bucket was artificially capped at 16-18 words. Bowling reads raw
  JSONL: the 16+ tail is *real* (34.2%, the modal bucket) and contains full feature specs and
  multi-symptom reports. Baseline's length metrics were systematically compressed; bowling
  shows the genuine shape.

- **What a delegated build's interrupt surface actually looks like.** Baseline measured
  attended, synchronous work. Bowling is the first window into the opposite mode and shows the
  interrupt corpus doesn't just shrink (8 markers across 570 sessions) — its *center of mass
  concentrates* onto plan presentation (75%). This is invisible in any attended corpus.

- **Where David's substantive thinking goes when he delegates.** The baseline implicitly
  assumed thinking happens in the turn-by-turn channel. Bowling shows that under delegation it
  **migrates out** — into the `PLAN.md` David writes up front, and into long diagnostic reports
  only when the autonomous output needs correcting. The terse live channel is not David being
  terse; it is David having front-loaded the intent.

- **A single coherent week-long build, not a cross-project mix.** Baseline blended four wings
  over two weeks. Bowling is one product, one intense week — so its patterns are not averages
  across heterogeneous work; they are what one sustained build actually looked like.

## 4. Recommendations tuned to intense / delegated build sessions

These refine baseline §4. The baseline's levers (suppress premature asks; treat precise→vague
as a change-tack trigger) all hold. Bowling adds that in a delegated build, **the entire
human-attention budget is spent at the plan gate**, so that is where tuning pays off most.

1. **Get the plan right on the first presentation — this is the whole game for a delegated
   build (B3a/e).** 75% of all corrections landed on `ExitPlanMode`. Concretely:
   - **Fold in the obvious adjacent scope before presenting.** `a68cadf2:76` "would it make
     sense to re-package this plan so it can be executed in a ralph loop?" and `f1e54751:42`
     "I would also like to add a voice option… handy if I'm using on a phone or ipad at the
     alley" are both *"your plan is good but too narrow"* — scope grafted onto a plan
     presented as complete. Present a plan already widened with the likely extensions and ask
     once.
   - **Surface the scope boundaries you are *assuming*, not just the steps.** `d9e08746:818`
     "wait you are saying remove fun stats from the LLM surface, that's just your tool not the
     page in the app right?" — a confident scope claim caught mid-thinking. State the boundary
     ("this removes the LLM tool surface, NOT the user-facing page") in the plan so David
     doesn't have to interrupt to extract it.
   - **Never silently re-present an unchanged plan after a kill.** `f1e54751` was interrupted,
     re-shown, and interrupted *again* (`:130`, `:140`) before David could park it to backlog
     (`:144`). A killed plan needs a *changed* re-presentation or an explicit "what should
     change?", not a verbatim replay.

2. **The autonomous middle is low-risk to interrupt — spend attention on the gate, not the
   loop (B3e).** 570 sessions produced 8 interrupts and zero corrective interrupts of
   *execution*. Once the plan is settled, the loop runs clean. Don't over-instrument the
   running build; instrument the plan.

3. **Treat the rare drop to vague affect as "abandon the approach," not "debug once more"
   (B2d).** In bowling the precise→vague tripwire fired twice and both times the correct move
   was to rip out the approach (drop local llama → switch to Anthropic API; stop fighting the
   ultra-plan round-trip). On the 2nd–3rd failed fix of the same theory, propose changing tack
   rather than iterating — David is about to anyway.

4. **In a delegated build, corrections arrive as next-session directives, not interrupts —
   read them as a stream (B3-limits).** B2's 22 diagnostics, not B3's 8 interrupts, are the
   real correction channel here. When picking up a ralph iteration, the prior session's
   closing diagnostic *is* the correction; treat it with the weight an interrupt would carry
   in attended work.

5. **Don't read terseness as low engagement.** The doubled ≤3-word rate (B1f) is an artifact
   of delegation, not disengagement. "merge and deploy" ×6 is David gate-keeping a fleet he
   designed up front. The substantive direction is in the `PLAN.md` — read it as the spec, not
   as boilerplate.

## 5. Methodology limits of the raw-transcript approach

- **Small N on interrupts (B3-limits).** 4 distinct corrections is too few for stable
  percentages; shares (75% / 25%) are reported alongside raw counts and should be read as
  *direction, not precision*. The direction (plan-gate dominance up, long tail gone) is robust
  because it is structural, not statistical.

- **Interrupts undercount in-loop friction (B3-limits).** A ralph-loop build records most
  corrections as fresh directives in the *next* session (the B2 stream), not as interrupt
  markers. B3 measures only synchronous friction — which in this corpus was almost entirely
  plan review. The 8 interrupts are the visible tip; the 22 diagnostics are the body.

- **The diagnostic rate is inflated by delegation, not behavior.** The 28% rate (vs baseline
  14%) is a *denominator* effect: the non-diagnostic conversational middle is absent, so
  diagnostics are a bigger fraction of a much smaller live corpus. The product-only 22.8% is
  the fairer comparison, and it is still above baseline — but the gap is partly compositional.

- **One feature dominates the diagnostic signal.** `d9e08746` (the AI-query saga) is 59% of
  all diagnostics. The corpus-high 82% precision is real but is heavily weighted by a single
  unusually-reproducible feature class (LLM output); a build without a quotable-defect surface
  would likely sit lower.

- **The vague/precise call is hand-classified.** Baseline §3e proved a keyword regex is wrong
  ~50% of the time on David's politeness-wrapped reports, so B2 classifies by judgment. This is
  the right call but is not mechanically reproducible; another reader might move a borderline
  message (the boundary cases are noted in `_b2_dump.txt`).

- **One corpus, one operating mode.** Bowling is a single delegated build. Its divergences
  from baseline are best read as *what delegation does to the metrics*, not as a second
  independent sample of David's behavior. The CONFIRMS in §1 are the durable findings; the
  DIVERGES in §2 are mode effects.
