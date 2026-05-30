# MemPalace

## How the palace gets populated (auto-mining) — 2026-05-25

The palace is **not** seeded with demo data. Everything in it is the user's own
content, ingested by mining. Verified on utilityserver: 1,970 drawers, dominated by
a `sessions` wing (1,419 — rooms `technical`/`problems`/`diary`), plus wings mined
from repos/dirs (`claude_contexts` 321, path-named wings like
`_users_david_github_wilhelmsk` 116, `_home_pi_github_pivac` 69) and targeted
`mempalace mine` runs (`wing_wilhelm`, `wing_docs`, `wing_contexts`).

**Auto-mining is driven by plugin-shipped hooks, NOT by `~/.claude/settings.json`.**
This is the key gotcha: searching settings.json for the hook finds nothing (only the
`extraKnownMarketplaces` entry). The hooks live in the plugin cache:
`~/.claude/plugins/cache/mempalace/mempalace/<ver>/hooks/hooks.json` (v3.3.6):
- **`Stop` hook** → `mempal-stop-hook.sh` (30s) — fires at the end of **every session**,
  mining that conversation into the palace.
- **`PreCompact` hook** → `mempal-precompact-hook.sh` (90s) — fires before context
  compaction, capturing the conversation before it's summarized away.

So the palace grows on its own, one drawer-batch per session. To pause it, disable/remove
the **plugin** hook (not settings.json). Behavior of the save (silent vs blocking) is
tuned via the `mempalace_hook_settings` MCP tool (`silent_save: true` = quiet direct save).

The Alice/Jordan/Riley/Max/Ben personas seen anywhere are only in the **AAAK dialect
format example** shipped in the spec — not real drawers.

## Wings & rooms are emergent labels, not created objects — 2026-05-25

There is no `create_wing`/`add_wing` anywhere — a wing is just a metadata field
stamped on each drawer. `list_wings`/`status` are a GROUP BY over the `wing` field;
a wing "exists" iff ≥1 drawer carries that label and vanishes when its last drawer is
deleted (so dedup can shrink/remove a wing). The miner derives the label at mine time
three ways: auto from source path via `normalize_wing_name(<dir/convo name>)` (→
path-shaped names like `_users_david_github_wilhelmsk`, `_home_pi_github_pivac`,
`claude_contexts`; the conversation source → `sessions`); explicit `--wing` override
(→ `wing_wilhelm`/`wing_docs`); or `config["wing"]` default. Rooms work identically
(label assigned by the room detector / AAAK halls `technical`/`problems`/`diary`).
So "hooks only add drawers" and "wings get created" are the same event.

## Compaction / dedup is MANUAL, not automatic — 2026-05-25

The hooks only ADD drawers; nothing auto-compacts, so the palace grows monotonically
and redundancy builds up (same files/conversations re-mined every session, plus
cross-machine mining shipped into `~/.mempalace/incoming/`). Dedup is a manual
maintenance op you must run yourself.

- **`dedup.py`** removes near-duplicate drawers *within the same `source_file`*
  (cosine distance < threshold; keeps the longest/richest, deletes the rest; API-free).
  In v3.3.6 it is **module-only** — `mempalace dedup` is NOT a CLI subcommand:
  `~/.local/share/uv/tools/mempalace/bin/python -m mempalace.dedup [--stats|--dry-run] [--threshold 0.15] [--wing W]`
- **`mempalace compress`** is a *different* thing (AAAK entity compression, takes
  `--config entities.json`) — not duplicate removal. Don't confuse them.
- Default threshold **0.15** = near-identical only (~85% sim). Looser `0.3`–`0.4`
  also catches paraphrased dupes (more removed, small risk of dropping distinct content).
- `--stats` over-estimates (counts large same-source groups); the **`--dry-run`**
  cosine pass gives the true removable count.
- Real run on utilityserver palace (2026-05-25, threshold 0.15): **2,004 → 1,871
  (-133, ~7%)** in ~21s. `--stats` had guessed ~656. No unique content lost — only
  redundant re-minings. Re-run periodically; heaviest reclaim is the
  `~/.mempalace/incoming/` cross-machine mining + big session transcripts.

The CLI also exposes `repair`/`repair-status` (prune corrupt) and `split` (split
oversized drawers) — likewise manual.

## Architecture reminders

Palace lives on the **Mac Mini**, reached over the SSH MCP wrapper; it aggregates mining
from multiple machines (MacBook `/Users/david/...`, Pi `/home/pi/...`, utilityserver).
Two layers: semantic-search **drawers** (populated by mining) and the **KG triple** layer
(populated only by explicit `mempalace_kg_add`, e.g. in `/save-context` step 8.5 — mining
does NOT write triples). Not auto-loaded each session; query on demand with
`mempalace_search` (prose) / `mempalace_kg_query` (entity facts).

## Local convo_miner.py patch + auto-reapply — 2026-05-30

`mempalace.convo_miner` line ~402 derives the fallback wing from
`Path(convo_dir).name`. When the convos source is Claude Code's encoded project
directory (e.g. `~/.mempalace/incoming/-Users-david-github-claude-contexts`), the
basename is the *full host filesystem path* with `/` replaced by `-`. Combined
with `normalize_wing_name` (which lowercases + replaces `-`/space with `_`), this
produced path-style wings like `_users_david_github_claude_contexts` instead of
`wing_claude_contexts`. Three of these existed before the 2026-05-30 cleanup:
`_users_david_github_wilhelmsk` (82), `_home_pi_github_pivac` (55),
`_users_david_github_claude_contexts` (53). All renamed to `wing_X` via
`mempalace_update_drawer`.

**Patch applied (Mac Mini only — MacBook/Pi are thin clients, no local install):**
`utilityserver:/Users/utilityserver/.local/share/uv/tools/mempalace/lib/python3.12/site-packages/mempalace/convo_miner.py`
— marker comment `Strip Claude Code project-dir encoding`. The patch detects the
encoding (`name.startswith("-") and "-github-" in name`), strips the host-path
prefix via `name.rsplit("-github-", 1)[1]`, and prepends `wing_`. Falls back to
the upstream behavior for non-encoded paths. Backup alongside as
`convo_miner.py.bak-YYYYMMDD-HHMMSS`.

**Reapply script:** `utilityserver:~/bin/mempalace-reapply-patch.py` — idempotent
(detects marker comment, no-op if already patched; aborts if upstream snippet
not found, indicating a real upstream change worth re-evaluating).

**Auto-reapply:** launchd user agent `com.dglc.mempalace-patch` at
`utilityserver:~/Library/LaunchAgents/com.dglc.mempalace-patch.plist`. Runs daily
at 04:00. Log: `utilityserver:~/.local/share/mempalace-patch.log`. Any
`uv tool upgrade mempalace` wipes the patch; the daily job catches it within 24h.

**Caveats:**
- Existing `wing_contexts` (from an explicit `--wing` override) won't merge with
  future `wing_claude_contexts` produced by the patched fallback. Decide later
  whether to rename one to the other or accept the divergence.
- If upstream changes the surrounding code, the reapply script's snippet match
  will fail loudly. Manual reconciliation needed at that point.
- When upstream fixes this in `normalize_wing_name` itself, remove the patch +
  this section + the launchd job + the reapply script.
