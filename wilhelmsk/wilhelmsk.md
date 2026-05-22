# WilhelmSK — Context Summary

## Overview

Marine-instrument display app for iOS/iPadOS/watchOS/tvOS/CarPlay that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner.

## Current State

- Cloned 2026-05-21 to `~/github/wilhelmsk` from `git@github.com:sbender9/Wilhelm.git` (SSH). Repo default `master`, but **working branch is `new-watch-app`** (the PR base per owner).
- Local `CLAUDE.md` + `.claude/` excluded via `.git/info/exclude` so they never land in upstream PRs.
- **Build prerequisites staged (per owner Scott Bender):**
  - `WilhelmSKLibrary` cloned to sibling `~/github/WilhelmSKLibrary` on `main` — it's a local Swift package (`relativePath = ../WilhelmSKLibrary`).
  - `git-lfs` installed + initialized. new-watch-app tree has no LFS pointers; ~1855 LFS files across other refs.
  - CocoaPods relative-path pods (`../aws-sdk-ios`, etc.) NOT yet resolved — new-watch-app moved some deps to SPM, so confirm what's still needed.
  - Owner's warning: "huge mess… a challenge to build." Real-time chat on the Signal K Discord.
- No feature work started yet.

## Build investigation (2026-05-21)

Xcode 26.5. Installed via CLI: iOS 26.5 + watchOS 26.5 platforms (`xcodebuild -downloadPlatform`), git-lfs. SPM resolves clean (incl. WilhelmSKLibrary @ local). Build then blocks on missing external binaries that must come from Scott:
1. FFmpeg xcframeworks (av*/sw*, 7) — gitignored, not in repo.
2. LTSupportAutomotive.framework — absent.
3. CocoaPods local-path siblings (aws-sdk-ios, ios-custom-alertview, UICKeyChainStore, MarqueeLabel, DGActivityIndicatorView, WaveAnimationView) — not cloned; CocoaPods not installed. Maybe vestigial post-SPM-migration.
NavionicsMobileSDK.xcframework is present and fine.

## Next Steps

1. **Discord shopping list for Scott:** where to get the FFmpeg xcframeworks, LTSupportAutomotive.framework, and whether the 6 CocoaPods siblings are still needed (URLs) or now vestigial.
2. After binaries obtained: clone pod siblings + `brew install cocoapods && pod install` (if still needed), then rebuild.
3. Code signing in Xcode (Team/provisioning) for device builds; simulator skips it.
4. Identify the actual feature/fix David intends to contribute; branch off `new-watch-app`, PR to `sbender9/Wilhelm`.
</content>
