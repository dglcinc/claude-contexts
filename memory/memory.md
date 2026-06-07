# Memory Index

Read this file at session start. Load specific topic files only when relevant.

| File | Description | Last updated |
|------|-------------|--------------|
| `general.md` | Cross-project conventions and preferences | 2026-05-14 |
| `user.md` | David — user profile, setup, working style, machines | 2026-05-08 |
| `tools/claude-hud.md` | claude-hud statusLine setup quirks (GNU grep `\t` workaround) | 2026-04-28 |
| `tools/gh.md` | macOS Security.framework TLS bug (OSStatus -26276): rebuild gh with CGO_ENABLED=0; git-lfs hits the same bug on push, fix via per-remote `lfs.locksverify=false` | 2026-04-29 |
| `tools/ralph.md` | Ralph loop — PLAN.md checklist + ralph.sh driver (~/github/claude-contexts/ralph.sh); each iteration spawns fresh sclaude for one task | 2026-05-22 |
| `tools/mempalace.md` | MemPalace auto-populates via plugin-shipped Stop/PreCompact hooks (NOT settings.json); palace = mined own content, not seed data; drawers vs KG-triple layers | 2026-05-25 |
| `tools/gh-stacked-prs.md` | Squash-merging parent w/ --delete-branch auto-closes child PRs; reopen blocked. Cherry-pick to recover. | 2026-05-08 |
| `tools/nfs.md` | D-state stuck procs survive SIGKILL; lazy-unmount + reboot to recover. fstab pattern for non-blocking boot. | 2026-05-08 |
| `tools/rsync.md` | rsync over NFSv4 starves on large sparse files (use cat\|ssh\|dd or cp instead); rsync 3.4 → older server needs `--old-args`. | 2026-05-08 |
| `tools/synology.md` | DSM rsync-over-SSH gate: code 43 even with toggle on; nasadmin+`--rsync-path='sudo rsync'` is the workaround. NFS+ACL recipe included. | 2026-05-08 |
| `tools/m365-graph.md` | Modern M365 tenants disable SMTP AUTH — use MSAL + Graph `sendMail` with client-credentials. Reusable Azure app pattern. | 2026-05-08 |
| `tools/signalk.md` | SignalK-server plugin admin: bundled-vs-`~/.signalk` install topology, force-disable un-toggleable built-ins via `plugin-config-data`, mint an admin JWT for `/skServer/plugins`, read in-app-browser 404s from the access log | 2026-06-07 |

## Cross-Memory Sync Rule

At session start, after reading this file:
1. Note the Last updated dates in the table above
2. Check projects.md (if it exists) for active project MEMORY.md paths
3. If any project MEMORY.md has content worth promoting to a global tools/ or domain/ file, flag it
4. Update the Last updated date on this file after any changes

## Domain Knowledge Lifecycle

1. Staging — knowledge accumulates in domain/{name}/
2. Promotion — enough knowledge exists to package as a plugin/skill
3. Pointer — after promotion, the memory file becomes a pointer to the plugin
