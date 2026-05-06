# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup{,_2}/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/github/nas-cleanup/nas_*.sh` on the Mac. New NAS (DS225+, 2×4TB RAID1) on hand. Strategy shifted 2026-04-29: SSDs become the read source for the curated-layout build on DS225+, with DS1512+ used only as a final cross-check, not as a primary copy source.

## Current State

**Phases 1–4 complete** (2026-05-06). 261 GB / 75,903 files now in `/volume1/snashome/staging/`:

```
music/      64 GB / 28,154 entries (Phase 3)
photos/    115 GB / 43,676 files (Phase 4b)
david/      82 GB / 4,073 files (Phase 4b non-camera-EXIF)
movies/      0  documents/  0  mmc/  0
```

**Phase 4a photoslibrary spike**: 14 libraries detected, only 4 have content (the rest are abandoned recovery shells). Combined ~126k originals across the 4 real libraries; 3,676 iCloud-only placeholders (~2.9%). User chose option (b) low-res-tag.

**Phase 4b photos curate**: 95,374 records scanned → 38,365 unique after dedup. Place dropped 5,707 orphan iPhoto edits (originals re-imported into newer Photos.app library; cross-library UUID linker can't bridge). 4,074 non-camera-EXIF lumped to `david/images/<YYYY>/`. Throughput consistent 117 MB/s on 1 GbE.

**Architecture finalized**: single `/volume1/snashome` DSM shared folder for both staging and final layout; PR #29 (snashome refactor) merged. Earlier `/volume1/staging` shared folder is now empty — user can delete via DSM Control Panel when convenient.

**All 17 build-phase scripts merged** (PRs #7–#23 plus follow-up fixes #25, #26, #29).

## Open PRs (small, post-discovery fixes; not blocking)
- **#27** — inventory: sanitize newlines+pipes from markdown table cells
- **#28** — phase 3/4/6/7: use legacy rsync progress flags

## Next Steps

1. **Spot-check** photos staging — pick 10 random files in `/volume1/snashome/staging/photos/<YYYY>/...` and verify they open as images with correct EXIF.
2. **Phase 5 videos**: install `ffmpeg` first (`brew install ffmpeg`), then run `videos_sort.sh` for capture-date-organized placement. Probably small volume.
3. **Phase 6 documents**: hash-dedup with manifest.
4. **Phase 7a/b mail + personal**: emlx→mbox conversion plus app-data/.bw/misc collection.
5. **Phase 8 skip audit**: read-only cross-tab against Phase 1 inventory.
8. **Phase 10** promote — `mv staging/<X> ../<X>` within snashome shared folder (atomic).
9. **Phase 11a–e** DS1512+ verification + gap-fill + post-verify baseline snapshot + DS1512+ decommission (user-paced).
10. (Optional) Re-run Phase 3 lowbitrate sub-phase after user reviews `cleanup_music_lowbitrate_orphan_albums.md` (700 albums classified cd-rip / mixed / download). Top cd-rip picks: Beatles compilations, Tom Waits — Mule Variations, NIN — The Fragile, Vivaldi Four Seasons.
