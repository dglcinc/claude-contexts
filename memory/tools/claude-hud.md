# claude-hud

## statusLine grep `\t` workaround (GNU grep vs ugrep)

The default `/claude-hud:setup` template generates a statusLine command whose `plugin_dir` lookup ends with `grep -E '^[0-9]+\.[0-9]+\.[0-9]+\t'`. This silently fails to match anything under `/usr/bin/grep` (GNU grep 3.11) because GNU grep does **not** interpret `\t` in BRE/ERE patterns — it treats `\t` as a literal `t`.

Inside Claude Code's interactive shell `grep` is aliased to `ugrep` (which does interpret `\t`), so the same command appears to work when tested manually but fails when statusLine spawns it via `/usr/bin/grep`. Result: empty `plugin_dir`, then node fails with `Cannot find module '/<cwd>/dist/index.js'`.

**Fix:** in the generated statusLine command, replace `\t` with `[[:space:]]` (POSIX bracket class). Works under both GNU grep and ugrep. Saved version in `~/.claude/settings.json` on the Pi already uses this fix.

## Diagnostics

- `command -v grep` returns a function in Claude Code's interactive bash; run `bash -c 'type grep'` to see the real binary statusLine will use.
- The HUD config file lives at `~/.claude/plugins/claude-hud/config.json` (separate from `~/.claude/settings.json` which only holds `statusLine.command`). Edit `display.show*` flags there to toggle the optional lines (tools, agents, todos, duration, configCounts, sessionName, customLine).
- Plugin install path follows the marketplace pattern `~/.claude/plugins/cache/claude-hud/claude-hud/<version>/`.

## When to revisit

If `/claude-hud:setup` runs again on a fresh machine, expect the template to write `\t` again — re-apply the `[[:space:]]` fix, or upstream a PR to `jarrodwatts/claude-hud` against the setup skill template.
