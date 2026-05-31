# Iteration-2 Synthesis — F-A + F-C across three wings (raw `.jsonl`)

> **Executive summary (5 lines).**
> 1. **Over-asking is NOT the dominant attended-work interrupt.** Across the three attended wings only **1 of 9** genuine interrupts was an `AskUserQuestion`/`ExitPlanMode` pause; the baseline's "47% over-asking" was a delegated-mode artifact — in *attended* multi-project work the plan/ask gate rarely bites.
> 2. **The real recurring attended failure is acting on the harder path before exhausting known sources/world-state — 5 of 9 interrupts.** Verify-world-state should be elevated above suppress-over-asking for attended work.
> 3. **The precise→vague tripwire is work-type-specific, not universal:** it fires cleanly only when Claude iterates its *own* fix across retries (wilhelm serif saga, ~34 turns). It is a **dead letter in directed infra** (contexts: zero diagnostics) and **misfires in docs** (the vague messages are David's own file-uncertainty or transient color-perception, not a wrong-fix signal).
> 4. **Mode, not project, sets the interrupt surface.** Delegated builds (bowling, docs-ralph) concentrate friction onto the plan gate (or emit none); attended work distributes it across the directive stream. The docs wing contains both modes and replicates the bowling delta internally.
> 5. **Iteration 3 can move the directive-length/density facet to cleaned drawers (P2/P3 landed), but F-A and F-C still require raw transcripts** until interrupt-pair mining (P1) and turn-segmentation land.

Sources: `wilhelm/{F-A,F-C}.md`, `contexts/{F-A,F-C}.md`, `docs/{F-A,F-C}.md`,
`00-inventory.md`; `baseline/INSIGHTS.md`; `bowling/INSIGHTS-bowling.md`.
Corpus: 33 attended + delegated main-thread sessions across three wings
(wilhelm 10, docs 17, contexts 6), raw `.jsonl` on the Mini, 2026-05-24 … 05-30.

---

## 1. Cross-project pattern (from F-A)

The cross-wing interrupt corpus, using the **two-variant probe** (catches both
`[Request interrupted by user]` and `…for tool use`, rejects markers embedded in
tool blocks — see the counting caveat below):

| Wing | Mode | Main sessions | Genuine interrupts | Rate /100 user-msg | Dominant theme |
|------|------|--------------:|-------------------:|-------------------:|----------------|
| `wing_wilhelm` | attended | 10 | **5** | ~1.8 | direction-of-effort (theory / misdiagnosis / skip-source) |
| `wing_contexts` | attended | 6 | **3** | ~3.0 | world-state + 1 over-ask (all in one session, `6d867d45`) |
| `wing_docs` (attended half) | attended | 6 | **1** | low | wrong-location / world-state |
| `wing_docs` (ralph half) | delegated | 11 | **0** | 0 | none — no synchronous human in loop |
| `wing_bowling` (ref) | delegated | 570 | 8 | — | plan gate (`ExitPlanMode` 75%) |

**The headline correction to the baseline.** Baseline Facet 4 named over-asking
(`AskUserQuestion`/`ExitPlanMode`) the *costliest* friction — 47% of corrected
interrupts. Iteration-2's clean per-wing extraction shows that across the **9
genuine attended interrupts**, the theme breakdown is:

- **Verify-world-state / exhaust-known-sources before the harder path — 5/9:**
  wilhelm #4 (`a79f4e6d` t7→t9: dig into break before checking the upstream lib
  version), wilhelm #5 (`bd1c1597` t9→t11: fresh start instead of recalling a
  prior-session design), contexts #2 (`6d867d45` t13→t14: Pi-NFS probe vs known
  direct rsync access), contexts #3 (`6d867d45` t15→t16: re-test vs NAS simply
  powered off), docs #1 (`2172308c` t13→t14: SSH-the-Pi vs files in OneDrive).
- **Misdiagnosis / narrating-a-theory — 3/9:** wilhelm #1 (`6c0209bd` e#1280:
  HSTS-pin theory narrated as it reasons), wilhelm #2 (`6c0209bd` e#1104:
  lazy-loading tangent), wilhelm #3 (`a79f4e6d` e#585: wrong-anchor misdiagnosis).
- **Over-asking — 1/9:** contexts #1 (`6d867d45` t6: `AskUserQuestion` fired on a
  question David had *already queued*, against an instruction that had *already*
  said "ask if you still have questions").

