# B2 — Vague-vs-precise diagnostics (bowling-league-tracker) + diff vs baseline

**Source:** the same 79 genuine David human messages B1 extracted from the 570
uuid-named `*.jsonl` main-thread sessions at
`~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker/`
(`agent-*.jsonl` and `*.md` excluded). Parser: `bowling/_b2_extract.py`, which
dumps all 79 messages cited `session:line` (raw dump is gitignored scratch).
The diagnostic detection and the VAGUE/PRECISE call are **hand-classified** — the
vague/precise boundary is a judgment baseline §e proved a keyword regex cannot
make reliably (David's hedges are usually politeness wrappers around precise
reports, not genuine vagueness). Citations are `<8-char-session>:<line>`.

**Classification criteria (same as baseline Facet 3):**
- **Diagnostic** = the message's primary job is to report a symptom, unexpected
  behavior, missing element, or a correction of the assistant's output. Dropped:
  pure directives ("merge and deploy"), acks ("yes refactor"), info/how-to
  questions ("which model is the ask tab using"), and feature specs (the
  voice-query request).
- **PRECISE** = concrete locator the assistant can act on without guessing: a
  named screen/file/tool/log, a file\:line or `#PR` ref, exact quoted output, or
  a named symptom+location — **or** an exact reproduction (the question asked +
  the wrong answer returned).
