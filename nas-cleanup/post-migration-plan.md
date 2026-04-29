# Post-DS225+ Migration Cleanup

## Context

The DS1512+ → DS225+ migration is the next major step in the nas-cleanup project (Phase 1: SSDs → DS225+ via USB; Phase 2: NAS-to-NAS rsync via daemon mode). Once the DS225+ has all the data, the user wants to do a **post-cutover cleanup pass on the DS225+ only** to convert what is currently a faithful backup of a messy filesystem into a clean preserved-data archive.

The user's stated goals:
1. Remove the application/system noise the rsync excludes have been catching (Caches, `.app` bundles, SyncServices, etc.) — applied retroactively as deletes on the destination
2. Hash-dedup byte-identical photos and music across the overlapping iPhoto / Photos / iTunes libraries
3. Inventory remaining large files (Parallels images, big videos, disk images) for case-by-case manual decisions

User explicitly does **not** need to restore the data to a Mac, phone, or other computer — this is purely a data archive (photos, mp3s, emails, documents). That assumption simplifies several decisions: e.g., it's OK to break a `.photoslibrary` bundle's internal references because we'll never reopen it in Photos.app.

**Key inventory findings** (from explore-agent scan of `/Volumes/ds_backup{,_2}/` 2026-04-28):

- **~650 MB** of cleanable noise (Caches, PubSub, SyncServices, app bundles, photo Database/Faces, etc.) — small absolute size, but worth doing for hygiene
- **~674 GB** in three overlapping photo libraries — the real dedup opportunity
  - `mmc_archive/Pictures/Photos Library 2.photoslibrary` 260 GB
  - `OldPhotoDirectories/Photos_Library.photoslibrary` 186 GB
  - `OldPhotoDirectories/iPhoto_Library.migratedphotolibrary` 228 GB
- **~792 GB** in iTunes media (`/Volumes/ds_backup_2/mp3/iTunes/`) — likely heavy internal duplication and now-unwanted TV/movie content
- **~164 GB** in a single video archive (`mmc_archive/2020_beyers_vid/` — wedding video + multiple proxies)
- **~3 GB** of old VM/installer files (Parallels installers, one Virtual PC image) — low-value retention candidates

Cleanup runs **on the DS225+**, never on the SSDs (which become the third-copy archive).

## Approach

Five phases. Each ships its own script. All phases are designed to be **idempotent** and **dry-run by default** — every script supports a `--dry-run` flag (default) and an explicit `--apply` flag to actually mutate the filesystem. This is critical because we are destructively modifying the canonical archive.

Repo layout: extend `nas-cleanup` with new scripts under `~/github/nas-cleanup/post_migration/` (new subdirectory to keep the migration backup scripts at the repo root unchanged).

### Phase 1 — Refactor exclude patterns into shared source

**Why:** the cleanup phase must apply the SAME pattern set the rsync excludes use, otherwise the two will drift. Today the patterns are duplicated across `nas_backup.sh`, `nas_backup_mp3.sh`, `nas_backup_photos.sh`, and `nas_ofd_backup.sh`.

**Actions:**
- Create `excludes.txt` at repo root — one pattern per line, no rsync-flag wrapping
- Add a small helper `_load_excludes.sh` that converts each line into `--exclude='<line>'` flags for rsync
- Refactor each `nas_backup*.sh` to source `_load_excludes.sh` and substitute into the rsync invocation (preserves all current per-script logic; just centralizes the pattern list)
- Cleanup scripts in later phases also read `excludes.txt`

**Critical files:**
- `excludes.txt` (new)
- `_load_excludes.sh` (new)
- `nas_backup.sh`, `nas_backup_mp3.sh`, `nas_backup_photos.sh`, `nas_ofd_backup.sh` (refactor)

**Note:** anchored patterns like `/mmc/Library` (used in `nas_backup.sh` only) stay in the script that uses them — `excludes.txt` is for the universal patterns.

### Phase 2 — Noise removal on DS225+

**Why:** strip the cruft that's been getting filtered out at backup time. ~650 MB reclaim, but more importantly removes irrelevant data that would clutter dedup hashing in later phases.

