# Post-DS225+ Migration Cleanup

## Context

The cleanup builds a curated content archive on the DS225+ by **reading from the SSDs** (`/Volumes/ds_backup{,_2}/`) and writing the new layout to the DS225+ internal volume. The DS1512+ is **not** a source — it's used at the end as a **verification cross-check** to catch anything the SSD copy might have missed.

**Strategy shift (2026-04-29)**: the original plan migrated the messy source tree onto DS225+ first (NAS-to-NAS rsync) and then cleaned in place. The revised plan skips the messy intermediate copy entirely. SSDs are the read source; DS225+ gets the curated output directly. Avoids stressing the degraded DS1512+ for a second full read pass.

**Architecture adjustment (2026-05-04)**: the SSDs are APFS-formatted. DSM 7 has no reliable APFS mount support, so plugging the SSDs into DS225+ via USB isn't viable. Cleanup orchestration moves to the Mac: it reads SSDs locally at ~400 MB/s and writes output to DS225+ via **rsync over SSH** (DS225+ has AES-NI, so SSH isn't a bottleneck the way it was on the DS1512+ Atom). Network mounts (SMB/NFS) are avoided — metadata-heavy operations (`open`/`stat`/`close` per file) get bogged down on RPC latency, while rsync batches efficiently and gives atomic transfer + resume semantics. Phase 11 gap-fill from DS1512+ → DS225+ was already network-rsync; that part is unchanged.

The user explicitly does **not** need to restore the data to a Mac, phone, or iPhoto/Photos.app — this is a preserved-data archive (photos, music, video, documents). That assumption simplifies several decisions: it's OK to break a `.photoslibrary` bundle's internal references because we'll never reopen it.

**Where things live:**
- **Source (read-only):** SSDs `/Volumes/ds_backup/` + `/Volumes/ds_backup_2/`, mounted on the Mac (APFS — stays on Mac)
- **Cleanup orchestration:** runs on the Mac. Local SSD read, network write to DS225+ via rsync over SSH.
- **Destination (write):** the curated layout on the DS225+ internal volume — built under `/volume1/staging/` first, promoted to `/volume1/{music,...}` at Phase 10
- **DS1512+:** stays online for verification only; not a source for the build

All scripts are dry-run by default with explicit `--apply` to mutate. **Cleanup never deletes from the SSDs and never modifies the curated layout dirs once built** — see Hard Guards below. Mutating commands on DS225+ (mkdir, mv, rm) execute via `ssh` from the Mac.

**Source scope (on the SSDs):** the full backup as it stood when migration began — `snashome/{david,mmc,mmc_archive,OldPhotoDirectories,mp3,old_fileserver_stuff,users}` plus the deferred trees on DS1512+ that get gap-filled in Phase 11. NAS-specific directories (DSM internals like `@appstore`, `@database`, etc.) are not preserved. `www/` is **deferred** — old static-web content not relevant to the curated archive; revisit only if Phase 9 anomaly review surfaces something interesting there.

## Final target layout

The cleanup produces a new top-level layout on the DS225+:

```
/volume1/
  music/                           — Artist/Album/NN Title.ext
  photos/                          — date- and album-organized originals + edits
  movies/
    iMovie/<project>/              — preserved iMovie project bundles
    FinalCut/<project>/            — preserved Final Cut project bundles
    other/<source-context>/        — standalone videos
  documents/<source-context>/      — preserved folder structure
  david/
    .bw/                           — segregated, deduped
    images/                        — non-camera (web-downloaded) photos
    app-data/                      — preserved application context (per-app)
    [other personal content the rules don't cover]
  mmc/
    [same shape as david/]
  staging/                         — work dir during cleanup; removed at end
```

User dirs are `david/` and `mmc/` — match the source tree's naming. Any content tagged "maureen" anywhere (folder names, metadata) is treated as `mmc` content for dedup purposes — same person, historical naming variation.

## Hard guards

Every cleanup script enforces these guards. A guard violation aborts the run.

1. **Never write under SSD source paths.** `/Volumes/ds_backup` and `/Volumes/ds_backup_2` are read-only sources — cleanup never deletes or modifies files there. The SSDs remain a third-copy archive forever.
2. **Never delete or modify the curated layout dirs.** `/volume1/{music,photos,movies,documents,david,mmc}` on DS225+ are write-once-by-the-cleanup-build, then read-only. Subsequent reruns of any phase compare against existing content but never overwrite or delete.
3. **Destructive operations refuse to run** unless given an explicit `--apply` AND a path argument under the expected source root for that phase. No defaults that could land somewhere unexpected.
4. **Staging-only deletes.** Anything destructive runs against `/volume1/staging/` during build; the curated layout is constructed there and *moved* into final position only after verification.

## Phases

All phases produce CSV/Markdown reports on dry run. `--apply` performs the destructive action. Each script is idempotent and re-runnable.

### Phase 1 — Inventory and classification

**Why:** before touching anything, produce a single classification map of every top-level subtree on the SSD source. The user reviews the map and approves before any phase ≥ 3 runs.

**Actions:**
- Walk both SSD source paths `/Volumes/ds_backup/` and `/Volumes/ds_backup_2/` in a single pass; emit one merged inventory tagged with each row's SSD origin.
- Walk to **depth 3** from each SSD root, with an **escape hatch**: at depth 3, if a dir is unclassifiable but contains known structural markers (`*.photoslibrary`, `*.fcpbundle`, `Masters/`+`Database/` siblings, `Pictures/`, `Music/`, etc.), descend further until classification resolves. Cap descent at depth 6 to avoid runaway walks.
- For each classified dir, classify by heuristic:
  - **photo-library**: contains `*.photoslibrary`, `*.migratedphotolibrary`, `iPhoto Library*`, or `Masters/`+`Database/` siblings
  - **music**: dominated by audio files — `.mp3`/`.m4a`/`.m4p`/`.m4b`/`.flac`/`.alac`/`.aac`/`.ogg`/`.opus`/`.aif`/`.aiff`/`.wav`/`.wma`/`.ape`. **Sticky classification**: a dir classified as `music` has ALL its contents (including non-audio files like `.mp4` music videos, `.pdf` liner notes, `.jpg` cover art, `.txt` track listings) treated as part of that album bundle and routed to the music destination at Phase 3 — they travel with the album, not separately.
  - **video**: predominantly `.mov`/`.mp4`/`.avi`/`.dv`/`.m4v` AND not classified as `music` (music videos that live inside a music dir stay with that album per the sticky rule above)
  - **video-project**: `*.iMovieProject`, `*.fcpbundle`, `*.imovielibrary`
  - **documents**: predominantly `.pdf`/`.doc{,x}`/`.xls{,x}`/`.ppt{,x}`/`.txt`/`.rtf`/`.pages`/`.numbers`/`.key`/`.md`/`.odt`. (iWork bundles like `.pages` are macOS package directories — classifier treats them as files, does not descend.)
  - **app-install**: `.app` bundles or installer pkg/dmg trees outside system Applications
  - **download-dump**: dirs literally named `Downloads` or `My Downloads`, or containing only browser-cache-shaped content
  - **game-install**: known patterns (Minecraft `*.jar` + `versions/`, Unreal Tournament `Engine/`, Steam `steamapps/`, etc.)
  - **app-data**: known per-app dirs (Skype chat DBs, GarageBand projects, OmniFocus, Quicken, TurboTax, 1Password, AddressBook, Mail Maildir/, etc.)
  - **bw**: any path matching `**/.bw/**`
  - **nas-internal**: `@appstore`, `@database`, `#recycle`, etc.
  - **unknown**: everything else (Phase 9 handles these)
- Symlinks: do not follow (record the link target in the inventory but classify by the link itself, not its destination — avoids double-counting and infinite-loop risk).
- Output: `cleanup_inventory.md` — Markdown table with one row per classified subtree. Columns: `path`, `ssd`, `depth`, `classification`, `size`, `file_count`, `modal_extension`, `sample_filenames` (5 random), `[ ] approve` checkbox.
- **No mutation.** User reviews the map and either approves or annotates each row. Subsequent phases consume this map. When in doubt, the classifier marks `unknown` and lets Phase 9 catch it — false `unknown` is cheaper than misclassification.

**Critical files:**
- `post_migration/inventory.sh` (new) — orchestrator
- `post_migration/inventory.py` (new) — classifier

### Phase 2 — Staging-dir scaffold

