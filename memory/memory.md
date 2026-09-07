# Memory Index

Read this file at session start. Load a topic file only when relevant.

| File | Description | Last updated |
|------|-------------|--------------|
| `general.md` | Cross-project conventions; where agent credentials live | 2026-09-02 |
| `user.md` | David: profile, working style, machines (M2 fixed `10.0.0.83`), home address, Obsidian vault | 2026-07-06 |
| `reference/mountain-lakes-code.md` | Mountain Lakes NJ municipal code as a grep-indexed local KB; how to query | 2026-07-06 |
| `reference/signalk-server-architecture.md` | Architecture review of signalk-server v2.28: report path, standing liabilities, AI-PR governance | 2026-08-18 |
| `tools/claude-hud.md` | claude-hud statusLine quirks | 2026-04-28 |
| `tools/macos.md` | Hostname falls back to the gateway's reverse-DNS name; fix with `scutil` | 2026-06-16 |
| `tools/unifi.md` | UCG Ultra controller at `10.0.0.1`: API key path, integration and classic API, fixed-IP recipe, moving a fixed IP between clients | 2026-09-07 |
| `tools/gh.md` | gh and git-lfs TLS bug (rebuild with `CGO_ENABLED=0`); Pi gh token recovery from the M4 | 2026-07-03 |
| `tools/arduino-cli.md` | arduino-cli on the Pi for UNO R4 compile and flash; placeholder credentials warning | 2026-07-03 |
| `tools/ralph.md` | Ralph loop: PLAN.md checklist plus `ralph.sh` driver | 2026-05-22 |
| `tools/mempalace.md` | MemPalace hooks, palace contents, drawers versus KG triples | 2026-05-25 |
| `tools/gh-stacked-prs.md` | Squash-merging a parent auto-closes child PRs; recovery | 2026-09-01 |
| `tools/nfs.md` | D-state processes survive SIGKILL; lazy unmount; non-blocking fstab | 2026-05-08 |
| `tools/rsync.md` | rsync over NFSv4 with sparse files; `--old-args` for old servers | 2026-05-08 |
| `tools/synology.md` | DSM rsync-over-SSH workaround; NFS plus ACL recipe | 2026-05-08 |
| `tools/m365-graph.md` | M365 SMTP AUTH is off; MSAL plus Graph `sendMail` pattern | 2026-05-08 |
| `tools/signalk.md` | Signal K plugin admin: install topology, force-disable, admin JWT; proxies must forward `/skServer/` and `/plugins/` | 2026-09-06 |

## Cross-Memory Sync Rule

At session start: note the Last updated dates above; if a project MEMORY.md holds something worth promoting to a global `tools/` or `domain/` file, flag it; update this file's date after any change.
