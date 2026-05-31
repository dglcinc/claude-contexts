# F-A — wing_wilhelm: interrupt corpus + theme grouping

**Facet A:** for every user interrupt, capture the in-flight assistant action,
the marker, and the user's correction; group by theme. Source: raw `.jsonl`
main-thread transcripts (10 sessions, 273 genuine user messages) enumerated in
`00-inventory.md`. Extractor: `wilhelm/_extract.py` (loader handles the
newline-delimited JSON these transcripts actually use; raw dump in the
gitignored `wilhelm/_extract_dump.txt`). Citations are `(session8, tN / e#)`
where `tN` = 0-based index in the session's ordered genuine-user messages and
`e#` = raw event index.

## Headline: wilhelm is NOT interrupt-heavy

The baseline tagged wilhelm the "highest-signal" wing for interrupts and
over-confident diagnoses (`00-inventory.md` flag #2 already cautioned this is
SignalK-plugin / server-side work, not pure iOS/UI). The raw transcripts settle
it: **only 5 interrupt markers exist across all 10 sessions / 273 user
messages — an interrupt rate of ~1.8 per 100 user messages.** The plan asked for
20–30 triples; wilhelm physically contains 5. That scarcity is itself the
finding (see "Why so few" below). Two marker variants appear:

- `[Request interrupted by user]` (3×) — user typed over an in-flight response.
- `[Request interrupted by user for tool use]` (2×) — user declined at a
  tool-permission prompt and redirected. Both are genuine interrupt+correction
  events and are included.

All 5 are listed below — the complete corpus, not a sample.

## The corpus (5 interrupts)

### 1. `6c0209bd` t48→t49 / e#1280 — assistant narrating a causal theory
- **In-flight (assistant text, no tool):** *"Still broken with HSTS off — so
  either HSTS wasn't the (whole) cause, or the in-app browser is still holding
  the **in-memory** HSTS pin from before (relaunching the app doesn't kill the
  separate Safari…"* — a multi-branch hypothesis stated as it reasons.
- **Marker:** `[Request interrupted by user]`
- **Correction:** *"no it's still not styled, on both my ipad and simulator. On
  my ipad I'm now getting skip to content and no jump"* — user cuts off the
  theorizing and re-asserts the bare observable.

### 2. `6c0209bd` t37→t38 / e#1104 — speculative investigation tangent
- **In-flight (tool):** `Bash` — *"=== images on the user-guide page +
  lazy-loading? ==="* (a speculative probe into image lazy-loading while
  chasing the styling/skip-to-content bug).
- **Marker:** `[Request interrupted by user]`
- **Correction:** *"where is AIS"* — user yanks Claude off the speculative
  thread and hands it a concrete page to reproduce against.

### 3. `a79f4e6d` t18→t19 / e#585 — acting on a misdiagnosis
- **In-flight (tool):** `Bash` in `signalk-wilhelmsk-docs` — *"exact heading
  matches for 'option…'"* (Claude assumed the bug was a wrong doc **anchor**).
- **Marker:** `[Request interrupted by user]`
- **Correction:** *"no the problem scott is reporting is not wrong anchor; the ?
  is appearing on the wrong **screen**. the ? that links to gauges should link
  to the gauge options page…"* — wrong diagnosis; user supplies the real one.

### 4. `a79f4e6d` t7→t9 / e#228 — skipped world-state check
- **In-flight:** tool-use during the instruction *"dig into the restEndpoint
  break"* (t7).
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction:** *"check and make sure you have the latest version of
  WilhelmSKLibrary"* — user stops the deep dig to verify world-state first
  (the break was an upstream change Scott had already fixed; see t10 *"Scott has
  done the same fix. Do a pull…"*).

### 5. `bd1c1597` t9→t11 / e#177 — re-deriving instead of recalling prior work
- **In-flight:** tool-use during *"let's work on the context-sensitive help
  integration for wilhelmsk"* (t9).
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction:** *"in a prior session, you had proposed a way to do the
  context-sensitive integration and proposed which pages to wire it to. Are you
  finding that?"* — user stops a fresh start and points at existing prior-session
  design.

## Theme grouping

| Theme (baseline lever it maps to) | Interrupts | Count |
|---|---|---|
| **Too-confident assertion** — narrating a causal theory as fact (lever: "state expected observable, don't narrate theory") | #1 | 1 |
| **Wrong analysis / acting on a misdiagnosis** (lever: re-derive the symptom from scratch on a flat "no…") | #2, #3 | 2 |
| **Skipped readable sources / world-state** before acting (levers: "exhaust readable sources"; "verify world-state before the harder path") | #4, #5 | 2 |

No interrupts fell in the baseline's "wrong file" or "wrong tool choice"
buckets. Every wilhelm interrupt is about **direction of effort** — Claude
theorizing, mis-diagnosing, or diving in without first reading state/history —
which is exactly the iteration-1 thesis that the costly friction is
interaction/approach mismatch, not mechanical error. Notably 3 of 5 (#3, #4, #5)
open with a flat **"no…"** or a redirect, the hard-stop signal `global.md`
already calls out.

## Why so few interrupts (the real story of wilhelm)

The wilhelm loop is **simulator-mediated**, not interrupt-mediated. The dominant
correction mechanism is not interrupting an in-flight action — it is David
running the app and reporting what he sees, then Claude fixing and David
re-verifying. Evidence: 9 of 10 sessions invoke the `run`/simulator skill, and
the `6c0209bd` styling thread alone has ≥8 "run it in the simulator / still
seeing X" observe-fix cycles (t9, t26, t30, t42, t47…). Because David watches
each build land, he rarely needs to interrupt — he just reports the next
observation. So wilhelm's friction shows up as **long observe-fix-reverify
chains** (the F-C convergence-failure pattern), not as a pile of interrupts.
This is the inverse of the delegated bowling/ralph mode, where the plan gate is
the only synchronous touchpoint and corrections land as interrupts.

## One caveat on counts

`6c0209bd` and `a79f4e6d` each carry both marker variants; `bd1c1597` carries
only the "for tool use" variant. Had extraction keyed solely on the exact
`[Request interrupted by user]` string (as the bowling pass did) it would have
reported 3 and missed #4 and #5. Both variants are real corrections, so all 5
are kept; the distinction is noted for the synthesis (Task 5) when comparing
wilhelm's count against bowling's.
