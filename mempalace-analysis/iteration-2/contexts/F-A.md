# F-A — wing_contexts: interrupt corpus + theme grouping

**Facet A:** for every user interrupt, capture the in-flight assistant action,
the marker, and the user's correction; group by theme. Source: raw `.jsonl`
main-thread transcripts (6 sessions enumerated in `00-inventory.md`, the genuine
`-Users-utilityserver-github-claude-contexts` dir — the three
`mempalace-analysis*` meta dirs are excluded). Extractor: `contexts/_extract.py`
(copy of the wilhelm extractor) plus `contexts/_probe.py`, which finds *all*
interrupt-marker variants and classifies each as a genuine standalone user turn
vs. a tool_use/tool_result-embedded artifact. Raw dumps in the gitignored
`contexts/_{extract,probe}_dump.txt`. Citations `(session8, tN / e#)` where `tN`
= 0-based index in the session's ordered genuine-user messages, `e#` = raw event
index.

## Headline: baseline's "zero" is directionally right, literally wrong — 3 exist

Baseline §1 said `wing_contexts` had **zero** genuine interrupts (drawer-mined).
The raw transcripts show **3** genuine standalone user-turn interrupts — all in a
single session (`6d867d45`, the mempalace-deployment build) and all the
`[Request interrupted by user for tool use]` (tool-permission-decline) variant.
Across all 6 sessions / ~99 genuine user messages that is an interrupt rate of
**~3 per 100** — about the same low rate as wilhelm (~1.8/100), and far below a
diagnostic wing's. So the baseline "zero" is a **magnitude artifact of drawer
mining** (the exact-string `[Request interrupted by user]` extractor finds 0
here too — see "Counting caveat"), but its *direction* holds: infra work is
near-zero-interrupt. The three that exist are forward redirects, not failed-fix
corrections, and every one maps cleanly onto an existing `global.md` lever.

Every other "interrupted by user" hit in the corpus is **embedded** in a
tool_use / tool_result / attachment block — overwhelmingly in today's
`set-context` session `91b095fe` (7 hits), which *read the wilhelm `F-A.md`* that
literally quotes the markers. None of those are user actions. Confirmed by
`_probe.py`: only `6d867d45` produces genuine standalone user-turn markers.

All 3 are listed below — the complete corpus.

## The corpus (3 interrupts, all in `6d867d45`)

### 1. `6d867d45` t6 / e#230 — over-asking via `AskUserQuestion`
- **Instruction (t5 / e#121):** *"ok we'll skip ipad. you have root ssh access
  for both the rpi and the m2. If you don't know how to do that review your
  global context inluding claude-contexts project. **Ask if you still have
  questions.**"*
- **In-flight (assistant, tool-only e#228):** `AskUserQuestion` — Claude finished
  a Phases-1–3 status table (e#227) and then popped a multiple-choice question.
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction (t7 / e#231):** *"do I have to enable MCP server to use it with
  claude?"* — David had already **queued** this exact question (e#224, a
  queue-operation) *before* the `AskUserQuestion` fired; he killed the prompt to
  ask it directly. Claude paused to ask when the user already had a direction.

### 2. `6d867d45` t13 / e#498 — probing instead of using known access
- **Instruction (t12 / e#482):** *"set up the backup, to the nas"*
- **In-flight (assistant, tool e#493):** `Bash` — `ssh … pi@10.0.0.82 'echo "===
  Pi NFS mount …'` (investigating a Pi-mediated NFS path to the NAS).
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction (t14 / e#500):** *"you should have root or nasadmin passwordless
  access to the NAS from this machine so you should be able to **rsync
  directly** for phase 5, please review and confirm"* — user redirects from the
  speculative Pi-NFS route to the simpler direct path he knows already exists.

### 3. `6d867d45` t15 / e#510 — re-testing against stale world-state
- **Instruction (t14 / e#500):** the rsync-directly redirect above.
- **In-flight (assistant, tool e#508):** `Bash` — `echo "=== sandbox DISABLED —
  retest NAS reachability ===" … for p in 22 5000 5001 …` (port-scanning the NAS
  after a failed reach).
- **Marker:** `[Request interrupted by user for tool use]`
- **Correction (t16 / e#513):** *"ok problem was, nas was powered off. Try
  again."* — the reachability failure was **external world-state** (NAS off),
  not a Claude error; user interrupts the retry-loop to supply the real cause.

## Theme grouping

| Theme (baseline lever it maps to) | Interrupts | Count |
|---|---|---|
| **Over-asking** — paused to `AskUserQuestion` when the user already had a direction (lever: "exhaust readable sources before asking; only ask on genuine preference") | #1 | 1 |
| **Verify world-state / use existing access** before the harder path (lever: "verify dependency currency, existing access, current versions before assuming the harder path") | #2, #3 | 2 |

No interrupt fell in the "wrong file", "wrong scope", "wrong tool choice", or
"too-confident assertion / wrong analysis" buckets. There are **zero** mid-text
type-over interrupts — none of the 3 is the `[Request interrupted by user]`
(typed-over an in-flight *response*) variant; all 3 are tool-permission declines.
That is itself diagnostic: in infra work David isn't cutting off Claude's
*reasoning*, he's vetoing a *tool action* a beat before it runs — a tighter,
cheaper correction than wilhelm's mid-theory interrupts.

Strikingly, the single `AskUserQuestion` interrupt (#1) is the over-asking
pattern the baseline named as the **costliest friction** ("~half of interrupts
landed on Claude pausing to ask or present a plan"). It appears here exactly
once, against an instruction (t5) that *pre-emptively told Claude "Ask if you
still have questions"* — David had already lowered the ask-bar, and Claude still
asked the one thing he'd already answered in the queue.

## Why so few interrupts (the real story of wing_contexts)

wing_contexts is **directed decision-elicitation**, not diagnosis or build-debug.
Five of the six sessions are pure Q&A / config / admin with **zero** interrupts:
`88bff61e` (memory-systems consolidation Q&A), `96bbb1db` (KG-seeding + memory
remodel), `7e3dce98` / `91b095fe` (set-context → kick off & watch a ralph run),
`0c8a0493` (set-context → merge PR → save-context). The dominant correction
mechanism is not the interrupt — it is **the next directive**. David's messages
read as a decision stream: *"what do you recommend"* → *"remodel"* → *"go with
#1"* → *"go ahead with the narrow scope"* (96bbb1db t6–t9), or *"Let's skip
cloudflare"* → *"let's do nginx"* → *"I don't want to port forward port 22"*
(6d867d45 t3–t4). He steers each step forward; he rarely has to reach back and
interrupt because he is approving/redirecting at every turn anyway. So infra
friction surfaces as **course-corrections inside the directive stream**, not as
marker-bearing interrupts. The one session that *does* carry interrupts
(`6d867d45`) is the only one with long autonomous tool-runs (SSH/backup setup) —
i.e. the only stretch where Claude acts far enough ahead of the next directive
for an interrupt to be the available correction tool.

## Counting caveat

The exact-string extractor (`_extract.py`, keyed on `== '[Request interrupted by
user]'`, the bowling/wilhelm method) reports **0** interrupts for wing_contexts —
the same false-zero the drawer-based baseline produced. All 3 real interrupts are
the `for tool use` variant, invisible to that key. `_probe.py` was written to
catch both variants *and* to reject embedded (tool_result/tool_use/attachment)
occurrences; it is the authoritative count here. The lesson for Task 5: any
cross-wing interrupt tally that keyed on the bare marker (baseline included)
systematically **undercounts tool-permission declines**, which are the dominant
interrupt form in directed infra work.
