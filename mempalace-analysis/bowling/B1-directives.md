# B1 — Directive histogram (bowling-league-tracker) + diff vs baseline

**Source:** the 570 uuid-named `*.jsonl` main-thread sessions at
`~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker/`
(`agent-*.jsonl` and `*.md` excluded). Parser: `bowling/_b1_extract.py`.
David's messages = lines where `type=="user"` and `message.role=="user"`, text
blocks only (tool_result/tool_use dropped), with `<system-reminder>`,
`<command-*>`, `<task-notification>`, `Caveat:` boilerplate and interrupt
markers removed. One leaked `sk-ant-…` key in the transcript was redacted.

> **The headline finding — this build was itself a ralph loop.** 560 of 570
> sessions open with the *identical* injected harness prompt
> `"Read PLAN.md. Find the first unchecked - [ ] task. Do it…"`. That is the
> automation driver, **not** a David directive, so it is filtered out. What
> remains is the true human-typed corpus: **79 directives**, and they live in
> **only 9 of 570 sessions** — **561 sessions (98.4%) contain zero human
> input.** Unlike the baseline (message-by-message collaboration), David
> directed this build by writing `PLAN.md` once and letting the loop run; his
> live typing collapsed to gate-keeping a mostly-autonomous fleet.

## (a) Top leading first-words (n=79)

| Rank | First word | Count | | Rank | First word | Count |
|--|--|--:|--|--|--|--:|
| 1 | yes | 10 | | 8 | ok | 2 |
| 2 | i | 10 | | 9 | let's | 2 |
| 3 | merge | 7 | | 10 | for | 2 |
| 4 | can | 5 | | 11 | you | 2 |
| 5 | do | 5 | | 12 | also | 2 |
| 6 | the | 3 | | 13 | why | 2 |
| 7 | which | 2 | | 14 | (singletons) | 1 each |

Singleton openers include `create, get, retrieve, add, update, check, please,
wait, before, looks, every, when, here's`.

**Imperative-verb-leading vs non-verb-leading:** only **12 / 79 (15.2%)** open
with a recognizable command verb (`merge` ×7, `do` ×5-as-imperative subset,
`create, get, retrieve, add, update, check`). The dominant openers are
**acknowledgments/approvals** (`yes` ×10, `ok`, `yup`, `let's`), **questions**
(`can, which, why, what, would, is`), and **first-person framing** (`i` ×10 —
"I like A", "I read somewhere…", "I already merged 122"). The verb-leading
share is *lower* than baseline's 26.1% — because in a delegated build, David
isn't issuing build commands, he's approving and probing.

## (b) Word-count histogram (full raw text — NOT truncated)

| Bucket | Count | % |
|--------|------:|----:|
| 1 word | 2 | 2.5% |
| 2-3 | 17 | 21.5% |
| 4-7 | 14 | 17.7% |
| 8-15 | 19 | 24.1% |
| 16+ | 27 | 34.2% |

**Modal bucket is 16+ (34.2%).** Note the **bimodal shape**: a tall spike at
≤3 words (24.1% combined) sitting against a fat 16+ tail (34.2%), with 4-7
hollowed out as the trough. The two peaks are two different *jobs*: the ≤3
cluster is **terse approvals/merges**, the 16+ tail is **feature specs and
multi-symptom diagnostic reports**. Because this is raw JSONL, the 16+ figure
is the *true* tail — unlike baseline, whose 16+ was capped at 16-18 words by
the mining hook's ~80-char truncation.

## (c) Representative directives per bucket (verbatim, `session:line`)

**1 word (n=2):**
- "private" — `43751840:42`
- "biggger" — `d9e08746:801`

**2-3 words (n=17) — the approval/merge spike:**
- "merge and deploy" — `39c75aa3:190` (recurs ×6: also `709bb189:124`,
  `d9e08746:551/740/876/1003`)
- "yes refactor" — `39c75aa3:235`
- "yes delete" — `d9e08746:233`
- "add it" — `d9e08746:259`
- "do 1" — `d9e08746:313`
- "update plan.md rules" — `d9e08746:334`
- "yes keep going" — `d9e08746:823`
- "do it" — `d9e08746:893`
- "yup it does" — `39c75aa3:214`
- "yes please do" — `88eca805:257`

**4-7 words (n=14):**
- "which model is the ask tab using" — `39c75aa3:6`
- "I like A. Do it." — `39c75aa3:303`
- "yes, add them to .gitignore" — `6d83450e:101`
- "merge all open prs" — `d9e08746:276`
- "yes kick off ralph" — `d9e08746:369`
- "merged all the prs - deploy" — `d9e08746:464`
- "the verify script failed on line 85" — `d9e08746:57`
- "which one do you recommend" — `d9e08746:93`
- "can you read diagrams in a PPT" — `e589c601:6`
- "let's do it now" — `a68cadf2:103`

**8-15 words (n=19):**
- "can you switch it to haiku? That should be good enough for this function
  right?" — `39c75aa3:12`