So in attended multi-project work the dominant interrupt is **not** over-asking —
it is **escalating to the harder/remote path before exhausting the local, known,
or prior-session source** (5/9). Over-asking is a single, almost pathological
instance. And the over-asking that the baseline did see was concentrated in
exactly the mode iteration-2 confirms it lives in: **delegated builds** (bowling,
75% `ExitPlanMode`), where the plan gate is the *only* synchronous touchpoint so
all friction piles onto it.

**What drives the variation: operating mode and what is pointable.** In attended
work David steers continuously, so a question that targets a genuine preference
is simply *answered*, not interrupted — docs proves this starkly: `AskUserQuestion`
fired **8 times** (`2bb09e72` ×5, `e8078067` ×3) and **0** were interrupted,
because they asked about brass-RGB matching and picker-UX, the exact
user-preference case where asking is warranted. The over-asking interrupt only
appears when the user *already had a direction* (contexts #1). Where the human is
NOT continuously in the loop (delegated ralph/bowling), the only correction tool
is interrupting the plan gate or killing the iteration at launch — so that is
where the entire interrupt surface concentrates.

**A second texture the baseline didn't predict (docs):** hands-on collaborative
operation of an *external system*. The npm-publish saga (`083cf8fa` t9–t26) is
long and interactive but produces **no interrupts and no Claude-fix spiral** —
David hand-drives npm's 2FA/publish UI and reports external behavior (*"it's not
giving me an authenticator option"* t16, *"I did not get a browser prompt"* t19);
Claude advises, npm misbehaves. This generates many precise status reports that a
naive classifier would read as bug reports, but the failure is in the external
system, not Claude's work.

## 2. Per-project convergence-failure profile (from F-C)

| Wing | Diagnostic sessions | Convergence failures | Fingerprint | Tripwire status |
|------|--------------------:|---------------------:|-------------|-----------------|
| `wing_wilhelm` | 2 (1 sustained) | **1** (`6c0209bd` Thread B) | non-mechanical bug spanning app + plugin + server (WebView styling/HSTS) | **fires, lagging** |
| `wing_docs` | 3 (none of the wilhelm kind) | 0 wrong-code | information-location, perceptual color-match, external-system | **misfires** |
| `wing_contexts` | **0** | 0 | directed decide-and-build; no fix is iterated | **never arms** |

**wilhelm — the one true convergence failure.** `6c0209bd` Thread B (serif/unstyled
font) ran reported-t17 → resolved-t51, **~34 turns over ≥5 failed fixes**. The
precise→vague tripwire **holds but is lagging**: the ask starts precise (t17
*"change to sans serif"*); the first wobble is t27 *"what gives?"* (after failed
fix #1); the unambiguous vague peak is t40 *"something is funny here… Why is this
getting messed up?"* — emitted only after **three+** failed attempts. The vague
turns did **not** resolve anything; resolution came ~10 turns later when David
**dropped back to precise** (t46 *"jumps correctly but unstyled"*) and re-asserted
the bare symptom over Claude's HSTS theory (the e#1280 interrupt). Contrast the
fast cases: Thread A (~3 turns) and `a79f4e6d` (~6 turns, even across a
misdiagnosis) stayed fully precise and converged quickly. **No failed-fix chain ⇒
no vague signal.**

**contexts — the clean negative control.** Zero diagnostic sessions. The
failure-vocabulary sweep (`_sweep.py`) across all 6 sessions / ~99 user messages
returns exactly **one** match, a false positive (an *instruction* containing the
word "don't"). The wilhelm convergence vocabulary (*"still seeing serif"*,
*"something is funny"*) is **completely absent**. Infra work is *directed* — a
forward decision stream (*"what do you recommend"* → *"remodel"* → *"go with #1"*,
`96bbb1db` t6–t9) — never *diagnosed*, because there is nothing visual to point
at. Baseline's "zero diagnostics" claim **HOLDS literally** in raw transcripts
(unlike its "zero interrupts" claim, which raw data corrected to 3).

**docs — the tripwire misfires.** docs *has* multi-turn diagnostic threads but
none is the wilhelm pattern. Thread 1 (`2172308c`, locate the `.wlyt` source of
truth): the vague message (t12 *"I'm not sure where it would be"*) is **David's
own uncertainty about his own files**, and it *precedes* Claude's misstep
(SSH-the-Pi) rather than lagging it — the tripwire reads backwards. Thread 2
(`2bb09e72`, color-matching): the one vague message (t15 *"they look a little
off"*) is **transient perceptual judgment, self-diagnosed in the same breath**
(*"let me resample as srgb"*) and resolved in ~3 turns. Thread 3 (`e8078067`, iOS
picker): precise symptom + self-supplied hypothesis, **one-turn** resolution. None
is a lagging indicator that Claude's approach is wrong.

**The durable F-C finding:** the precise→vague signal is **specific to
debug-by-retry of a non-mechanical bug** (Claude iterating its *own* fix across
retries). It is a dead letter where no fix is iterated (contexts) and actively
misleading where vagueness comes from the user's own missing information or
normal perceptual iteration (docs). Bowling independently confirms the scope: the
tripwire fired **twice**, both inside the single non-converging feature
(`d9e08746`, the AI-query engine), both times correctly predicting David would
abandon the approach within a message or two.

## 3. Bowling delta

The bowling pass was one product, one intense week, **delegated** ralph mode
(98.4% autonomous). Iteration-2 is **attended**, multi-project, several work
types. Reading them together:

**Confirms (durable across modes):**
- **Precision tracks how pointable the defect is.** Bowling pushed this to 82%
  precise on quotable LLM output; iteration-2 extends it across the *nameability
  spectrum*: contexts (nothing to point at) = 0 diagnostics, wilhelm (visible UI
  artifact) = the one convergence saga, docs (reproducible/visual) = precise
  symptoms throughout. The thesis generalizes cleanly.
- **The precise→vague abandonment tripwire.** Bowling fired it twice (both in the
  one non-converging feature); iteration-2 fired it once (wilhelm's one
  non-converging bug). Same shape both passes: the signal **concentrates in the
  single non-converging artifact**, not spread across the work.
- **Corrections-arrive-as-next-directive in delegated mode.** docs-ralph (11
  sessions, 1 user prompt each, 0 interrupts) reproduces bowling's structural
  finding exactly: a delegated build has no synchronous human, so the interrupt
  is not an available tool and corrections, if any, land as the *next* session's
  opening directive.

**Diverges (mode effects, now shown to be mode effects):**
- **Over-asking / plan-gate dominance is a DELEGATION artifact, not universal.**
  Bowling: 75% of interrupts on `ExitPlanMode`. Attended iteration-2:
  **0** `ExitPlanMode` interrupts across all three wings, and 8 `AskUserQuestion`
  calls in docs drew **0** interrupts. The plan/ask gate dominates the interrupt
  surface *only when it is the sole synchronous touchpoint*. This is the single
  most important reconciliation between the two passes: the baseline's "over-asking
  is costliest" was measuring a corpus skewed toward delegated/gated interaction.
- **The docs wing replicates the bowling delta internally.** Its 6 attended
  sessions (1 interrupt, asks-answered-not-interrupted) vs its 11 delegated ralph
  sessions (0 interrupts by construction) are a within-wing, work-controlled
  version of the cross-corpus baseline-vs-bowling comparison — and they agree.

**Net:** bowling's CONFIRMS are the durable behavioral findings; bowling's
DIVERGES were mode effects, and iteration-2's attended multi-project data is the
control that proves it. The precise→vague tripwire and the nameability-precision
law survive both modes; the plan-gate interrupt concentration does not.

## 4. Revised CLAUDE.md / global.md recommendations

The five validated levers currently in `global.md` ("Asking, planning, and
diagnosing") were derived from one pass. Iteration-2's verdict on each:

1. **"Exhaust readable sources before asking/planning; only ask on genuine
   preference."** → **KEEP, but reframe the cost.** docs refutes the literal
   "asking is costly" reading (8 asks, 0 interrupts). The cost is asking **when
   the user already had a direction** (contexts #1), not asking per se. Merge this
   with lever 4: the unifying attended failure (5/9 interrupts) is *escalating to
   the harder/remote path or starting fresh before exhausting the local, known,
   or prior-session source*. The lever should lead with "before the harder path
   **or** before asking, exhaust local/known sources and recall prior-session
   work," and treat "don't over-ask" as the *narrow* case of it.

2. **"In a plan, fold in adjacent scope; state assumed boundaries."** → **KEEP
   as-is, but note it bites hardest in delegated builds.** Validated overwhelmingly
   by bowling (75% plan-gate); in attended iteration-2 it drew zero interrupts
   because the human re-scopes continuously. Worth a half-sentence that this lever
   pays off most when the plan gate is the only synchronous touchpoint (ralph /
   delegated builds) — which `global.md` already gestures at.

3. **"Treat a flat 'no…' as a hard stop; re-derive the symptom; state the expected
   observable."** → **KEEP, strongly confirmed.** 3 of 5 wilhelm interrupts open
   with a flat "no…" or redirect (#3, #4, #5); the canonical e#1280 case is Claude
   narrating an HSTS theory while the page is simply still broken.

4. **"Verify world-state (deps, access, versions) before assuming the harder
   path."** → **KEEP and ELEVATE.** This is the **most common attended-interrupt
   theme** across all three wings (wilhelm #4, contexts #2/#3, docs #1 = 4 of 9
   directly, 5 counting the recall-prior-work case). It deserves to sit *above*
   the over-asking lever in priority for attended work, which inverts the
   baseline's emphasis.

5. **"Read precise→vague as a change-tack signal; by the 2nd–3rd failed fix
   propose abandoning the theory."** → **KEEP, but ADD A SCOPE QUALIFIER — the
   single most important refinement.** The signal fires *only* when Claude is
   iterating its **own fix** across retries. It is a dead letter in directed infra
   (contexts) and **misfires** in docs, where vagueness is the user's own
   missing-information state (*"I'm not sure where it would be"*) or transient
   perceptual judgment (*"look a little off"* → self-diagnosed to sRGB). As written
   the lever reads as always-on and would mislead in the majority of sessions
   (config/admin/Q&A/visual-iteration) where no fix is being iterated. Add: *"this
   applies only when you are iterating your own fix across retries; David's
   vagueness about his own files, or transient perceptual judgment on visual
   output, is not this signal."*

**Candidate new lever (minor):** when David is hand-driving an external system
(npm, app-store, a 2FA UI) and reporting its behavior, the failures are in that
system, not in your work — advise and wait; don't treat his precise status
reports as bugs to fix or as a diagnostic spiral. (docs npm saga.) Low frequency;
worth at most one line.

## 5. What iteration 3 should do differently

P2 (`recent:` truncation 80→400) and P3 (meta-analysis mining filter) have landed,
but they only affect **future drawer mining** — existing drawers are unchanged.
The question PLAN poses is whether iteration 3 can run on cleaner drawers instead
of raw transcripts. **Partially — and the split is sharp:**

**Answerable on cleaned drawers now (P2/P3 sufficient):**
- **Directive-length / word-count distribution** (baseline Facet 1, bowling B1).
  P2 uncaps the `recent:` field, so word counts are no longer compressed at ~80
  chars — the metric bowling could only get from raw JSONL is now drawer-queryable.
- **De-duplicated, meta-filtered per-wing density** (baseline F-D / Facet 2g).
  P3 stops the palace mining its own analysis sessions (the 35% contamination
  baseline found), so a cleaned density re-run is finally meaningful.
- Iteration 3 should re-run *these two* on post-patch drawers as a cheap
  validation that P2/P3 did what they claim.

**STILL requires raw transcripts (P2/P3 insufficient):**
- **F-A (interrupt corpus)** needs the **interrupt→correction-pair extractor**
  (INSIGHTS §5 #1, "P1") plus the **two-variant marker fix**. Iteration-2's whole
  F-A method depended on (a) catching the `…for tool use` variant and (b)
  rejecting markers embedded in tool blocks — *every* attended wing's exact-string
  count was wrong (contexts 0→3, docs 0→1). Drawers isolate the marker only and
  never preserve next-message adjacency, so F-A collapses to ~0 on drawers until
  P1 lands. **This is a hard blocker.**
- **F-C (precise/vague timelines)** needs **turn-segmentation / `has_user_turn`
  metadata** (INSIGHTS §5 #2, still unaddressed). The per-turn precise→vague
  timeline cannot be reconstructed from `extract_mode=exchange` content windows.
  Until drawers are turn-segmented, F-C stays a raw-transcript facet.

**So the iteration-3 plan:** (1) move directive-length + density to cleaned
drawers and confirm P2/P3; (2) keep F-A/F-C on raw transcripts and **file P1
(pair mining + two-variant marker) and turn-segmentation as the explicit blockers**
that would let iteration 4 retire the raw-transcript path; (3) bake the
two-variant probe into whatever extractor iteration 3 uses — any tally keyed on
the bare `[Request interrupted by user]` string systematically undercounts
tool-permission declines, which iteration-2 showed are the *dominant* interrupt
form in directed work (all 3 contexts + the 1 docs interrupt are that variant).

**A new corpus iteration 3 could open:** the `(other)` wings are sizeable and
unanalyzed — `nas-cleanup`/`nas-cleanup-post-migration` (26 sessions, ~21 MB) and
`arch-as-code`. Infra-migration is a *fourth* work type, distinct from contexts'
decide-and-build; it would test whether the "directed, zero-diagnostic" infra
profile generalizes or whether migration surfaces its own failure mode
(stale-state, partial-cutover) the three-wing set didn't contain.