**Actions:**
- New script: `post_migration/cleanup_noise.sh` — runs **on the DS225+** (executed via `ssh admin@ds225 bash -s < cleanup_noise.sh` from the Mac, or copied to the NAS and run there)
- For each pattern in `excludes.txt`, run `find <root> -type d -path '*<pattern>' -prune -print` (dry run) or `... -exec rm -rf {} +` (apply mode)
- Special case for the few patterns that match files (not directories) — handled separately
- Always logs what would be / was removed to a timestamped log file
- **Hard guard:** script must refuse to run unless invoked under a known DS225+ path prefix (`/volume1/...`); explicit safety check against accidentally pointing it at an SSD

**Critical files:**
- `post_migration/cleanup_noise.sh` (new)
- Reads `excludes.txt`

**Verification:** dry-run on DS225+ with output diffed against expected list (the patterns in `excludes.txt`); then apply; then re-run dry-run to confirm it now reports zero matches (idempotency check).

### Phase 3 — Large-file inventory

**Why:** the user wants to manually decide on Parallels images, the 164 GB wedding video, big disk images, etc. — not delete blindly.

**Actions:**
- New script: `post_migration/inventory_large.sh` — runs on DS225+
- `find /volume1/<root> -type f -size +1G -printf '%s\t%p\n' | sort -rn`
- Categorize by extension and path heuristics:
  - VM images: `*.pvm`, `*.hdd`, `*.vmdk`, `*.vdi`, `*.vhd`
  - Disk images: `*.dmg`, `*.iso`
  - Video: `*.mov`, `*.mp4`, `*.avi`, `*.dv`
  - Photos library internals: paths under `*.photoslibrary/`
  - Other
- Output: a plain Markdown table per category with size, path, and a `[ ] keep / [ ] delete` checkbox the user can fill in
- Output goes to `~/nas_large_files_review.md` on the user's Mac (scp from DS225+ at end)
- **No deletion in this script** — purely produces the review document

**Critical files:**
- `post_migration/inventory_large.sh` (new)

**Follow-on:** once user marks the file with keep/delete decisions, run `post_migration/apply_large_decisions.sh` (also new, also dry-run-by-default) to action the deletions.

### Phase 4 — Photo dedup

**Why:** the three overlapping `.photoslibrary` / iPhoto libraries almost certainly share most originals. Hash dedup across all of them, keeping one copy.

**Actions:**
- New script: `post_migration/dedup_photos.sh` — runs on DS225+ (likely needs Python, which DSM ships)
- Walks `Masters/` (iPhoto-era) and `originals/` (modern Photos-era) inside every `*.photoslibrary` and `*.migratedphotolibrary` plus loose `iPhoto_Library*` dirs
- Computes SHA-256 of each file, stores in a SQLite index (`/tmp/photo_dedup.db`) so reruns are cheap
- For each hash with >1 file: keeps the copy in the **largest library** (most likely canonical), deletes the others
- The deletion is the trick: removing a `Masters/` file breaks Photos.app's reference to it, but per user direction we will never reopen these libraries in Photos.app, so this is acceptable. Library bundles become "ragged" but the unique files stay accessible.
- Outputs a per-pair "kept X, deleted Y" log
- `--dry-run` mode produces a CSV (path, hash, action) the user can review before `--apply`

**Critical files:**
- `post_migration/dedup_photos.sh` (new)
- `post_migration/dedup_photos.py` (new — does the SHA-256 work)

**Caveat:** byte-identical only. Photos that were re-encoded between libraries (e.g., a JPEG re-saved at different quality) will look like duplicates to a human but be different to sha256. Documented as a limitation; the user's stated goal is "duplicates" which is what this does.

### Phase 5 — Music dedup

**Why:** same logic for the iTunes media tree (~792 GB). Multiple iTunes libraries on the source likely have many of the same tracks, plus internal duplicates from re-imports (the user already noted "Track 1.m4a" iTunes-duplicate-import suffixes resolved earlier in `mp3/iTunes/iTunes Music/A Paris/`).