**Why:** create the empty curated layout under `/volume1/staging/{music,photos,movies,documents,david,mmc}` with the right ownership. Everything is built under `staging/` and only promoted to its final position at Phase 10. This keeps Hard Guard #2 trivial: `/volume1/{music,...}` doesn't exist as a target during the build, so scripts can't accidentally write to the final layout.

**Actions:**
- `mkdir -p /volume1/staging/{music,photos,movies,documents,david,mmc}`
- `chown -R nasadmin:nasadmin /volume1/staging` — single owner during the build. UID mapping from DS1512+ is not preserved.
- Idempotent: re-running the script reapplies ownership cleanly even if some dirs already exist.
- Staging is visible at `/volume1/staging/` (no hiding) — single-user operation, easier to debug, Phase 10 removes it anyway.

**Post-build re-permissioning (deferred, optional):** once the curated layout is promoted in Phase 10, ownership/perms can be tightened per-dir without rebuilding — `chown -R` on Synology is metadata-only, takes minutes for a TB-scale tree. Suggested later: `david:dglc 770` for the shared dirs (`music`, `photos`, `movies`, `documents`), `david:dglc 750` for `david/`, `mmc:dglc 750` for `mmc/`. Not blocking; can wait until SMB browsing is set up.

**Critical files:**
- `post_migration/scaffold.sh` (new) — trivial; could be inlined

### Phase 3 — Music: dedup, organize, comedy filter, low-bitrate review

**Why:** ~792 GB of iTunes media has heavy internal duplication and now-unwanted content. The user's rules: keep CD rips at higher bitrate, organize Artist/Album/Track, drop comedy artists, optionally drop ≤128 kbps survivors.

