# WilhelmSK — Context Summary

## Overview

Marine-instrument display app for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner.

## Current State

- **Branch:** `docs/user-guide` (ralph loop writing documentation; base is `development`)
- **Build:** confirmed working on `development` — `xcodebuild -workspace Wilhelm.xcworkspace -scheme Wilhelm -destination 'generic/platform=iOS Simulator'` BUILD SUCCEEDS
- `.claude/analysis.md` expanded with Reliability, Startup Time, Security, Error Handling, and Build Tooling sections (2026-05-23)
- Key security findings: cert validation disabled for Venus/MQTT + WebSocket; hardcoded API keys; widget passwords in shared UserDefaults
- Ralph loop doc status: C1 (prerequisites.md) + C2 (connecting.md) committed; C3–A3 unknown — check `/tmp/ralph-wilhelmsk.log`

## Next Steps

1. Check ralph loop — verify C3–A3 completed; review doc quality; open PR to `sbender9/Wilhelm` targeting `development`
2. Fix cert validation bypass in `Venus.m` and `SignalK.m` (most critical security finding)
3. Move widget passwords from shared UserDefaults to Keychain; remove hardcoded API keys
4. Add automatic WebSocket reconnect to `SignalK.m`

## Key Facts

- **PRs target `development`** (not `master` or `new-watch-app`)
- **Remote:** `git@github.com:sbender9/Wilhelm.git` (SSH)
- **Commit identity:** `David Lewis <david@dglc.com>`
- **Local-only:** `CLAUDE.md`, `.claude/`, `PLAN.md`, `xcuserdata/` excluded via `.git/info/exclude`
- **WilhelmSKLibrary:** must be cloned at `~/github/WilhelmSKLibrary` on `main` — only external build prerequisite
- **7 targets:** WilhelmSK (iOS), WilhelmTV, WilhelmSKWatch Watch App, WilhelmSKWatch WidgetsExtension, WilhelmSKWidgetsExtension, WilhelmSKPushProvider, SwiftUIPreviewsWidgetsExtension
- **Stack:** Objective-C core + Swift/SwiftUI for watch/widgets; CocoaPods + SPM; FFmpeg xcframeworks + NavionicsMobileSDK vendored in repo
- Real-time coordination with Scott Bender on Signal K Discord
