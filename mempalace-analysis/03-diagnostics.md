# Facet 3 — Vague-vs-precise diagnostic ratio

**Sources & method.** Two corpora, per the plan:

1. **Diary `recent:` field** (`room=diary`, all wings) — 80 checkpoint drawers,
   parsed into pipe-delimited user messages and deduped (longest-prefix wins, as
   in Facet 1) → **223 unique user messages**. This is the only clean
   user-message-only source in the palace.
2. **`room=problems` sample** — the 200 lowest-sorted-by-`embedding_id` drawers
   of the 838 in that room. **This yielded almost nothing usable** (see caveat).

Each message was first routed through a broad **diagnostic detector** (does it
report a symptom, unexpected behavior, missing element, or a correction of the
assistant's output?), dropping pure directives ("merge it"), info-questions
("what is pr 99"), acknowledgments, and tool-output noise (`<bash-input>`,
`<task-notification>`). The surviving diagnostics were then **hand-classified**
VAGUE vs PRECISE — the vague/precise boundary is a judgment the plan's regex
patterns cannot make reliably (see §e).

> **Caveat — `room=problems` is not a user-message source.** All 838 problems
> drawers are `extract_mode=exchange` / `ingest_mode=convos`: arbitrary content
> windows of mined transcripts, dominated by skill-file text, code, and
> assistant prose with no isolable user turn. Scanning the 200-drawer sample for
> `>`-quoted user-turn prose surfaced only **14 lines**, and exactly **1** passed
> the diagnostic detector — and that one ("Can you start / add to an analysis
> file…", `drawer_..._3e793111126ac363e65c5850`) is actually a long *directive*,
> not a diagnostic. **Net usable diagnostics from the problems sample: 0.** The
> ratio below is therefore computed on the diary corpus alone. This is the same
> structural limit Facet 2 hit: mined drawers are not turn-segmented, so
> user-behavior facets must lean on the diary `recent:` field.

**Classification criteria (stated, since they drive the ratio):**
- **PRECISE** = the message gives a concrete locator the assistant can act on
  without guessing: a named screen / file / UI element / setting / version /
  root cause, exact quoted text, a file\:line or `#PR` defect reference, or a
  specific named symptom ("serif font", "raw html not a link", "skip to content
  page").
- **VAGUE** = the symptom is carried only by hedge or affect ("seems", "weird",
  "something is", "screwed up", "off", "I think … may") with **no** concrete
  locator.

## (a) Overall vague/precise ratio

Diary corpus: 223 user messages → **32 genuine diagnostics** (the other 191 are
directives, info-questions, acks, status confirmations, or feature requests).

| Class | Count | % of diagnostics |
|-------|------:|-----:|
| PRECISE | 22 | 68.8% |
| VAGUE | 10 | 31.2% |
| **Total diagnostics** | **32** | 100% |

**Vague : precise = 10 : 22 = 0.45.** David's diagnostics skew **precise** —
roughly **2.2 precise for every vague** one. Diagnostics are also a *minority*
register overall: only 32 / 223 ≈ 14% of diary user messages are problem reports
at all; the rest are commands and context.

## (b) Ratio per wing

| Wing | Vague | Precise | Total diag. | Vague:Precise | %precise |
|------|------:|--------:|------:|:---:|---:|
| wing_wilhelm | 7 | 17 | 24 | 0.41 | 70.8% |
| wing_docs | 3 | 5 | 8 | 0.60 | 62.5% |
| wing_contexts | 0 | 0 | 0 | — | — |
| wing_pivac | 0 | 0 | 0 | — | — |
| wing_code | 0 | 0 | 0 | — | — |

Diagnostics live **almost entirely in the two product wings** (wilhelm = iOS app,
docs = the SignalK doc plugin / npm-publish work). The infra/memory wings
(`wing_contexts`, `wing_pivac`, `wing_code`) produced **zero** diagnostic
messages in the diary corpus — their user messages are directives and
info-questions ("remodel", "add the rule", "how do I add kg triples"),
consistent with Facet 1 (contexts is the terse, command-driven exception) and
Facet 2 (those wings carry ~no genuine interrupts). **Infra work doesn't get
diagnosed; it gets directed.**

Both product wings skew precise; docs is slightly vaguer (0.60 vs 0.41), driven
by visual-polish ("a little off") and file-state-uncertainty ("I think I never
put the edits in the repo") reports.

## (c) Examples (verbatim, stored text truncated ~80 chars by the mining hook)

### 10 VAGUE (all of them)

| # | Wing | Message | Why vague | Drawer |
|--|--|--|--|--|
| 1 | wilhelm | "there still seem to be a number of screens that could have help and don't, like…" | "seem"; screen set unspecified | `diary_wing_wilhelm_20260525_114649469101_2b440ddddf06` |
| 2 | wilhelm | "now there's a weird thing where it shows a panel and I have to click proceed to…" | "weird thing" | `diary_wing_wilhelm_20260525_135023331669_de687949d4ee` |
| 3 | wilhelm | "ok that's not super obvious - you should link directly to this readme in the top…" | "not super obvious" UX hedge | `diary_wing_wilhelm_20260525_141814745374_3a3c9bb519a4` |
| 4 | wilhelm | "still showing serif, something else is going on. Also, in the menu, if I select…" | "something else is going on" | `diary_wing_wilhelm_20260525_154107842443_92e1b9e6d523` |
| 5 | wilhelm | "the doc navigation in the live app now seems completely screwed up. It's always…" | "seems completely screwed up" | `diary_wing_wilhelm_20260525_155214331580_962c6c68b099` |
| 6 | wilhelm | "something is funny here. This should be very simple - when you click on the ? yo…" | "something is funny" | `diary_wing_wilhelm_20260525_161256379756_d06694e919da` |
| 7 | wilhelm | "so it's weird, not all the plugins appear to allow you to disable them, and none…" | "weird", "appear to" | `diary_wing_wilhelm_20260525_181504101271_63691fda1408` |
| 8 | docs | "they look a little off, let me resample as srgb" | "a little off" | `diary_wing_docs_20260526_185003512507_25e37a4a9d83` |
| 9 | docs | "actually I use static thermostat. I think you may not have the latest file for t…" | "I think you may not" — wrong-file hunch | `diary_wing_docs_20260526_214652264231_fe93856267b2` |
| 10 | docs | "you know, I think I never put the edits in the repo. Yes, copy the onedrive ones…" | "I think I never" — uncertain self-diagnosis | `diary_wing_docs_20260526_220050305825_6ea2d1542903` |

### 10 PRECISE (representative of 22)

| # | Wing | Message | Locator | Drawer |
|--|--|--|--|--|
| 1 | wilhelm | "why is there no help on the layouts page?" | named screen | `diary_wing_wilhelm_20260525_110837461972_fecdca157d09` |
| 2 | docs | "it's not giving me an authenticator ooption/qr code, it's only letting me set up…" | named missing element | `diary_wing_docs_20260525_123726819193_bd97f5450cfa` |
| 3 | docs | "there is no classic tokens option" | named missing UI option | `diary_wing_docs_20260525_130211165236_e87bbefffeac` |
| 4 | docs | "the link is showing but it's raw html not a link" | exact symptom | `diary_wing_docs_20260525_131200463713_a681808beca3` |
| 5 | wilhelm | "i'm getting the skio to content thing when I click on a ?. It should just go dir…" | named symptom + trigger | `diary_wing_wilhelm_20260525_144001191825_3417fdfbc988` |
| 6 | wilhelm | "I'm still getting the skip to content page, with github doc source selected." | named page + config state | `diary_wing_wilhelm_20260525_144001191825_3417fdfbc988` |
| 7 | wilhelm | "one more thing for the plugin - the font that shows in the simulator is a serif…" | named symptom + location | `diary_wing_wilhelm_20260525_145705612797_0bfddde75d30` |
| 8 | wilhelm | "the ? is gone from advanced, but there is no ? on gauge options" | two named screens + element | `diary_wing_wilhelm_20260529_203154906549_12867c5f8cd2` |
| 9 | wilhelm | "The bootstrap.sh is not tier 1; it's not really even needed. Per your note on th…" | named file, corrects a claim | `diary_wing_wilhelm_20260529_203908011292_27595a2967b9` |
| 10 | wilhelm | "for the json-parse nil in the not tiered table, when does that get fixed?" | named defect + table | `diary_wing_wilhelm_20260529_205138020219_b1d46df0fbdc` |

## (d) Observation — which projects favor which mode

The corpus splits cleanly by work type:

- **iOS/UI (`wing_wilhelm`, 24 diagnostics, 71% precise).** David diagnoses UI
  bugs *precisely* because he can see and name the broken artifact — "the font in
  the simulator is a serif", "the ? is gone from advanced", "skip to content page
  with github doc source selected". Vagueness here is the *escalation* register:
  it appears only after repeated fixes fail. The serif-font saga is the textbook
  case — precise for four turns ("font … is serif" → "still seeing serif" →
  "still serif / unstyled") then collapsing to vague ("**something else is going
  on**", "seems **completely screwed up**") in drawers
  `…154107842443…` / `…155214331580…`. Those are the same interrupt-dense
  sessions Facet 2 flagged (`6c0209bd`, `a79f4e6d`) — vague escalation and
  interrupts co-locate at the moments fixes aren't landing.
- **Docs / npm-publish (`wing_docs`, 8 diagnostics, 63% precise).** Precise about
  *missing UI elements* during the painful npm-publish flow ("no classic tokens
  option", "didn't get a browser prompt"), but vaguer about visual polish ("a
  little off") and his own file-state ("I think I never put the edits in the
  repo") — the two areas where he himself is uncertain.
- **Infra / memory (`wing_contexts` / `wing_pivac` / `wing_code`, 0 diagnostics).**
  These wings generate directives, not symptom reports. There is nothing visual
  to point at, so work proceeds as commands ("add the rule", "remodel").

## (e) Why the plan's literal vague-patterns are an unreliable classifier

Cross-checking against the plan's literal VAGUE patterns ("something is", "I
think", "doesn't look", "still not", "not working", "feels off", "weird"):

- Those patterns match only **9** of the 32 diagnostics — and the surface match
  disagrees with the judgment call **half the time**.
- **Over-counts (vague register, precise content) — 4 messages** match a "vague"
  pattern yet carry a precise locator, so they were classed PRECISE:
  - "scott dicvered an issue where his doc link was **not working** because he
    uses **SSL**" (`…150857156439…`) — root cause named.
  - "no it's **still not** styled, on both my ipad and simulator…"
    (`…162737329497…`) — named symptom + reproduction on two devices.
  - "it jumps correctly, but **I think** the anchor is wrong. It should jump to
    the gauge…" (`…203154906549…`) — names the component and the expected target.
  - "The item that you labeled as an observation \"Icloud sync is partial\". **I
    think** th…" (`…205138020219…`) — quotes the exact claim being corrected.
- **Under-counts — 5 truly-vague messages** match **no** listed pattern, because
  they use affect words outside the list: "seem", "screwed up", "a little off",
  "not super obvious", "something else is going on" (rows 1, 3, 4, 5, 8 of the
  vague table).

**Takeaway for Facet 5:** David's hedges ("I think", "still not") are mostly
*politeness wrappers around precise reports*, not genuine vagueness — so a
keyword classifier overstates vagueness in one direction and misses it in
another. True blind vagueness is rare (≈10/223 ≈ 4.5% of all diary user
messages) and clusters tightly: UI-styling work that has failed to converge
across several retries. The actionable lever isn't "ask David to be more
precise" (he usually is) but "watch for the *escalation* from precise to vague
as the signal that the current fix approach is wrong and a different tack is
needed."
