# B3 — Interrupt + correction corpus (bowling-league-tracker) + diff vs baseline

**Source & method.** Full scan of all **570** uuid-named `*.jsonl` main-thread
sessions at `~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker/`
(`agent-*.jsonl` and `*.md` excluded). Parser `bowling/_b3_extract.py` (raw dump
is gitignored scratch). For every line whose user-message body contains
`[Request interrupted by user…` it captures (1) the **in-flight assistant action**
— the last assistant message before the marker, summarized as its tool_use
name(s) + a brief input snippet (a thinking-only block is reported as the Read/tool
that immediately preceded it) — and (2) the **next genuine David message** in the
same session (same `is_human` filter as B1/B2: drops tool-results, `isMeta`,
`<system-reminder>`/slash-command boilerplate, ralph-loop prompts). Marker count
cross-checked with `grep`: **8 markers** (3 `…by user]`, 5 `…for tool use]`) across
**5 sessions** — parser yield matches exactly. Citations are `<8-char-session>:<line>`.

> **Headline — the largest single build in the corpus produced almost no
> interrupts, and every one that mattered landed on a plan.** 570 sessions yielded
> just **8 interrupt markers** (vs baseline's 20 across a far smaller, attended
> corpus). **6 of the 8 markers, and 3 of the 4 distinct corrections, interrupted
> `ExitPlanMode` or a re-presented plan** — the single most-interrupted action is
> Claude *presenting a plan*. The autonomous ralph-loop **execution generated zero
> corrective interrupts**; you cannot interrupt a build you are not watching. This
> both **confirms** and **intensifies** baseline's #1 finding (47% over-asking):
> in an intense delegated build the interrupt surface collapses onto the one
> moment David is still in the loop — the plan-approval gate.

## (a) Volume & density

| Metric | Value |
|---|---|
| Sessions scanned (uuid main-thread) | 570 |
| Genuine David messages (B1/B2 corpus) | 79 |
| **Interrupt markers** | **8** |
| Distinct (interrupt → correction) pairs | 4 |
| Terminal interrupts (no free-text follow-up) | 3 |
| Sessions containing any interrupt | 5 |
| **Interrupts per 100 David-messages** | **10.1** |

Two markers (`f1e54751:130`, `f1e54751:140`) are Claude re-presenting the *same*
plan after the first kill; both resolve to the **one** follow-up `f1e54751:144`, so
5 "corrected" markers collapse to **4 distinct corrections**. The 3 terminal
interrupts are not behavioral corrections (see Theme C): two are David killing a
ralph-loop session at launch, one is a parked-plan re-display with no reply.

### In-flight action when interrupted (all 8 markers)

| In-flight action | Markers | Note |
|---|--:|---|
| `ExitPlanMode` (plan presentation) | 5 | the dominant surface |
| `Read` (+ thinking) | 2 | one mid-analysis (`d9e08746`), one ralph PLAN.md read (`4583c448`) |
| (none — interrupted at session launch) | 1 | `d8cdcf9a` ralph prompt killed before any action |

**`ExitPlanMode` is 5/8 = 62.5% of all interrupts**; counting the
`d9e08746` mid-analysis scope-catch (which was *about* a plan's scope), plan-related
activity is **6/8 = 75%** of every interrupt in 570 sessions.

## (b) The full corpus — all 8 interrupt markers (verbatim)

The plan asks for 20–30 pairs; the corpus contains only 8. **That scarcity is the
finding** (same shape as B2, where 4 vague messages existed, not 10): a ralph-loop
build is mostly unattended, so the interruptible surface is tiny and almost
entirely the plan gate.

### Theme A — Over-asking: interrupted a plan dialog (3 of 4 corrections, 75%)

| # | Session:idx | In flight | Correction (verbatim, trimmed) | Sub-type |
|---|---|---|---|---|
| 1 | `a68cadf2:75→76` | ExitPlanMode (Local LLM Stats plan) | "would it make sense to re-package this plan so it can be executed in a ralph loop?" | plan-too-narrow / reframe |
| 2 | `f1e54751:39→42` | ExitPlanMode (same plan) | "I would also like to add a voice option, so I can speak the query. This will be handy if I'm using on a phone or ipad … at the alley, and someone asks a question" | scope graft onto approved plan |
| 3 | `f1e54751:130→144` & `:140→144` | ExitPlanMode (re-presented twice) | "I will revisit this plan later, save to backlog" | abandonment / defer |

Sub-reading: identical to baseline Theme A. #1/#2 are "your plan is good but too
narrow" — David grafts scope (ralph-executability; a voice/phone mode for use at the
bowling alley) onto a plan Claude presented as complete. #3 is outright
deferral — Claude re-presented the plan, was cut off, re-presented it again, and
David finally parked it to backlog. Every one of these is Claude *pausing to get
plan sign-off* and David needing the dialog to be something other than the
yes/no it offered.

### Theme B — Wrong analysis / over-confidence, caught pre-action (1 of 4, 25%)

| # | Session:idx | In flight | Correction (verbatim, trimmed) | Sub-type |
|---|---|---|---|---|
| 4 | `d9e08746:817→818` | Read + mid-thinking (scope of a removal) | "wait you are saying remove fun stats from the LLM surface, that's just your tool not the page in the app right?" | scope-misread caught before action |

