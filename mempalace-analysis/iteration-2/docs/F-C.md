# F-C — wing_docs: diagnostic timelines + precise/vague convergence

**Facet C:** for each multi-turn diagnostic session, build a timeline of precise
vs vague user messages and measure turns-to-resolution; evaluate the baseline
hypothesis *"vague language is a lagging signal of a wrong fix approach."*
Classification is by judgment (the keyword classifier was dropped per
`baseline/INSIGHTS.md` §3e). Source: `docs/_extract.py` Deliverable 3 and the
failure-vocabulary sweep `docs/_sweep.py`. Citations `(session8, tN / e#)` as in
F-A.

**Precise** = names a concrete artifact/observable/decision (an RGB triple, a
file path, *"merge it"*). **Vague** = affect/uncertainty without a new locus
(*"looks a little off"*, *"I'm not sure where it would be"*). Routine directives
(*"merge both PRs"*, *"save context"*) are precise-operational.

## Which sessions are diagnostic: 3 attended threads, 0 of the wilhelm kind

Unlike wing_contexts (zero diagnostic sessions), wing_docs **does** carry
multi-turn diagnostic threads — but **none is the wilhelm pattern** of Claude
iterating a code fix across retries with rising user vagueness. All three are a
*different kind* of convergence work, and in each the (rare) vague message is
**not** a lagging signal of a wrong Claude fix. The 11 delegated ralph sessions
have 1 user message each → no timeline, no diagnostics (F-A covers why).

The failure-vocabulary sweep (`_sweep.py`) across all 17 sessions returns only
**3** hits, all in attended sessions, none a vague-frustration spiral:
- `2172308c` e#43 — *"revert those two typos, keep the pivac edit"* (precise op)
- `2172308c` e#331 — *"no that's not it. I put the edited copies in the OneDrive
  Claude share…"* (precise correction — supplies the real locus)
- `e8078067` e#688 — *"show me failure path"* (precise instruction)

The wilhelm saga's convergence-failure vocabulary (*"still seeing serif"*,
*"something is funny… why is this getting messed up?"*) is **absent** here too.

## Thread 1 — `2172308c`: locate-the-source-of-truth (the `.wlyt` files)

The only thread containing an interrupt. David and Claude hunt for David's edited
layout files; the "convergence failure" is **missing information**, not a wrong
fix.

| t / e# | message (verbatim, short) | class |
|---|---|---|
| t9 / e#237 | "actually I use static thermostat. I think you may not have the latest file for the wlyts" | precise (names the gap) |
| t10 / e#262 | "where are you finding my 'live' layout if not in the repo?" | precise (probe) |
| t11 / e#269 | "can you look in the clone on the M2… Maybe I forgot to check them in" | precise (hypothesis) |
| t12 / e#316 | "I know I changed them somewhere… I'm not sure where it would be if it's not on this machine or m2." | **vague** (David's own location uncertainty) |
| t13 / e#326 | *[interrupt — Claude SSHing to the Pi]* | — |
| t14 / e#331 | "no that's not it. I put the edited copies in the OneDrive Claude share…" | precise (correction) |
| t16 / e#375 | "I think I never put the edits in the repo. Yes, copy the onedrive ones…" | precise (resolution) |

**Turns to resolution:** ~6 from the first probe (t10) to resolution (t16); the
vague message (t12) precedes the interrupt and the redirect. **But the vagueness
is David's, about his own file management** — not a lagging signal that Claude's
*approach* was wrong. Claude's only misstep (escalating to SSH-the-Pi) came
*after* the vague turn, triggered by it, not signalled by it. The tripwire reads
backwards here.

## Thread 2 — `2bb09e72`: iterative color-matching to Scott's site

Visual tuning, resolved by perceptual iteration — the textbook case where
vagueness is *expected and benign*.

| t / e# | message (verbatim, short) | class |
|---|---|---|
| t3 / e#235 | "the styling is different than for the docs. How hard would it be to make it look more similar?" | vague-ish (subjective goal) |
| t6 / e#369 | "why did you pick the teal? I don't see that being used on Scott's site." | precise (pushback, named color) |
| t8 / e#450 | "make the color of the main text background more like the body background on Scott's site" | precise-ish |
| t13 / e#592 | "title bar should be 10,28,29 rgb. body background 49,37,32 rgb. I'm using digital color meter" | **precise** (exact RGB) |
| t15 / e#692 | "they look a little off, let me resample as srgb" | **vague → instantly self-diagnosed** |
| t16 / e#698 | "title: 8,30,32; body: 56,42,35; brass: 171,149,103" | precise (resampled values) |