**Actions:**
1. **Find** all audio files under inventoried `music` sources: `.mp3`, `.m4a`, `.m4p`, `.m4b`, `.flac`, `.alac`, `.aac`, `.ogg`, `.opus`, `.aif`, `.aiff`, `.wav`, `.wma`, `.ape`. Also collect **non-audio companion files** in those same dirs (`.mp4` music videos, `.pdf` liner notes, `.jpg`/`.png` cover art, `.txt`/`.nfo` track listings) — they travel with the album per the Phase 1 sticky-classification rule.
2. **Drop without review:** iTunes library metadata files (`.itl`, `.xml`, `.musiclibrary` bundles) and all playlists (any `.m3u`/`.m3u8`/`.pls` plus the playlist data inside `.itl`). Useless without iTunes; user does not need them preserved.
3. **Read tags** (artist, album artist, album, title, track #, genre, bitrate, codec) — Python `mutagen`. Filename/path fallback for missing tags. **Local tags only** — no MusicBrainz / AcoustID lookups.
4. **Group by (album artist || artist, album, title)** — case-insensitive, normalized. Album Artist takes precedence over Artist for grouping AND for directory placement, so compilation albums don't fragment across the tree.
5. **Dedup within group** — preference order: **lossless** (`.flac`/`.alac`/`.ape`/`.wav`) > **lossy ≥192 kbps** > **lossy <192 kbps**. Within a tier, highest bitrate wins; final tiebreak = larger file size.
6. **Napster-source filter** — flag any file with `nappy` or `napster` (case-insensitive) anywhere in its source path or any tag (artist/album/title/genre/comment/etc.) for user review. Emit `cleanup_music_napster.md`. User marks each `[ ] keep / [X] drop`. Default action on `--apply` = drop. These were imported from Napster in the early 2000s; user keeps only the ones not currently available on streaming.
7. **Comedy filter** — auto-pre-mark using genre tag: any track whose genre matches `Comedy`/`Spoken Word`/`Stand-Up` (case-insensitive) counts as a comedy track. For each artist, if >50% of their tracks are comedy-tagged, the artist is auto-checked `[X] comedy`. Emit `cleanup_music_artists.md` listing every distinct artist with the auto-mark and a track count. User reviews and flips overrides. `--apply` removes everything still marked comedy.
8. **Low-bitrate handling:**
   - Tracks **<128 kbps** (strictly less than) → dropped automatically without review. Default-low-quality early-2000s rips, generally available better elsewhere.
   - Tracks **=128 kbps** → emit `cleanup_music_lowbitrate.md` for user review. User marks `[ ] keep / [X] drop` (default drop). Keep only what's not on streaming services.
9. **Place winners**:
   - Audio tracks → `music/<Album Artist>/<Album>/<NN Title>.<ext>` (track number zero-padded; missing track # → omit prefix; falls back to Artist if no Album Artist tag)
   - Companion files → `music/<Album Artist>/<Album>/<original-filename>` (original name preserved; no track-number prefix)
10. **Sources unchanged** — build is copy-only from SSDs to DS225+. SSDs are never modified per Hard Guard #1. User can clean up SSD sources later, separately, if desired.

**Filename normalization:**
- Strip iTunes "Track 1" / "Track 2" duplicate-import suffixes (already seen in `iTunes Music/A Paris/` — see CLAUDE.md normalization-clashes note)
- Resolve NFC/NFD normalization to NFC
- Sanitize filesystem-illegal chars
- Preserve leading numbers that are part of the actual title (e.g. `01-01-bonus.mp3` keeps both numbers — only strip the iTunes-generated " N" / " Track N" suffixes, not legitimate numeric prefixes)

**Critical files:**
- `post_migration/music_curate.sh` (new) — orchestrator with `--phase tag-scan|dedup|napster|comedy|lowbitrate|place`
- `post_migration/music_curate.py` (new) — does the work

**Output reports for user review (all dry-run, all checkbox-driven):**
- `cleanup_music_napster.md` — Napster-tagged files, default drop, user can flip to keep.
- `cleanup_music_artists.md` — distinct artists with auto-marked comedy column, user reviews.
- `cleanup_music_lowbitrate.md` — 128 kbps tracks (only) for keep/drop decision.

**Verification:**
- SSDs are unchanged after run (per Hard Guard #1 — verified by `find /Volumes/ds_backup* -newer <run-start-marker>` returning empty for files under inventoried music sources).
- Spot-check 10 random tracks at `staging/music/<Album Artist>/<Album>/...` — playable, tags intact.
- Track count at `staging/music/` matches the dedup CSV's "kept" count.
- No `.itl`/`.xml`/`.musiclibrary`/playlist files anywhere under `staging/music/`.

### Phase 4 — Photos: extract originals + edits, dedup, organize

**Why:** 674 GB across three overlapping `.photoslibrary`/iPhoto libraries plus loose photo dirs. User wants originals + edits, no application exhaust, organized by date and album where possible.

**Actions:**

1. **Spike first** (`photoslibrary_inspect.py`) — run-once probe before any extraction. For each detected library, sample structure and report to `cleanup_photos_spike.md`:
   - Format detected (iPhoto / Photos.app / migrated)
   - Originals path layout (dated `Masters/YYYY/MM/DD/` vs hash-bucketed `originals/<HH>/<UUID>`)
   - Edits storage (iPhoto: `Modified/<path>.jpg` real files; Photos.app: rendered files under `resources/renders/<HH>/` paired with `.AAE` adjustment plists or DB rows)
   - **iCloud-only count** — photos with a `Photos.sqlite` record but no local file at the expected path, or local file <100 KB when expected size is megabytes. These were optimized to placeholders; full quality lives in iCloud.
   - Live Photos pairing detected (`.HEIC`/`.JPG` + matching-basename `.MOV`)
   - Album count, photo count, **multi-album photo count** (photos in 2+ albums)
   - HEIC vs JPG breakdown
   - Sample paths: 5 originals, 5 edits, 5 multi-album, 5 iCloud-only (if any)
   - SQLite opened read-only with `?mode=ro&immutable=1` flags.
   - **Pauses for user review** with three iCloud-handling options (the user picks based on the actual count):
     - **(a) Re-sync from iCloud first** — sign in on a Mac, wait for download, then restart migration. Best for full quality if the iCloud-only count is significant.
     - **(b) Extract whatever's local, tag as low-resolution** — proceeds with what's on disk; iCloud-only items are extracted as placeholders into `photos/low-resolution/` and flagged in `album_map.csv`.
     - **(c) Skip iCloud-only assets entirely** — only full-quality photos make it into the curated layout; iCloud-only items are listed in `cleanup_photos_iclond_skipped.md` for the audit trail.
   - Recommended default by count: <1% → (c) is fine, 1–20% → (b), >20% → (a) is worth the wait. User confirms.

   **Things explicitly NOT extracted** (no flag, no review): slideshows/books/cards/calendar projects, AAE adjustment plists, Faces/People tags, Memories. All metadata-only constructs that don't translate to files.

2. **Locate sources** — every `*.photoslibrary`, `*.migratedphotolibrary`, `iPhoto_Library*`, plus loose photo dirs from inventory.

3. **Per library, extract:**
   - **Originals**: iPhoto `Masters/YYYY/MM/DD/<filename>.jpg` (dated paths) or Photos.app `originals/<HH>/<UUID>.<ext>` (hash-bucketed by UUID).
   - **Edits**: iPhoto `Modified/YYYY/MM/DD/<filename>.jpg` (real JPEG, copy operation). Photos.app: join `ZASSET.ZUUID` to rendered file at `resources/renders/<HH>/<UUID>.<ext>`. Pair each edit with its original.
   - **Album metadata**: iPhoto `AlbumData.xml`; Photos.app `database/Photos.sqlite` (`ZGENERICALBUM` joined `ZASSETALBUM` joined `ZASSET`). Read-only access.
   - **Live Photos pairs**: `.HEIC` or `.JPG` + `.MOV` with matching UUID/basename → travel together as a unit; placed alongside each other at the same destination path.
   - **HEIC kept as-is** — no auto-conversion to JPG. Modern Apple tooling reads them; preserved-data archive doesn't need universal compatibility.

4. **Discard application exhaust** — `Database/`, `Thumbnails/`, `resources/proxies/`, `resources/derivatives/`, `resources/modelresources/`, faces/ML caches, iCloud sync state. Same intent as the rsync exclude set, applied as a non-extraction (we just don't copy them; SSDs are unchanged).

5. **Hash-dedup originals** — SHA-256 across all extracted originals. Largest-source wins (most likely canonical). Edits keyed to their original — if original is a duplicate of one in another library, the edit follows the original's winner placement. Burst photos (`IMG_1234_001.jpg`, `IMG_1234_002.jpg`, ...) are byte-distinct and all survive — no thinning.

6. **Non-camera split (lump-and-defer)** — any file without camera-make/model EXIF gets routed to `david/images/<YYYY>/<filename>` regardless of subtype (screenshots, scans, web downloads, AirDropped photos with stripped EXIF, etc.). Single bucket, user reorganizes later if desired. Emit `cleanup_photos_no_exif.md` so user can spot-check the split.

7. **Date resolution chain** (in order; first hit wins):
   1. EXIF `DateTimeOriginal`
   2. EXIF `DateTimeDigitized`
   3. Filename date pattern (`IMG_20180615_*`, `2018-06-15-*`, `IMG-20180615*`, etc.)
   4. Parent dir if date-shaped (iPhoto `Masters/2018/06/15/`)
   5. File mtime (last resort because rsync rewrites it)
   6. None → `photos/unknown-date/<filename>`

8. **Album resolution** — each photo can be in 0, 1, or many albums in source. Placement strategy: **largest-album wins** for the visible directory; full membership preserved in a sidecar manifest (see step 9). Photos in 0 albums → date dir only.

9. **Album manifest** — emit `photos/album_map.csv` with one row per photo:
   ```
   path, original_uuid, all_albums
   2018/2018-06-15 — Family Trips/IMG_1234.jpg, AB12CD34-..., "Family Trips|Hawaii 2018|2018 highlights"
   ```
   Allows reconstruction of any album later via grep/scripting. Lossless metadata preservation without symlinks/hardlinks (which DSM/SMB handle inconsistently).

10. **Place winners**:
    - `photos/<YYYY>/<YYYY-MM-DD>[ — <Album>]/<filename>.<ext>` (largest album in name; bare date dir if no album)
    - Edits sidecar with original: `IMG_1234.jpg` (original) + `IMG_1234_edit.jpg` (1st edit) + `IMG_1234_edit2.jpg` (2nd edit if any) at the same dir level
    - Live Photos: `IMG_1234.HEIC` + `IMG_1234.MOV` together
    - Non-camera-EXIF files → `david/images/<YYYY>/<filename>.<ext>`

**Critical files:**
- `post_migration/photos_curate.sh` (new) — orchestrator
- `post_migration/photos_curate.py` (new) — does the work
- `post_migration/photoslibrary_inspect.py` (new, run-once spike) — pre-extraction probe; pauses for user review before Phase 4 proper runs

**Output reports:**
- `cleanup_photos_spike.md` — spike output, reviewed before extraction
- `cleanup_photos_no_exif.md` — files routed to `david/images/`, for spot-check
- `photos/album_map.csv` — full multi-album-membership manifest, lives in the curated layout permanently

**Caveats** (documented in dry-run output):
- Byte-identical dedup only — re-encoded duplicates (re-saved JPEG at different quality) look identical to humans but differ to SHA-256.
- Album metadata extraction may be incomplete for libraries with corrupted `AlbumData.xml` / `Photos.sqlite`.
- Re-importing the curated layout into a new Photos.app library will not auto-restore album associations regardless of how the layout is structured — Photos.app reads metadata, not paths. The `album_map.csv` is the recovery path if you ever want to script-rebuild album organization.
- iCloud-only photos (in DB but not on disk) will not be extracted — flagged by the spike. Re-syncing iCloud first is a manual prerequisite.

### Phase 5 — Videos: sort

**Why:** videos appear in three contexts that need different placement rules. Phase 5 handles the standalone-video case; project bundles get preserved atomic; iPhoto/Photos library videos are handled in Phase 4.

**Video extensions in scope:** `.mov`, `.mp4`, `.m4v`, `.avi`, `.dv`, `.mkv`, `.wmv`, `.mts`, `.m2ts`, `.3gp`, `.flv`, `.webm`. Exclude `.mov` files that are part of a Live Photos pair (those are paired with their `.HEIC`/`.JPG` and routed by Phase 4).

**Actions:**
1. **Route by context** — for each video file in scope:
   - **Inside a `.photoslibrary` / iPhoto library** → handled by Phase 4 (placed alongside other extracted media). Phase 5 ignores.
   - **Inside an iMovie project bundle** (`*.iMovieProject`, `*.imovielibrary`) → `movies/iMovie/<project-name>/` (preserve the bundle wholesale, including rendered proxies — bundle is atomic)
   - **Inside a Final Cut bundle** (`*.fcpbundle`) → `movies/FinalCut/<project-name>/` (preserve the bundle wholesale)
   - **Standalone (loose)** → date-organized placement (see step 2)
2. **Standalone video placement** — extract capture date via metadata, organize by year while preserving the source-context cluster:
   - **Date extraction**: `ffprobe` (FFmpeg) for QuickTime/MP4/MKV `creation_time` atoms, AVI RIFF metadata, DV tape timecode. Fallback chain: container metadata → filename date pattern (`VID_20180615_*`, `2018-06-15_*`) → file mtime → `unknown-date`.
   - **Path**: `movies/other/<YYYY>/<source-context>/<filename>` where `<source-context>` is the slugified original parent dir (e.g., `mmc_archive_2020_beyers_vid` from `mmc_archive/2020_beyers_vid/`). Preserves provenance; related files in the same dir stay grouped.
   - **No-date fallback**: `movies/other/unknown-date/<source-context>/<filename>`.
3. **Project-bundle name collisions** — strip extension for the dir name (`Vacation 2018.iMovieProject` → `Vacation 2018/`). On collision, append counter: `Vacation 2018 (2)/`, `Vacation 2018 (3)/`.
4. **DV review report** — `.dv` files are huge (~13 GB/hour) and often only useful as project source. Emit `cleanup_videos_dv.md` listing every `.dv` file with: size, source path, year, and any same-dir sibling video files (likely the rendered output). User marks each `[ ] keep / [X] drop` (default drop for files where a rendered sibling exists; default keep otherwise). Run AFTER initial placement so the user reviews against the actual placed layout, not the source.
5. **No video dedup** — multi-GB files rarely have byte-identical duplicates; the cost of hashing is high relative to expected savings. If Phase 9 surfaces anything, run a one-off dedup script then.
6. **The 164 GB `mmc_archive/2020_beyers_vid/` case** — classification depends on contents:
   - If project bundle → treat per rule 1.
   - If source DV + finished mp4 → land under `movies/other/2020/mmc_archive_2020_beyers_vid/` per rule 2; the DV will be flagged in step 4's report for keep/drop.

**Critical files:**
- `post_migration/videos_sort.sh` (new) — orchestrator
- `post_migration/videos_sort.py` (new) — does the work; uses `ffprobe` (system dependency) for metadata.

**Output reports:**
- `cleanup_videos_dv.md` — DV files with size + sibling-render candidates for keep/drop review.

### Phase 6 — Documents

**Why:** documents should keep their original folder structure (the user's organization) under a `documents/` root, with source-context preserved.

**Document extensions in scope:** `.pdf`, `.doc`/`.docx`, `.xls`/`.xlsx`, `.ppt`/`.pptx`, `.txt`, `.rtf`, `.pages`, `.numbers`, `.key`, `.md`, `.odt`, `.tex`, `.csv`, `.tsv`, `.html`/`.htm`, `.epub`, `.mobi`, `.djvu`, `.ps`, `.eps`, `.opml`, `.fdx`. iWork bundles (`.pages`/`.numbers`/`.key`) are macOS package dirs at the filesystem level — treated as files (no descend), copied as units.

**Actions:**
1. **Find** all in-scope document files under inventoried `documents` and `unknown` sources (anywhere a Phase 1 classifier put a `documents` tag, plus loose docs in user dirs).
2. **Hash-dedup with manifest**:
   - SHA-256 every doc.
   - Largest-source wins as canonical placement (consistent with the photos rule).
   - Emit `documents/dedup_map.csv` listing every doc + every source path that pointed at the same hash:
     ```
     canonical_path, sha256, all_source_paths
     documents/snashome_david_Documents/Bank/2018-Statement.pdf, abc123..., "snashome/david/Documents/Bank/2018-Statement.pdf|users/david/Documents/old/2018-Statement.pdf"
     ```
3. **Place winners** at `documents/<source-context>/<original-relative-path>`:
   - `<source-context>` = slugified top-level source dir (path separators, dots, spaces, special chars all → `_`). Examples: `snashome/david/Documents/` → `snashome_david_Documents`; `users/mmc/Desktop/` → `users_mmc_Desktop`.
   - Original relative path under that dir is preserved verbatim.
4. **Hidden files** — copy hidden dotfiles in source dirs (often user content: `.notes/`, project metadata, etc.) **except** macOS noise denylist: `.DS_Store`, `.Spotlight-V100/`, `.fseventsd/`, `.Trashes`, `.TemporaryItems/`, `._*` AppleDouble files.
5. **Symlinks** — record in dedup manifest, do not follow (consistent with Phase 1).
6. **Empty dirs** — not preserved. Source dirs whose contents all filter out simply don't appear under `documents/`.
7. **Archives flagged separately** — `.zip`, `.7z`, `.tar`, `.tar.gz`/`.tgz`, `.tar.bz2`/`.tbz`, `.rar` placed at their natural `documents/<source-context>/<original-relative-path>` like other docs (default: keep as-is), AND listed in `cleanup_documents_archives.md` with size, source path, and a sampled top-level content listing (`unzip -l` / `tar -tf` first 20 entries). User can extract any they want manually before Phase 10 promotes staging — automatic recursion into archives is out of scope.

**Critical files:**
- `post_migration/documents_collect.sh` (new) — orchestrator
- `post_migration/documents_collect.py` (new) — does the dedup + manifest

**Output reports:**
- `documents/dedup_map.csv` — canonical → all-source-paths mapping, lives in the curated layout permanently.
- `cleanup_documents_archives.md` — archives discovered, with sampled content listings, for manual review.

### Phase 7 — Personal trees: `.bw`, `images`, `app-data`, miscellaneous

**Why:** content that's clearly David's or mmc's but doesn't fit a global category goes in their personal folders.

**Actions:**

1. **`.bw/` content** — David's personal archive of photos and videos downloaded from the internet, stored as a hidden dot-dir.
   - Find every `**/.bw/**` path under david-owned source trees.
   - Hash-dedup across versions (different backups may have copied the same content; structure within `.bw/` is unlikely to change between backups).
   - Preserve as hidden: place under `david/.bw/<original-relative-path-after-.bw>`.
   - mmc trees are not expected to have `.bw`; confirm in inventory and treat as anomaly if found.

2. **`images/`** — non-camera-EXIF photos identified in Phase 4 are already routed there. Phase 7 doesn't re-process; just confirms the dir exists at `david/images/<YYYY>/`.

3. **`app-data/`** — application data preserved for possible future recovery. Each app gets a subdir under `david/app-data/<app>/` or `mmc/app-data/<app>/`. Internal structure preserved verbatim — applications expect specific paths. **No dedup within `app-data/`** — fragile data, byte-identical copies may still differ in their relationship to a parent app, and disk savings would be small.

   **Default-keep app-data categories:**
   - **Personal data**: 1Password vaults, Quicken / TurboTax records, OmniFocus / Things DBs, Bento DBs, AddressBook
   - **Communications**: Mail (special-handled — see step 4), Skype chats, **Messages history** (`chat.db`)
   - **Calendars**: `.calendar` dirs from `~/Library/Calendars/` (NOT the `.caldav` server caches, which are excluded)
   - **Notes / Stickies**: Notes.app DBs (`group.com.apple.notes/`), `StickiesDatabase`
   - **Media**: Voice Memos, Photo Booth Library, GarageBand loops & projects
   - **Browser bookmarks**: Safari (`Bookmarks.plist`), Chrome (`Bookmarks`), Firefox (`places.sqlite`). Bookmarks only — NOT history, cookies, cache, or session data.
   - **Game progress**: Steam saves (under `Documents/`, not `Application Support/Steam/` install dir), Minecraft saves (`saves/` subdirs only, not the install or `assets/objects/`)

   Anything else from `Application Support/` not on this list is dropped as exhaust (consistent with Phase 8 skip-by-construction).

4. **Mail conversion to mbox (best-effort)** — Apple Mail's V2-V9 storage format is a directory hierarchy with one `.emlx` file per message. Pure preservation works but means millions of tiny files in the curated layout (the same readdir-stall pain that hit the original backup). Conversion plan:
   - For each `*.mbox` package dir in source (e.g., `Mail/V2/<account>/<mailbox>.mbox/`), walk all `.emlx` files inside.
   - Parse each `.emlx` (RFC 822 message with appended Apple binary plist). Strip the plist, keep the message bytes.
   - Concatenate into a single mbox-format file at `david/app-data/Mail/<account>/<mailbox>.mbox` with traditional `From ` line separators.
   - Importable by Thunderbird, mutt, or any modern email client.
   - **Fallback on failure**: if any `.emlx` fails to parse (corruption, missing data, encoding issues), the entire mailbox falls back to verbatim raw preservation at `david/app-data/Mail/raw/<original-relative-path>/`. Per-mailbox decision so partial successes don't block.
   - Emit `cleanup_mail_conversion.md` reporting per-mailbox: source path, message count, conversion status (`converted` / `raw_fallback`), output path, any warnings.

5. **Miscellaneous personal content** — anything Phase 1 inventory tagged as user-data-misc that didn't match the above buckets (random user-created folders, scripts, dotfiles) → `david/<original-relative-path>` or `mmc/<original-relative-path>` preserving the in-user folder structure.

6. **Per-user assignment**:
   - Source path under `david/` or `mmc/` → respective user (no review needed).
   - Source path under `users/<other-uid>/` → all such content ultimately belongs to david or mmc, but the right answer isn't always obvious from path/content.
   - For ambiguous cases: emit `cleanup_personal_assignment.md` listing each unresolved subtree with size + sample contents. User marks each row `david / mmc / drop`. Default: nothing placed for that subtree until the user decides.

**Critical files:**
- `post_migration/personal_collect.sh` (new) — orchestrator
- `post_migration/personal_collect.py` (new) — does the work
- `post_migration/mail_emlx_to_mbox.py` (new) — Apple Mail conversion utility

**Output reports:**
- `cleanup_personal_assignment.md` — ambiguous user-uid mappings for david/mmc/drop decision.
- `cleanup_mail_conversion.md` — per-mailbox conversion outcome.

### Phase 8 — Skip-by-construction (audit phase, no mutation)

Under the "read SSD, write curated layout" strategy, content the user wants to drop is simply **never copied** into the curated layout in the first place. There's no retroactive-delete pass. Phase 8 is the **audit step** that documents what was skipped — generated from the Phase 1 inventory rather than maintained by hand, so it can never drift from reality.

**Categories typically skipped:**
- **Game installs** (Minecraft, Steam, Battle.net, Unreal Tournament, etc.) — `game-install` classification
- **Old app installs** in user `Applications/` dirs — `app-install` classification
- **Download dumps** — `download-dump` classification
- **Application exhaust** (Caches, PubSub, SyncServices, Database/Faces, photoslibrary/resources, Thumbnails) — covered by classifier; matches the rsync exclude set
- **NAS-internal directories** — `nas-internal` classification — `@appstore`, `@database`, `#recycle` (Synology trash)
- **`/volume1/rsync`** — Pi backup target on the OLD NAS only, not on SSDs. Pi backup job is recreated pointing at DS225+ post-cleanup.

**Actions:**

1. **Auto-derive the skip list** from Phase 1 inventory: any classification not consumed by Phases 3–7 is by definition skipped. Phase 3 reads `music`, Phase 4 reads `photo-library`, Phase 5 reads `video` and `video-project`, Phase 6 reads `documents`, Phase 7 reads `app-data`, `bw`, and unclassified-as-user-misc. Anything else (`game-install`, `app-install`, `download-dump`, `nas-internal`, application-exhaust subdirs flagged inside other classifications, `unknown` if not yet handled) lands in the skip list.

2. **Emit `cleanup_skip_audit.md`** — one row per source dir that wasn't read, with classification, size, and SSD origin. Becomes the permanent audit trail for "why isn't X in the curated layout?"

3. **Coverage check** — emit `phase_3_to_7_input_coverage.md` cross-tabulating: for each Phase 1 classification, the list of source dirs that fed each phase. The total dir count across {Phases 3–7 inputs} ∪ {Phase 8 skip list} must equal Phase 1's total classified dir count. If there's a gap, something fell through silently (likely an `unknown` that no phase claimed) — flagged for Phase 9 attention.

4. **`nas_cleanup.sh` is a separate concern** — the existing `~/github/nas-cleanup/nas_cleanup.sh` handles file-level macOS junk (`.DS_Store`, `@eaDir`, AppleDouble `._*`) that snuck through during the original rsync. Phase 8 is about classification-driven exclusion of whole categories. They don't overlap; both stay in scope but Phase 8 doesn't replace `nas_cleanup.sh`.

**Critical files:**
- `post_migration/skip_audit.sh` (new) — derives the skip list from inventory; emits both reports.

**Output reports:**
- `cleanup_skip_audit.md` — every skipped dir with classification, size, SSD origin.
- `phase_3_to_7_input_coverage.md` — coverage cross-tab; flags any classification that didn't reach a phase.

**Hard Guard #1 reaffirmed:** Phase 8 is read-only against the inventory CSV. Nothing is deleted from the SSDs, nothing is touched in staging. Pure audit reporting.

### Phase 9 — Anomaly review

**Why:** anything not classified by Phase 1, or anything Phases 3–8 couldn't decide on, surfaces here for user case-by-case decision. Phase 9 is the catchall — once it finishes, the curated layout is ready for promotion in Phase 10.

**Actions:**

1. **Walk what's left** — after Phases 3–8 run, walk all source paths and identify content that wasn't placed by any phase or surfaced by Phase 8's coverage cross-tab as a fall-through.

2. **Sub-classify anomalies** by extension/content rather than relying on the broad `unknown` bucket:
   - `vm-disk` — `.pvm`, `.hdd`, `.vmdk`, `.vdi`, `.vhd`, `.qcow2`, `.ova`, `.ovf`
   - `disk-image` — `.dmg`, `.iso`, `.img`, `.cdr`
   - `source-code` — `.py`, `.sh`, `.rb`, `.js`, `.ts`, `.go`, `.c`/`.cpp`/`.h`, `.swift`, `.java`, `.rs`, `.lua`, `.pl`, plus `.git/`, `.hg/`, `Makefile`, `Cargo.toml`, `package.json`
   - `large-binary` — single file >100 MB with no other classification
   - `loose-text` — `.txt`/`.md`/`.log` outside any documents source-context
   - `unknown` — truly nothing identified

3. **Inclusion threshold** — surface in `cleanup_anomalies.md`:
   - Every file or top-level subdir **>1 MB**
   - PLUS anything sub-classified as `unknown`, `vm-disk`, `disk-image`, or `large-binary` regardless of size
   - **Below the threshold and not flagged as suspicious**: default-keep at `david/<source-context>/<original-relative-path>` or `mmc/<source-context>/<original-relative-path>` so nothing is silently lost. The threshold filters what to surface for review, not what to drop.

4. **Default actions per sub-category** (each row in `cleanup_anomalies.md` has a default the user can override):
   - `vm-disk` → keep, route to `david/vms/<source-context>/<filename>` (new subdir under user)
   - `disk-image` → review (mix of OS installers to drop and user images to keep)
   - `source-code` → keep, route to `david/code/<source-context>/<original-relative-path>` (or `mmc/code/...`); whole top-level source-code dir routed as a unit (e.g., a git repo with all its files), not just loose `.py` files. **`.git/`/`.hg/` dirs flagged separately** in the report so user can decide per-repo whether to keep the history.
   - `large-binary` → review
   - `loose-text` → keep, route to `david/text/<source-context>/<filename>`
   - `unknown` → review

5. **`apply_anomaly_decisions.sh` semantics:**
   - User-marked `keep` with a destination → copy SSD source → `staging/<destination>`. Hard Guard #1 still holds (SSD never modified).
   - User-marked `drop` → no action; the file just isn't placed in the curated layout.
   - **Destination must be under `staging/`**; the script validates and refuses any path under `/volume1/{music,photos,...}` (Hard Guard #2).
   - **Idempotent**: safe to rerun. Files already placed are skipped; newly-keep'd rows get placed; `drop` rows stay un-placed. User can iterate freely.
   - **Cross-category rerouting allowed**: if the user marks an anomaly's destination as `staging/music/<artist>/<album>/...` because it's actually music we missed, the script honors it. The full curated layout is reachable as a destination.

6. **Phase ordering**: Phase 9 must complete (all anomaly decisions applied) **before** Phase 10 promotes staging. Once staging is moved to final position at Phase 10, Hard Guard #2 kicks in and the layout becomes read-only.

**Critical files:**
- `post_migration/anomalies.sh` (new) — produces the review doc with sub-classified rows
- `post_migration/apply_anomaly_decisions.sh` (new) — actions user-marked decisions; idempotent; staging-only writes

**Output reports:**
- `cleanup_anomalies.md` — one row per surviving file/dir >1 MB or with a suspicious sub-classification, with size, path, sub-category, default action, destination.

### Phase 10 — Move staging into final position

**Why:** until now, the curated layout was being built under `/volume1/staging/` to keep Hard Guard #2 (never modify `/volume1/{music,photos,...}` once built) trivially enforceable during the build. After Phase 9 sign-off, staging is promoted to the final layout.

**Actions:**

1. **Pre-promote sanity checks** — script runs all of these, emits a summary, waits for explicit `yes` to proceed:
   - Top-level dir count under `staging/` equals 6 (`music`, `photos`, `movies`, `documents`, `david`, `mmc`). Anything else → abort.
   - Total `staging/` size > 100 GB (sanity floor — rules out an empty build).
   - Per-dir minimums: `music/` ≥1000 audio files, `photos/` ≥1000 image files, `documents/` ≥100 files. Zero in any category → abort (would indicate a phase didn't run).
   - All expected manifests exist: `photos/album_map.csv`, `documents/dedup_map.csv`.
   - All expected reports were generated and reviewed (the `cleanup_*.md` set).

2. **Existing-destination check** — if any of `/volume1/{music,photos,movies,documents,david,mmc}` already exists (shouldn't happen on first run; can happen if the script is rerun), script **pauses and asks** rather than auto-deciding. User specifies whether to abort, rename existing → backup name, or merge. No silent overwrites.

3. **btrfs snapshot** of `/volume1/` immediately before the `mv` — DS225+ runs btrfs, snapshots are instant and metadata-only. Snapshot name: `volume1-pre-promote-<YYYYMMDD-HHMM>`. **Aborts the script if snapshot creation fails** — no rollback path = no `mv`.

4. **Promote each top-level dir** in a loop:
   ```
   for dir in music photos movies documents david mmc; do
     mv "/volume1/staging/$dir" "/volume1/$dir" || { echo "FAILED at $dir"; exit 1; }
   done
   ```
   On first failure: **abort and ask the user**. Output what completed, what failed, the failure reason. The btrfs snapshot is the rollback path. Do not auto-roll-back, do not auto-retry, do not auto-clean — let the user decide based on context.

5. **Post-promote verification** — `ls /volume1/` shows the 6 curated dirs + no `staging/`. Spot-check 3 random files in each curated dir to confirm they're readable. If any check fails, surface to user before declaring success.

6. **Cleanup**: `rm -rf /volume1/staging` only if empty.

7. **Disable DSM indexing for the new curated dirs** — DSM's Indexing Service auto-indexes content for Photo Station / Audio Station / Video Station. Heavy CPU during initial indexing; not needed during post-cleanup. Script ensures the curated dirs are NOT in `/var/packages/Universal Search/etc/index_path.json` (or equivalent DSM 7 config). Emit a reminder in `cleanup_post_promote_steps.md`: "Re-enable indexing later via DSM Control Panel → Indexing Service → Indexed Folder List when you want Photo/Audio/Video Station browsing to work."

8. **Permission re-application reminder** — `cleanup_post_promote_steps.md` also reminds: "Curated layout is currently `nasadmin:nasadmin`. To switch to user-specific perms run: `chown -R david:dglc /volume1/{music,photos,movies,documents,david} && chown -R mmc:dglc /volume1/mmc && chmod -R 770 /volume1/{music,photos,movies,documents} && chmod -R 750 /volume1/{david,mmc}`."

9. **Snapshot retention** — manual cleanup. Script does NOT auto-delete the snapshot. Reminder in `cleanup_post_promote_steps.md`: "After Phase 11 verification + gap-fill confirms the curated layout is complete, release the snapshot with `btrfs subvolume delete /volume1/.snapshots/volume1-pre-promote-<YYYYMMDD-HHMM>` (path varies by DSM)." Snapshot disk impact is minimal until you start mutating things post-promote (copy-on-write).

10. **Hard Guard #2 takes effect** from this point on. The curated layout dirs are read-only by convention; any subsequent cleanup-phase rerun refuses to write to them.

**Critical files:**
- `post_migration/promote_staging.sh` (new) — single-purpose mover with sanity-check → snapshot → mv → verify; aborts on any failure.

**Output reports:**
- `cleanup_post_promote_steps.md` — manual reminders: re-enable indexing, re-permission, release snapshot. Generated by the script with placeholder values filled in.

### Phase 11 — DS1512+ verification cross-check, gap-fill, decommission

**Why:** the SSDs were the read source for the build, but they may have been incomplete (the deferred `users/mmc/Library/` tree, anything that stalled and got skipped, anything excluded by an over-broad pattern). The DS1512+ still has the original data. Before decommissioning it, verify the curated layout against the DS1512+ contents.

**Sub-phases:**

**11a — Inventory DS1512+** (lightweight)
- SSH to DS1512+, walk `/volume1/snashome/` and `/volume1/users/`. Skip the always-skip patterns: same set as Phase 1's `nas-internal` + `app-install` + `game-install` + `download-dump` + the rsync-exclude graveyards (`Library/Caches`, `photoslibrary/resources`, `Mail/V2/<...>/Attachments` in raw form, etc.).
- **Read** everything else, including the deferred `users/mmc/Library/` and `users/mmc_OldUserFiles/Library/` (DS1512+-only — Phase 1 inventory didn't see them).
- Output a manifest: relative path + size + mtime for every file.
- Use `find -printf` (readdir + stat only, no content read) so even degraded-array Mail trees stall once per dir, not per file.
- Retry-loop wrapper similar to `nas_backup.sh`'s pattern — tolerates repeated stalls, keeps grinding through.

**11b — Inventory DS225+ curated layout**
- Same shape: relative path + size + mtime for every file under `/volume1/{music,photos,movies,documents,david,mmc}/`.
- **Content fingerprint** per file: size + first/last 64KB hash. Fast (skips most of the file). Full SHA-256 only on demand for ambiguous cases.

**11c — Reconcile**
- Reconciliation strategy: **fingerprint primary, filename secondary**.
  - **Fingerprint match** (size + first/last 64KB hash) → match regardless of path. The curated layout's renamed file is recognized as the same content.
  - **Fingerprint mismatch but same filename** → flag as "possible match" (likely re-saved/re-encoded, not gap) for user review rather than gap.
  - **No fingerprint or filename match** → genuine gap, flagged in `cleanup_gaps.md`.
- **Sub-classify each gap**:
  - `mmc-library` — under DS1512+ `users/mmc/Library/` (deferred during initial backup; expected to dominate)
  - `mmc_oldUserFiles-library` — under `users/mmc_OldUserFiles/Library/` (also deferred)
  - `excluded-by-pattern` — under a path that an rsync exclude caught too aggressively
  - `corrupted-on-ssd` — DS1512+ has the file, SSD copy is missing/zero-bytes/unreadable
  - `truly-missing` — no obvious explanation
- Default actions per sub-category (used as defaults in 11d):
  - `mmc-library` / `mmc_oldUserFiles-library` → fetch and route through Phase 7 sub-flow (app-data classification or skip)
  - `excluded-by-pattern` → fetch and route per the appropriate phase
  - `corrupted-on-ssd` → fetch into curated layout with `_recovered` suffix; SSD remains untouched (Hard Guard #1 holds)
  - `truly-missing` → review per file

**11d — Selective gap-fill**
- User reviews `cleanup_gaps.md`, marks each entry `[ ] fetch / [ ] skip` (with default per sub-category).
- **Fetch path**: daemon-mode rsync from DS1512+ → DS225+ to bypass the Atom D2700's SSH-AES-NI throughput ceiling.
  - Set up `/etc/rsyncd.conf` on DS1512+ defining a module (e.g., `[snashome]` → `/volume1/snashome`, `[users]` → `/volume1/users`).
  - Source URI: `rsync://10.0.0.2/snashome/<path>` and `rsync://10.0.0.2/users/<path>`.
  - Unencrypted but on wired LAN — acceptable per CLAUDE.md.
  - Daemon stopped post-Phase-11d; not needed for the long-term coexistence.
- After fetch, route the new content through the appropriate cleanup phase script (Phase 3/4/5/6/7) so it lands in the curated layout consistent with everything else.
- **Skip**: noted in the manifest as intentionally-not-on-DS225+.

**11e — Post-verification snapshot**
- Once 11d completes and the user signs off on the gap-fill outcome:
  - **Release the pre-promote snapshot** from Phase 10: `btrfs subvolume delete /volume1/.snapshots/volume1-pre-promote-<TS>` (path varies by DSM).
  - **Take a new baseline snapshot**: `volume1-archive-baseline-<YYYYMMDD>` — captures the "complete and verified" state of the archive. Btrfs copy-on-write means this consumes nearly zero disk; lives forever as a known-good anchor.
  - **Enable DSM Snapshot Replication** on the curated dirs with a light schedule: weekly, 4-week retention. Catches accidental modifications within a week without significant disk burden.

**11f — DS1512+ decommission** (user-paced, no script-driven decision)
- DS1512+ shutdown is **at the user's discretion** — no fixed grace period, no auto-shutdown.
- Drive disposition (wipe + dispose vs. wipe + cold-spare) is also a manual decision post-shutdown.
- Final state once user decides: DS225+ has the curated layout (with baseline snapshot + replication), SSDs remain as belt-and-suspenders archive, DS1512+ powered down.

**Critical files:**
- `post_migration/verify_ds1512.sh` (new) — orchestrator running 11a–11c, produces gap report
- `post_migration/inventory_ds1512.py` (new) — does the manifest walk with retry logic
- `post_migration/reconcile.py` (new) — DS1512+ vs DS225+ reconciliation; fingerprint primary, filename secondary
- `post_migration/gap_fill.sh` (new) — actions the user-marked gap decisions; routes fetched content through the appropriate cleanup phase
- `post_migration/post_verify_snapshot.sh` (new) — releases pre-promote snapshot, takes baseline, configures DSM Snapshot Replication

**Output reports:**
- `cleanup_gaps.md` — sub-classified gaps with default actions; user-driven fetch/skip decision.
- `cleanup_gaps_corrupted.md` — `corrupted-on-ssd` sub-category broken out (Hard-Guard-#1-relevant)

**Verification:**
- After 11d, re-run `verify_ds1512.sh`; expected output: only entries the user explicitly marked `skip`. Anything else means gap-fill missed something.
- **Final paranoia check**: `verify_ds1512.sh --strict` on a 100-file random sample — full SHA-256 on both sides for those 100. If any mismatch, surface for manual review.

## Critical files (summary)

**Modify (none — backup scripts are unchanged by this work):**
- The original Phase 1 of the previous plan (refactor `excludes.txt` shared across `nas_backup*.sh`) is **deferred** — backup is nearly done; refactor is hygiene, not blocking. Can be a future small PR.

**Create under `~/github/nas-cleanup/post_migration/`:**

| File | Purpose |
|------|---------|
| `inventory.sh` + `inventory.py` | Phase 1 classification map |
| `scaffold.sh` | Phase 2 staging-dir creation |
| `music_curate.sh` + `music_curate.py` | Phase 3 music dedup/organize/filter |
| `photos_curate.sh` + `photos_curate.py` + `photoslibrary_inspect.py` | Phase 4 photo extract/dedup/organize |
| `videos_sort.sh` + `videos_sort.py` | Phase 5 video routing |
| `documents_collect.sh` | Phase 6 document copy |
| `personal_collect.sh` | Phase 7 .bw / images / app-data / misc |
| `anomalies.sh` + `apply_anomaly_decisions.sh` | Phase 9 review and apply |
| `promote_staging.sh` | Phase 10 move staging into final position |
| `verify_ds1512.sh` + `inventory_ds1512.py` + `reconcile.py` + `gap_fill.sh` | Phase 11 DS1512+ cross-check, gap-fill, decommission |

(No Phase 8 scripts — content the user wants dropped is skipped at read time, not deleted retroactively. See Phase 8 section.)

**Output reports** (Markdown checkboxes the user fills in, per phase):

| File | Phase |
|------|-------|
| `cleanup_inventory.md` | 1 |
| `cleanup_music_artists.md` | 3 |
| `cleanup_music_lowbitrate.md` | 3 |
| `cleanup_photos_web_candidates.md` | 4 |
| `cleanup_anomalies.md` | 9 |
| `cleanup_gaps.md` | 11 |

## Ordering

1. SSDs mounted on Mac as today (read-only source — APFS, stays on Mac); DS225+ ready as the rsync-over-SSH destination
2. **Phase 1** — inventory of SSD source; user reviews and approves classification
3. **Phase 2** — scaffold under `/volume1/staging/`
4. **Phase 3** — music
5. **Phase 4** — photos (after the photoslibrary spike confirms edit-extraction approach)
6. **Phase 5** — videos
7. **Phase 6** — documents
8. **Phase 7** — personal
9. **Phase 8** — no-op (skip-by-construction; the build phases didn't copy what we don't want)
10. **Phase 9** — anomaly review on whatever the SSD source had that didn't match a classifier
11. **Phase 10** — promote `/volume1/staging/` → final `/volume1/{music,photos,...}/`
12. **Phase 11** — DS1512+ verification, gap-fill, decommission

## Verification plan

- **Phase 1**: user approves the classification map. No mutation, no verification needed.
- **Phase 2**: `ls /volume1/staging/{music,photos,movies,documents,david,mmc}` returns six empty dirs.
- **Phase 3**: spot-check 10 random tracks (playable, correct tags); track count in `staging/music/` matches the dedup CSV's "kept" count.
- **Phase 4**: spike output reviewed and acknowledged before extraction; spot-check 10 random photos (readable, EXIF preserved); spot-check 5 multi-album photos (confirmed in `album_map.csv`); spot-check 5 Live Photos pairs (`.HEIC`+`.MOV` together); spot-check 5 photos in `david/images/`; album-organization sanity check on a known album.
- **Phase 5**: every project bundle is intact (open in iMovie/FCP if curious); standalone count matches expectation; spot-check 5 standalone videos in `movies/other/<YYYY>/<source-context>/` (date sane, file plays); DV review report (`cleanup_videos_dv.md`) reviewed and applied.
- **Phase 6**: file count under `staging/documents/` ≈ classifier's `document` count minus duplicates in `dedup_map.csv`; spot-check folder structure preservation; spot-check 5 entries in `dedup_map.csv` (canonical path resolves to a real file, all listed source paths actually existed); review `cleanup_documents_archives.md` for any archives needing manual extraction.
- **Phase 7**: `staging/david/.bw/` deduped (no two files with same hash); `staging/david/images/` matches Phase 4's no-EXIF set; spot-check 5 mbox files (open in Thunderbird or `mutt -f`); review `cleanup_mail_conversion.md` for any raw-fallback mailboxes; review `cleanup_personal_assignment.md` and confirm no user-uid subtrees were left unrouted.
- **Phase 9**: after applying anomaly decisions, every row in `cleanup_anomalies.md` is either marked `drop` or has a destination under `staging/`. Phase 8's coverage cross-tab now shows zero unhandled fall-throughs. `apply_anomaly_decisions.sh` rerun is a no-op (idempotency check).
- **Phase 10**: pre-promote sanity-check summary passed; btrfs snapshot exists; `ls /volume1/staging` reports empty (or no longer exists); `ls /volume1/{music,photos,movies,documents,david,mmc}` matches expectation; spot-check 3 random files in each curated dir readable; `cleanup_post_promote_steps.md` generated; DSM indexing confirmed disabled for curated dirs.
- **Phase 11**: re-run `verify_ds1512.sh` after gap-fill; expected output is only entries the user explicitly marked `skip`. Strict-mode 100-file sample passes. Pre-promote snapshot released; baseline snapshot taken; DSM Snapshot Replication enabled. DS1512+ shutdown is at user's discretion (no auto-decommission).

Roll-back path for any phase: restore from the SSDs (untouched, read-only throughout the build) or the DS1512+ (until decommissioned). Document SSD-path → DS225+-path mapping so partial restores are easy.

## Decisions made (during plan walkthrough, 2026-05-04+)

**Layout / scope:**
- **User dirs:** keep `david/` and `mmc/` (not `maureen/`). Any "maureen"-tagged content treated as `mmc` via normal dedup.
- **`www/`:** deferred — not in active scope. Revisit only if Phase 9 surfaces something.
- **`users/<other-uid>/` UIDs:** all such content belongs to david or mmc. Phase 7 flags the ambiguous ones for user review rather than guessing.

**Phase 1 (inventory):**
- Single-pass merged inventory across both SSDs, tagged per row with origin.
- Depth 3 + escape-hatch descent (cap at depth 6) for known-marker subtrees.
- Music classification is **sticky** — non-audio files in a music dir travel with the album.
- Symlinks recorded but not followed.

**Phase 2 (scaffold):**
- Build everything as `nasadmin:nasadmin`. User-specific ownership/perms is a post-build optional step.
- Staging visible at `/volume1/staging/`, single-user operation.

**Phase 3 (music):**
- **Group/place** by Album Artist (fall back to Artist) + Album + Title.
- **Format preference** for dedup ties: lossless > lossy ≥192 kbps > lossy <192 kbps; bitrate within tier; file size as final tiebreak.
- **Drop without review:** iTunes Library files (`.itl`/`.xml`/`.musiclibrary`) and all playlists.
- **Keep as-is:** `.m4p` DRM AAC files (no special handling).
- **Napster filter:** any "nappy"/"napster" string in path/tags → flagged in `cleanup_music_napster.md` (default drop, user can flip).
- **Comedy filter:** auto-marked using genre tag (`Comedy`/`Spoken Word`/`Stand-Up`); >50% of an artist's tracks comedy-tagged → artist auto-checked. User reviews `cleanup_music_artists.md`.
- **Low-bitrate:** `<128 kbps` dropped automatically; `=128 kbps` reviewed in `cleanup_music_lowbitrate.md`.
- **Local tags only** — no MusicBrainz/AcoustID lookup.

**Phase 4 (photos):**
- **Spike first** (`photoslibrary_inspect.py`) — pre-extraction probe per library; reviewed before Phase 4 proper runs.
- **Date scheme:** `photos/<YYYY>/<YYYY-MM-DD>[ — <Album>]/<filename>`.
- **Date fallback chain:** EXIF DateTimeOriginal → DateTimeDigitized → filename pattern → date-shaped parent dir → file mtime → `photos/unknown-date/`.
- **Edits:** sidecar pattern with `_edit` suffix at the same dir level (`IMG_1234.jpg` + `IMG_1234_edit.jpg`).
- **Albums:** largest-album wins for the path; full multi-album membership preserved in `photos/album_map.csv`.
- **Live Photos:** `.HEIC`/`.JPG` + paired `.MOV` placed together at the same destination.
- **HEIC kept as-is** — no auto-conversion.
- **Bursts kept as-is** — all frames survive dedup; thinning is a deferred separate operation.
- **Non-camera-EXIF photos** (screenshots, scans, web, AirDropped no-EXIF) → lump into `david/images/<YYYY>/<filename>`. Spot-check via `cleanup_photos_no_exif.md`.
- **Re-import caveat documented**: re-importing into a new Photos.app library doesn't auto-restore album associations; `album_map.csv` is the recovery path for script-based reconstruction.
- **iCloud handling**: spike detects iCloud-only placeholders, pauses for user decision (re-sync / low-res-tag / skip). Decision is data-driven — depends on the actual placeholder count.
- **Drop without review:** slideshows, photo books, cards, calendar projects, AAE adjustment plists, Faces/People, Memories.

**Phase 5 (videos):**
- **Extension list:** mov, mp4, m4v, avi, dv, mkv, wmv, mts, m2ts, 3gp, flv, webm. Live Photos `.MOV` files excluded (handled by Phase 4 as paired media).
- **Standalone placement:** date-organized by year via `ffprobe` capture-date extraction. Path: `movies/other/<YYYY>/<source-context>/<filename>`. Source-context preserved as slugified parent-dir name; related files stay grouped within their year.
- **Project bundles** (iMovie, FCP) preserved wholesale, including rendered proxies — bundle is atomic. Name collisions get a `(2)`, `(3)` counter suffix.
- **No video dedup** — multi-GB files rarely byte-duplicate; hashing cost high vs. expected savings.
- **DV review** (`cleanup_videos_dv.md`) — every `.dv` file flagged for keep/drop, default drop where a rendered sibling exists, default keep otherwise.

**Phase 6 (documents):**
- **Hash-dedup with manifest** — same pattern as photos. `documents/dedup_map.csv` records canonical path + all source paths.
- **Extension list extended:** csv, tsv, html, htm, epub, mobi, djvu, ps, eps, opml, fdx (in addition to the original PDF/doc/xls/ppt/txt/rtf/pages/numbers/key/md/odt/tex set).
- **Placement:** `documents/<source-context>/<original-relative-path>` where `<source-context>` is slugified source-tree path.
- **iWork bundles** treated as files (no descend), copied as units.
- **Hidden files** copied except macOS noise denylist (`.DS_Store`, `.Spotlight-V100/`, `.fseventsd/`, `.Trashes`, `._*` AppleDouble).
- **Archives** (.zip/.7z/.tar*) placed in natural location AND flagged in `cleanup_documents_archives.md` with sampled content listings; user manually extracts any they want before Phase 10. No automatic recursion.

**Phase 7 (personal):**
- **`.bw/`** is David's hidden archive of internet-downloaded photos/videos. Hash-dedup across backup versions, preserve hidden as `david/.bw/<original-relative-path>`.
- **App-data keep-list** finalized: 1Password, Quicken/TurboTax, OmniFocus/Things, Bento, AddressBook, Mail, Skype, Messages history, .calendar dirs, Notes/Stickies DBs, Voice Memos, Photo Booth, GarageBand, browser bookmarks (Safari/Chrome/Firefox — bookmarks only, no history/cookies/cache), Steam saves (under Documents only), Minecraft saves. Everything else in Application Support is exhaust.
- **No dedup within app-data** — fragile, small savings.
- **App-data internal structure preserved verbatim** — apps expect specific paths.
- **Mail conversion to mbox** (best-effort) via `mail_emlx_to_mbox.py`. Per-mailbox: convert if all .emlx files parse cleanly, else raw fallback at `david/app-data/Mail/raw/<...>`. Result reported in `cleanup_mail_conversion.md`.
- **Ambiguous user-uid assignment** — flagged in `cleanup_personal_assignment.md` for david/mmc/drop decision; nothing placed until user decides.

**Phase 8 (skip audit):**
- Skip list **auto-derived from Phase 1 inventory** — anything not consumed by Phases 3–7 is by definition skipped. Eliminates drift between hand-maintained list and reality.
- `cleanup_skip_audit.md` — permanent audit trail of every skipped dir.
- `phase_3_to_7_input_coverage.md` — coverage cross-tab; flags silent fall-throughs for Phase 9 review.
- Phase 8 is read-only (Hard Guard #1 reaffirmed). Doesn't replace `nas_cleanup.sh` (file-level macOS junk handler — separate concern).

**Phase 9 (anomaly review):**
- Sub-classifier breaks anomalies into: `vm-disk`, `disk-image`, `source-code`, `large-binary`, `loose-text`, `unknown` (rather than one fat `unknown` bucket).
- Surface threshold for review: >1 MB, OR any suspicious sub-classification (`unknown`, `vm-disk`, `disk-image`, `large-binary`) regardless of size.
- Below-threshold files default-kept at `david/<source-context>/<...>` or `mmc/<source-context>/<...>` — nothing silently lost.
- Default actions: vm-disks → `david/vms/`; source code → `david/code/<source-context>/` (whole repo as a unit, `.git/` flagged separately for keep/drop); loose-text → `david/text/`.
- `apply_anomaly_decisions.sh` is idempotent; staging-only writes (Hard Guard #2 enforced); cross-category rerouting allowed (user can route an anomaly into `staging/music/`, etc.).

**Phase 10 (promote):**
- Pre-promote sanity checks: top-level dir count = 6, size floor 100 GB, per-dir file-count minimums, manifests exist, user types `yes`.
- Existing-destination check pauses and asks (won't normally happen; only on rerun).
- btrfs snapshot of `/volume1/` immediately before the `mv`. `promote_staging.sh` aborts before the `mv` if snapshot fails.
- Per-dir `mv` loop. On first failure: abort and ask; don't auto-rollback. Snapshot is the recovery path.
- DSM indexing **disabled** for curated dirs initially. `cleanup_post_promote_steps.md` reminds the user to re-enable when Photo/Audio/Video Station browsing is desired.
- Permission re-application reminder included in the post-promote steps doc.
- Snapshot retention is manual; release with `btrfs subvolume delete` after Phase 11 confirms.

**Phase 11 (verification + gap-fill + decommission):**
- **Reconciliation strategy**: fingerprint primary (size + first/last 64KB hash) + filename secondary. Default mode for the archive's scale and the degraded array.
- **Gap sub-classifier**: mmc-library, mmc_oldUserFiles-library, excluded-by-pattern, corrupted-on-ssd, truly-missing — each with a per-category default action.
- **Corrupted-on-SSD handling**: fetched into curated layout with `_recovered` suffix; SSD never touched (Hard Guard #1 preserved).
- **Daemon-mode rsync** from DS1512+ for gap-fill (bypasses Atom SSH-AES-NI ceiling). Daemon stopped post-11d.
- **DS1512+ decommission**: user-paced, no fixed grace period, no auto-shutdown. Drive disposition is a manual decision post-shutdown.
- **Post-verification snapshot**: release pre-promote snapshot, take new baseline `volume1-archive-baseline-<YYYYMMDD>`, enable DSM Snapshot Replication weekly with 4-week retention.

**Hard Guard #1 reaffirmed:** SSDs are never modified. Build is copy-only from SSD → DS225+. User can clean up SSD sources later, separately.

## Open questions for the user

All resolved. Plan is fully specified.

## Out of scope (deferred)

- **Aggressive content-archive rebuild** — already de-scoped in the prior plan.
- **Mutation on the SSDs.** They stay as read-only source during the build and a third-copy archive forever after.
- **Mutation on the DS225+ curated layout** once Phase 10 promotes staging into final position. Cleanup is build-once.
- **Mail re-extraction to mbox/Maildir** — handled by Phase 7 routing as `app-data/Mail/`. Format conversion deferred.
- **Refactor of `excludes.txt`** in the backup scripts — hygiene, not blocking; deferred as a future small PR.
- **Re-encode pass on duplicate-but-not-byte-identical media** (e.g., re-saved JPEGs that differ only by quality) — visual-similarity dedup is hard and out of scope.