Sub-reading: the lone analysis correction, and it never reached code — David
interrupted *while Claude was still thinking* to confirm a scope boundary (the
removal targets the LLM tool surface, not the user-facing Fun Stats page). This is
the same beat as baseline Facet 4 #11 (`d9e08746:816`, the WilhelmSK "your tool not
the page" catch) — same session-id family, same instinct to verify a confident-
sounding scope claim before it turns into an edit. No "no…"-opened root-cause
reversal (baseline's canonical over-confidence tell) appears anywhere in bowling.

### Theme C — Terminal / not a correction (3 markers, excluded from tallies)

| # | Session:idx | In flight | What it was |
|---|---|---|---|
| 5 | `4583c448:12` | Read PLAN.md | ralph-loop session killed seconds after launch |
| 6 | `d8cdcf9a:7` | (none — ralph prompt queued) | ralph-loop session killed before any action |
| 7 | `f1e54751:162` | ExitPlanMode (parked-plan re-display) | plan re-shown after backlog decision; no reply |

These carry no behavioral-correction signal: #5/#6 are David stopping an
autonomous ralph iteration he didn't want to run (an *operational* interrupt of the
loop harness, unique to this delegated-build corpus and absent from the baseline),
and #7 is the tail of the already-parked plan in #3.

## (c) Theme tally (4 distinct corrections)

| Theme | Pairs | Share | Baseline share |
|---|--:|--:|--:|
| A — over-asking (interrupted plan dialog) | 3 | **75%** | 47% |
| B — wrong analysis / over-confidence (caught pre-action) | 1 | **25%** | 24% |
| D — stale state / wrong-env assumption | 0 | 0% | 18% |
| E — mid-flight redirect | 0 | 0% | 12% |
| C — terminal/operational (excluded; +3 markers) | — | — | (baseline: 3 terminal) |

## (d) Comparison vs baseline (Facet 4)

| Metric | Baseline (all-project transcripts) | Bowling (570 sessions, 1 product) |
|---|---|---|
| Interrupt markers | 20 | **8** |
| Distinct corrections | 17 | **4** |
| Terminal (no follow-up) | 3 | 3 |
| Over-asking share (Theme A) | 47% | **75%** |
| Over-confidence share (Theme B) | 24% | 25% |
| Stale-state (D) + redirect (E) | 30% | **0%** |
| Single most-interrupted action | `AskUserQuestion`/`ExitPlanMode` (8/17) | `ExitPlanMode`/plan (6/8) |

**Does the densest single build match the cross-project mix? On structure yes, on
proportion no — it amplifies the dominant pattern and erases the long tail.**

- **CONFIRMED & INTENSIFIED — over-asking is the #1 interrupt, even more so here.**
  Baseline: nearly half of interrupts land on Claude asking/planning. Bowling:
  three-quarters of corrections, and 75% of *all* markers, land on a plan. The
  one moment a delegated build still routes through David is the `ExitPlanMode`
  gate, so that is where 100% of the surviving interrupt pressure concentrates.
  The lever is the same baseline named — **fold likely scope in before presenting,
  and don't re-present an unchanged plan after a kill** (#3 was interrupted, then
  re-shown and interrupted *again* before David could park it).
- **CONFIRMED — over-confidence is caught at the same rate (~24–25%) and the same
  way:** a scope/analysis claim intercepted *before* it became an action
  (`d9e08746:818`), the twin of baseline's `:816`. The negation-opened root-cause
  reversal that dominated baseline's UI saga ("no it's still not styled…") does
  **not** occur — bowling's hard feature was an AI-query engine whose defects David
  reported precisely (B2), so corrections arrived as new directives, not as
  interrupts of a wrong fix.
- **DIVERGED — the long tail vanishes, and a new operational category appears.**
  Baseline's stale-state (18%) and mid-flight-redirect (12%) categories are **empty**
  in bowling: the autonomous loop wasn't proceeding on stale facts David needed to
  fix mid-stream, because he wasn't watching it proceed. In their place are **3
  terminal/operational interrupts** — two of them David killing a ralph-loop
  iteration at launch (#5/#6), an interrupt *of the harness*, not of Claude's
  reasoning, that the attended baseline never produced.

## (e) Observation for synthesis (feed B4)

**The interrupt corpus shrank, but its center of mass did not move — it
concentrated.** The richest behavioral signal baseline identified (interrupt →
correction adjacency) is *thinner* in the largest single build precisely because
delegation removed David from the execution loop: 570 sessions, 79 live messages,
8 interrupts. What remains is almost pure plan-gate friction. The actionable
reading for intense build sessions: the autonomous middle is low-risk to interrupt
(it barely is), so the entire human-attention budget should be spent making the
**plan-presentation moment** correct on the first try — present a plan already
widened with the obvious adjacent scope, surface the scope boundaries Claude is
*assuming* (the `d9e08746:818` catch), and never silently re-present an unchanged
plan that was just dismissed. Get the plan right and a week-long build runs with
near-zero corrective interrupts — which is exactly what bowling shows once the
Local LLM Stats plan was settled.

## Methodology note / limits

- **Small N.** 4 distinct corrections is too few for stable percentages; the shares
  above are reported alongside raw counts and should be read as direction, not
  precision. The *direction* (plan-gate dominance up, long tail gone) is robust
  because it is structural, not statistical.
- **Interrupts undercount in-loop friction.** A ralph-loop build records David's
  corrections mostly as *fresh directives in the next session* (the B2 diagnostic
  stream), not as interrupt markers — so this facet measures only the friction that
  occurred while he was synchronously watching, which in this corpus was almost
  entirely plan review. B2's 22 diagnostics are the larger correction channel for
  this build; B3's 8 interrupts are the synchronous tip of it.
