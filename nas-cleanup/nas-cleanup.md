# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/nas_*.sh` on the Mac. New NAS + disks arriving ~2026-05-04.

## Current State

Most dirs rsynced. Backup scripts have per-directory timing logs, SSH keepalive, `--partial`, `--timeout=60`, and an extensive metadata-graveyard exclude set hardened across three PRs on 2026-04-28: (#1) readdir-stall + defunct-service graveyards (MobileSync/Backup, all `.app` bundles under `Application Support/`, SyncServices, plus 10 preemptively-identified defunct services like MobileMeSyncClient / Missing Sync / Yahoo! Sync / PocketMac / Front Row / AIM / iPhone Simulator / iLifeAssetManagement; CalDAV calendar caches kept narrow to preserve local `*.calendar` dirs and loose `.ics` files), (#2) defunct `Library/FileSync`, (#3) the whole `users/mmc/Library/` tree deferred to DS225+ Phase 2 (anchored exclude `/mmc/Library`) after 7+ stalls landed there. `users/david/Library` and `users/mmc_OldUserFiles/Library` still in scope. Two NFC/NFD normalization-clash dirs in `mp3/iTunes/iTunes Music/` previously resolved in place. **Two-disk destination architecture**: `/Volumes/ds_backup/` (everything except mp3) + `/Volumes/ds_backup_2/` (mp3). DS225+ (2×4TB RAID1) on hand. Sandbox config on this Mac mini and David-M2 updated to allow SSH and `/Volumes/ds_backup*` writes without `dangerouslyDisableSandbox` flag (pi has no sandbox config).

## Next Steps

1. **Re-run `nas_backup.sh`** with the now-hardened exclude set — `users/` should finally complete without stalls.
2. **Migrate to DS225+** (two-phase plan; details in project CLAUDE.md). Both `ds_backup` and `ds_backup_2` need to migrate.
   - Phase 1: SSDs → DS225+ via direct USB plug (~400 MB/s, fastest), or LAN copy from Mac as fallback
   - Phase 2: DS1512+ → DS225+ rsync run **on the DS225+ itself**, using **rsync daemon mode** on the DS1512+ source (Atom CPU lacks AES-NI so SSH caps at ~30–60 MB/s; daemon mode unblocks gigabit). Pass `--chown=user:users`. Also catches the deferred `users/mmc/Library/` tree.
3. **Post-migration cleanup** — execute the plan in `post-migration-plan.md` (this folder). Five phases on the DS225+ only: noise removal + photo dedup + music dedup + large-file inventory. SSDs stay as untouched archive. Plan is approved-but-deferred; don't start without re-confirming with user.
4. Decide on `rsync` and `www` source dirs (not currently in scripts).
5. Optional: clean ~518MB partial graveyard data on destination (regeneratable; pre-hardened-excludes leftover).
6. After DS225+ verified, decommission DS1512+.
