# nas-cleanup — Context Summary

## Overview

Backing up a failing Synology DS1512+ NAS (10.0.0.2) to a local SSD (`/Volumes/ds_backup{,_2}/`) before decommissioning. Array is degraded RAID6 (3/5 drives) — urgent. Scripts are `~/github/nas-cleanup/nas_*.sh` on the Mac. New NAS (DS225+, 2×4TB RAID1) on hand. Strategy shifted 2026-04-29: SSDs become the read source for the curated-layout build on DS225+, with DS1512+ used only as a final cross-check, not as a primary copy source.

## Current State

`nas_backup.sh` now wraps each per-directory rsync in a retry-until-exit-0 loop and has an extensive metadata-graveyard exclude set. Across two days (2026-04-28/29) the exclude set was hardened in eleven commits (currently on PR #5, branch `retry-until-success`):
- (#1–3, 2026-04-28) readdir-stall + defunct-service graveyards, FileSync, defer `users/mmc/Library`
- (PR #5, 2026-04-29) retry loop; game launchers (minecraft/techniclauncher/Steam/Battle.net/Blizzard/Origin/Epic/GOG/Unity/MultiMC/GameKit); defunct Apple apps (iWeb/iDVD/iChat); broadened `*.caldav` to `**/*.caldav` (catches nested `Calendars/Unmigrated/<UUID>.caldav/`); `**/Downloads` + `**/My Downloads`; `**/Library/{Contextual Menu Items, Logs, CrashReporter, Saved Application State}`; defer `users/mmc_OldUserFiles/Library` (mirrors the 2026-04-28 mmc deferral after 6 successive stalls landing there, last being Mail/V2/AosIMAP-dglcinc/Sent Messages.mbox attachments).

`users/david/Library` is the only `users/<user>/Library` tree still in scope for the active backup; both mmc-flavored Library trees are deferred to DS225+ Phase 11 gap-fill via daemon-mode rsync. `nas_cleanup.sh` (post-rsync junk remover) now runs clean — exclude set catches everything before it lands on the SSD.

**Migration strategy** (revised CLAUDE.md):
- **Phase 1**: plug SSDs into DS225+ via USB (read-only, ~400 MB/s)
- **Phase 2**: build curated layout on DS225+ from SSDs (no NAS-to-NAS rsync as primary path)
- **Phase 3 / cleanup-Phase-11**: DS1512+ verification cross-check (inventory, reconcile, selective gap-fill via daemon-mode rsync, decommission)

**Sandbox / hook plumbing** (claude-contexts):
- New `hooks/pre-tool-sandbox-bypass.sh` PreToolUse Bash hook denies `dangerouslyDisableSandbox: true` on git/ssh/docker/gh
- `setup.sh` extended to install on any Mac (Darwin gate): adds git/docker/ssh/gh to `sandbox.excludedCommands`, adds `$HOME/github` + ds_backup volumes to `filesystem.allowWrite`, registers the hook
- Pi sandbox config skipped (no sandbox there)
- Caveat: `gh` still has unresolved sandbox TLS verify issue — works in shell, fails for Claude Code's gh calls when sandboxed. Either expand `sandbox.network` or live with it.

## Next Steps

1. **Let the active backup finish** — `users/` iteration should now process only david's tree.
2. **Merge PR #5** when the rsync settles. Seven commits stacked; all related.
3. **DS225+ migration** following the rewritten plan (`~/github/claude-contexts/nas-cleanup/post-migration-plan.md`):
   - Plug SSDs into DS225+ → build curated layout under `/volume1/staging/{music,photos,movies,documents,david,maureen}/`
   - Phases 1–7 build content into staging (inventory → scaffold → music → photos → videos → documents → personal)
   - Phase 8 is a no-op (skip-by-construction); Phase 9 is anomaly review; Phase 10 promotes staging into final layout
   - Phase 11 verifies against DS1512+, gap-fills (especially the deferred Library trees), then decommissions
4. **Answer 11 open questions** in the plan before Phase 3 starts (comedy filter, photo edits spike, maureen↔mmc, users/<other-UID>/, app-data keep-list, documents dedup, web-photo heuristic, decommission timing, www/, iTunes Library files, reconciliation strictness).
5. **Decide on the user's `NAS Cleanup.md`** at repo root — it's still untracked. Source-of-truth cleanup spec; probably commit it.
6. **Optional follow-ups**: refactor `excludes.txt` shared across `nas_backup*.sh` (deferred hygiene), resolve `gh` sandbox TLS so PR ops work without bypass.