**Actions:**
- New script: `post_migration/dedup_music.sh` — same shape as the photo dedup, scoped to `*.mp3`, `*.m4a`, `*.m4p`, `*.aif`, `*.wav`, `*.flac`
- Same SHA-256 → SQLite → keep largest-library approach
- Walks the entire mp3 tree (it's all on `ds_backup_2/mp3/` so will be on `/volume1/<wherever-mp3-lives>` on DS225+)
- Same `--dry-run` / `--apply` discipline

**Critical files:**
- `post_migration/dedup_music.sh` (new)
- `post_migration/dedup_music.py` (new)

## Critical files (summary)

**Modify:**
- `nas_backup.sh`, `nas_backup_mp3.sh`, `nas_backup_photos.sh`, `nas_ofd_backup.sh` — refactor to read shared excludes
- `CLAUDE.md` — document the new `post_migration/` workflow and ordering

**Create:**
- `excludes.txt`
- `_load_excludes.sh`
- `post_migration/cleanup_noise.sh`
- `post_migration/inventory_large.sh`
- `post_migration/apply_large_decisions.sh`
- `post_migration/dedup_photos.sh` + `dedup_photos.py`
- `post_migration/dedup_music.sh` + `dedup_music.py`

**Reuse:**
- The exclude-pattern set already developed in `nas_backup.sh` is the source of truth for Phase 2 (extracted to `excludes.txt`)
- The existing `nas_cleanup.sh` (current macOS junk remover on `/Volumes/ds_backup/`) is **not** reused — its scope is narrower and SSD-targeted; the new `cleanup_noise.sh` is broader and DS225+-targeted

## Ordering

Strict ordering matters because each phase changes what later phases see:
1. Migration completes → DS225+ has all data
2. **Phase 1** (exclude refactor) — non-destructive, can be done anytime; ideally before migration runs so Phase 2 works as soon as DS225+ has data
3. **Phase 2** (noise removal) — first, because it strips cruft that would otherwise pollute dedup hashes
4. **Phase 3** (large-file inventory) — produces the review doc; user reviews on their schedule
5. **Phase 4** (photo dedup) — independent of Phase 3
6. **Phase 5** (music dedup) — independent
7. User actions Phase 3 review doc with `apply_large_decisions.sh`

## Verification plan

End-to-end testing happens incrementally. At each phase:

- **Phase 1:** Run `nas_backup.sh --dry-run` (after refactor) and confirm the rsync command line includes the same excludes as before the refactor. Verify by capturing the full rsync command both before and after refactor and `diff`-ing.
- **Phase 2:** Run `cleanup_noise.sh --dry-run` on DS225+; expected output is the list of all dirs matching the excludes. Run `--apply`. Re-run `--dry-run`; expected output is empty (idempotent).
- **Phase 3:** Run `inventory_large.sh`; verify the output Markdown is well-formed and the categories make sense. Spot-check the largest 5 files in each category against `du`.
- **Phase 4:** Run `dedup_photos.sh --dry-run`; review the CSV — confirm that the "keep" column always names a file in the largest library, and the "delete" column never has the same file path as a "keep". After `--apply`, sample 10 random photos by hash from the kept library to confirm they're still readable. Confirm total free space on DS225+ increased by approximately the dedup CSV's reported reclamation.
- **Phase 5:** Same as Phase 4 but for music files. Spot-check by playing a few tracks from the kept library.

Roll-back path for any phase: restore from one of the SSDs (which we've deliberately left untouched). Document which SSD path maps to which DS225+ path so a partial restore is easy.

## Out of scope (deferred)

- **Aggressive content-archive rebuild** (extracting `Masters/` out of every `.photoslibrary` into a flat `/archive/photos/` tree). User chose to defer; can be a Phase 6 later.
- **Cleanup on the SSDs themselves.** They stay as untouched belt-and-suspenders archive.
- **Decommissioning the DS1512+.** That happens on its own timeline once the DS225+ + cleanup are verified.
- **Mail re-extraction** to mbox/Maildir format. Mail data is small (<500 MB); leave in place for now.

## Open questions for the user

None blocking — happy to start when the migration completes. Two things worth deciding before then, but not gating:

1. Whether to also dedup files **within** a single library (e.g., Photos.app's own `.photoslibrary/Masters/` sometimes has byte-identical files due to import quirks). Default plan = yes (the dedup just operates on all files in one pass).
2. Threshold for "large file" review in Phase 3. Default = 1 GB. Higher threshold = fewer files to review but might miss some. Lower = more review work.
