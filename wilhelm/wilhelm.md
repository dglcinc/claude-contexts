# Wilhelm — Context Summary

## Overview

Marine-instrument display app (the **WilhelmSK** product) for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner. Local clone: `~/github/wilhelm` (renamed from `wilhelmsk` 2026-05-24 to match the repo and avoid confusion with the separate `dglcinc/wilhelm-sk` repo).

## Current State (2026-05-25)

- **PR #99 merged** (docs picker + context-help). New work on branch **`fix/docs-url-double-slash`** off `development`: open upstream PR **[sbender9/Wilhelm #100](https://github.com/sbender9/Wilhelm/pull/100)** — fixes a malformed `user-guide//` (double-slash) URL in `WSKDocsSource` that 404'd the docs' relative CSS/JS, leaving the in-app help **unstyled (serif) with no scroll**. Awaiting Scott. Content-side stopgap for already-installed apps shipped as **signalk-wilhelmsk-docs 0.1.4** (inline redirect collapsing the double slash). Confirmed fixed on real iPad + sim. Full debug story: session-state memory + [[docs-deeplink-double-slash]].
- **signalk-wilhelmsk-docs 0.1.4 published** this session: WebApps icon routing fix + new docs icon, system sans-serif font (`font: false`), and the double-slash workaround. Plus Scott's `restProtocol` SSL docs-link fix + a nil guard in the app.
- **Rename complete (2026-05-24):** local clone `~/github/wilhelm`, context id `wilhelm`, mirror `claude-contexts/wilhelm/wilhelm.md`. Old `~/github/wilhelmsk` shell dir removed. `WilhelmSK` product name kept.
- **Build:** confirmed working on both MacBook (Xcode 26.5) and utilityserver (Xcode 26.4).
- **Docs migrated out of this repo** to **`dglcinc/signalk-wilhelmsk-docs`** (see [signalk-wilhelmsk-docs](../signalk-wilhelmsk-docs/signalk-wilhelmsk-docs.md) context). There is no `docs/` dir here anymore. Published at https://dglcinc.github.io/signalk-wilhelmsk-docs/ and also served by a SignalK plugin.
- **In-app help reworked:** the bundled `HelpWebViewController` was **removed**; Settings → Help now pushes `HelpDocsViewController`, a picker choosing the docs source (SignalK server / GitHub web / None, key `helpDocSource` in `NSUserDefaults`). Recent commits: HEAD reachability probe before opening, modal presentation fix (the picker was unreachable under SWRevealViewController), extracted UI-free `WSKDocsSource` resolver, Help-close returns to the app.
- `.claude/` directory committed to repo (Scott approved): analysis.md, UTILITYSERVER_SETUP.md, setup-utilityserver.sh. (Only `CLAUDE.md` itself is excluded via `.git/info/exclude`.)
- utilityserver fully configured as dev machine — SSH, repos cloned, simulators installed.

## Next Steps

1. **Wait for Scott's review of PR #99**; address feedback. (PR #99 now also carries the context-help work — see below.)
2. **Context-help: DONE in PR #99 (2026-05-25, commits `34f7fb2b` + `44182fdd`), ~26 screens.** `UIViewController+WSKHelp` category: a "?" → `WSKDocsSource docsURLForAnchor:` → user-guide anchor; no picker; falls back to web when source none/unset or SignalK unreachable. Two installers — `wsk_installHelpButtonForAnchor:` (navbar) and `wsk_installFloatingHelpButtonForAnchor:` (pinned button for nav-bar-less screens; pins to scroll view `frameLayoutGuide` in UITableViewControllers). ARCHITECTURE.md gained a Help & Documentation section; README architecture link repointed in-repo. Build + simulator verified. Skipped: Gauge Selector/Theme Editor (redundant), IP Camera (video overlay), Log (no anchor).
3. Code contributions — review Tier 1 from `.claude/analysis.md` with Scott on Discord.

## Key Facts

- **PRs target `development`** (not `master` or `new-watch-app`)
- **Remote:** `git@github.com:sbender9/Wilhelm.git` (SSH)
- **Bundle ID:** `com.scottbender.Wilhelm`
- **Commit identity:** `David Lewis <david@dglc.com>`
- **Local-only:** `CLAUDE.md`, `xcuserdata/`, `PLAN.md`, `Wilhelm/wilhelmsk-docs/`, `site/`, `.claude/settings.local.json` in `.git/info/exclude`
- **WilhelmSKLibrary** at `~/github/WilhelmSKLibrary` on `main` — required on both machines
- **utilityserver:** `macmini` SSH alias (10.0.0.84), Xcode 26.4, macOS 26.4.1, M-series; git-lfs at `~/.local/bin`; GitHub SSH key ID 152367109; Homebrew not installed (user lacks admin)
- **LFS fix:** `git config lfs.https://github.com/sbender9/Wilhelm.git/info/lfs.locksverify false`
