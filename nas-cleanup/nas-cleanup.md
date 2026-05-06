# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup{,_2}/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/github/nas-cleanup/nas_*.sh` on the Mac. New NAS (DS225+, 2×4TB RAID1) on hand. Strategy shifted 2026-04-29: SSDs become the read source for the curated-layout build on DS225+, with DS1512+ used only as a final cross-check, not as a primary copy source.

## Current State

**Phase 3 music place is running** (2026-05-05). Mac is rsyncing winners (post-dedup, post-comedy-filter, post-napster-filter, post-lowbitrate-default-drop) to `/volume1/snashome/staging/music/` on DS225+. Latest progress: ~39 GB cumulative at ~110 MB/s instantaneous (~165 MB/s avg). 10,346 of 18,037 audio files plus companions are scheduled to land in staging. Background task `b6dgy8p9b`, monitor `bmcxj9i3y`, log `/tmp/music-place.log`.

The plan walkthrough is **complete** (claude-contexts PR #9 merged with all 11 phases specified end-to-end and all 11 original open questions resolved). Ralph generated all 17 cleanup scripts in ~3.5 hours; PRs #7–#23 in nas-cleanup, all merged.

**Phase 1 (inventory) and Phase 2 (scaffold) are clean.** Phase 1 surfaced two real bugs (Spotlight misclassified, iMovie TAPE bytes-ratio fallback) — fixed in PR #25. Phase 2 surfaced the `nasadmin:users` group-naming gotcha — fixed in PR #26. Phase 3 surfaced two more (markdown cell newline corruption — PR #27; rsync 3.x-only flag — PR #28) and one architectural change (DSM rsync wrapper requires DSM-managed shared folders — refactored to single `snashome` shared folder in PR #29).

## Open PRs (small, all post-discovery fixes)
- **#27** — inventory: sanitize newlines+pipes from markdown table cells
- **#28** — phase 3/4/6/7: use legacy rsync progress flags
- **#29** — refactor: snashome top-level layout (one shared folder)

## Next Steps

1. **Wait for Phase 3 place to complete**, then spot-check 10 random tracks in `/volume1/snashome/staging/music/`.
2. **Merge open PRs** #27/#28/#29.
3. **Phase 4a** (photoslibrary spike) — read-only probe, pauses for iCloud-handling decision.
4. **Phase 4b** (photos curate) — largest phase by volume (674 GB).
5. **Phases 5–7** videos, documents, personal. Install ffmpeg/ffprobe before Phase 5.
6. **Phase 8** skip audit (read-only).
7. **Phase 9** anomaly review (manual + idempotent apply).
8. **Phase 10** promote — `mv staging/<X> ../<X>` within snashome shared folder (atomic).
9. **Phase 11a–e** DS1512+ verification + gap-fill + post-verify baseline snapshot + DS1512+ decommission (user-paced).
10. (Optional) Re-run Phase 3 lowbitrate sub-phase after user reviews `cleanup_music_lowbitrate_orphan_albums.md` (700 albums classified cd-rip / mixed / download). Top cd-rip picks: Beatles compilations, Tom Waits — Mule Variations, NIN — The Fragile, Vivaldi Four Seasons.
