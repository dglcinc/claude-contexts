# Task 1 — Corpus Inventory (raw `.jsonl` transcripts on the Mini)

Enumerates the raw Claude Code transcripts available on `utilityserver` (Mac
Mini) and maps each source directory to a MemPalace **wing**, so Tasks 2–4 can
reference concrete paths instead of palace drawers. This is the grounding pass:
it does not analyze content.

## Method

- **Sources scanned:** `~/.claude/projects/-*/` (local sessions) and
  `~/.mempalace/incoming/-*/` (transcripts shipped from David's MacBook and the
  Pi by the auto-capture client hook, awaiting/after host-side mining).
- **Path→cwd decoding:** a project dir name is the session cwd with `/` → `-`,
  e.g. `-Users-utilityserver-github-wilhelm` = cwd `/Users/utilityserver/github/wilhelm`.
- **cwd→wing rule** (implicit, as used by the `bowling/` extract scripts and the
  baseline): the wing is derived from the **repo basename** of the cwd, not an
  explicit tag in the transcript. So `…/github/bowling-league-tracker` → `wing_bowling`,
  `…/github/wilhelm` → `wing_wilhelm`, `…/github/claude-contexts` → `wing_contexts`,
  `…/github/{signalk-wilhelmsk-docs,wilhelm-docs-ralph}` → `wing_docs`.
- **Counts:** `sessions` = top-level UUID-named `*.jsonl` (main-thread
  conversations). `+side` = additional `agent-*.jsonl` / sub-dir sidechain
  transcripts found recursively (sub-agent tool runs; excluded from analysis,
  matching the bowling extract which keys only on UUID main-thread files).
- **Size:** `du -sk` of the whole dir (KB). **Date range:** min/max file mtime
  (proxy for session date; no clock call was made — these are filesystem dates).
- **<50 KB skip rule:** applied below. *No* candidate dir falls under 50 KB, so
  nothing is dropped for thinness; the meta/self-analysis dirs are excluded for a
  different reason (see Exclusions).

## Inventory

Counts/sizes are exact (`os.walk`, summed `*.jsonl` bytes); `Size` is the sum of
transcript bytes only, not `du` of the whole dir.

| Wing | Source | Path prefix (under the source root) | Sessions | +side | Size | Date range |
|------|--------|-------------------------------------|---------:|------:|-----:|------------|
| `wing_bowling` ✅done | projects | `-Users-utilityserver-github-bowling-league-tracker` | 569 | +9 | 25.1 MB | 2026-04-30 … 05-07 |
| `wing_wilhelm` | projects | `-Users-utilityserver-github-wilhelm` | 9 | +11 | 19.9 MB | 2026-05-25 … 05-29 |
| `wing_wilhelm` | incoming | `-Users-david-github-wilhelmsk` | 1 | 0 | 0.9 MB | 2026-05-25 |
| `wing_docs` | projects | `-Users-utilityserver-github-signalk-wilhelmsk-docs` | 6 | +1 | 6.8 MB | 2026-05-25 … 05-26 |
| `wing_docs` | projects | `-Users-utilityserver-github-wilhelm-docs-ralph` | 11 | +4 | 3.3 MB | 2026-05-24 |
| `wing_contexts` | projects | `-Users-utilityserver-github-claude-contexts` | 6 | +2 | 4.8 MB | 2026-05-25 … 05-30 |
| `wing_pivac` | projects | `-Users-utilityserver-github-pivac` | 4 | 0 | 3.0 MB | 2026-05-07 … 05-08 |
| `wing_pivac` | incoming | `-home-pi-github-pivac` | 1 | 0 | 0.7 MB | 2026-05-25 |
| `(other)` | projects | `-Users-utilityserver-github-arch-as-code` | 2 | +3 | 4.0 MB | 2026-05-03 … 05-29 |
| `(other)` | projects | `-Users-utilityserver-github-nas-cleanup` | 4 | +1 | 10.5 MB | 2026-05-06 … 05-09 |
| `(other)` | projects | `-Users-utilityserver-github-nas-cleanup-post-migration` | 22 | +20 | 10.3 MB | 2026-05-05 |
| `(other)` | projects | `-Users-utilityserver-github` (bare repo-root cwd) | 1 | +5 | 3.8 MB | 2026-05-25 |