**Turns to resolution:** t13→t16, ~3 turns, clean. t15 (*"look a little off"*) is
the single closest thing to a wilhelm-style vague signal — but David **attributes
it to a concrete cause in the same breath** (sRGB colorspace) and re-supplies
precise values. Vagueness here is transient perceptual judgment, self-corrected,
not a lagging indicator of a wrong approach.

## Thread 3 — `e8078067`: iOS app integration test (doc-source picker)

The wilhelm-adjacent iOS/UI work. One real bug, resolved in one iteration.

| t / e# | message (verbatim, short) | class |
|---|---|---|
| t10 / e#379 | "I'd like to see how this works from the app, can you start it in the simulator" | precise |
| t12 / e#447 | "the connection didn't seem to wire in (maybe the simulator didn't restart) but I picked the discovered 68lookout connection. When I click settings/help, nothing happens" | **precise symptom + hypothesis** |
| t13 / e#515 | "ok it's all working now. when does the source picker screen appear…" | resolved ("all working now") |
| t14–t21 | UX-design discussion: should the picker reappear every time? | precise design Q&A |

**Turns to resolution:** the t12 bug (*"nothing happens"*) clears by t13 — **one
turn.** No vague spiral; David's symptom report was precise and came with a
self-supplied hypothesis (*"maybe the simulator didn't restart"*). The remainder
of the session is forward UX design, not debugging.

## The npm-publish saga (`083cf8fa` t9–t26): external-system, not diagnostic

Long and interactive, but **not a Claude-fix-convergence thread.** David
hand-drives npm's publish/2FA UI and reports external behavior: *"it's not giving
me an authenticator option"* (t16), *"I did not get a browser prompt"* (t19),
*"there is no classic tokens option"* (t20), then pastes a token (t21) and it
publishes. The failures are in **npm and app-store propagation**, not Claude's
work — so no precise→vague dynamic applies. Later, *"the link is showing but it's
raw html not a link"* (t29/e#649) is a precise bug report, fixed without spiral.

## Hypothesis evaluation (precise→vague as a lagging signal)

**Partially supported, but the tripwire mostly misfires in this wing.** The
baseline mechanism — vague language lagging a wrong *Claude fix* — requires a
Claude fix being iterated across retries. wing_docs has multi-turn threads, but:

- Thread 1's vagueness (t12) is **David's uncertainty about his own files**, and
  it *precedes* rather than lags Claude's misstep.
- Thread 2's vagueness (t15) is **transient perceptual judgment**, immediately
  self-diagnosed to a concrete cause and resolved in ~3 turns.
- Thread 3 and the npm saga have **no vague messages** — precise symptoms,
  one-turn resolutions, external-system reports.

So the precise→vague signal that fires cleanly in wilhelm (debug-by-retry of a
non-mechanical bug) is **not a reliable tripwire in docs**: the few vague
messages here are either the user's own missing-information state or normal
visual iteration, neither of which is a lagging indicator that Claude's approach
is wrong. This corroborates the wing_contexts F-C finding from the other
direction — the tripwire is **specific to convergence-failure-by-retry work** and
should not be framed as always-on. wing_docs is the case that shows *even when
multi-turn threads exist*, vagueness only carries the baseline meaning if the
thread is Claude iterating its own fix.

## Bottom line for the synthesis (Task 5)

1. **Baseline placement HOLDS on volume, REFINES on kind.** docs sits between
   wilhelm and contexts in diagnostic volume (3 threads vs wilhelm's saga vs
   contexts' zero), but its convergence work is **information-location +
   external-system + perceptual**, not wrong-code-approach. The fingerprint is
   distinct from wilhelm's.
2. **The precise→vague tripwire is the wrong instrument for docs.** Its few vague
   signals don't track a wrong Claude fix. Reinforces contexts §2: scope the
   tripwire to debug-by-retry work or it misleads.
3. **Delegated ralph mode (11 sessions) = no F-C signal at all** — single-prompt
   autonomous runs, no timeline. The convergence-failure construct only exists in
   attended, multi-turn work; bowling-style delegated builds are invisible to it.
