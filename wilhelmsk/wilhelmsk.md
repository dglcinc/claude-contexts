# WilhelmSK — Context Summary

## Overview

Marine-instrument display app for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner.

## Current State

- **Branch:** `docs/user-guide` (ralph loop writing documentation; base is `development`)
- **Build:** confirmed working on `development` — `xcodebuild -workspace Wilhelm.xcworkspace -scheme Wilhelm -destination 'generic/platform=iOS Simulator'` BUILD SUCCEEDS
- Comprehensive technical analysis in `.claude/analysis.md` covering architecture, security, reliability, and tiered contributor recommendations
- Ralph loop in progress writing user documentation (C1 prerequisites.md and C2 connecting.md committed; C3–A3 remaining)

## Next Steps

1. Verify ralph loop completed C3–A3; review doc quality
2. Open PR to `sbender9/Wilhelm` targeting `development` once all docs are committed
3. Identify first code contribution — review Tier 1 recommendations from analysis.md with Scott on Discord

## Key Facts

- **PRs target `development`** (not `master` or `new-watch-app`)
- **Remote:** `git@github.com:sbender9/Wilhelm.git` (SSH)
- **Commit identity:** `David Lewis <david@dglc.com>`
- **Local-only:** `CLAUDE.md`, `.claude/`, `PLAN.md`, `xcuserdata/` excluded via `.git/info/exclude`
- **WilhelmSKLibrary:** must be cloned at `~/github/WilhelmSKLibrary` on `main` — only external build prerequisite
- **7 targets:** WilhelmSK (iOS), WilhelmTV, WilhelmSKWatch Watch App, WilhelmSKWatch WidgetsExtension, WilhelmSKWidgetsExtension, WilhelmSKPushProvider, SwiftUIPreviewsWidgetsExtension
- **Stack:** Objective-C core + Swift/SwiftUI for watch/widgets; CocoaPods + SPM; FFmpeg xcframeworks + NavionicsMobileSDK vendored in repo
- Real-time coordination with Scott Bender on Signal K Discord