- **VAGUE** = symptom carried only by hedge/affect ("seems", "messed up", "not
  sure", "issues", "looks like") with **no** concrete locator or repro.

> **Headline — bowling skews even *more* precise than the baseline, and it's the
> reproducibility of the AI-query feature that does it.** 22 of 79 live messages
> are diagnostics; **18 are precise, only 4 are vague (vague:precise = 0.22, vs
> baseline 0.45 — twice as precise).** Because the painful feature was an
> LLM-stats engine, David could paste the *exact* question and the *exact* wrong
> answer every time, so "seems unreliable" is always followed by a verbatim
> repro. The 4 genuinely-vague messages are not random: every one is an
> **abandonment signal** at the tail of a chain of precise reports that failed to
> converge — the same precise→vague escalation baseline saw in the serif saga.

## (a) Overall ratio and diagnostic rate

| Class | Count | % of diagnostics |
|-------|------:|-----:|
| PRECISE | 18 | 81.8% |
| VAGUE | 4 | 18.2% |
| **Total diagnostics** | **22** | 100% |

**Vague : precise = 4 : 18 = 0.22.** ≈ **4.5 precise for every vague** one.

**Diagnostic rate.** 22 / 79 live human messages = **27.8%** are diagnostics —
*double* baseline's 14%. The inflation is a delegation artifact, not a
personality shift: in a ralph-loop build the conversational middle (step-by-step
collaboration) is gone, so the live channel is just two registers — **gate-keeping**
(merge/yes/deploy) and **correcting the autonomous output**. Diagnostics are a
much larger slice of what little David types. Restricting to baseline-comparable
*product/system-symptom* diagnostics (excluding the 4 design/process corrections
`:241 :364 :796 :818`) gives 18/79 = **22.8%** — still well above 14%.

### Diagnostics per session — one session is the epicenter

| Session | Diagnostics | Precise | Vague | What it was |
|---|--:|--:|--:|---|
| `d9e08746` | **13** | 12 | 1 | the llama→Anthropic AI-stats-query saga |
| `6d83450e` | 3 | 2 | 1 | ralph-loop bootstrap |
| `39c75aa3` | 2 | 2 | 0 | ask-tab model/render |
| `709bb189` | 1 | 1 | 0 | site-down incident |
| `a68cadf2` | 1 | 1 | 0 | login-attempt review |
| `88eca805` | 1 | 0 | 1 | PR-133 triage |
| `f1e54751` | 1 | 0 | 1 | ultra-plan round-trip |
| `e589c601`,`43751840` | 0 | — | — | PPT ingest / "private" |

**`d9e08746` alone holds 13/22 = 59% of all diagnostics.** Diagnostics cluster in
the single session where a feature wouldn't converge — exactly as baseline's
diagnostics concentrated in `wing_wilhelm` (the iOS product) and its
non-converging serif sessions.

## (b) Examples (verbatim, full text — NOT truncated)

### All 4 VAGUE (the plan asks for 10; there are only 4 — that scarcity *is* the finding)

| # | Message | Why vague | Cite |
|--|--|--|--|
| 1 | "I wonder how useful this will be, seems like every time I ask a question I could be back here adding more tools… Otherwise I'm not sure how useful it will be." | value-doubt by affect ("I wonder", "not sure"); no defect | `d9e08746:629` |
| 2 | "looks like things got messed up on the plan side, let's just leave it the way it is." | "messed up" + no locator; abandons | `f1e54751:126` |
| 3 | "can you put that in an sh, I've had issues copy-pasting from this window" | "issues" — symptom unspecified | `6d83450e:90` |
| 4 | "can you review pr 133, looks like it is not needed any more" | "looks like it is not needed" — hunch, no reason | `88eca805:230` |

### 10 PRECISE (representative of 18)

| # | Message | Locator / repro | Cite |
|--|--|--|--|
| 1 | "the verify script failed on line 85" | file + exact line | `d9e08746:57` |
| 2 | "on the ask page in the app, you are putting ** ** around some items, which is markdown for bold… What exactly did you intend?" | named page + exact symptom | `39c75aa3:292` |
| 3 | "the results from the llama engine seem unreliable. For example, I asked \"Who has the most career strikes\" and I got \"…Peter Mancini… 707.\" How can you explain that answer?" | hedge + **exact Q→wrong-A repro** | `d9e08746:473` |
| 4 | "also the audio ask button seems to cut the last letter (I ask \"who has the most career strikes\" and the last s gets dropped" | named button + exact repro | `d9e08746:534` |
| 5 | "this feature seems pretty worthless. For example I asked who won the harry russell tournament the most times, the llm says it can't answer. This is easily answered just by looking at the fun stats page." | hedge + repro + where the answer lives | `d9e08746:558` |
| 6 | "The answer always starts with tools used, why is that?… it gave a long list of partial answers about who won what years but didn't actually answer the question. Am I actually calling the anthropic API?" | exact behavior + repro + hypothesis | `d9e08746:783` |
| 7 | "you need to update the text displayd on the screen, it still shows llama model comment." | named location + exact stale text | `d9e08746:972` |
| 8 | "Is the bowling site down? Please investigate and also tell me why I didn't get a notification email" | named system + two concrete symptoms | `709bb189:35` |
| 9 | "I'm seeing a substantial number of login attempts. Assess and recommend." | named source (logs) + concrete observation | `a68cadf2:207` |
| 10 | "every time I set context I there are a number of cancelled parallel tool calls. What is that?" | named action + exact symptom | `d9e08746:80` |

Other precise diagnostics not tabled: `:219` (save-context perf), `:116`
(env/`sclaude` not inherited by the script), `:145` (must ctrl-c, loop won't
exit), `:398` (three tee errors in ralph log), `:796` (sending 20K back vs
querying the DB — design critique), `:818` ("wait you are saying remove fun stats
from the LLM surface, that's just your tool not the page in the app right?" —
catches a possible misread), `:241` (ralph-finish is an optional file — corrects a
claim), `:364` (why soak-in, just go ralph — challenges the plan).

## (c) Comparison vs baseline

| Metric | Baseline (palace diary, 223 msgs, 4 wings) | Bowling (raw JSONL, 79 msgs, 1 product) |
|---|---|---|
| Vague : precise | 10 : 22 = **0.45** | 4 : 18 = **0.22** (≈ ½) |
| % precise | 68.8% | **81.8%** |
| Diagnostic rate | 32 / 223 = **14%** | 22 / 79 = **27.8%** (product-only 22.8%) |
| Where diagnostics live | product wings (wilhelm 71% precise; infra = 0) | one product session (`d9e08746` = 59% of all) |
| Vague trigger | escalation after fixes fail to converge | **same** — every vague msg ends a failed chain |
| Hedge ≠ vague | "I think"/"still not" wrap precise reports | **same, stronger** — "seems" always + a repro |

Two baseline findings **confirm and intensify** here; one diverges:

- **Confirmed, stronger: hedges are politeness wrappers, not vagueness.** Every
  "seem(s)" in bowling (`:473 :534 :558 :783 :796`) is immediately backed by a
  verbatim reproduction. Baseline flagged this as a classifier trap; bowling makes
  it almost a law — a keyword regex keying on "seems unreliable / seems worthless"
  would misclassify 5 of the most precise messages in the corpus.
- **Confirmed: vagueness is the abandonment register** (see §d).
- **Diverged: the diagnostic *rate* doubles** (14%→28%) and **precision rises**
  (69%→82%). Both flow from the same two causes: (1) delegation strips out the
  non-diagnostic conversational middle, concentrating the live channel; (2) the
  hard feature was an **AI-query engine**, the most reproducible bug class
  possible — you ask a question, you get a literally-quotable wrong answer — so
  David's reports are near-perfectly precise. Baseline's most-precise wing
  (`wing_wilhelm`, visible UI bugs) hit 71%; an LLM-output feature beats even
  that because the defect *is* text he can paste.

## (d) Observation — product work skews precise; vague marks the abandon point

**Bowling is hands-on product work, and it skews precise even harder than the
baseline product wings did.** Baseline §d split the corpus by work type:
iOS/UI = 71% precise (he can see and name the broken artifact), infra/memory = 0
diagnostics (nothing visual; work proceeds as directives). Bowling is *all*
product, *and* its hardest surface emits quotable text, so it lands at 82%
precise. This **confirms** the baseline thesis (precision tracks how nameable the
broken artifact is) and extends it: **reproducible-output features are the
high-water mark of diagnostic precision** — higher than visible-UI bugs.

**Vague spikes cluster exactly where a fix failed across retries — confirmed
twice.** The 4 vague messages are not scattered noise; each is the *terminal*
beat of a precise chain that stopped converging — the same precise→vague collapse
baseline documented in the serif saga:

- **The llama-engine saga (`d9e08746`).** A run of precise diagnostics —
  `:473` (wrong "707" strikes answer) → `:534` (audio drops last letter) → `:558`
  ("worthless", with repro) → `:783` ("always starts with tools used", with
  repro) → `:796` (20K-payload critique) — never makes the feature good. It
  collapses to the one **vague** message in the session, `:629` *"I'm not sure how
  useful it will be… every time I ask a question I could be back here adding more
  tools,"* and immediately David changes tack entirely: `:634` "prepare for me to
  ask to remove all the llama infrastructure." The vague message is the signal
  that the *approach* (local llama) is wrong, not any single bug — and the fix was
  to switch to the Anthropic API, then question tool-calling altogether (`:884`).
- **The ultra-plan round-trip (`f1e54751`).** Precise attempts to get the edited
  plan back — `:82` "how do I bring the updated plan back here", `:90` "do you
  have the updated plan? I approved it in ultra plan", `:111` "I was able to copy
  the plan to a markdown file" — fail to sync, and the session ends on the
  **vague** `:126` *"looks like things got messed up on the plan side, let's just
  leave it the way it is"* — abandonment.

The actionable lever is identical to baseline's: don't ask David to "be more
precise" (he is, to a fault) — **treat the rare drop from precise repro to vague
affect as the tripwire that the current approach has failed and a different tack
is needed**, not as a request to debug the same path once more. In bowling that
tripwire fired twice, and both times the right move was to abandon the approach
(rip out llama; stop fighting the ultra-plan round-trip), which is exactly what
David did within one or two messages of going vague.
