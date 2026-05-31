# F-A — wing_docs: interrupt corpus + theme grouping

**Facet A:** for every user interrupt, capture the in-flight assistant action,
the marker, and the user's correction; group by theme. Source: raw `.jsonl`
main-thread transcripts (17 sessions enumerated in `00-inventory.md` across two
repos — `signalk-wilhelmsk-docs` = **attended** npm-publish-prep, 6 sessions;
`wilhelm-docs-ralph` = **delegated** ralph build, 11 sessions). Extractor:
`docs/_extract.py` (mode-tagged copy of the contexts extractor) plus
`docs/_probe.py`, which finds *all* `interrupted by user` variants and rejects
embedded (tool_use/tool_result/attachment) artifacts. Raw dumps in the
gitignored `docs/_{extract,probe}_dump.txt`. Citations `(session8, tN / e#)`
where `tN` = 0-based index in the session's ordered genuine-user messages, `e#`
= raw event index.

## Headline: one genuine interrupt in the whole wing — and it is *not* over-asking

The exact-string extractor finds **0** interrupts. The two-variant probe finds
exactly **1** genuine standalone user-turn interrupt across all 17 sessions —
`2172308c` t13/e#326, the `[Request interrupted by user for tool use]`
(tool-permission-decline) variant. Every other `interrupted by user` string in
the corpus is embedded in a tool block, not a user action.

So the over-asking / over-planning interrupt the baseline named as the costliest
friction **does not appear in wing_docs at all.** This is not because Claude
never asked: across the attended sessions `AskUserQuestion` fired **8 times**
(5× in `2bb09e72`, 3× in `e8078067`) and **`ExitPlanMode` 0 times** — yet *none*
produced an interrupt. David answered every question and never killed a prompt.
The contrast with the baseline matters: in wing_docs, asking was **cheap**, not
costly, because the questions landed on genuine David-preferences (which brass
RGB to match Scott's site; whether the doc-source picker should reappear every
time) — exactly the case `global.md` says asking *is* warranted. The lone
interrupt is a different failure: a **wrong-location file search**, not an ask.

## The corpus (1 interrupt)

### 1. `2172308c` t13 / e#326 — wrong location: reached for SSH-to-Pi when files were in OneDrive
- **Instruction (t12 / e#316):** *"I know I changed them somewhere, because
  that's what I use on my devices. I'm not sure where it would be if it's not on
  this machine or m2."* — David is himself uncertain where his edited `.wlyt`
  layout files live.
- **In-flight (assistant, tool e#322):** `Bash` — `echo "=== Pi (10.0.0.82)
  reachability + pivac wlyt ===" ssh …` — Claude jumped to SSH-probing the Pi
  for the missing layout files.
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction (t14 / e#331):** *"no that's not it. I put the edited copies in
  the OneDrive Claude share, then copied them to my devices. So first look in the
  Claude directory, but also read the claude files in the claude-contexts dir…"*
  — David vetoes the speculative remote-host hunt and points at the local
  OneDrive path the files were actually in.

This is the **same family** as wing_contexts interrupts #2/#3 (*"rsync directly,
you have access"*, *"nas was powered off"*): a tool-permission decline that
redirects Claude from a **speculative harder path** (SSH the Pi) to a **known
simpler locus** (a local share). It maps directly onto the `global.md` lever
*"verify world-state — existing access, current versions — before assuming the
harder path."* Nuance worth carrying to synthesis: David's own instruction (t12)
was vague about location, so this is a **collaborative search where neither party
knew the answer at t12** — not a clean Claude-error. Claude's avoidable move was
escalating to a remote host before exhausting local/OneDrive sources.

## Theme grouping

| Theme (baseline lever it maps to) | Interrupts | Count |
|---|---|---|
| **Wrong location / verify world-state before the harder path** (lever: "verify existing access / current versions before assuming the harder path"; "exhaust readable sources before…") | #1 | 1 |
| Over-asking (`AskUserQuestion`/`ExitPlanMode`) | — | **0** (8 asks fired, 0 interrupted) |
| Wrong file / wrong scope / wrong tool / too-confident assertion | — | 0 |

No interrupt fell in the wrong-file, wrong-scope, wrong-tool, or
too-confident-assertion buckets, and there are **zero** mid-text type-over
(`[Request interrupted by user]`) interrupts. As in wing_contexts, the single
real correction is a *tool-action veto a beat before it ran*, not a cut-off of
Claude's reasoning.

## The PLAN's question: over-asking pattern, or a publishing-specific failure mode?

Task 4 asked whether docs shows (a) the over-asking-on-`AskUserQuestion`/
`ExitPlanMode` pattern, or (b) a publishing-workflow failure like *"wrong version
published"* / *"wrong file built"*. **Neither.**

- **(a) does not hold:** over-asking generated 0 friction here (8 asks, 0
  interrupts; 0 `ExitPlanMode`). When the work is subjective/visual (color
  matching) or product-UX (picker behavior), asking is appropriate and David
  answers without complaint.
- **(b) did not occur:** there is no *"wrong version published"* or *"wrong file
  built"* event. The npm-publish saga (`083cf8fa` t9–t26) ran clean from Claude's
  side; what friction existed there was **external-system operation**, not a
  Claude mistake — David hand-driving npm's 2FA/publish UI and reporting back
  (*"it's not giving me an authenticator option, it's only letting me set up
  passkeys"* t16/e#378; *"I did not get a browser prompt"* t19/e#422; *"there is
  no classic tokens option"* t20/e#438). Claude advised; npm misbehaved. These
  are not interrupts and not Claude failures.

So the publishing nature of wing_docs surfaces a **third texture** the baseline
didn't predict: **hands-on collaborative operation of an external system** (npm
registry, SignalK app-store propagation) where David is the operator at the
keyboard and Claude is the advisor. That texture produces lots of precise
status-report messages but **no interrupts and no diagnostic spiral**, because
the failures live in npm/the app store, not in Claude's work.

## The delegated half: 11 ralph sessions, 0 interrupts by construction

The 11 `wilhelm-docs-ralph` sessions each contain **exactly one** genuine user
message — the ralph driver prompt (*"Read PLAN.md. Find the first unchecked task.
Do it…"*) — and **zero** interrupts. This is structural, not behavioral: a
delegated autonomous build has **no synchronous human in the loop**, so the
interrupt is not an available correction tool. Unlike the attended sessions
(which at least have a plan/ask touchpoint), this ralph prompt has no
plan-approval gate at all — corrections, if any, would arrive only as the *next*
session's opening directive. The 11 sessions are pure execution. (This is the
same operating mode as the `bowling/` pass; kept separable per inventory flag 4
for the Task-5 "bowling delta" comparison.)

## Bottom line for the synthesis (Task 5)

1. **wing_docs sits between wilhelm and contexts on interrupt *volume* (1, vs
   wilhelm's several and contexts' 3) but its failure *mode* is distinct:** the
   one interrupt is wrong-location/world-state, identical in family to contexts —
   not the diagnostic mid-theory interrupts of wilhelm.
2. **The over-asking-interrupt is absent here despite 8 `AskUserQuestion` calls.**
   Asking is cheap when it targets genuine preference (color, UX). This refines
   the baseline's "over-asking is costliest": the cost is specific to asking when
   the user *already had a direction* (the contexts #1 case), not to asking per se.
3. **Delegated ralph mode emits zero F-A signal by construction** — a clean
   confirmation of the `global.md` delegated-mode note (corrections arrive as the
   next session's opening directive; here there isn't even a plan gate).
