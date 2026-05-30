# Facet 1 — Imperative-verb histogram + directive length distribution

**Source:** `recent:` field of every diary-room drawer (`room=diary`, all wings).
78 drawers fetched (`mempalace_list_drawers room=diary`; store reported 78, one
more than the planned 77). Each drawer is a rolling-window CHECKPOINT whose
`recent:` field is a pipe-delimited list of the most recent USER messages at that
checkpoint. Consecutive checkpoints in a session overlap, so messages were
deduped (longest-prefix wins; wing = first appearance). Boilerplate dropped:
`Base directory for this skill:` lines, `Invoke the generic mempalace skill`,
bare `npm_…` tokens, empty fragments.

**Result: 211 unique directives.**

> **Critical caveat — snippet truncation.** The mining hook stores each
> `recent:` message truncated at ~80 chars; many end mid-word
> (e.g. `"...is there any "`). Word counts in buckets 8-15 and 16+ therefore
> measure the *stored truncated text*, not the full original message. Long
> directives are artificially capped near 16-18 words. This **strengthens** the
> refutation in (f): true messages are even longer than measured.

## (a) Unique directive counts per wing

| Wing | Count |
|------|------:|
| wing_wilhelm | 152 |
| wing_docs | 41 |
| wing_contexts | 14 |
| wing_code | 4 |
| **Total** | **211** |

## (b) Top 30 leading first-words

| Rank | First word | Count | | Rank | First word | Count |
|--|--|--:|--|--|--|--:|
| 1 | ok | 14 | | 16 | run | 4 |
| 2 | what | 11 | | 17 | open | 4 |
| 3 | can | 11 | | 18 | why | 3 |
| 4 | yes | 8 | | 19 | i'm | 3 |
| 5 | scott | 8 | | 20 | it | 3 |
| 6 | the | 7 | | 21 | one | 3 |
| 7 | for | 7 | | 22 | still | 3 |
| 8 | please | 5 | | 23 | no | 3 |
| 9 | where | 5 | | 24 | in | 2 |
| 10 | merge | 5 | | 25 | we | 2 |
| 11 | i | 5 | | 26 | update | 2 |
| 12 | add | 5 | | 27 | there | 2 |
| 13 | you | 4 | | 28 | switch | 2 |
| 14 | commit | 4 | | 29 | start | 2 |
| 15 | how | 4 | | 30 | if | 2 |

**Imperative-verb-leading vs. non-verb-leading:**

- Only **55 / 211 (26.1%)** start with a recognizable imperative verb
  (merge, add, commit, run, open, update, switch, start, publish…).
- **156 / 211 (73.9%)** start with a non-verb: a question word
  (what/where/why/how), an acknowledgment/filler (ok/yes/no), a
  pronoun/article (the/i/it/you/we), or a proper noun (scott).

The leading token is dominated by conversational openers and questions, not
commands. The "terse imperative" stereotype is the minority register.

## (c) Word-count histogram (whitespace tokens, on stored truncated text)

| Bucket | Count | % |
|--------|------:|----:|
| 1 word | 3 | 1.4% |
| 2-3 | 24 | 11.4% |
| 4-7 | 41 | 19.4% |
| 8-15 | 94 | 44.5% |
| 16+ | 49 | 23.2% |

Modal bucket is **8-15 words (44.5%)**; the long tail (16+) is capped by
truncation and would be larger with full text.

## (d) Representative directives per bucket (verbatim, wing + sample drawer)

**1 word (n=3):**
- `[wing_contexts]` "remodel" — `diary_wing_contexts_20260525_131726005306_e0f6f34fb3f4`
- `[wing_wilhelm]` "styled" — `diary_wing_wilhelm_20260525_164607115835_de1f502f9525`
- `[wing_docs]` "161,138,92" — `diary_wing_docs_20260526_184317658902_18b136553610`

**2-3 words (n=24):**
- `[wing_wilhelm]` "sync them now" — `diary_wing_wilhelm_20260525_120545959630_859bc5b84bda`
- `[wing_docs]` "merge both PRs" — `diary_wing_docs_20260525_122351728537_676397bd3802`
- `[wing_docs]` "merge it" — `diary_wing_docs_20260525_123726819193_bd97f5450cfa`
- `[wing_contexts]` "add the rule" — `diary_wing_contexts_20260525_131726005306_e0f6f34fb3f4`
- `[wing_wilhelm]` "commit this" — `diary_wing_wilhelm_20260525_133107474757_b64831c5a83d`
- `[wing_wilhelm]` "push it" — `diary_wing_wilhelm_20260525_135023331669_de687949d4ee`
- `[wing_wilhelm]` "update session state" — `diary_wing_wilhelm_20260525_135023331669_de687949d4ee`
- `[wing_wilhelm]` "where is it" — `diary_wing_wilhelm_20260525_145705612797_0bfddde75d30`
- `[wing_wilhelm]` "ok merge" — `diary_wing_wilhelm_20260525_145705612797_0bfddde75d30`
- `[wing_wilhelm]` "publish 0.1.3" — `diary_wing_wilhelm_20260525_150857156439_f3c5847e48e6`

