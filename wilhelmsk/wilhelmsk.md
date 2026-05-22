# WilhelmSK — Context Summary

## Overview

Marine-instrument display app for iOS/iPadOS/watchOS/tvOS/CarPlay that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner.

## Current State

- Cloned 2026-05-21 to `~/github/wilhelmsk` from `git@github.com:sbender9/Wilhelm.git` (SSH). Default branch `master`.
- No work started yet — context just set up.
- Local `CLAUDE.md` + `.claude/` excluded via `.git/info/exclude` so they never land in upstream PRs.
- **Build gotcha:** `Podfile` uses relative-path pods (`../aws-sdk-ios`, `../MarqueeLabel`, etc.) expecting sibling repos checked out next to `wilhelmsk/`. `pod install` fails without them.

## Next Steps

1. Identify the actual task / feature David intends to contribute.
2. If building locally: resolve the sibling-repo pod dependencies before `pod install`.
3. Create a feature branch off `master`; open PR to `sbender9/Wilhelm`.
</content>
