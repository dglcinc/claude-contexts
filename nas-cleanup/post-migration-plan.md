# Post-DS225+ Migration Cleanup

## Context

After the DS1512+ → DS225+ migration completes (Phase 1: SSDs → DS225+ via USB; Phase 2: NAS-to-NAS rsync via daemon mode), the DS225+ holds a faithful but messy archive of ~13 years of Mac home directories from `snashome/` and `users/` (and any other backup dirs found under `/volume1/`). The cleanup converts that into a curated, application-agnostic content archive organized by content type, not by user-Mac-of-origin.

The user explicitly does **not** need to restore the data to a Mac, phone, or iPhoto/Photos.app — this is a preserved-data archive (photos, music, video, documents). That assumption simplifies several decisions: it's OK to break a `.photoslibrary` bundle's internal references because we'll never reopen it.

Cleanup runs **on the DS225+**, never on the SSDs (which become the third-copy archive). All scripts are dry-run by default with explicit `--apply` to mutate.

**Source scope**: everything under `/volume1/` on the DS225+ after migration. Notable sources expected:
- `snashome/` — more recent shared mounts (david, mmc, mmc_archive, OldPhotoDirectories, mp3, old_fileserver_stuff, users, www)
- `users/` — older LDAP-era home directory experiment, same era of content
- `rsync/` — Pi backup target, will be deleted (user will recreate after cleanup)
- `www/` — to be reviewed; not currently in any backup script
- Any other top-level dirs found — flagged for review

NAS-specific directories (DSM internals like `@appstore`, `@database`, etc.) are not preserved.

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
  maureen/
    [same shape as david/]
  cleaned/                         — staging dir during cleanup; removed at end
