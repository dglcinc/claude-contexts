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
- Remote desktop: **Jump Desktop on Mac → xrdp on the Pi (port 3389) is the canonical path**. RealVNC was tried first but Jump Desktop's built-in VNC viewer only speaks RFB 3.3, which has no security type compatible with RealVNC Server's defaults — connection attempts fail with `No configured security type is supported by 3.3 VNC Viewer`. The RealVNC service is left running on port 5900 in case a different VNC client (e.g. RealVNC Viewer for Mac) is ever needed, but the everyday path is RDP.
- Mouse cursor (the "black bounding box" symptom): Raspberry Pi OS ships `/etc/xdg/lxsession/rpd-x/desktop.conf` with `sGtk/CursorThemeName=PiXtrix`, but `/usr/share/icons/PiXtrix/` is not actually installed. X falls back to a software cursor that remote viewers render as a black box. Fixed via three layers — only `~/.xsessionrc` is strictly required for the xrdp path (xrdp's `startwm.sh` sources `/etc/X11/Xsession`, which sources `~/.xsessionrc` and exports `XCURSOR_THEME=Adwaita` / `XCURSOR_SIZE=24` into the `:10` session). The other two layers (`~/.config/lxsession/rpd-x/desktop.conf` overriding `sGtk/CursorThemeName=Adwaita`, and `~/.Xresources` setting `Xcursor.theme: Adwaita`) are belt-and-braces for the physical LXDE session and the RealVNC `:0` path. A logout/login (or reboot) is required for already-running apps to pick up the change.
- xrdp known noise: `/etc/xrdp/xrdp.ini` has `new_cursors=false` (default), but xrdp still logs `Send pointer: client does not support new cursors. The only valid bpp is 24, received 32` on every session — benign, the server falls back to a 24-bit cursor that Jump Desktop renders correctly. Also expected: a `Connecting to session` / `Connecting to chansrv` overlay at the start of every connection (and after any reconnect from Mac sleep or network blip). Both are normal xrdp behavior, not bugs to chase.
- Kernel quirk: RPi kernel package carries a `~bookworm` build label (e.g. `1:6.12.62-1+rpt1~bookworm`) even though userland is Debian trixie. This appears in `platform.version()` and pip install logs — it is cosmetic and not a misconfiguration.

## Projects on This Pi

- `~/github/pivac` — HVAC/home monitoring daemon (main project)
- `~/github/claude-contexts` — Global Claude context files (keep pulled)

The Pi also hosts nginx TLS termination for `mlb.dglc.com`, proxying to the Bowling League Tracker app on the Mac Mini (`10.0.0.84:5001`). Config: `/etc/nginx/sites-available/mlb.dglc.com`. The bowling app and its database live on the Mac Mini — the Pi is proxy-only for this service.

## Backup

The Pi backs up to LookoutNas (DS225+, `10.0.0.3`) using **RonR's `image-utils`** — rsync-based, produces a directly bootable `.img` file, supports incremental updates against an existing image, and is safe to run on a live system. Tooling is cloned to `/home/pi/github/RonR-RPi-image-utils/` (upstream `seamusdemora/RonR-RPi-image-utils`). The intended flow is monthly incrementals against an .img stored on the NAS.

**NAS share `pi-backups`** at `/volume1/pi-backups`, snapshotted via DSM (12-week retention to cover late-discovered corruption). Mounted on the Pi over NFSv4:

```
/etc/fstab:
10.0.0.3:/volume1/pi-backups  /mnt/nas-pi-backups  nfs4  noauto,vers=4.1,rw,hard,timeo=600,retrans=2,_netdev  0  0
```

`noauto` keeps boot non-blocking when the NAS is offline; mount on demand with `sudo mount /mnt/nas-pi-backups`.

**Synology NFS+ACL gotcha** (cost an hour to find): a fresh DSM share has only `group:administrators` in its ACL, with traditional unix bits set to `d---------`. The NFS export uses `no_root_squash` so the Pi's root keeps UID 0, but UID 0 is **not** a member of the NAS's `administrators` group, so the share looks empty/permission-denied to the Pi even though writes succeed. Fix on the NAS:

```
synoacltool -add /volume1/pi-backups user:root:allow:rwxpdDaARWcCo:fd--
synoacltool -enforce-inherit /volume1/pi-backups
```

After that, `sudo` operations on the Pi see the share as `drwxrwxrwx+`. Non-root Pi users (e.g. `pi`) are still blocked by the ACL — fine for backup use since image-backup runs as root.

**Architecture (planned, not yet fully running):**

| Layer | Tool | Frequency | Protects against |
|---|---|---|---|
| Hot recovery | `rpi-clone` → spare 128 GB SD in USB reader | Weekly | Card death (swap-in recovery) |
| Versioned recovery | `image-backup` → `.img` on NFS-mounted `pi-backups`, snapshotted by DSM | Monthly | Late-discovered corruption (rolls back N weeks via DSM snapshots) |
| Off-device disaster | (same — NAS is off-device) | Same | Fire/theft/flood |

The hot-recovery layer is on hold pending the SD reader + spare card purchase. The versioned-recovery layer is being bootstrapped now via a temp 1.8 TB SanDisk Extreme SSD (`/dev/sda` → ext4 → `/mnt/tempssd`) — Phase 1 (initial image-backup to local SSD) and Phase 2 (one-time rsync of the .img to the NAS) avoid the slow first-time random-write-into-NFS-loopback pattern. After bootstrap, monthly incrementals run image-backup directly against `/mnt/nas-pi-backups/pivac.img`.

**Image creation/refresh command** (run inside `tmux` over SSH; xrdp drops will SIGHUP a foreground job):
```bash
sudo systemctl stop pivac-1wire pivac-redlink pivac-gpio pivac-arduino-psi pivac-arduino-therm-psi pivac-emporia pivac-sentry signalk influxdb nginx
sudo /home/pi/github/RonR-RPi-image-utils/image-backup [-i] /path/to/pivac.img
sudo systemctl start nginx signalk influxdb pivac-1wire pivac-redlink pivac-gpio pivac-arduino-psi pivac-arduino-therm-psi pivac-emporia pivac-sentry
```
`-i` for first-time creation; omit for incremental updates against an existing image. Stopping write-heavy services (especially InfluxDB, Signal K, Grafana) before the rsync prevents per-file inconsistency in the resulting image.

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
