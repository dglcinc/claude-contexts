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

## Architecture reminders

Palace lives on the **Mac Mini**, reached over the SSH MCP wrapper; it aggregates mining
from multiple machines (MacBook `/Users/david/...`, Pi `/home/pi/...`, utilityserver).
Two layers: semantic-search **drawers** (populated by mining) and the **KG triple** layer
(populated only by explicit `mempalace_kg_add`, e.g. in `/save-context` step 8.5 — mining
does NOT write triples). Not auto-loaded each session; query on demand with
`mempalace_search` (prose) / `mempalace_kg_query` (entity facts).