```

Sources under `snashome/` and `users/` are read during cleanup; once a content type is migrated and verified, the corresponding source subtree is deleted.

`maureen` ≡ `mmc` in the source tree — confirm before renaming.

## Phases

All phases produce CSV/Markdown reports on dry run. `--apply` performs the destructive action. Each script is idempotent and re-runnable.

### Phase 1 — Inventory and classification

**Why:** before touching anything, produce a single classification map of every top-level subtree on the DS225+. The user reviews the map and approves before any phase ≥ 3 runs.

**Actions:**
- Walk `/volume1/<top-level-dirs>` to depth 3
- For each dir at depth 1–3, classify by heuristic:
  - **photo-library**: contains `*.photoslibrary`, `*.migratedphotolibrary`, `iPhoto Library*`, or `Masters/`+`Database/` siblings
  - **music**: predominantly `.mp3`/`.m4a`/`.flac`/`.aif`/`.wav`
  - **video**: predominantly `.mov`/`.mp4`/`.avi`/`.dv`
  - **video-project**: `*.iMovieProject`, `*.fcpbundle`, `*.imovielibrary`
  - **documents**: predominantly `.pdf`/`.doc{,x}`/`.xls{,x}`/`.txt`/`.rtf`/`.pages`/`.numbers`/`.key`/`.md`
  - **app-install**: `.app` bundles or installer pkg/dmg trees outside system Applications
  - **download-dump**: dirs literally named `Downloads`, or containing only browser-cache-shaped content
  - **game-install**: known patterns (Minecraft `*.jar` + `versions/`, Unreal Tournament `Engine/`, Steam `steamapps/`, etc.)
  - **app-data**: known per-app dirs (Skype chat DBs, GarageBand projects, OmniFocus, Quicken, TurboTax, 1Password, AddressBook, Mail Maildir/, etc.)
  - **bw**: any path matching `**/.bw/**`
  - **nas-internal**: `@appstore`, `@database`, `#recycle`, etc.
  - **unknown**: everything else
- Output: `cleanup_inventory.md` — Markdown table per top-level subtree, with size, classification, and a `[ ] approve / [ ] flag` column
- **No mutation.** User reviews the map and either approves or annotates. Subsequent phases consume this map.

**Critical files:**
- `post_migration/inventory.sh` (new) — orchestrator
- `post_migration/inventory.py` (new) — classifier

### Phase 2 — Target layout scaffold

**Why:** create the empty `music/`, `photos/`, `movies/`, `documents/`, `david/`, `maureen/`, `cleaned/` dirs with the right ownership before anything moves in.

**Actions:**
- `mkdir -p` the layout under `/volume1/`
- Set ownership to a single canonical user (per CLAUDE.md, the new NAS uses `admin` or a dedicated user; UID mapping from DS1512+ is not preserved)

**Critical files:**
- `post_migration/scaffold.sh` (new) — trivial; could be inlined

### Phase 3 — Music: dedup, organize, comedy filter, low-bitrate review

**Why:** ~792 GB of iTunes media has heavy internal duplication and now-unwanted content. The user's rules: keep CD rips at higher bitrate, organize Artist/Album/Track, drop comedy artists, optionally drop ≤128 kbps survivors.

**Actions:**
1. **Find** all music files under inventoried music sources: `.mp3`, `.m4a`, `.m4p`, `.aif`, `.wav`, `.flac`
2. **Read tags** (artist, album, title, track #, bitrate) — Python `mutagen`. Filename/path fallback for missing tags
3. **Group by (artist, album, title)** — case-insensitive, normalized
4. **Within each group, keep the highest bitrate**; ties broken by file size (larger wins)
5. **Comedy filter** — emit a `cleanup_music_artists.md` listing every distinct artist found. User marks each `[ ] keep / [ ] comedy`. `--apply` removes everything tagged comedy.
6. **Low-bitrate review** — after dedup, list every surviving track at ≤128 kbps. User reviews `cleanup_music_lowbitrate.md` and marks `[ ] keep / [ ] drop`.
7. **Place winners** at `music/<Artist>/<Album>/<NN Title>.<ext>` (track number zero-padded; missing track # → omit prefix)
8. **Sources unchanged** — copy not move during dry run; `--apply` deletes source after place succeeds

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
- **`app-data/`** — application data the user wants kept for possible future recovery. From the rsync exclude analysis, the kept-by-default categories are: 1Password vaults, Quicken / TurboTax records, OmniFocus / Things DBs, Skype chats, Bento DBs, AddressBook, Mail (Maildir/mbox), GarageBand loops & projects, Steam saves, Minecraft saves. Each gets a subdir under `david/app-data/<app>/` or `maureen/app-data/<app>/`.
- **Miscellaneous personal content** — anything categorized as user-data but not matching above (random user-created folders, scripts, dotfiles) → `david/<original-relative-path>` or `maureen/<original-relative-path>` preserving the in-user folder structure
- **Per-user assignment**: source path under `david/` or `mmc/` → respective user. Source path under `users/<other-user>/` → flag for review (might be old David/Maureen content under a different LDAP UID).

**Critical files:**
- `post_migration/personal_collect.sh` (new) — per-user pass

### Phase 8 — Hard-delete categories

**Why:** content the user has explicitly said to remove. Run after Phases 3–7 have extracted everything they want from the source trees.

**Targets:**
- **Game installs** — Minecraft (path or `*.jar` + `versions/` shape), Unreal Tournament, Steam (`steamapps/common/`), generic game launchers (Origin, Battle.net), per-game Application Support saves that aren't on the keep list
- **Old app installs** in user `Applications/` dirs — `.app` bundles outside `/Applications/`. The existing rsync excludes already drop `Applications (Parallels)` and Parallels' `* Applications.app` shadow bundles; this phase catches the rest.
- **Download dumps** — any dir literally named `Downloads`, plus browser caches the rsync excludes already covered (these are deletes from the source side now).
- **`/volume1/rsync`** — entirely removed (user recreates the Pi backup job)
- **NAS-internal directories** that we're not preserving (per inventory)
- **Application "exhaust"** caught by the existing rsync exclude set: Caches, PubSub, SyncServices, Database/Faces, photoslibrary/resources & Thumbnails, etc. — applied retroactively as deletes since no later phase needs them.

**Actions:**
- `find` each pattern, list, dry-run, `--apply`
- All deletions logged to a timestamped log file
- **Hard guard:** script refuses to run unless invoked under a known DS225+ path prefix (`/volume1/...`); explicit safety check against accidentally pointing it at an SSD

**Critical files:**
- `post_migration/hard_delete.sh` (new) — patterns from a config file (`hard_delete_patterns.txt`)
- `post_migration/hard_delete_patterns.txt` (new) — pattern list, version-controlled

### Phase 9 — Anomaly review

**Why:** anything not classified by Phase 1, or anything Phases 3–8 couldn't decide on, surfaces here for user case-by-case decision.

**Actions:**
- After Phases 3–8 run, what remains in `snashome/`, `users/`, etc. should be empty or near-empty. Whatever survives is the anomaly set.
- Walk what's left, emit `cleanup_anomalies.md` — one entry per surviving file/dir > 10 MB, with size, path, suggested action
- Categories of anomaly to expect:
  - **VM disk images** — `.pvm`, `.hdd`, `.vmdk`, `.vdi`, `.vhd`. Per the original plan inventory, ~3 GB of VM/installer files. User likely wants to keep specific images and drop installers. Manual decision per file.
  - **DMG / ISO** — `.dmg`, `.iso`. Mix of OS install media (drop) and user-created images (keep). Manual decision.
  - **Source code / scripts** — small but contextual. Default: route to `david/code/` or `maureen/code/` preserving structure.
  - **Email** — Apple Mail Maildir/mbox lives under `Library/Mail/`. Already routed to `app-data/Mail/` in Phase 7.
  - **Truly unknown** — flagged.
- User fills in actions; `apply_anomaly_decisions.sh` actions them.

**Critical files:**
- `post_migration/anomalies.sh` (new) — produces the review doc
- `post_migration/apply_anomaly_decisions.sh` (new) — actions the user-marked decisions

### Phase 10 — Source decommission

**Why:** once Phases 3–9 verify clean and the new layout is good, the original `snashome/` and `users/` (and other source dirs) get deleted. Until then, both source and target coexist.

**Actions:**
- After user signs off on each of Phases 3–9 individually, AND after spot-check of the new layout, AND after disk-space sanity check (target tree size matches expectation):
  - `rm -rf /volume1/snashome` (and other migrated sources)
  - The SSD archives remain as belt-and-suspenders
- Final state: `/volume1/{music,photos,movies,documents,david,maureen}` plus DSM internals

**Critical files:**
- Manual operation; no script. The user runs the deletes after signing off on each phase.

## Critical files (summary)

**Modify (none — backup scripts are unchanged by this work):**
- The original Phase 1 of the previous plan (refactor `excludes.txt` shared across `nas_backup*.sh`) is **deferred** — backup is nearly done; refactor is hygiene, not blocking. Can be a future small PR.

**Create under `~/github/nas-cleanup/post_migration/`:**

| File | Purpose |
|------|---------|
| `inventory.sh` + `inventory.py` | Phase 1 classification map |
| `scaffold.sh` | Phase 2 target dir creation |
| `music_curate.sh` + `music_curate.py` | Phase 3 music dedup/organize/filter |
| `photos_curate.sh` + `photos_curate.py` + `photoslibrary_inspect.py` | Phase 4 photo extract/dedup/organize |
| `videos_sort.sh` + `videos_sort.py` | Phase 5 video routing |
| `documents_collect.sh` | Phase 6 document copy |
| `personal_collect.sh` | Phase 7 .bw / images / app-data / misc |
| `hard_delete.sh` + `hard_delete_patterns.txt` | Phase 8 deletes |
| `anomalies.sh` + `apply_anomaly_decisions.sh` | Phase 9 review and apply |

**Output reports** (Markdown checkboxes the user fills in, per phase):

| File | Phase |
|------|-------|
| `cleanup_inventory.md` | 1 |
| `cleanup_music_artists.md` | 3 |
| `cleanup_music_lowbitrate.md` | 3 |
| `cleanup_photos_web_candidates.md` | 4 |
| `cleanup_anomalies.md` | 9 |

## Ordering

1. Migration completes → DS225+ has all data
2. **Phase 1** — inventory; user reviews and approves classification
3. **Phase 2** — scaffold
4. **Phase 3** — music
5. **Phase 4** — photos (after the photoslibrary spike confirms edit-extraction approach)
6. **Phase 5** — videos
7. **Phase 6** — documents
8. **Phase 7** — personal
9. **Phase 8** — hard deletes (only after 3–7 have extracted what they want)
10. **Phase 9** — anomaly review
11. **Phase 10** — source decommission, after user sign-off on the new layout

## Verification plan

- **Phase 1**: user approves the classification map. No mutation, no verification needed.
- **Phase 2**: `ls /volume1/{music,photos,movies,documents,david,maureen,cleaned}` returns six empty dirs.
- **Phase 3**: spot-check 10 random tracks (playable, correct tags); source music tree is empty after `--apply`; free space increased by reported reclamation.
- **Phase 4**: spot-check 10 random photos by hash from kept-library (readable, EXIF preserved); web-candidate spot-check passes user review; album organization sanity check on a known album.
- **Phase 5**: every project bundle is intact (open in iMovie/FCP if curious); standalone count matches expectation.
- **Phase 6**: file count under `documents/` ≈ source document file count; spot-check folder structure preservation.
- **Phase 7**: `david/.bw/` deduped (no two files with same hash); `david/images/` matches Phase 4's web-candidate set after user review.
- **Phase 8**: re-run dry-run after `--apply`; expected zero matches (idempotent).
- **Phase 9**: after applying anomaly decisions, source dirs are empty or contain only items user explicitly opted to keep in place.
- **Phase 10**: post-decommission, `du -sh /volume1/*` shows the curated layout only; DS225+ free space matches projection.

Roll-back path for any phase: restore from the SSDs (untouched). Document SSD-path → DS225+-path mapping so partial restores are easy.

## Open questions for the user

These are best resolved before Phase 3, but none gate Phase 1 (inventory):

1. **Comedy artist list** — confirm the workflow (enumerate → user marks each artist) is OK, or do you want to seed an initial list (e.g., specific artists from "Nappy Tunes" you remember)?
2. **Photo edits format** — for `*.photoslibrary` (Photos.app era), edits aren't stored as a separate JPEG; they're rendered output paired with adjustment XMP-like sidecars under `resources/`. Plan: spike at start of Phase 4 to confirm. Acceptable?
3. **`maureen` ≡ `mmc`** — confirm. The source uses `mmc`; you wrote `maureen` in the instructions. I'll rename `mmc/` → `maureen/` at placement time unless you want to keep `mmc` as the dirname.
4. **`users/<other-user>/` UIDs** — the older LDAP-era `users/` dir likely contains UIDs for david and mmc plus possibly others. Each non-david/non-mmc UID's content needs a manual call: assign to one of david/maureen, drop, or treat as separate.
5. **App-data scope** — the keep-by-default list (1Password, Quicken/TurboTax, OmniFocus/Things, Skype, Bento, AddressBook, Mail, GarageBand projects, Steam saves, Minecraft saves) — anything to add or drop?
6. **Documents dedup** — preserve folder structure verbatim (default), or also hash-dedup across the documents tree? Path context vs. disk savings.
7. **Web-photo heuristic threshold** — false-positive risk. Default: anything without camera EXIF gets flagged for review. Acceptable?
8. **Source decommission timing** — delete `snashome/`/`users/` immediately after Phase 9 sign-off, or hold for a grace period (e.g., 30 days) in case something's missing?
9. **`www/` and any other untouched source dirs** — these aren't in any backup script and weren't classified by the original work. Treat per Phase 1 inventory output (default: classify and ask) — confirm.
10. **iTunes Music Library files** (`iTunes Library.itl`, `iTunes Music Library.xml`) — application metadata that could regenerate iTunes' view of the library, but useless without iTunes. Default: drop. Confirm.

## Out of scope (deferred)

- **Aggressive content-archive rebuild** — already de-scoped in the prior plan.
- **Cleanup on the SSDs.** They stay as untouched archive.
- **Decommissioning the DS1512+** — separate timeline once DS225+ + cleanup verified.
- **Mail re-extraction to mbox/Maildir** — handled by Phase 7 routing as `app-data/Mail/`. Format conversion deferred.
- **Refactor of `excludes.txt`** in the backup scripts — hygiene, not blocking; deferred as a future small PR.
- **Re-encode pass on duplicate-but-not-byte-identical media** (e.g., re-saved JPEGs that differ only by quality) — visual-similarity dedup is hard and out of scope.
