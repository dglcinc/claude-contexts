# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/nas_*.sh` on the Mac. New NAS + disks arriving ~2026-05-04.

## Current State

Most dirs rsynced. Backup scripts have per-directory timing logs, SSH keepalive, `--partial`, `--timeout=60` (fail-fast, dropped from 600s on 2026-04-28), and a hardened metadata-graveyard exclude set (Database/Faces, Database/Versions, PubSub, Caches, Parallels Coherence dir, Parallels per-VM launcher .apps, all of `*.photoslibrary/resources`, `*.photoslibrary/Thumbnails`). Two NFC/NFD normalization-clash dirs in `mp3/iTunes/iTunes Music/` resolved in place on source and destination. Timing data confirmed timeouts come from degraded-array `readdir` stalls on directories with millions of tiny files (varied 1316s / 1649s / 5266s — keepalive issues would cluster). **Two-disk destination architecture** as of 2026-04-27: `/Volumes/ds_backup/` holds everything except mp3; `/Volumes/ds_backup_2/` holds mp3 (split into `nas_backup_mp3.sh`). New NAS DS225+ (2×4TB RAID1) on hand and ready to receive.

## Next Steps

1. **Migrate to DS225+** (two-phase plan; details in project CLAUDE.md). Both `ds_backup` and `ds_backup_2` need to migrate.
   - Phase 1: SSDs → DS225+ via direct USB plug (~400 MB/s, fastest), or LAN copy from Mac as fallback
   - Phase 2: DS1512+ → DS225+ rsync run **on the DS225+ itself**, using **rsync daemon mode** (not rsync-over-SSH) on the DS1512+ source — the old NAS's Atom CPU lacks AES-NI so SSH caps at ~30–60 MB/s; daemon mode skips encryption and unblocks gigabit. Pass `--chown=user:users` since DS1512+ UIDs won't map
2. Watch ongoing backup runs for new graveyard paths (iPhoto-format libraries `iPhoto_Library_v2`, `iPhoto_Library.migratedphotolibrary`, the recovered ones haven't been hit yet — they use `Data/`, `Previews/` instead of the modern `.photoslibrary` layout)
3. Decide on `rsync` and `www` source dirs (not currently in scripts)
4. Optional: clean ~518MB partial graveyard data on destination (regeneratable)
5. After DS225+ verified, decommission DS1512+