## Per-wing rollup (the behavioral targets)

- **`wing_bowling`** — 569 sessions / 25.1 MB. *Already analyzed* in the
  `bowling/` pass (delegated-build mode). Not re-run.
- **`wing_wilhelm`** (Task 2 target) — **10 main-thread sessions / ~20.8 MB**
  across two sources. Bulk is `projects/-Users-utilityserver-github-wilhelm`
  (9 sessions; the WilhelmSK repo, renamed locally `wilhelmsk`→`wilhelm` —
  confirmed by the rename session in the bare-`github` cwd). One additional
  MacBook-shipped session sits in `incoming/-Users-david-github-wilhelmsk`.
  **Read both.**
- **`wing_docs`** (Task 4 target) — **17 main-thread sessions / ~10.1 MB** across
  two repos: `signalk-wilhelmsk-docs` (6 sessions, attended npm-publish-prep
  work) and `wilhelm-docs-ralph` (11 sessions, a *delegated ralph build* of the
  docs — same operating mode as bowling, useful contrast for the synthesis).
- **`wing_contexts`** (Task 3 target) — **6 sessions / 4.8 MB**, the genuine
  claude-contexts infrastructure work. Smallest of the three target wings but
  well above the 50 KB floor. (Baseline claimed ~zero interrupts/diagnostics
  here; Task 3 tests that against raw transcripts.)

## Exclusions (meta / self-analysis — do not analyze)

Per the iteration-2 conventions and the P3 mining patch, sessions whose subject
*is* this MemPalace analysis are excluded so the analysis doesn't mine itself:

| Source | Path prefix | Sessions | Size | Why excluded |
|--------|-------------|---------:|-----:|--------------|
| projects | `-Users-utilityserver-github-claude-contexts-mempalace-analysis` | 9 | 2.7 MB | meta — the analysis project itself |
| projects | `-Users-utilityserver-github-claude-contexts-mempalace-analysis-iteration-2` | 1 | 0.9 MB | meta — this ralph run |
| incoming | `-Users-david-github-claude-contexts` | 2 | 2.7 MB | meta — the analysis *genesis* convo ("analyze the content of my mempalace database … facet the data") |

## Flags for downstream tasks

1. **wing_wilhelm path is non-obvious.** Its transcripts live under
   `…/github/wilhelm` (the locally-renamed repo), *not* a dir literally named
   `wilhelmsk`. Task 2 must point its extractor at
   `~/.claude/projects/-Users-utilityserver-github-wilhelm/` **plus**
   `~/.mempalace/incoming/-Users-david-github-wilhelmsk/`.
2. **wing_wilhelm framing nuance.** Baseline described wing_wilhelm as "iOS/UI"
   work, but the Mini transcripts are largely SignalK-plugin / server-side
   (first user msg: *"how do you uninstall a plugin from skserver?"*). The pure
   iOS-app session is the single MacBook-shipped one in `incoming`. Task 2's
   theme grouping should expect plugin/integration work, not just UI.
3. **wing_contexts name collision** (carried from HANDOFF.md): the shortened
   `wing_contexts` (drawers) won't merge with a future full-name
   `wing_claude_contexts`. Irrelevant to raw-transcript analysis (this task keys
   on filesystem paths, not drawer wing labels) — noted only so a palace query
   in a later task isn't surprised by both names.
4. **Mode mix inside wing_docs.** `wilhelm-docs-ralph` is delegated-build mode;
   `signalk-wilhelmsk-docs` is attended. Keep them separable so the synthesis
   (Task 5 §3, "bowling delta") can compare delegated vs attended within one wing.
5. **`(other)` wings are out of scope** for Tasks 2–4 (not in the baseline
   behavioral set) but are inventoried for completeness; `nas-cleanup*` and
   `arch-as-code` are sizeable and could seed a future iteration if desired.

## Bottom line

All three iteration-2 target wings — **wilhelm, docs, contexts** — have raw
`.jsonl` transcripts present on the Mini, each comfortably above the 50 KB
floor, so Tasks 2–4 are all runnable. Concrete enumerated paths are in the table
above; the only gotcha is the wilhelm rename (flag 1).
</content>
</invoke>
