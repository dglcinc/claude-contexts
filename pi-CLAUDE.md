# Global Context — Raspberry Pi

This file lives at `~/CLAUDE.md` on the Pi, providing Pi-specific context on top of `~/.claude/CLAUDE.md` (global rules via `global.md`). Claude Code reads it automatically from the home directory when working in any subdirectory.

To install as a symlink (run once, or via `setup.sh`):
```bash
ln -sf ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
```

## This Machine

- Host: Raspberry Pi at `10.0.0.82` (local), `68lookout.dglc.com` (external)
- User: `pi`
- GitHub directory: `~/github/`
- Python venv for pivac: `~/pivac-venv/` — always activate before running pivac scripts
- Storage: 128GB SD card (swapped 2026-04-19); ~42 MB/s buffered read, 60GB free
- Swap: 1 GB (`CONF_SWAPSIZE=1024` in `/etc/dphys-swapfile`, file at `/var/swap`)
- journald: persistent, capped at 200 MB. Raspberry Pi OS ships `/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` which forces `Storage=volatile` (logs in RAM only, lost on reboot). We override it with `/etc/systemd/journald.conf.d/50-persistent.conf` setting `Storage=persistent` and `SystemMaxUse=200M`. Without that override, post-mortem diagnosis of any hang is impossible because tmpfs is wiped on the power-cycle.
- rsyslog: installed as a parallel log sink writing `/var/log/syslog`, `/var/log/kern.log`, `/var/log/auth.log`. Belt-and-braces backup in case journald wedges again like it did from Mar 22 to May 7, 2026.
- xterm font: FiraCode Nerd Font Mono 11pt (installed to `~/.local/share/fonts/`; configured in `~/.Xresources`)
- VNC mouse cursor: Raspberry Pi OS ships `/etc/xdg/lxsession/rpd-x/desktop.conf` with `sGtk/CursorThemeName=PiXtrix`, but `/usr/share/icons/PiXtrix/` is **not actually installed** on this Pi. That makes X fall back to a software cursor, which RealVNC encodes as a black bounding box when viewed via Jump Desktop. Fixed in three layers (all required, since `~/.Xresources` alone is overridden by LXSession startup): `~/.xsessionrc` exports `XCURSOR_THEME=Adwaita` and `XCURSOR_SIZE=24`, `~/.config/lxsession/rpd-x/desktop.conf` overrides `sGtk/CursorThemeName=Adwaita`, and `~/.Xresources` sets `Xcursor.theme: Adwaita`. A logout/login (or reboot) is required for already-running apps to pick up the change.
- Kernel quirk: RPi kernel package carries a `~bookworm` build label (e.g. `1:6.12.62-1+rpt1~bookworm`) even though userland is Debian trixie. This appears in `platform.version()` and pip install logs — it is cosmetic and not a misconfiguration.

## Projects on This Pi

- `~/github/pivac` — HVAC/home monitoring daemon (main project)
- `~/github/claude-contexts` — Global Claude context files (keep pulled)

The Pi also hosts nginx TLS termination for `mlb.dglc.com`, proxying to the Bowling League Tracker app on the Mac Mini (`10.0.0.84:5001`). Config: `/etc/nginx/sites-available/mlb.dglc.com`. The bowling app and its database live on the Mac Mini — the Pi is proxy-only for this service.

## Keeping Context in Sync

Context is synchronized through GitHub. Since `~/CLAUDE.md` and `~/.claude/CLAUDE.md` are symlinks into the claude-contexts repo, a `git pull` there automatically updates both. Pull claude-contexts at the start of each session (the `/set-context` skill does this).

Update CLAUDE.md files when:
- New or changed systemd service → update `pivac/CLAUDE.md` Active Services table
- nginx config changes → update `pivac/CLAUDE.md` Remote Access and Key File Locations
- New hardware or device → update `pivac/CLAUDE.md`
- Pi hardware changes (SD card swap, IP change) → update This Machine section here

## Skills

Use `/set-context <project>` to load full project context at session start. Use `/save-context` before finishing.

## Current Work

- **pivac Emporia setup complete** (PR #17 merged 2026-03-22): `pivac-emporia.service` is installed, enabled, and running. All PyEmVue API compatibility issues fixed. No outstanding Emporia work.
- **pivac Sentry setup complete** (PRs #28–#32 merged 2026-03-23, #34–#35 merged 2026-03-24/25): `pivac-sentry.service` is installed, enabled, and running. Grafana panels "Sentry Boiler Values" and "Sentry Boiler Status" are working. PR #34 replaced `errorCode` SK path with semantic `status` string. PR #35 changed DHW label from `"DHW"` to `"dh2o"` (WilhelmSK rendering fix). Status values: `"Idle"` | `"Call"` | `"Run"` | `"dh2o"` | error code. No outstanding Sentry work.
- **Grafana power panel circuits** (PR #33 merged 2026-03-24, PR #36 merged 2026-03-26): Apartment Power panel includes air_cond, furnace, garage_entry_basement, kit_plugs_6, kit_plugs_14, trophy_a, trophy_b. House Power panel includes wall_oven, bosch_bova. Dashboard refresh slowed to 30s (PR #37 merged 2026-03-26) to prevent SQLite lock contention under concurrent query load. No outstanding Grafana work.
- **pivac architecture diagram** (PR #38 merged 2026-03-28): Added Mermaid architecture diagram to README showing data flow from sensors through pivac modules, Signal K, InfluxDB, and Grafana. No outstanding work.
- **bowling-league-tracker** (mlb.dglc.com, app on Mac Mini `10.0.0.84`): 2025-2026 season fully entered (22 regular + 4 post-season tournament weeks). 2026-2027 season roster and schedule seeded. No open PRs. Pi hosts nginx reverse proxy only — app and DB are on the Mac Mini (`~/bowling-data/league.db`). No outstanding Pi-side work.
- **SD card swap** (2026-04-19): Upgraded to 128GB card. Partition auto-expanded to fill card (~117GB, 60GB free). FiraCode Nerd Font Mono installed for xterm Unicode symbol rendering.
- **Pi hang and journald fix** (2026-05-07): Pi hung at 14:23 EDT, 4½ days into uptime; recovered via power-cycle. Root cause unknown — diagnosis was impossible because Raspberry Pi OS's `40-rpi-volatile-storage.conf` drop-in had silently switched journald to volatile mode, so all logs were in `/run` (tmpfs) and lost on the power-cycle. The orphaned `/var/log/journal/` data from before the switch (Mar 22) was archived to `/var/log/journal-broken-2026-05-07/`. Persistent journal is now restored via `/etc/systemd/journald.conf.d/50-persistent.conf` (200 MB cap), and rsyslog is installed as a parallel log sink. Next hang should leave forensic evidence.
