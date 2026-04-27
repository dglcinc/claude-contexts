# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/nas_*.sh` on the Mac. New NAS + disks arriving ~2026-05-04.

## Current State

Most dirs rsynced. Filename encoding issues in mp3 fixed — 0 bad-named files remain. Scripts updated (Database/Faces + Database/Versions excluded, timeout 300s). Large dirs (mmc, mmc_archive, david, users) still timing out — plan to rewrite `nas_backup.sh` to drill into subdirs with `--partial`, higher timeout, and retry loop (not yet implemented).

## Next Steps

1. Rewrite `nas_backup.sh` — SSH-enumerate subdirs, rsync each individually with `--partial`, 600–900s timeout, retry loop
2. Run updated script to push large dirs further
3. Decide on `rsync` and `www` dirs (not currently backed up)
4. Monitor destination space (was 1.3TB free as of 2026-04-27)
