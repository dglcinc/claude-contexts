# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup{,_2}/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/github/nas-cleanup/nas_*.sh` on the Mac. New NAS DS225+ at **10.0.0.3** (hostname `LookoutNas`, 2×4TB RAID1). Strategy shifted 2026-04-29: SSDs became the read source for the curated-layout build on DS225+, with DS1512+ used only as a final cross-check, not a primary copy source.

## Current State

**Phases 1–11e complete** (2026-05-07). Curated layout is **live at `/volume1/snashome/{music,photos,movies,documents,david,mmc}`** (~1.09 TB):

```
music/      64 GB
photos/    115 GB
movies/    206 GB
documents/  20 GB  (Phase 6 26 GB + fallthrough +12 GB − dedup 0.18 GB − SPGI nuke 20.18 GB)
david/     159 GB  (Phase 4b 82 GB + Phase 7 77 GB)
mmc/       531 GB  (Phase 7 391 GB + Phase 11d Library +140 GB)
```

**Phase 11d gap-fill complete.** `users/mmc/Library` 62.8 GB / 376k files done 2026-05-06 in 1h1m. `users/mmc_OldUserFiles/Library` resumed 2026-05-07 with `--exclude='Application Support/TurboTax*'` (sidesteps the Xcode `XCContentsDir` dir↔symlink conflict) — finished in 7 min, transferred 0 bytes (everything was already on DS225+ from the prior partial run; the rsync just couldn't exit cleanly without the exclude).

**Documents/ post-promote dedup** (2026-05-07). User flagged the flat slug names in `documents/` as suspicious dups of structured paths in `david/`/`mmc/`. SHA-256 walk + cross-reference revealed only ~180 MB / 0.5% of `documents/` had hash-twins elsewhere — most of the slugs hold unique content (Phase 6 only took doc-extension files; Phase 7b skipped documents-classified rows; fall-through fetch dumped everything else). Action: file-level dedup deleted 10,657 hash-matched files (180 MB); 38 slugs went empty and were rmdir'd. Plus SPGI nuke per user direction (8,953 files / 20.18 GB). `documents/` 40.49 → **20.13 GB** / 129 → 90 slug dirs.

**Phase 11a–c reconcile** (2026-05-07, post-dedup). 537,080 residual gaps total — **all classified as expected**. 100% AppleDouble in library buckets (86,214 files); truly-missing decomposes into Pi backups under `snashome/rsync/` (285k, never in scope), iPhoto thumbnails + dropped edits (43k), AppleDouble (60k), iTunes filter drops (17k), `old_fileserver_stuff/public/` samba src + Windows installers (13k, declined), the SPGI just removed (8.7k), iMovie 6 `.rcproject` internals (4.7k regeneratable cache), `mmc_archive/Documents_svr/$RECYCLE.BIN/` (2.8k), corrupted-on-ssd (95). **Zero unexpected losses confirmed.** iMovie spot-check verified rendered output movies preserved in curated `movies/`.

**Phase 11e — post-verify snapshot** complete. Pre-promote snapshot released; btrfs-level baseline `/volume1/.snapshots/volume1-archive-baseline-20260507` created.

**Weekly snapshot cron live** (2026-05-07). Snapshot Replication package installed but its CLI is DR-replica-oriented — no clean way to schedule local-share snapshots via package CLI. Workaround: `/etc/cron.d/snashome-snapshot` triggers `/usr/local/bin/snashome-weekly-snapshot.sh` every Sunday 02:00. Script calls `synosharesnapshot create snashome desc=weekly-<YYYYMMDD> lock=false` (DSM-visible) and prunes non-locked snapshots older than 28 days. **Critical gotcha**: `synosharesnapshot create` defaults to `lock=true`; must pass `lock=false` explicitly or prune filter never matches. DSM-tracked pinned baseline `archive-baseline-pinned-20260507` (lock=true) created in parallel to the btrfs-level baseline. Source-controlled at `post_migration/snashome-{weekly-snapshot.sh,snapshot.cron}`.

**IP renumber** (2026-05-07). DS225+ moved from 10.0.0.179 → 10.0.0.3 during the server-room move. Bulk-replaced across 18 files in PR #40.

**Session PRs merged**: #39 (post_verify --yes + dedup tooling), #40 (IP change + snapshot cron docs).

## Open PRs (small, post-discovery fixes; not blocking)
- **#27** — inventory: sanitize newlines+pipes from markdown table cells
- **#28** — phase 3/4/6/7: use legacy rsync progress flags

## Next Steps

1. **Server-room move + dual network links** — user is finishing this now. NAS is at new IP 10.0.0.3.
2. **Verify weekly cron fires** — first scheduled run is Sunday 2026-05-10 02:00 EDT. Check `/var/log/snashome-snapshot.log` and `synosharesnapshot list snashome` after.
3. **Manual followups** (user-paced):
   - **DSM indexing**: Control Panel → Indexing Service → Indexed Folder List → add `/volume1/snashome/{music,photos,movies,documents,david,mmc}`. Initial indexing is hours; queue overnight.
   - **DS1512+ decommission**: stop rsync daemon (`pkill rsync`), power down via DSM, dispose drives at user discretion.
   - **NOT NEEDED**: per-user `chown`/`chmod`. User mounts via SMB as `nasadmin` (no longer NFS, where uid/gid mattered). SMB access is governed by DSM share permissions, not unix perms.
4. (Optional) **Music lowbitrate review** — 700 albums in `cleanup_music_lowbitrate_orphan_albums.md`. Top picks: Beatles compilations, Tom Waits — Mule Variations, NIN — The Fragile, Vivaldi Four Seasons. Re-run `music_curate.sh --phase lowbitrate`.
5. (Optional) **`old_fileserver_stuff/public/` selective fetch** — 40 GB / 15k files mostly samba src + Windows installers; 76 real jpgs inside.
