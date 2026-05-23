# WilhelmSK — Context Summary

## Overview

Marine-instrument display app for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner.

## Current State

- **Branch:** `docs/user-guide` (pushed to origin, 11 commits, PR to `development` pending)
- **Build:** confirmed working on both MacBook (Xcode 26.5) and utilityserver (Xcode 26.4)
- Full documentation in `docs/` — user-guide.md, architecture.md, contributing.md, MkDocs site config
- `HelpWebViewController` added: Settings → Help / Documentation opens bundled WKWebView docs with remote fallback
- `.claude/` directory committed to repo (Scott approved): analysis.md, UTILITYSERVER_SETUP.md, setup-utilityserver.sh
- utilityserver fully configured as dev machine — SSH, repos cloned, simulators installed

## Next Steps

1. Open PR to `sbender9/Wilhelm` targeting `development`
2. Add `Wilhelm/wilhelmsk-docs/` to Xcode as folder reference (rebuild first: `python3 -m mkdocs build --config-file mkdocs.yml --site-dir Wilhelm/wilhelmsk-docs`)
3. Fix broken MkDocs anchor `#layout-editor` in user-guide.md
4. Consider `dglcinc/signalk-wsk-docs` plugin — serves docs from SignalK server locally
5. Code contributions — review Tier 1 from `.claude/analysis.md` with Scott on Discord

## Key Facts

- **PRs target `development`** (not `master` or `new-watch-app`)
- **Remote:** `git@github.com:sbender9/Wilhelm.git` (SSH)
- **Bundle ID:** `com.scottbender.Wilhelm`
- **Commit identity:** `David Lewis <david@dglc.com>`
- **Local-only:** `CLAUDE.md`, `xcuserdata/`, `PLAN.md`, `Wilhelm/wilhelmsk-docs/`, `site/`, `.claude/settings.local.json` in `.git/info/exclude`
- **WilhelmSKLibrary** at `~/github/WilhelmSKLibrary` on `main` — required on both machines
- **utilityserver:** `macmini` SSH alias (10.0.0.84), Xcode 26.4, macOS 26.4.1, M-series; git-lfs at `~/.local/bin`; GitHub SSH key ID 152367109; Homebrew not installed (user lacks admin)
- **LFS fix:** `git config lfs.https://github.com/sbender9/Wilhelm.git/info/lfs.locksverify false`
