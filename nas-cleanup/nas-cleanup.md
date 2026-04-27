# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/nas_*.sh` on the Mac.

## Current State

Most dirs rsynced. Filename encoding issues in mp3 fixed — 0 bad-named files remain. Scripts updated (Database/Faces excluded, timeout 300s). Encoding tools on NAS at `/root/nas_fix_encoding.py`.

## Next Steps

1. Run `~/nas_backup.sh` — verify mp3 clean and catch remaining dirs
2. Decide on `rsync` and `www` dirs (not currently backed up)
3. Finish any outstanding photo library dirs via `~/nas_ofd_backup.sh`
4. Monitor destination space (was 1.3TB free)
