# Wilhelm — Context Summary

## Overview

Marine-instrument display app (the **WilhelmSK** product) for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner. Local clone: `~/github/wilhelm` (renamed from `wilhelmsk` 2026-05-24 to match the repo and avoid confusion with the separate `dglcinc/wilhelm-sk` repo).

## Current State (2026-06-05) — Anchor Live Activity (3 PRs open, cross-repo)

New Scott project: a DoorDash-style **ActivityKit Live Activity** for the anchor-deployment
process, **watch-first** (watchOS 11+ mirrors the iOS activity into the Smart Stack). Spec in
OneDrive "Live Activity anchor monitoring..." docx; full design in the local (git-excluded)
`ANCHOR-LIVE-ACTIVITY-PLAN.md` in the wilhelm repo root. Planned with David: full-stack scope,
watch-primary, spike the mini radar, devices available.

**Built + 3 PRs open (all build/type-check clean; NOT yet device-verified):**
- **sbender9/Wilhelm#122** (iOS, `feature/anchor-live-activity` off `development`):
  AnchorActivityAttributes + AnchorLiveActivity (ActivityConfiguration: lock-screen + Dynamic
  Island + static radar) + @objc AnchorActivityManager (push-to-start + per-activity tokens).
  Builds clean (xcode MCP sim).
