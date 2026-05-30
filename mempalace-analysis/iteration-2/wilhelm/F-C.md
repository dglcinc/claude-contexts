# F-C — wing_wilhelm: diagnostic timelines + precise/vague convergence

**Facet C:** for each multi-turn diagnostic session, build a timeline of
precise vs vague user messages and measure turns-to-resolution; evaluate the
baseline hypothesis *"vague language is a lagging signal of a wrong fix
approach."* Classification is by judgment (the keyword classifier was dropped
per `baseline/INSIGHTS.md` §3e). Citations `(session8, tN / e#)` as in F-A.
Source data: `wilhelm/_extract.py` Deliverable 3.

**Precise** = names a concrete artifact/observable/action (a screen, a value,
"styled", "commit and push"). **Vague** = affect/uncertainty without a new
locus ("something is funny", "what gives?", "still not right"). Routine
directives ("merge it", "run in the simulator") are precise-operational and not
counted as diagnostic friction.

## Which sessions are diagnostic

Of 10 sessions, most are **directed build / Q&A / admin**, not diagnosis:
`09909247` (plugin-admin Q&A), `1fb07798` (mostly commit/push + one micro-bug),
`495b618a` (gauge-doc authoring), `6c2b2575`/`d3573868`/`7f36198c` (short
feature/PR-tracking), `bd1c1597` (help-integration build), `74433fdf`
(analysis/setup). One micro-diagnostic thread lives inside `a79f4e6d`. The only
**sustained convergence-failure** is `6c0209bd`. Timelines below cover the two
that carry diagnostic signal.

---

## Session `6c0209bd` — the styling / "skip-to-content" saga (THE case)

79 user messages; 2 interrupts (both inside the failure window). Two intertwined
bug threads run through it.

### Thread A — "skip to content" page on `?` tap
| t / e# | message (verbatim, short) | class |
|---|---|---|
| t8 / e#159 | "i'm getting the skio to content thing when I click on a ?. It should just go directly." | precise (symptom + expected) |
| t9 / e#280 | "run in the simulator so I can test" | precise-op |
| t10 / e#310 | "I'm still getting the skip to content page, with github doc source selected." | precise (symptom persists, adds condition) |
| t11 / e#354 | "it looks like it's working now" | precise (resolved) |

**Thread A: reported t8 → resolved t11, ~3 turns.** Stayed precise throughout;
fast convergence. (It later *regresses* at t34 e#988 *"some of the pages are
still giving me the skip to content page. How do I fix this everywhere?"* — note
the shift to a vaguer "everywhere", folding into Thread B.)

### Thread B — serif / unstyled font (the convergence failure)
| t / e# | message (verbatim, short) | class |
|---|---|---|
| t17 / e#558 | "the font that shows in the simulator is a serif font. Can you change to sans serif" | precise (clear ask) |
| t27 / e#819 | "still seeing the serif font in the new plugin version, **what gives?**" | tipping → vague |
| t31 / e#887 | "still seeing serif" | precise-terse (failed fix #2) |
| t32 / e#926 | "still showing serif, **something else is going on.** Also… Settings… blank page" | vague |
| t40 / e#1132 | "**something is funny here. This should be very simple… Why is this getting messed up?**" | vague (peak frustration) |
| t41 / e#1134 | (near-duplicate of t40) | vague |
| t44–t46 / e#1181–1229 | "jumped correctly but still serif / unstyled font" … "jumps correctly but unstyled" | precise (isolating) |
| t48–t49 / e#1276–1285 | "no it's still not styled, on both my ipad and simulator…" | precise (post-interrupt re-assert) |
| t50 / e#1312 | "styled" | precise (resolved) |
| t51 / e#1345 | "that was the problem. page is styled now, and jumping seems to work" | precise (confirmed) |

**Thread B: reported t17 → resolved t51, ~34 turns**, spanning ≥5 failed fixes.
The two interrupts (F-A #1 e#1280, #2 e#1104) both land in t37–t49, the deepest
part of the failure.

### Hypothesis evaluation (precise→vague as a lagging signal)

**Thread B supports the baseline hypothesis, with a refinement.** The ask starts
precise (t17). The vague messages do **not** appear until *after* fixes have
already failed: the first wobble is t27 *"what gives?"* (after failed fix #1),
and the unambiguous vague peak is t40 *"something is funny here… Why is this
getting messed up?"* — emitted after **three+** failed attempts. So vagueness is
**lagging, not leading**: by the time David goes vague, the approach has been
wrong for many turns. Crucially, the vague turns did *not* themselves produce the
fix — resolution (t50–t51) came ~10 turns later, only after David **dropped back
to precise** ("jumps correctly but unstyled", t46) to isolate the variable, and
after re-asserting the bare symptom over Claude's HSTS theory (the e#1280
interrupt). The actionable read for Claude: t40-style vagueness is a tripwire
that the *current theory is spent* — the right response is to abandon the theory
and re-derive from the last precise observable, exactly `global.md`'s
"precise→vague = change-tack" lever. Here Claude kept theorizing (HSTS pin)
instead, which is why David had to interrupt.

---

## Session `a79f4e6d` — micro-diagnostic (gauge `?` placement)

| t / e# | message | class |
|---|---|---|
| t18 / e#565 | "Scott reported… Context sensitive help for Gauges is shown under Advanced Gauges" | precise (symptom) |
| t19 / e#587 | "no the problem… is not wrong anchor; the ? is appearing on the wrong screen…" | precise (corrects misdiagnosis) — F-A #3 |
| t23 / e#793 | "the ? is gone from advanced, but there is no ? on gauge options" | precise (partial) |
| t24 / e#842 | "it jumps correctly, but I think the anchor is wrong. It should jump to the gauge reference table." | precise (refine) |

**Reported t18 → working t24, ~6 turns, fully precise throughout.** No vague
phase. This is the contrast case: when David stays precise, convergence is quick
even across a misdiagnosis (t19) — the single flat "no…" corrected course in one
turn rather than spiraling. Supports the hypothesis by its absence: **no failed-
fix chain ⇒ no vague signal.**

---

## Bottom line for the synthesis (Task 5)

1. wilhelm produces **one** real convergence failure (`6c0209bd` Thread B, ~34
   turns) and several fast-converging precise threads. Convergence failure here
   correlates with a **non-mechanical bug** (the WebView styling/HSTS interaction
   spanning app + plugin + server) that no single precise instruction could
   pin down.
2. The **precise→vague tripwire holds** but is *lagging*: vagueness trails the
   first wrong-fix by several turns and does not itself resolve anything. Its
   value is as a signal to Claude to **switch tack**, which the transcript shows
   Claude failing to do (it kept theorizing → got interrupted).
3. wilhelm's friction is concentrated in **observe-fix-reverify loops**, not
   interrupts (see F-A "Why so few") — so for this work type, F-C is the more
   informative facet, and the durable lever is *treat a repeated "still X" +
   rising vagueness as "the theory is wrong, re-derive," not "tune the theory."*
