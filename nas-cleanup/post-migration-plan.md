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
2. **Read tags** (artist, album, title, track #, bitrate) — Python `mutagen`. Filename/path fallback for missing tags.
3. **Group by (artist, album, title)** — case-insensitive, normalized.
4. **Within each group, keep the highest bitrate**; ties broken by file size (larger wins).
5. **Comedy filter** — emit a `cleanup_music_artists.md` listing every distinct artist found. User marks each `[ ] keep / [ ] comedy`. `--apply` removes everything tagged comedy.
6. **Low-bitrate review** — after dedup, list every surviving track at ≤128 kbps. User reviews `cleanup_music_lowbitrate.md` and marks `[ ] keep / [ ] drop`.
7. **Place winners**:
   - Audio tracks → `music/<Artist>/<Album>/<NN Title>.<ext>` (track number zero-padded; missing track # → omit prefix)
   - Companion files → `music/<Artist>/<Album>/<original-filename>` (original name preserved; no track-number prefix)
8. **Sources unchanged** — copy not move during dry run; `--apply` deletes source after place succeeds.

**Filename normalization:**
- Strip iTunes "Track 1" / "Track 2" suffixes (already seen in `iTunes Music/A Paris/`)
- Resolve NFC/NFD normalization to NFC
- Sanitize filesystem-illegal chars

**Critical files:**
- `post_migration/music_curate.sh` (new) — orchestrator with `--phase tag-scan|dedup|comedy|lowbitrate|place`
- `post_migration/music_curate.py` (new) — does the work

**Verification:**
- After `--apply`, source music trees should be empty (or contain only files the user excluded)
- Spot-check 10 random tracks — playable, correct tags
- DS225+ free space should increase by approximately the dedup CSV's reported reclamation

### Phase 4 — Photos: extract originals + edits, dedup, organize

**Why:** 674 GB across three overlapping `.photoslibrary`/iPhoto libraries plus loose photo dirs. User wants originals + edits, no application exhaust, organized by date and album where possible.

**Actions:**
1. **Locate sources** — every `*.photoslibrary`, `*.migratedphotolibrary`, `iPhoto_Library*`, plus loose photo dirs from inventory
2. **Per library, extract:**
   - **Originals** from `Masters/` (iPhoto-era, dated path: `Masters/YYYY/MM/DD/`) and `originals/` (Photos.app-era, hash-bucketed paths)
   - **Edits** — iPhoto stores in `Modified/`; Photos.app stores rendered edit output under `resources/renders/` or `resources/modelresources/` (paired with adjustment XMPs). **Need spike at start of phase to confirm structure on the actual libraries** before automating.
   - **Album metadata** — iPhoto: parse `AlbumData.xml` for album → photo associations. Photos.app: read `Photos.sqlite` (read-only) for `ZGENERICALBUM` joins.
3. **Discard everything else** — Database/, Thumbnails/, resources/proxies/, faces/, ML caches, iCloud sync state. Same intent as the rsync exclude set, applied as a delete after extraction
4. **Hash-dedup originals** — SHA-256 across all extracted originals. Largest-source wins (most likely canonical). Edits keyed to their original — if original is a duplicate of one in another library, the edit version follows the original's "winner" placement.
5. **Internet-downloaded heuristic** — files with no camera EXIF (no `Make`/`Model` tags) AND filename matching common web patterns (`image-N.jpg`, `IMG_N.jpg` without camera EXIF, `download-N.png`, etc.) → routed to `david/images/` instead of `photos/`. **Heuristic is fuzzy; emit a `cleanup_photos_web_candidates.md` for user spot-check before final placement.**
6. **Place winners** at:
   - `photos/<YYYY>/<YYYY-MM-DD>[ — <Album>]/filename.ext` (date from EXIF `DateTimeOriginal`, fallback to file mtime)
   - Edits placed alongside the original with `_edit` suffix or in an `edits/` sibling — TBD after the spike in step 2
   - Web candidates → `david/images/<YYYY>/filename.ext`

**Critical files:**
- `post_migration/photos_curate.sh` (new) — orchestrator
- `post_migration/photos_curate.py` (new) — does the work
- `post_migration/photoslibrary_inspect.py` (new, run-once spike) — sample structure of each library before automation

**Caveats** (documented in dry-run output):
- Byte-identical dedup only — re-encoded duplicates (re-saved JPEG at different quality) look identical to a human but differ to SHA-256
- Album metadata extraction may be incomplete for libraries with corrupted `AlbumData.xml` / `Photos.sqlite`
- The web/camera split is heuristic — anything ambiguous goes in the spot-check report

### Phase 5 — Videos: sort

**Why:** videos appear in three contexts that need different placement rules.

**Actions:**
- For each video file (`.mov`, `.mp4`, `.avi`, `.dv`, `.m4v`) found anywhere in scope:
  - **Inside a `.photoslibrary` / iPhoto library** (extracted in Phase 4) → `photos/` alongside other extracted media (Phase 4 handles)
  - **Inside an iMovie project bundle** (`*.iMovieProject` or `*.imovielibrary`) → `movies/iMovie/<project-name>/` (preserve the bundle wholesale)
  - **Inside a Final Cut bundle** (`*.fcpbundle`) → `movies/FinalCut/<project-name>/` (preserve the bundle wholesale)
  - **Standalone (loose)** → `movies/other/<source-context>/<filename>` where source-context is the original parent dir name (e.g., `mmc_archive_2020_beyers_vid/`)
- Inside project bundles: do NOT strip rendered proxies, even though they're regeneratable — they're part of the bundle and stripping risks breaking the project. Bundle is an atomic unit.
- The 164 GB `mmc_archive/2020_beyers_vid/` wedding video case: classification depends on what's in there — if it's a project bundle, treat as such; if it's source DV + finished mp4, place under `movies/other/2020_beyers_vid/` and emit a review note about whether to keep DV originals + finished render or just the finished render.

**Critical files:**
- `post_migration/videos_sort.sh` (new) — orchestrator
- `post_migration/videos_sort.py` (new) — does the work

### Phase 6 — Documents

**Why:** documents should keep their original folder structure (the user's organization) under a `documents/` root, with source-context preserved.

**Actions:**
- Find all document files (`.pdf`, `.doc{,x}`, `.xls{,x}`, `.ppt{,x}`, `.txt`, `.rtf`, `.pages`, `.numbers`, `.key`, `.md`, `.odt`, `.tex`)
- Place under `documents/<source-context>/<original-relative-path>`
  - `source-context` = top-level source dir slug (`snashome_david_Documents`, `users_mmc_Desktop`, etc.)
- Optional: hash-dedup across the documents/ tree — defer pending user decision (small disk footprint vs. losing path context)

**Critical files:**
- `post_migration/documents_collect.sh` (new) — straightforward rsync with file-type filter

### Phase 7 — Personal trees: `.bw`, `images`, `app-data`, miscellaneous

**Why:** content that's clearly David's or Maureen's but doesn't fit a global category goes in their personal folders.

**Actions:**
- **`.bw` content** — find every `**/.bw/**` path under david-owned source trees. Hash-dedup. Place under `david/.bw/<original-relative-path-after-.bw>`. Maureen's trees are not expected to have `.bw` — confirm in inventory.
- **`images/`** — receives web-downloaded photos identified in Phase 4 (already routed there)
- **`app-data/`** — application data the user wants kept for possible future recovery. From the rsync exclude analysis, the kept-by-default categories are: 1Password vaults, Quicken / TurboTax records, OmniFocus / Things DBs, Skype chats, Bento DBs, AddressBook, Mail (Maildir/mbox), GarageBand loops & projects, Steam saves, Minecraft saves. Each gets a subdir under `david/app-data/<app>/` or `mmc/app-data/<app>/`.
- **Miscellaneous personal content** — anything categorized as user-data but not matching above (random user-created folders, scripts, dotfiles) → `david/<original-relative-path>` or `mmc/<original-relative-path>` preserving the in-user folder structure
- **Per-user assignment**: source path under `david/` or `mmc/` → respective user. Source path under `users/<other-uid>/` → all such content ultimately belongs to either david or mmc (this NAS only ever had two real users, plus historical LDAP UIDs). When the right answer isn't obvious from path or content, flag for user review rather than guessing.

**Critical files:**
- `post_migration/personal_collect.sh` (new) — per-user pass

### Phase 8 — Skip-by-construction (no destructive phase needed)

Under the new "read SSD, write curated layout" strategy, content the user wants to drop is simply **never copied** into the curated layout in the first place. There's no retroactive-delete pass:

- **Game installs** (Minecraft, Steam, Battle.net, Unreal Tournament, etc.) — Phase 1 inventory classifies as `game-install` → not read by Phases 3–7
- **Old app installs** in user `Applications/` dirs — classified as `app-install` → not read
- **Download dumps** — classified as `download-dump` → not read
- **Application "exhaust"** (Caches, PubSub, SyncServices, Database/Faces, photoslibrary/resources & Thumbnails) — same as the rsync exclude set → not read
- **NAS-internal directories** — `nas-internal` classification → not read
- **`/volume1/rsync`** — Pi backup target on the OLD NAS only; not on SSDs. User recreates the Pi backup job pointing at DS225+ post-cleanup.

The classification map from Phase 1 is the audit trail showing what was excluded and why. Nothing is deleted from the SSDs (per Hard Guard #1).

### Phase 9 — Anomaly review

**Why:** anything not classified by Phase 1, or anything Phases 3–8 couldn't decide on, surfaces here for user case-by-case decision.

**Actions:**
- After Phases 3–8 run, what remains in `snashome/`, `users/`, etc. should be empty or near-empty. Whatever survives is the anomaly set.
- Walk what's left, emit `cleanup_anomalies.md` — one entry per surviving file/dir > 10 MB, with size, path, suggested action
- Categories of anomaly to expect:
  - **VM disk images** — `.pvm`, `.hdd`, `.vmdk`, `.vdi`, `.vhd`. Per the original plan inventory, ~3 GB of VM/installer files. User likely wants to keep specific images and drop installers. Manual decision per file.
  - **DMG / ISO** — `.dmg`, `.iso`. Mix of OS install media (drop) and user-created images (keep). Manual decision.
  - **Source code / scripts** — small but contextual. Default: route to `david/code/` or `mmc/code/` preserving structure.
  - **Email** — Apple Mail Maildir/mbox lives under `Library/Mail/`. Already routed to `app-data/Mail/` in Phase 7.
  - **Truly unknown** — flagged.
- User fills in actions; `apply_anomaly_decisions.sh` actions them.

**Critical files:**
- `post_migration/anomalies.sh` (new) — produces the review doc
- `post_migration/apply_anomaly_decisions.sh` (new) — actions the user-marked decisions

### Phase 10 — Move staging into final position

**Why:** until now, the curated layout was being built under `/volume1/staging/` to keep Hard Guard #2 (never modify `/volume1/{music,photos,...}` once built) trivially enforceable during the build. After Phase 9 sign-off, staging is promoted to the final layout.

**Actions:**
- Verify staging matches expectation (rough size, top-level dir count).
- **btrfs snapshot** of `/volume1/` immediately before the `mv` — DS225+ runs btrfs, snapshots are instant and metadata-only. Gives a one-command rollback if Phase 10 goes wrong. Synology DSM exposes this via `btrfs subvolume snapshot` (or Snapshot Replication). Suggested name: `volume1-pre-promote-<YYYYMMDD-HHMM>`.
- `mv /volume1/staging/{music,photos,movies,documents,david,mmc} /volume1/`
- `rm -rf /volume1/staging` (only if empty).
- From this point on, the curated layout dirs are read-only by convention; reruns of any cleanup phase refuse to write to them.
- Snapshot can be retained for a grace period (e.g., until Phase 11 verification + gap-fill clears) and then released to reclaim metadata space.

**Critical files:**
- `post_migration/promote_staging.sh` (new) — single-purpose mover with snapshot-then-move-then-verify; aborts before the `mv` if the snapshot creation fails.

### Phase 11 — DS1512+ verification cross-check, gap-fill, decommission

**Why:** the SSDs were the read source for the build, but they may have been incomplete (the deferred `users/mmc/Library/` tree, anything that stalled and got skipped, anything excluded by an over-broad pattern). The DS1512+ still has the original data. Before decommissioning it, verify the curated layout against the DS1512+ contents.

**Sub-phases:**

**11a — Inventory DS1512+** (lightweight)
- SSH to DS1512+, walk `/volume1/snashome/` and `/volume1/users/` (skip the always-skip patterns: graveyards, NAS-internal, games, app installs)
- Output a manifest: relative path + size + mtime for every file
- Use `find` with `-printf` rather than reading file content — readdir-only, fastest possible scan on the degraded array
- Retry-loop wrapper similar to `nas_backup.sh` (Phase 11a may stall multiple times; tolerate it)

**11b — Inventory DS225+ curated layout**
- Same shape: relative path + size + mtime for every file under `/volume1/{music,photos,movies,documents,david,mmc}/`
- Plus a content fingerprint per file (size + first/last 64KB hash, fast — full SHA-256 only if needed)

**11c — Reconcile**
- For each DS1512+ file: is content equivalent represented in DS225+?
  - **Same filename + size** → assume match (filename collisions across reorganization are tolerable — we're checking presence, not lineage)
  - **Different name but matching content fingerprint** → assume match (file was renamed during curation)
  - **No match** → flag in `cleanup_gaps.md` with size, DS1512+ path, suggested category
- The `users/mmc/Library/` tree is expected to dominate the gap list (deferred during initial backup)

**11d — Selective gap-fill**
- User reviews `cleanup_gaps.md`, marks each entry `[ ] fetch / [ ] skip`
- Fetch: rsync from DS1512+ → DS225+ staging area (re-using the daemon-mode trick to bypass DS1512+'s SSH AES-NI ceiling), then run the appropriate cleanup phase script on the fetched content to integrate into the curated layout
- Skip: noted in the manifest as intentionally-not-on-DS225+

**11e — DS1512+ decommission**
- After 11d completes and user signs off on the gap-fill outcome:
  - DS1512+ powered down, drives wiped or repurposed
  - Final state: DS225+ has the curated layout, SSDs remain as belt-and-suspenders archive

**Critical files:**
- `post_migration/verify_ds1512.sh` (new) — orchestrator running 11a–11c, produces gap report
- `post_migration/inventory_ds1512.py` (new) — does the manifest walk with retry logic
- `post_migration/reconcile.py` (new) — DS1512+ vs DS225+ reconciliation
- `post_migration/gap_fill.sh` (new) — actions the user-marked gap decisions

**Verification:**
- After 11d, re-run `verify_ds1512.sh`; expected output: only entries the user explicitly marked `skip`. Anything else means gap-fill missed something.

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
- **Phase 4**: spot-check 10 random photos (readable, EXIF preserved); web-candidate spot-check passes user review; album organization sanity check on a known album.
- **Phase 5**: every project bundle is intact (open in iMovie/FCP if curious); standalone count matches expectation.
- **Phase 6**: file count under `staging/documents/` ≈ classifier's `document` count; spot-check folder structure preservation.
- **Phase 7**: `staging/david/.bw/` deduped (no two files with same hash); `staging/david/images/` matches Phase 4's web-candidate set after user review.
- **Phase 9**: after applying anomaly decisions, the classifier's `unknown` set has been resolved (kept-with-target, dropped, or fetch-from-DS1512+).
- **Phase 10**: `ls /volume1/staging` reports empty; `ls /volume1/{music,photos,movies,documents,david,mmc}` matches expectation; staging dir removed.
- **Phase 11**: re-run `verify_ds1512.sh` after gap-fill; expected output is only entries the user explicitly marked `skip`. DS1512+ powered down once that holds.

Roll-back path for any phase: restore from the SSDs (untouched, read-only throughout the build) or the DS1512+ (until decommissioned). Document SSD-path → DS225+-path mapping so partial restores are easy.

## Decisions made (during plan walkthrough, 2026-05-04)

- **User dirs:** keep `david/` and `mmc/` (not `maureen/`). Any "maureen"-tagged content treated as `mmc` via normal dedup.
- **`www/`:** deferred — not in active scope. Revisit only if Phase 9 surfaces something.
- **`users/<other-uid>/` UIDs:** all such content belongs to david or mmc. Phase 7 flags the ambiguous ones for user review rather than guessing.

## Open questions for the user

These are best resolved before Phase 3, but none gate Phase 1 (inventory):

1. **Comedy artist list** — confirm the workflow (enumerate → user marks each artist) is OK, or do you want to seed an initial list (e.g., specific artists from "Nappy Tunes" you remember)?
2. **Photo edits format** — for `*.photoslibrary` (Photos.app era), edits aren't stored as a separate JPEG; they're rendered output paired with adjustment XMP-like sidecars under `resources/`. Plan: spike at start of Phase 4 to confirm. Acceptable?
3. **App-data scope** — the keep-by-default list (1Password, Quicken/TurboTax, OmniFocus/Things, Skype, Bento, AddressBook, Mail, GarageBand projects, Steam saves, Minecraft saves) — anything to add or drop?
4. **Documents dedup** — preserve folder structure verbatim (default), or also hash-dedup across the documents tree? Path context vs. disk savings.
5. **Web-photo heuristic threshold** — false-positive risk. Default: anything without camera EXIF gets flagged for review. Acceptable?
6. **DS1512+ decommission timing** — power down DS1512+ as soon as Phase 11 verification + gap-fill succeeds, or hold for a grace period (e.g., 30 days) in case something surfaces later?
7. **iTunes Music Library files** (`iTunes Library.itl`, `iTunes Music Library.xml`) — application metadata that could regenerate iTunes' view of the library, but useless without iTunes. Default: drop. Confirm.
8. **Phase 11 reconciliation strictness** — match by filename+size (looser, fewer false-gap-flags) or by content fingerprint (stricter, catches renamed-on-import cases)? Default: fingerprint with size as a fast pre-filter.

## Out of scope (deferred)

- **Aggressive content-archive rebuild** — already de-scoped in the prior plan.
- **Mutation on the SSDs.** They stay as read-only source during the build and a third-copy archive forever after.
- **Mutation on the DS225+ curated layout** once Phase 10 promotes staging into final position. Cleanup is build-once.
- **Mail re-extraction to mbox/Maildir** — handled by Phase 7 routing as `app-data/Mail/`. Format conversion deferred.
- **Refactor of `excludes.txt`** in the backup scripts — hygiene, not blocking; deferred as a future small PR.
- **Re-encode pass on duplicate-but-not-byte-identical media** (e.g., re-saved JPEGs that differ only by quality) — visual-similarity dedup is hard and out of scope.
