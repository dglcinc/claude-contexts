# Facet 4 — Correction-after-interrupt labeled corpus

**Source & method.** Facet 2 established that the mined drawers are a *lower
bound* on interrupts and do not preserve chronological next-message ordering —
its own closing takeaway was that "true interrupt density needs the raw
`.jsonl` transcripts, not the mined drawers." This facet therefore goes to that
source directly: a scan of all 20 Claude Code transcript files under
`~/.claude/projects/` for user messages whose entire body is the interrupt
marker (`[Request interrupted by user]` / `…for tool use]`), then, for each, the
**next genuine user message** in the same file (skipping tool-result envelopes,
`isMeta` records, skill-bundle boilerplate, and `<system-reminder>` blocks) plus
the assistant action that was in flight when the user cut in.

**Yield: 20 interrupt events; 17 with a recorded follow-up** (3 were terminal —
the session ended or was resumed via a skill with no free-text correction).
This is ~3x the drawer-derived count in Facet 2 (which found ~5 genuine events),
confirming Facet 2's lower-bound warning. Citations are `session-prefix:idx`
(transcript UUID + line index), which are auditable against the raw files.

## Headline pattern

**8 of 17 corrections (47%) interrupted an `AskUserQuestion` or `ExitPlanMode`
dialog** — i.e. the single most common thing a user interrupts is *Claude
pausing to ask or to present a plan*. The user dismisses the prompt and types
free-form instead, almost always to (a) add scope the options didn't cover,
(b) redirect to "go investigate first," or (c) defer/abandon. The offered
choices rarely fit what the user actually wanted to say. The next-largest
cluster is **wrong analysis / over-confident diagnosis** (4 pairs), where Claude
asserted a cause or a fix and the user's first word is literally "no".

## Theme A — Over-asking: interrupted a question/plan dialog (8 pairs)

Claude stopped to confirm via `AskUserQuestion` or `ExitPlanMode`; the user
killed the dialog and typed. Strong signal that Claude asks/plans at moments
where it should either act, or where its canned options miss the real intent.

| # | Session:idx | In flight | Correction (verbatim, trimmed) |
|---|---|---|---|
| 1 | `64edd6be`:73 | AskUserQuestion | "you should. Read the claude config files in the claude-contexts folder" |
| 2 | `64edd6be`:232 | AskUserQuestion | "sorry, I gave wrong answer. Rather than give a prompt, just have the selector on the help page. The first time they visit the help page, list the options and let them pick…" |
| 3 | `bd1c1597`:177 | AskUserQuestion | "in a prior session, you had proposed a way to do the context-senstive integration and proposed which pages to wire it to. Are you finding thta?" |
| 4 | `6d867d45`:230 | AskUserQuestion | "do I have to enable MCP server to use it with claude?" |
| 5 | `f1e54751`:38 | ExitPlanMode | "I would also like to add a voice option, so I can speak the query… handy if I'm using on a phone or ipad at the alley…" |
| 6 | `a68cadf2`:74 | ExitPlanMode | "would it make sense to re-package this plan so it can be executed in a ralph loop?" |
| 7 | `f1e54751`:139 | ExitPlanMode | "I will revisit this plan later, save to backlog" |
| 8 | `f1e54751`:129 | ExitPlanMode | (slash command) `/save-context` |

Sub-reading: #1/#3 are "stop asking, go look" — the answer was discoverable
(config files; a prior-session proposal) and Claude should have searched before
prompting. #5/#6 are "your plan is too narrow" — the user grafts scope onto an
otherwise-approved plan. #7/#8 are outright abandonment of the plan.

## Theme B — Wrong analysis / over-confident diagnosis (4 pairs)

Claude asserted a cause or a fix; the correction opens by negating it.

| # | Session:idx | In flight | Correction (verbatim, trimmed) |
|---|---|---|---|
| 9 | `a79f4e6d`:585 | Bash (verifying anchor fix) | "no the problem scott is reporting is not wrong anchor; the ? is appearing on the wrong screen. the ? that links to gauges should lik to the gauge options page…" |
| 10 | `6c0209bd`:1280 | asserted HSTS-pin theory for unstyled page | "no it's still not styled, on both my ipad and simulator. On my ipad I'm now getting skip to content and no jump" |
| 11 | `d9e08746`:816 | Read (mid scope claim) | "wait you are saying remove fun stats from the LLM surface, that's just your tool not the page in the app right?" |
| 12 | `2172308c`:326 | Bash (searching for edited files) | "no that's not it. I put the edited copies in the OneDrive Claude share, then copied them to my devices. So first look in the Claude directory…" |

