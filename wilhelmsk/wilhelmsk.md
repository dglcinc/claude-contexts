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

## Next Steps

1. Identify the actual task / feature David intends to contribute.
2. Attempt a build (Xcode `Wilhelm.xcworkspace`); resolve remaining pod/SPM issues as they surface.
3. Create a feature branch off `new-watch-app`; open PR back to `sbender9/Wilhelm`.
</content>
