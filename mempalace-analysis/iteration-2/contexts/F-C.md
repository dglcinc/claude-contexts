# F-C — wing_contexts: diagnostic timelines + precise/vague convergence

**Facet C:** for each multi-turn diagnostic session, build a timeline of
precise vs vague user messages and measure turns-to-resolution; evaluate the
baseline hypothesis *"vague language is a lagging signal of a wrong fix
approach."* Classification is by judgment (the keyword classifier was dropped per
`baseline/INSIGHTS.md` §3e). Source: `contexts/_extract.py` Deliverable 3 and the
failure-vocabulary sweep `contexts/_sweep.py`. Citations `(session8, tN / e#)` as
in F-A.

**Precise** = names a concrete artifact/observable/decision ("remodel", "go with
#1", "rsync directly", "don't port forward 22"). **Vague** = affect/uncertainty
without a new locus ("something is funny", "what gives?", "still not right").
Routine directives ("merge it", "save context") are precise-operational.

## Which sessions are diagnostic: none

Of the 6 sessions, **zero** are diagnostic / convergence-failure. They split into
two non-diagnostic shapes:

- **Decision-elicitation builds** (`6d867d45` mempalace deploy; `96bbb1db` KG +
  memory remodel; `88bff61e` memory-systems consolidation): David drives a
  forward decision stream — *"what do you recommend"* → *"remodel"* → *"go with
  #1"* (96bbb1db t6–t9); *"Let's skip cloudflare"* → *"let's do nginx"* → *"I
  don't want to port forward port 22"* (6d867d45 t3–t4). Every message advances
  the build; none reports a failed fix.
- **Admin / orchestration** (`0c8a0493`, `7e3dce98`, `91b095fe`): set-context,
  kick off and *watch* a ralph run, merge a PR, save-context. `91b095fe`'s 25
  "user messages" are mostly `<task-notification>` monitor events (t4, t7,
  t9–t17) — automated, not diagnostic.

## The failure-vocabulary sweep (the dispositive evidence)

`_sweep.py` scans every genuine user message across all 6 sessions for
failure/frustration markers (`still`, `not work`, `doesn't`, `broken`, `wrong`,
`fail`, `error`, `what gives`, `something's funny`, `not right`, `stuck`, `no
it`, `revert`…). **Exactly one** non-command message matches, and it is a false
positive:

> `6d867d45` t5 / e#121 — *"…If you **don't** know how to do that review your
> global context… **As**k if you still have questions."*

That is an *instruction* (telling Claude to read context and ask), not a
report of a broken fix. There is **no** *"still broken"*, *"what gives"*, *"not
right"*, or any vague-frustration message anywhere in wing_contexts. The wilhelm
saga's entire vocabulary of convergence failure — *"still seeing serif"*,
*"something is funny here… Why is this getting messed up?"* (wilhelm F-C
`6c0209bd` t27–t40) — is **completely absent** here.

## The closest thing to friction: 3 one-turn redirects

The only corrections in the wing are the 3 interrupts from F-A, all in
`6d867d45`. Each is a **forward redirect resolved in a single turn**, not a
failed-fix chain:

| t / e# | message (verbatim, short) | class | resolution |
|---|---|---|---|
| t6→t7 / e#230→231 | (interrupt) → "do I have to enable MCP server to use it with claude?" | precise | answered next turn (t8 advances) |
| t13→t14 / e#498→500 | (interrupt) → "you should… rsync directly for phase 5, please review and confirm" | precise | redirect adopted immediately |
| t15→t16 / e#510→513 | (interrupt) → "ok problem was, nas was powered off. Try again." | precise | external cause supplied, retried OK |

All three stay **precise** through the correction — David names the exact pivot
(MCP enable, rsync-directly, NAS-powered-off) and the work moves on. Zero turns
of vague spiral; zero repeated-symptom loops.

## Hypothesis evaluation (precise→vague as a lagging signal)

The baseline hypothesis — *vague language is a lagging signal of a wrong fix
approach* — is **supported by its absence**, the same way wilhelm's `a79f4e6d`
micro-case supported it: **no failed-fix chain ⇒ no vague signal.** wing_contexts
has no wrong-fix chains (nothing here is a *fix* being iterated; it is decisions
being made), so the tripwire never arms, and indeed no vague message is ever
emitted. This is the clean negative control for the wilhelm positive: the
precise→vague mechanism is **specific to convergence-failure work** (debugging a
non-mechanical bug across retries), and does **not** fire in directed
build/config/admin work — which is most of what infra is. For Claude operating in
wing_contexts, F-C offers no tripwire to watch; the relevant lever is the F-A one
(don't over-ask, use known world-state), not the change-tack-on-vagueness signal.

## Bottom line for the synthesis (Task 5)

1. **Baseline "zero diagnostics" HOLDS in raw transcripts.** Unlike the "zero
   interrupts" claim (which raw data corrected to 3), there genuinely are zero
   convergence-failure / diagnostic sessions in wing_contexts. Infra work is
   *directed*, not *diagnosed* — confirmed, not an artifact of drawer mining.
2. **The precise→vague tripwire is work-type-specific, not universal.** It is a
   live signal in wilhelm (debug-by-retry) and a dead letter in contexts
   (decide-and-build). Any global.md framing of the tripwire should scope it to
   convergence-failure work, or it will read as always-on and mislead in the
   ~majority of sessions (config/admin/Q&A) where no fix is being iterated.
3. **wing_contexts is the negative-control wing.** Lowest friction of the three
   targets; what little exists is F-A (over-ask + world-state), resolved in one
   turn each. It anchors the "where the over-asking interrupt does NOT dominate"
   end of the Task-5 cross-project spectrum — and even its lone `AskUserQuestion`
   interrupt fired against an instruction that had *already* invited questions,
   underscoring how low the over-asking bar should be set.