- "why does save-context tool take so long to run" — `39c75aa3:219`
- "what prompt should I use for a ralph wiggum loop" — `6d83450e:66`
- "get rid of the stat builder tab, merge and deploy" — `88eca805:6`
- "can you review pr 133, looks like it is not needed any more" — `88eca805:230`
- "check the llama token rate again to make sure it didn't change after the
  reboot" — `d9e08746:350`
- "why are we doing the soak-in? maybe just go ahead with ralph?" — `d9e08746:364`
- "If I tail ralph log there are three tee errors - are those non-critical?"
  — `d9e08746:398`
- "do I need any tool calls at all or can the model just operate directly?"
  — `d9e08746:884`
- "I will revisit this plan later, save to backlog" — `f1e54751:144`

**16+ words (n=27) — the feature-spec / diagnostic tail:**
- "I would like to download an open source model that could run with the
  bowling app to allow interactive queries for stats. Which model would be best
  for this mac…" — `f1e54751:10`
- "I would also like to add a voice option, so I can speak the query. This will
  be handy if I'm using on a phone or ipad at the alley…" — `f1e54751:42`
- "for the ask tab, when I press the microphone button, clear the current text.
  When I release it, submit the request." — `88eca805:154`
- "the results from the llama engine seem unreliable. For example, I asked the
  question \"Who has the most career strikes\" and I got the answer…" — `d9e08746:473`
- "also the audio ask button seems to cut the last letter (I ask \"who has the
  most career strikes\" and the last s gets dropped" — `d9e08746:534`
- "this feature seems pretty worthless. For example I asked who won the harry
  russell tournament the most times, the llm says it can't answer…" — `d9e08746:558`
- "Is the bowling site down? Please investigate and also tell me why I didn't
  get a notification email" — `709bb189:35`
- "one more thing, can you review the logs, I'm seeing a substantial number of
  login attempts. Assess and recommend." — `a68cadf2:207`
- "would it make sense to re-package this plan so it can be executed in a ralph
  loop?" — `a68cadf2:76`
- "OK draft a PR, and prepare for me to ask to remove all the llama
  infrastructure, including the services and tools." — `d9e08746:634`

## (d) Central tendency

| Stat | Value |
|------|------:|
| n directives | 79 |
| mean words | 15.9 |
| median words | 10.0 |
| ≤3 words | 19 / 79 = **24.1%** |

Mean (15.9) sits well above median (10.0): the 16+ tail drags the average up
while half of all directives are ≤10 words.

## (e) Comparison vs baseline

| Metric | Baseline (palace diary, 211 directives, 4 wings) | Bowling (raw JSONL, 79 directives, 1 product) |
|---|---|---|
| Median words | ~11 | **10** |
| % ≤3 words | 12.8% | **24.1%** (≈2×) |
| Modal bucket | 8-15 (44.5%) | **16+ (34.2%)** |
| Verb-leading | 26.1% | **15.2%** |
| Top verbs | merge, add, commit, run, open, update | **merge** (×7), do, add, create, get, update, check |
| Text fidelity | truncated ~80 chars (16+ capped) | **full / uncapped** |
| Human-input density | message-by-message | **9 of 570 sessions (98.4% autonomous)** |

`merge` is the #1 verb in *both* corpora — the git/publish mechanics ("merge it",
"merge and deploy") are David's most stable terse-command register across every
project. What changes in bowling is everything around it.

**How directing an intense single-product build differs.** The baseline was a
post-2026-05-25 *cross-project* week of hands-on, turn-by-turn collaboration; its
modal directive was a full ~11-word explanatory sentence (8-15 bucket, 44.5%).
Bowling is the opposite operating mode: David front-loaded the intent into a
`PLAN.md` and ran a **ralph loop**, so 98.4% of sessions have no human in them at
all. His live directives bifurcated into two registers — a doubled spike of
**terse approvals/merges** ("merge and deploy" ×6, "do it", "yes keep going":
the ≤3-word rate jumps to 24.1%) and a **fat 16+ tail of feature specs and
multi-symptom diagnostics** ("the results from the llama engine seem unreliable.
For example…"). The conversational *middle* — baseline's bread and butter —
hollows out, because the loop, not David, was doing the step-by-step work. He
shows up to **gate** (approve/merge/deploy) and to **steer at the spec level**
(define the voice-query feature, triage the llama engine's quality), and little
in between.

## (f) Re-evaluating the refuted hypothesis ("most directives are ≤3 words")

**Still REFUTED — but far less decisively than baseline.** ≤3-word directives
are **24.1%** here vs 12.8% in baseline: the ralph-delegation roughly *doubles*
the terse share, partially rehabilitating the "terse operator" stereotype. Yet a
24% minority is still not "most," the median is 10 words, and the single largest
bucket (16+, 34.2%) is the *opposite* of terse. The accurate statement is: **the
more David delegates execution to a loop, the terser his live directives become**
— approval-gating compresses toward "merge and deploy," while the substantive
thinking migrates out of the turn-by-turn channel and into the `PLAN.md` he wrote
up front (and into the long diagnostic reports when the autonomous output needs
correcting). The stereotype is a function of *operating mode*, not of David.
