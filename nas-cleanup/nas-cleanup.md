# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup{,_2}/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/github/nas-cleanup/nas_*.sh` on the Mac. New NAS (DS225+, 2×4TB RAID1) on hand. Strategy shifted 2026-04-29: SSDs become the read source for the curated-layout build on DS225+, with DS1512+ used only as a final cross-check, not as a primary copy source.

## Current State

**Phases 1–10 complete; Phase 11d in progress** (2026-05-06). Curated layout is **live at `/volume1/snashome/{music,photos,movies,documents,david,mmc}`** (~1.11 TB):

```
music/      64 GB
photos/    115 GB
movies/    206 GB
documents/  38 GB  (Phase 6 26 GB + Phase 11d fallthrough fetch +12 GB)
david/     159 GB  (Phase 4b 82 GB + Phase 7 .bw/misc/app-data 77 GB)
mmc/       531 GB  (Phase 7 misc 391 GB + Phase 11d Library +140 GB)
```

**Phase 10 promote** completed in 8 seconds (2026-05-06): `NAS_SSH_USER=root ./promote_staging.sh --apply --yes` → btrfs snapshot + 6 atomic same-volume mvs. Pre-promote rollback snapshot at `/volume1/.snapshots/volume1-pre-promote-20260506-1330` (Subvolume ID 261), kept until Phase 11e sign-off.

**Phase 11d gap-fill** is partial. Bypassed the script's per-file design (619k SSH connections / multi-day) for two batched SSH-mode rsyncs per Library tree. `users/mmc/Library` complete (62.8 GB / 376k files in 1h1m). `users/mmc_OldUserFiles/Library` partial — stuck on TurboTax 2012 download archive containing an Xcode bundle with `XCContentsDir` dir↔symlink replacement conflict; needs `--exclude='Application Support/TurboTax*'` to resume. `nasadmin@DS225+ → root@DS1512+` SSH key installed during this session.

**Fall-through audit + recovery** (2026-05-06): user noticed `david/demi/*.jpg` (6 images) didn't reach the curated layout because Phase 1 classified the dir as `video` (one .mp4 inside) and Phase 5 only takes video files. Bulk-fix recovered +12 GB across 62 documents-classified rows (SPGI screenshots/diagrams +8 GB, Real_Estate, etc.). Comprehensive audit confirmed no other silent data loss outside intentional drops (Phase 3 lowbitrate filter, AppleDouble exclusion, `rsync/` never-backed-up, iPhoto migrated library duplicates collapsed by SHA-256).

**8 PRs merged this session** (PR-#29 fallout + Phase 7b bug discoveries): #31 (docs scan UTF-8 crash), #32–34 (Phase 7b: dotfile mangling, dst collisions, symlink loop), #35–36 (promote validator + --yes flag), #37–38 (reconcile snashome paths).

## Open PRs (small, post-discovery fixes; not blocking)
- **#27** — inventory: sanitize newlines+pipes from markdown table cells
- **#28** — phase 3/4/6/7: use legacy rsync progress flags

## Next Steps

1. **Resume `users/mmc_OldUserFiles/Library` fetch** with `--exclude='Application Support/TurboTax*'` to skip the Xcode-bundle conflict.
2. (Optional) **Music lowbitrate review** — `cleanup_music_lowbitrate_orphan_albums.md` has 700 albums classified cd-rip/mixed/download. Top picks: Beatles compilations, Tom Waits — Mule Variations, NIN — The Fragile, Vivaldi Four Seasons. Re-run `music_curate.sh --phase lowbitrate` to keep marked albums.
3. (Optional) **`old_fileserver_stuff/public` selective fetch** — 40 GB / 15k files mostly samba source code + Windows installers; 76 real jpgs inside.
4. **Re-run reconcile** after gap-fill completes (current report is pre-fetch snapshot; everything just fetched still appears as "missing").
5. **Phase 11e — Post-verify snapshot**: `post_verify_snapshot.sh` releases pre-promote snapshot, takes `volume1-archive-baseline-20260506`, configures DSM Snapshot Replication weekly with 4-week retention.
6. **Post-promote followup** (manual, per `cleanup_post_promote_steps.md`): re-enable DSM indexing for the 6 curated dirs, re-apply user perms (`chown -R david:dglc .../{music,photos,movies,documents,david}`, `chown -R mmc:dglc .../mmc`, `chmod -R 770/750`).
7. After Phase 11e + sign-off: DS1512+ decommissioning (user-paced).
