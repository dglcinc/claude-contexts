# Global Context — Raspberry Pi

This file lives at `~/CLAUDE.md` on the Pi. Claude Code reads it automatically
from the home directory whenever you work in any subdirectory (e.g. `~/github/pivac`).

To install or update it:
```bash
cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
```

## This Machine

- Host: Raspberry Pi at `10.0.0.82` (local), `68lookout.dglc.com` (external)
- User: `pi`
- GitHub directory: `~/github/`
- Python venv for pivac: `~/pivac-venv/` — always activate before running pivac scripts

## Projects on This Pi

- `~/github/pivac` — HVAC/home monitoring daemon (main project)
- `~/github/claude-contexts` — Global Claude context files (keep pulled)

The Pi also hosts nginx TLS termination for `mlb.dglc.com`, proxying to the Bowling League Tracker app on the Mac Mini (`10.0.0.84:5001`). Config: `/etc/nginx/sites-available/mlb.dglc.com`. The bowling app and its database live on the Mac Mini — the Pi is proxy-only for this service.

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code and docs.** Always create a feature branch and open a pull request for code changes, README updates, and module documentation. Only push directly to the default branch for meta/context files (CLAUDE.md files). When in doubt, use a PR.
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Keeping Context in Sync

Claude runs on three machines: this Pi, and two Macs. Context is synchronized through GitHub repos:

- **Pi global context**: `claude-contexts/pi-CLAUDE.md` → pushed to GitHub → `~/CLAUDE.md` (local copy on Pi). After pushing updates via GitHub MCP, also update the local copy: `cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md`
- **Mac/Cowork global context**: `claude-contexts/CLAUDE.md` — read by Cowork sessions automatically; keep it pulled on each Mac
- **Project context**: Each project's `CLAUDE.md` (e.g. `pivac/CLAUDE.md`, `bowling-league-tracker/CLAUDE.md`) — pushed to their respective GitHub repos; pull on each machine to sync

**Update these files when:**
- New or changed systemd service on the Pi → update `pivac/CLAUDE.md` Active Services table and deployment restart commands; note the milestone in Current Work here
- nginx config changes (new site, new proxy target, auth) → update `pivac/CLAUDE.md` Remote Access and Key File Locations; update Projects on This Pi here if the Pi's role changes
- New hardware or device added to the Pi → update `pivac/CLAUDE.md`
- Bowling app deployment changes (new host, DB path, gunicorn config) → update `bowling-league-tracker/CLAUDE.md`
- Season rollover or significant bowling milestone → update `bowling-league-tracker/CLAUDE.md` and Current Work here
- Pi hardware changes (SD card swap, IP change, new Pi) → update This Machine section here

CLAUDE.md files always push directly to main/master (no PR needed). All other code changes use feature branches + PRs.

## Shortcuts

- **"save context"**: Update all relevant CLAUDE.md files (project and global) to reflect current state, save any unsaved facts to local memory files, and update the MEMORY.md index. Do this as if the user is about to quit and needs a future session to have a complete picture.

## Current Work

- **pivac Emporia setup complete** (PR #17 merged 2026-03-22): `pivac-emporia.service` is installed, enabled, and running. All PyEmVue API compatibility issues fixed. No outstanding Emporia work.
- **pivac Sentry setup complete** (PRs #28–#32 merged 2026-03-23, #34–#35 merged 2026-03-24/25): `pivac-sentry.service` is installed, enabled, and running. Grafana panels "Sentry Boiler Values" and "Sentry Boiler Status" are working. PR #34 replaced `errorCode` SK path with semantic `status` string. PR #35 changed DHW label from `"DHW"` to `"dh2o"` (WilhelmSK rendering fix). Status values: `"Idle"` | `"Call"` | `"Run"` | `"dh2o"` | error code. No outstanding Sentry work.
- **Grafana power panel circuits** (PR #33 merged 2026-03-24, PR #36 merged 2026-03-26): Apartment Power panel includes air_cond, furnace, garage_entry_basement, kit_plugs_6, kit_plugs_14, trophy_a, trophy_b. House Power panel includes wall_oven, bosch_bova. Dashboard refresh slowed to 30s (PR #37 merged 2026-03-26) to prevent SQLite lock contention under concurrent query load. No outstanding Grafana work.
- **bowling-league-tracker** (mlb.dglc.com, app on Mac Mini `10.0.0.84`): 2025-2026 season fully entered (22 regular + 4 post-season tournament weeks). 2026-2027 season roster and schedule seeded. No open PRs. Pi hosts nginx reverse proxy only — app and DB are on the Mac Mini (`~/bowling-data/league.db`). No outstanding Pi-side work.