Sub-reading: #9 and #10 are the WilhelmSK UI saga — Claude's stated root cause
(wrong anchor; HSTS pin) was wrong twice and the user had to re-specify the
actual symptom by hand. #10 is the canonical "too-confident assertion": Claude
wrote a multi-clause causal theory ("either HSTS wasn't the cause, or the
in-app browser is holding the in-memory HSTS pin…") and the page was simply
still broken. #11 catches a scope misunderstanding before Claude acted on it.

## Theme C — Wrong location / didn't read the available source (2 pairs)

Claude searched the wrong place or asked instead of reading a file that was
right there. (Overlaps Theme A #1; #13 below is the same root cause from the
analysis side.)

| # | Session:idx | In flight | Correction (verbatim, trimmed) |
|---|---|---|---|
| 12* | `2172308c`:326 | Bash searching for files | "…first look in the Claude directory, but also read the claude files in the claude-contexts directory. there may be a record you're not seeing yet — mempalace explicitly does not have memories." |
| 13 | `64edd6be`:73 | AskUserQuestion (asked whether to look) | "you should. Read the claude config files in the claude-contexts folder" |

(*#12 is listed under Theme B too — its negation is a diagnosis correction, but
the substance is a wrong-location fix, so it spans both.)

## Theme D — Stale state / wrong environment assumption (3 pairs)

Not Claude reasoning errors per se — the user interrupts to correct a fact about
the world (dependency version, host power state, access rights) that Claude was
proceeding on incorrectly.

| # | Session:idx | In flight | Correction (verbatim, trimmed) |
|---|---|---|---|
| 14 | `a79f4e6d`:228 | AskUserQuestion | "check and make sure you have the latest version of WilhelmSKLibrary" |
| 15 | `6d867d45`:510 | Bash (backup/rsync attempt failed) | "ok problem was, nas was powered off. Try again." |
| 16 | `6d867d45`:498 | Bash (planning backup path) | "you should have root or nasadmin passwordless access to the NAS from this machine so you should be able to rsync directly for phase 5, please review and confirm" |

Sub-reading: #14/#16 are the user supplying a fact Claude should have verified
(is the dep current? do we already have passwordless root?) rather than assuming
the harder path. #15 is pure external state (NAS off) — a false-negative Claude
could not have known, the cleanest "not your fault" interrupt in the corpus.

## Theme E — Mid-flight redirect (next directive, not a correction) (2 pairs)

Borderline cases: the interrupt is followed by a fresh instruction or question,
not a correction of an error. Kept for completeness; excluded from the
"mistake" tallies above.

| # | Session:idx | In flight | Correction (verbatim, trimmed) |
|---|---|---|---|
| 17 | `7ecc991c`:845 | reporting two clean merges | "merge remaining prs" |
| 18 | `6c0209bd`:1104 | Bash | "where is AIS" |

## Theme tally (primary assignment, 17 corrected events)

| Theme | Pairs | Share |
|---|------:|------:|
| A — over-asking (interrupted question/plan) | 8 | 47% |
| B — wrong analysis / over-confident diagnosis | 4 | 24% |
| D — stale state / wrong env assumption | 3 | 18% |
| E — mid-flight redirect (not a correction) | 2 | 12% |
| (C overlaps A/B — wrong-location, 2 cross-listed) | — | — |

Three additional interrupt events (`4583c448`:11, `d8cdcf9a`:6, `f1e54751`:161)
were **terminal** — no free-text follow-up (session end / skill resume), so they
carry no correction signal.

## Observations for synthesis (feed Facet 5)

- **The dominant "mistake" is not a code bug — it's an interaction mismatch.**
  Nearly half of all interrupts land on Claude *asking* (`AskUserQuestion`) or
  *proposing* (`ExitPlanMode`). The user's correction is usually "you already
  had enough to act" (#1, #3, #4, #13) or "your options/plan missed the point"
  (#2, #5, #6). Reducing premature `AskUserQuestion`/`ExitPlanMode` calls — read
  the obvious source first, fold likely scope in before presenting — would erase
  the largest interrupt category outright.
- **"no…" is the tell for over-confidence.** Every Theme-B correction begins by
  negating a confident assertion (#9, #10, #12 literally start "no"). The
  WilhelmSK UI work (`6c0209bd`, `a79f4e6d`) is where this concentrates —
  consistent with Facet 2's weak qualitative lean that hands-on iOS/UI work
  interrupts somewhat more, and with Facet 3's finding that UI work is where
  vague-symptom debugging lives.
- **The transcript is the right grain, the drawer is not.** 17 corrected pairs
  vs Facet 2's ~5 drawer-events confirms the mining pipeline drops the
  interrupt→correction adjacency. If this signal matters (it's the richest
  behavioral data in the corpus), the pipeline should mine the *pair*, not the
  isolated marker line — see Facet 5 recommendation on drawer-level metadata.