**4-7 words (n=41):**
- `[wing_wilhelm]` "what is pr 99" — `diary_wing_wilhelm_20260525_104958118648_03677da97259`
- `[wing_wilhelm]` "update tools/mempalace.md to note dedup isn't automatic" — `diary_wing_wilhelm_20260525_110837461972_fecdca157d09`
- `[wing_wilhelm]` "commit the batch and update PR #99" — `diary_wing_wilhelm_20260525_114649469101_2b440ddddf06`
- `[wing_docs]` "start the npm publish prep" — `diary_wing_docs_20260525_121542758259_ccfa5b419fba`
- `[wing_docs]` "run the publish for me" — `diary_wing_docs_20260525_123726819193_bd97f5450cfa`
- `[wing_docs]` "there is no classic tokens option" — `diary_wing_docs_20260525_130211165236_e87bbefffeac`
- `[wing_docs]` "yes, keep an eye on it" — `diary_wing_docs_20260525_130211165236_e87bbefffeac`
- `[wing_docs]` "I did not get a browser prompt" — `diary_wing_docs_20260525_130211165236_e87bbefffeac`
- `[wing_wilhelm]` "yet pull reconcile review" — `diary_wing_wilhelm_20260525_104958118648_03677da97259`
- `[wing_wilhelm]` "open an issue" — `diary_wing_wilhelm_20260525_205258924923_19470ee7415a`

**8-15 words (n=94):**
- `[wing_wilhelm]` "let's work on the context-sensitive help integration for wilhelmsk" — `diary_wing_wilhelm_20260525_103308466663_6a387374f903`
- `[wing_wilhelm]` "in a prior session, you had proposed a way to do the context-senstive integratio" — `diary_wing_wilhelm_20260525_103308466663_6a387374f903`
- `[wing_wilhelm]` "Please run the app in the simulator and let me test." — `diary_wing_wilhelm_20260525_110837461972_fecdca157d09`
- `[wing_wilhelm]` "why is there no help on the layouts page?" — `diary_wing_wilhelm_20260525_110837461972_fecdca157d09`
- `[wing_wilhelm]` "please review the readme, architecture overview, and analysis doc you did, and u" — `diary_wing_wilhelm_20260525_114649469101_2b440ddddf06`
- `[wing_contexts]` "how do I add kg triples for mempalage" — `diary_wing_contexts_20260525_115724461661_cd8993f0e366`
- `[wing_contexts]` "yes, seed the KG with the deployment facts" — `diary_wing_contexts_20260525_115724461661_cd8993f0e366`
- `[wing_wilhelm]` "switch that remote to SSH and rotate the token" — `diary_wing_wilhelm_20260525_120545959630_859bc5b84bda`
- `[wing_wilhelm]` "where is the token exposed, will this be publicly visible?" — `diary_wing_wilhelm_20260525_120545959630_859bc5b84bda`
- `[wing_wilhelm]` "you should review the claude context for the signalk-plugin project too. We are" — `diary_wing_wilhelm_20260525_102723945021_100cc444d445`

**16+ words (n=49 — all capped at 16-18 by snippet truncation):**
- `[wing_wilhelm]` "we should just have everything in this PR, keep it simple for scott, and it's al" — `diary_wing_wilhelm_20260525_104958118648_03677da97259`
- `[wing_wilhelm]` "please also check any other candidates that should have a ? link, now that you k" — `diary_wing_wilhelm_20260525_110837461972_fecdca157d09`
- `[wing_wilhelm]` "there still seem to be a number of screens that could have help and don't, like" — `diary_wing_wilhelm_20260525_114649469101_2b440ddddf06`
- `[wing_docs]` "how big is the complete plugin plus docs when installed? I'd like to make that p" — `diary_wing_docs_20260525_122351728537_676397bd3802`
- `[wing_docs]` "ok I did not have an npm account, I created one. let me what you need to publish" — `diary_wing_docs_20260525_123726819193_bd97f5450cfa`
- `[wing_docs]` "I'm not seeing the doc plugin in the app store. how long should it take to appea" — `diary_wing_docs_20260525_130211165236_e87bbefffeac`
- `[wing_docs]` "ok this works, but it would be nicer if there was a direct link in the config pa" — `diary_wing_docs_20260525_130211165236_e87bbefffeac`
- `[wing_wilhelm]` "this file got touched in this PR. Did you edit manually or did xcode update it?" — `diary_wing_wilhelm_20260525_135023331669_de687949d4ee`
- `[wing_wilhelm]` "when you go to the help menu item to view the doc, it still briefly flashes the" — `diary_wing_wilhelm_20260525_135023331669_de687949d4ee`
- `[wing_wilhelm]` "now there's a weird thing where it shows a panel and I have to click proceed to" — `diary_wing_wilhelm_20260525_135023331669_de687949d4ee`

## (e) Per-wing word count

| Wing | n_directives | mean_words | median_words |
|------|-------------:|-----------:|-------------:|
| wing_wilhelm | 152 | 10.72 | 11.0 |
| wing_docs | 41 | 11.44 | 12.0 |
| wing_contexts | 14 | 6.86 | 7.0 |
| wing_code | 4 | 12.50 | 13.5 |

`wing_contexts` (infra/memory plumbing) runs notably terser than the
product/iOS work in `wing_wilhelm`/`wing_docs`.

## (f) Hypothesis: "most directives are ≤3 words"

≤3-word directives: **27 / 211 = 12.8%**.

**REFUTED.** Only 12.8% are ≤3 words; the median directive is ~11 words and the
modal bucket is 8-15 words (44.5%). Terse commands ("merge it", "push it") are
real but a small minority. Truncation only makes long directives look shorter,
so the true distribution refutes the hypothesis even more strongly.

## Observation

The picture is the opposite of the "terse imperative operator" stereotype. Three
quarters of directives open with a question word, an acknowledgment, or a proper
noun ("scott…") rather than a command verb, and the typical directive is a full
~11-word sentence. Short barked commands cluster around git/publish mechanics
("merge it", "push it", "commit this", "publish 0.1.3"), while the bulk of the
corpus is conversational: explaining context, reporting symptoms, and asking
"why / where / how". Infra work (`wing_contexts`) is the terse exception; iOS and
docs work skews longer and more explanatory.