- **sbender9/signalk-push-notifications#13** (from **dglcinc fork** — no direct push access):
  orchestrates start/update/end off anchoring.started/ended (anchoralarm **PR #87 merged**).
  `tsc` clean (`src/icon.ts` w/ AWS creds is git-ignored/absent — stub locally).
- **sbender9/wilhelmsk-lambda-push#1** (David has push): `pushLiveActivityHandler`. **Scott must
  deploy** an AWS Lambda fn `sendLiveActivity` wired to it (David has no AWS access).

**NEXT: on-device test on the M2.** `git checkout anchor-live-activity-devtest` (throwaway branch
w/ Automatic signing for all targets — NOT for merge), build to iPhone, read the Xcode console
`AnchorActivityManager: push-to-start token <hex>`. Test spike lives on the **Mac Mini** at
`~/wilhelm-spike/` (`node anchor-spike.mjs start <hex>` etc.) — fires ActivityKit pushes straight
at APNs, bypassing plugin+Lambda. WilhelmSKPushProvider (NetworkExtension) is the device-build
snag; not needed for the LA test. Then get Scott to deploy the Lambda fn.

## Current State (2026-06-04 evening)

Two contributions tonight, both build-verified and tested on the iPad sim against **Scott's
live (read-only) SignalK connection**:

- **PR #120 MERGED** (Scott landed it into `development`). Beyond the orientation feature it
  now also carries a **note-bubble upright fix**: in Head/Course Up the whole NMSMapView
  viewport rotates, so note callout bubbles (and the anchor marker) were spinning with the
  chart. Fix honors the `isFlat` flag — `isFlat:NO` billboards are counter-rotated by
  `+mapBearing` to stay screen-upright (`isFlat:YES` AIS/own-ship still rotate). `NMSMarker`
  has no rotation property, so it's an image redraw, **throttled to ~2° of bearing change** to
  bound CPU cost.
- **PR #121 OPEN** — Alerts panel bulk-action title bar. The floating "?" help button sat over
  the rows and obscured each alert's mute/ack/clear buttons; replaced it with a fixed title
  bar of **Silence/Ack/Clear-all** + Help (same size/icons as the per-row buttons). Bulk
  actions iterate notifications gated by the same canSilence/canAcknowledge/canClear + V1/V2
  rules; each enables only if ≥1 alert supports it (so all three correctly disable/gray on a
  read-only connection). One file, built in code (no storyboard XML). Branched off latest
  `origin/development` (post-#120-merge).

**Next:** Scott's review of #121; physical-device test of the merged orientation feature;
resume App Store crash triage (the original session intent — crash-summary screenshot never
arrived).

## Current State (2026-06-04, earlier — #120 pre-merge)

**Navionics map-gauge orientation feature (Scott's request) — PR #120 open, awaiting review.**
Apple/Google map gauges support North/Head/Course Up; the Navionics gauge didn't
(`animateToBearing:` was an empty stub). The Navionics SDK can't rotate the chart
programmatically (`NMSCameraPosition.h`: bearing is read-only for rotation; only GPS-driven
modes rotate, useless with SignalK data), so orientation is done by **rotating the NMSMapView
viewport** (Scott's idea):

- `animateToBearing:` applies a `CGAffineTransform` rotation; the shared `refresh:`/`mapUpChanged:`
  path already feeds COG/heading/0, so tracking is automatic.
- `viewDidLayoutSubviews` oversizes the map view to a **diagonal-sized square**, centered, with the
  container clipping → rotated chart fills the frame (no blank corners, no pixel scaling).
- `setupChartRotation` detaches the map view from storyboard edge constraints and builds the
  Course/Head/North Up control **in code** (the Navionics scene has no `mapUpSegmented`).
- Markers need no counter-rotation (they're SDK subviews and rotate with the viewport).

One file (`NavionicsViewController.m`, ~84 lines). **Verified** in iPad sim (all 3 modes +
landscape) and iPhone 17 sim (narrow-width control fit): frame filled edge-to-edge, build green.
Tested against a local `signalk-server` on this machine replaying Scott's recorded NMEA2000 log
(FileStream/Multiplexed playback; server stopped at session end).

**Gotcha:** WilhelmSK persists its page layout in iCloud KVS, so a gauge can't be injected via
prefs/bundle — it must be added through the app UI. (Full detail + the local test-server recipe
are in the project `CLAUDE.md`.)

**Next:** Scott's review of #120; then a physical-device test.

## Current State (2026-06-03 PM — App Store crash mining)

Scott granted David **Developer-role App Store Connect access** (David's own Apple ID, no shared creds) to offload crash/feedback triage. Built a working pipeline — **Xcode Organizer backtrace screenshot → map symbol to source → focused PR** — and shipped **4 crash-fix PRs** (all build-verified, base `development`):
- **#116** `StreamingBoat connect` `dispatch_group` over-leave (top crash, 21 devices) — Venus/MQTT source fires its completion handler >1×; added `__block` idempotent-leave guard.
- **#117** `NMEA2000 parse:data:forBoat:` nil-object array (15 devices) — `@[data]` with nil from a non-UTF8 socket decode; extended the nil guard.
- **#118** `LocalPushReader sendNotification:` nil-value dictionary (~7, PushProvider) — built `userInfo` defensively.
- **#119** `AppleMapViewController findOverlay:` unrecognized selector (~5) — `isKindOfClass:[Overlay class]` guards.

Got an **ASC API key** from Scott (`~/github/wilhelm/.asctoken`, git-excluded; tooling at `~/.wilhelm-asc/asc.py`). Reality: the key is **Developer-level** — reviews read OK, but **Analytics Reports + TestFlight beta-feedback APIs return 403** (need an Access-to-Reports/Admin key for crash/perf *trends*). Reviews are a tiny corpus (**25 total**, 4.46★, 24 unanswered) and fully analyzed — no new bugs; dominant negative theme is **support responsiveness**. Drafted developer responses for the 3 negatives + the iPhone-GPS question (which IS supported via `useDeviceLocation`) → `~/.wilhelm-asc/review-drafts.md`, **sent to Scott for approval** (not posted). TestFlight + App Store crashes both land in Organizer (Distribution filter); Organizer "Feedback" tab is empty.

**Still diagnosed / pending:** PushProvider `GCDAsyncSocket` dealloc race (14 devices — `LocalPushReader connect` releases the socket mid async teardown) needs Scott's OK before a fix; `doesNotRecognizeSelector` (16) + `__exceptionPreprocess` (13) need the selector name / exception reason; `dayThemeChanged:`/`tapGesture:`/`putPath:` await backtrace screenshots.

## Current State (2026-06-03 AM)

Large contribution session. **Nine PRs open against `development`** awaiting Scott (all build clean for the iOS Simulator):
- Dead-code cleanups closing pre-filed issues: **#109** (AWS Info.plist dict → #107), **#110** (OBD/ELM327 orphans ~720 LOC → #105), **#111** (ActiveCaptain map residue → #106). Issues #105/#106/#107 closed.
- **#112** — Tier 1 crash-risk force-unwraps (NotificationsManager server-data parse, watch `SessionHandler`, 5 widget `Calendar` unwraps).
- **#113** — Keychain Surface 1 (stop syncing creds to iCloud) + `.claude/keychain-migration-plan.md`. **Issue #114** opened for Surfaces 2+3 (coupled via the App Group → needs a coordinated iOS+watchOS release).
- **#115** — Tier 1 cellular cold-start: scope the WebSocket subscription to `vessels.self` (+ AIS-on-demand + legacy escape hatch), cellular low-bandwidth throttle (default off), parallel startup reads; + `.claude/cellular-startup-plan.md`. Safe core implemented; UI + snapshot-reorder deferred; needs runtime verification (alarms/AIS/no-stale-gauges).
- **#104** — analysis.md refresh + this session's corrections (below). (pre-existing: #103, #108.)

**analysis.md substantially corrected** after several Tier 1 claims proved wrong on inspection: auto-reconnect **retracted** (it IS implemented via `streamReconnectTimer`/`reconnectTimer:`); Keychain Surfaces 2+3 found coupled; Tier 2–5 re-verified (CI scheme is `Wilhelm` not `WilhelmSK`, `SBJson` now unused, idiom count 84); crash-reporting reworked (MetricKit-first; Firebase footprint is vestigial/not linked). `GenericGaugeWidget:488` unwrap was a false positive (commented-out).

**Recurring facts:** pull WilhelmSKLibrary (`main`) before building or the Watch build fails on a non-public `restEndpoint`; `gh` needs a **classic** PAT for the `sbender9/Wilhelm` API (fine-grained 404s) — now set up on both machines. Working principle: for this third-party repo a documented good-faith PR is an acceptable deliverable even when not runtime-verifiable; Scott's review is the gate.

## Current State (2026-05-29)

- **Three PRs open, all base `development`, awaiting Scott's review:**
  - **#103** — drop the dangling `AISTargetsTable` entry from `gauges.json` (no backing
    `GaugeConfig` class; fixes #101, Scott pre-approved).
  - **#104** — comprehensive refresh of the internal `.claude/analysis.md` (rewritten as a
    current-point-in-time analysis: corrected metrics, consistent AWS references, new
    SignalK v1/v2 + Help & Documentation + Cellular/cold-start sections, reworked Tier list)
    plus a one-line `ARCHITECTURE.md` fix (ActiveCaptain keys removed).
  - **#108** — context-help fix: removed the misplaced gauge-catalog "?" from the Advanced
    editor and repaired the Gauge Options "?" (was clobbered by the Cancel/Save bar-button
    setup) to point at the Gauge Reference doc. Verified in the simulator and via the xcode MCP.
- **Filed 3 cleanup issues** (each offering the deletion PR): **#105** OBD/ELM327 orphan
  files (~720 LOC), **#106** ActiveCaptain residue in the map layer, **#107** dead AWS dict
  in `Info.plist`.
- **PR #102 merged** (settings-menu icons) into `development` on 2026-05-26.
- **Build break fixed:** `RESTSignalK.restEndpoint` was `internal` (broke the Watch
  connection-error display added to `development`); Scott made it `public` in
  `WilhelmSKLibrary` `main`, now pulled. Clone builds clean (verified via xcode MCP).
- **xcode MCP** is connected and now the preferred path for build/test/issues/preview
  (see [[prefer-xcode-mcp]]); it surfaced new analysis findings (deprecated-API debt,
  Swift-6 readiness, a latent `GoogleMapViewController` return-type bug).
- Local clone on branch `refresh-analysis-2026-05` (PR #104), tree clean.

## Prior State (2026-05-25)

- **App docs fully fixed; everything merged.** Scott **merged [sbender9/Wilhelm #100](https://github.com/sbender9/Wilhelm/pull/100)** into `development` — the permanent fix for a malformed `user-guide//` (double-slash) URL in `WSKDocsSource` that 404'd the docs' relative CSS/JS, leaving in-app help **unstyled (serif) with no scroll**. (Found via the SignalK server access log; full story in [[docs-deeplink-double-slash]].) Local clone now on `development` with the fix.
- **signalk-wilhelmsk-docs at 0.1.5 (published, App-Store-ready):** content-side inline-redirect workaround for already-installed apps (0.1.4), WebApps icon routing fix + docs icon, system sans-serif font (`font: false`, offline), rewritten App Store description, four category keywords (utility/instruments/notifications/ais), listing screenshot (confirmed rendering), CHANGELOG, and enable-by-default. Plus Scott's `restProtocol` SSL docs-link fix + a nil guard.
- **Pi:** SignalK Server upgraded to **2.28.0-beta.2**; docs plugin on clean managed **0.1.5**.
- **Pi plugin cleanup (2026-05-25):** disabled the never-configured built-in conversion plugins `sk-to-nmea0183` / `sk-to-nmea2000` (via `~/.signalk/plugin-config-data/<id>.json`) and **uninstalled `signalk-to-influxdb` v1** (redundant with v2). Why the UI hid the toggles + how to query the admin API are in the `signalk-plugin-admin` memory.
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
