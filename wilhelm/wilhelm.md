# Wilhelm — Context Summary

## Overview

Marine-instrument display app (the **WilhelmSK** product) for iOS/iPadOS/watchOS/tvOS that renders live boat data from a [SignalK](https://signalk.org) server as customizable gauges. Objective-C + Swift, Xcode workspace + CocoaPods. **Third-party repo** `sbender9/Wilhelm` (maintainer: Scott Bender) — David is a contributor working via clone + feature-branch PRs, not the owner. Local clone: `~/github/wilhelm` (renamed from `wilhelmsk` 2026-05-24 to match the repo and avoid confusion with the separate `dglcinc/wilhelm-sk` repo).

## Current State (2026-07-05) — domestic-water tile display lag root-caused to the app (handed off from pivac)

New `environment.water.domestic.*` tiles (GPM / Run Time / Gallons) added to the iPhone + iPad
layouts take **~20–40 s** to update after water starts, and the lag **grows with connection
uptime**. Root-caused (from a pivac session) to the **WilhelmSK app**, not the data pipeline:
a WebSocket subscriber on WilhelmSK's *exact* path (through nginx, `subscribe=all`) receives the
deltas in **~1 s**, but the tile renders 20–40 s later. Ruled out node/pivac/Signal K/nginx (all
~1 s) and delta volume (~7.6 deltas/s idle — trivial). A fresh app relaunch roughly halves it.
**Full findings, the 4-point synchronized-monitor evidence, repro scripts, and app-side next
steps (delta-handling / unbounded-growth / redraw-storm hypotheses) are in
[`water-tile-lag-diagnosis.md`](water-tile-lag-diagnosis.md).** This is the active pick-up target
for app-side work in `~/github/wilhelm`.

## Current State (2026-07-01) — Autopilot #143: full command path verified correct; real issues are app build + EV-1 detection

Diagnosis-only session (no code; tree clean). disk3333 sent more detail and I traced the whole
heading-adjust chain against **actual source** (app + signalk-server core + signalk-autopilot plugin),
superseding the earlier version-mismatch theories.

**His facts:** WilhelmSK **1.17.4 build 249**; server **signalk-server 2.19.1**; plugin
**@signalk/signalk-autopilot 2.6.0** (current — his Appstore screenshot via Victron VRM shows "Configure",
and the "1" pending-update badge is a different plugin). **Mode + Tack work; +1/-1/±10 heading-adjust does
NOT.** Autopilot **reachable only via his "YDWG" connection, "not reachable" via the Cerbo.**

**Verified code path:** WilhelmSK's autopilot gauge is v2-only. Only heading-adjust carries a numeric body —
state=string, tack=`{}`, adjust=`{units:"deg",value:N}` (legacy fallback removed in `f5951515`). The plugin's
`putAdjustHeading` requires the pilot **engaged in auto/wind** and accepts **only ±1/±10**; signalk-server core
≥2.13 (he's on 2.19.1) **converts deg→rad on the `target/adjust` route**; the round-trip lands ±1/±10 cleanly.
**Conclusion:** on his stack the code is correct — `[object Object]`, deg-not-converted, and old-second-server
theories are ruled out. Other EV-1 users work on a current stack **with the pilot engaged and the EV-1 detected.**
Only two live causes remain, with different symptoms: (1) pressing +1 while **not engaged** → "Autopilot not in
auto or wind mode"; (2) command accepted but **EV-1 not driven** (no error) → the #88 detection / source-id-204
gap, which is exactly why the Cerbo reads "not reachable."

**NEW build finding:** the W2K-1 connection bug (`BoatDeviceType` enum/array off-by-one) was **introduced in
1.14.4** (per fix commit `ed4c095e`, 2026-06-05) and first fixed in **build 251**. disk3333's **build 249 still
has it**, and **YDGW-02 is in the affected device-type range** (discovery can't tell a W2K-1 from a Yacht Devices
gateway — both N2K-RAW over UDP 2002). So **step 1 for him is to UPDATE THE APP off build 249** (App Store 1.18.0
/ TestFlight 1.19.0) and re-test connections before more autopilot debugging. Drafted a Discord reply (David sends).

## Current State (2026-06-24) — Autopilot #143 root cause CORRECTED from user's live server

The affected Discord user (`disk3333`) sent his actual Signal K config (Victron Cerbo GX / VRM
remote console), which overturned two assumptions in the 2026-06-21 diagnosis below. **(1)** His
`signalk-server` core is **2.19.1** — well above the v2 autopilot API's 2.13.0 floor, and Cerbo cores
are firmware-gated, so "update the server core" neither applies nor is possible. **(2)** He already
runs **`@signalk/signalk-autopilot` with the V2 API enabled** (Autopilot Type = Raymarine NMEA2000),
so "switch plugins" is moot. Refined root cause: `Invalid adjustment: [object Object]` = the v2
`{units,value}` body reaching the plugin's *legacy* `putAdjustHeading` (±1/±10 only) → a
plugin-version bug (Appstore showed 1 update pending); and the deeper blocker is the config's
**"No EV-1 Found"** — the plugin isn't detecting the EV-1/ACU400 on the N2K bus (falls back to default
id 204), so commands have no target. Verified the plugin source. Posted a correction comment on
**sbender9/Wilhelm#143** (body left intact, core-version note marked superseded) and filed upstream
**SignalK/signalk-autopilot#88** — smarter EV-1 detection (it keys off Product Information PGN 126996,
not bus presence, so aggregating gateways like Venus OS break autodetect); cross-linked both ways.
Helped David craft the Discord reply (he sends). No code changes; tree clean.

## Current State (2026-06-21) — Autopilot "Invalid adjustment: [object Object]" diagnosis → issue #143

Diagnosed a Discord report (Raymarine via Yacht Devices YDWG-02 / SeaTalkNG): after an App Store
update, autopilot heading-adjust fails with **"Unable to send autopilot command. Invalid
adjustment: [object Object]"** while all instrument data flows fine. Drafted a Discord reply (not
posted — David sends) and filed **sbender9/Wilhelm#143** to strengthen backwards compatibility. No
code changes; tree clean.

**Root cause (fully traced).** App commit `f5951515` ("autopilot V2 api support", shipped in
release **v1.17.3+**) switched the in-app AP gauge to `PUT /signalk/v2/api/.../target/adjust` with
body `{units:"deg", value:N}` and **removed the legacy fallback**. The error string is server-side,
in provider plugin **`SignalK/signalk-autopilot`** (current **v2.6.0**; the v2 replacement for the
deprecated `sbender9/signalk-raymarine-autopilot`, legacy-only at v1.3.1) — `Invalid adjustment:
${value}` in its `putAdjustHeading` handler, which accepts only exact integer ±1/±10 (present since
the 2020 initial commit). `[object Object]` = the raw `{units,value}` body reached that handler as
the value rather than an extracted number → a **version mismatch** on the user's server. signalk-server
core has extracted `req.body.value` + handled `units` since the v2 AP API debuted in **core v2.13.0**
(2024-12-15), so the v2 path requires server ≥ 2.13.0. User fix: update signalk-server + signalk-autopilot.
App fix (#143): capability-detect/legacy fallback, clearer error, resolve the gauge-vs-widget
asymmetry (widget still PUTs legacy `steering.autopilot.actions.adjustHeading`). **Not** the recent
connection-discovery bug — different subsystem.

## Current State (2026-06-15) — On-device anchor LA test; root-caused the end-at-set bug

A live on-device test run (David's iPhone + watch vs the mini test bed; TestFlight **v1.19.0 /
build 231**; Claude drove only boat position). Root-caused the end-at-set bug and confirmed
several items left unverified on 06-07. **Findings folded into the git-excluded
`.claude/anchor-la-scott-writeup.md` (new "2026-06-15 UPDATE" section) + the session memory.**
No code committed — the working tree stays as David's local-only debug WIP.

**Confirmed working on device:** the **throttling fix** (distance tracks smoothly on the phone
island over a gradual rode payout on the ~10s cadence — resolves the prior "unverified");
phone-drop **local-start** spawns the island; **watch-drop push-to-start** spawns it on the
phone and mirrors to the watch Smart Stack; **raise ends the activity correctly**.

**BUG 1 (headline) — the activity ENDS at "set"**, reproduced on both local-start and
push-to-start. **Not an app bug** (the app's `endLiveActivity` is reactive to ActivityKit
`.ended`/`.dismissed`, `AnchorActivityManager.swift:108-109`). **Root cause = push-notifications
plugin state machine:** anchoralarm `setRadius()` emits `anchoring.started→'normal'` +
`anchoring.ended→'alert'`; the plugin's STARTED handler records `lastAnchoringStartedState='normal'`
(`index.ts:1337`); the ENDED-`normal` end-branch is guarded only by
`lastAnchoringStartedState !== 'alert'` (`index.ts:1357-1361`), meant to tell a real raise from
the retained resting `ended='normal'` replayed during deploy — but `setRadius` flips `started`
to `normal` itself, so when `anchoring.ended` settles back to resting `normal` after the
transient `alert`, the guard mis-reads it as a raise and ends the activity. **Fix dir:**
discriminate set-vs-raise off `navigation.anchor.position` (raise clears it, set doesn't) /
never end while `anchorPhase==='set'` unless the position is gone — **plugin-side (PR #13),
fixable + testable on the mini without an app build.**

**BUG 2 (app-side)** — the compact Dynamic Island shows `rodeLength` (static) instead of
`distanceFromBow` (the live distance); expanded shows both; the watch gauge correctly shows
distance. Fix = the LA widget's Dynamic Island compact region. **Token registration** still
needs a manual Settings→Notifications→Remote-Notifications OFF→ON toggle (flaky auto-register).
**Watch UX:** the LA card (Smart Stack, from the face) and the watch app's anchor gauge are
mutually exclusive — after a watch drop you're on the gauge, can't see the card.

**David's decision: DROP the watch mirror;** pursue a phone-only ambient/live display only if
BUG 1 + BUG 2 are fixed. **Next:** hand the writeup to Scott. Mini test bed **left running**
(server up; rode-capable feeder `~/wilhelm-test/posfifo-writer-rode.cjs` reads `/tmp/feedrode`
for `navigation.anchor.rodeLength` injection; feedpos recentered, rode off).

## Current State (2026-06-12) — Four docs/review PRs + anchor LA staleness/orphan fixes

A documentation + review session, all output as PRs against `development` (plus one cross-repo
plugin change). Seven PRs now open, all awaiting Scott — no local work is blocked on David.

1. **Reviewed + corrected the testing plan (#137) and units/localization plan (#140).** Commit
   forensics corrected the W2k root cause: the shipped break was an array↔enum desync window
   (`51bb5df7` removed `ODB II` from the `Boat.m` arrays 2026-05-22; the `Boat.h` enum kept
   `BoatDeviceTypeODBII` until `ed4c095e` 2026-06-05), NOT the #110 cleanup. Added a three-list
   parity guard + a discovery-classification (W2K‑1↔YDGW on UDP 2002) regression class to #137;
   added tvOS-propagation + locale-blind-`floatValue` notes to #140.
2. **tvOS modernization plan** (`.claude/tvos-modernization-plan.md`, **PR #141**, issue #135) —
   Scott left "modernization" undefined, so the doc proposes it as the verified gap vs Apple's 2026
   platform bar: P1 mandatory hygiene (tvOS 26 SDK/Liquid Glass audit, UIScene adoption, stale
   OBD/HomeKit plist keys, deprecations), P2 focus/HIG, P3 TV-native settings/connections (after
   #140), P4 SwiftUI shell (gated on Scott; no gauge-render rebuild ahead of Tier 4), P5 Top Shelf.
3. **Refreshed analysis.md / ARCHITECTURE.md / README.md** (**PR #142**): README drops the CarPlay
   claim (verified absent) + corrects platform floors (watchOS 10.6, tvOS 17.6); ARCHITECTURE gains
   the two-engine units truth + the three-list device-type fragility section + a WilhelmTV
   description; analysis.md gains improvement items 11 (i18n/units) + 12 (positional device-type
   lists), the corrected W2k root cause, and tier updates (CI revised to local-first on the private
   repo; new tvOS Tier-4 item).
4. **Reviewed the anchor Live Activity (PR #122)** and implemented its two ship-blocker fixes.
   **Staleness:** a frozen "anchored" card used to keep its green tint when pushes stopped — now the
   plugin (`b781069`, PR #13) stamps `stale-date` = now+60s on every push, and the app (`ba5b24f2`)
   grays the tint + dims + shows "No data — updated N min ago". **Orphan cleanup:** `start()`
   reconciles against the server's `navigation.anchor.position` (definitive null ends strays, errors
   keep — fail-safe); a fresh drop ends activities not updated within 120s instead of bailing. Full
   assessment in the git-excluded `ANCHOR-LA-ASSESSMENT.md`; feasibility verdict: solid
   implementation, but the watch-first premise is undermined by Apple's push-to-start rationing +
   watch-can't-wake-phone, leaving phone-first ambient display as the real value. On-device verify
   of stale-date + throttling awaits Scott's next TestFlight build + a push-to-start budget reset.

## Current State (2026-06-12) — Units/localization plan PR #140 + connection-bug diagnostics

Two threads. **(1) Units & Localization recommendation** — authored `.claude/units-localization-plan.md`
for issue **#138** and opened **PR #140** (docs-only, base `development`). Frames the work as two tracks
sharing one seam: **Track A propagation** (the literal #138 ask — `unitsChanged:` writes the pref but
broadcasts nothing; surfaces only refresh on the next data tick; the watch `updateWatchData()` trigger
exists but is never called) and **Track B i18n** (app is effectively English-only; the headline bug is
**zero `NumberFormatter`/`Locale.current` anywhere** → C-locale decimals break international users — also
a units concern). Doc adds a per-category expose/retire table (retire dead Angle/electrical/Charge/Ratio
settings; add fathoms + imperial gallon), a marine-aware Imperial/Metric/Nautical preset seeded from
`Locale.current` on first run, and a SignalK server/plugin coordination section (SI on the wire; display
pref is client-only; scattered write-back conversions → centralize + round-trip tests; `meta.units` for
arbitrary paths; LA content-state contract; server-emitted strings can't be localized app-side). Phased,
each phase an independent PR; P1 closes #138 and is simulator-verifiable.

**(2) Connection-bug diagnostics (investigation only, no code).** Diagnosed two post-release reports.
Root mechanism is the **W2k regression class again**: device types are tracked by fragile positional
alignment across three hand-maintained lists (`BoatDeviceType` enum `Boat.h:48` + `boatConnectionTypes`
constants + `boatConnectionTypeNames` `Boat.m:134-136`), with array-index→enum casts (`NonSKSource.m:31`).
The ODB removal was split across two releases — arrays lost ODB **May 22** (`51bb5df7`), enum kept it
until **Jun 5** (`ed4c095e`) — leaving an off-by-one window for every device after HelmSmart.
**Scott's W2K‑1 → YDGW (likely):** discovery can't distinguish an Actisense W2K‑1 from a Yacht Devices
gateway — both broadcast NMEA2000 RAW over **UDP 2002** in the same format; the YDGW socket hardcodes the
match as `kYDWGDevice`/"YDGW‑02" (`SignalKBrowser.m:367`), and discovered connections rebuild
`connectionType` from `deviceType` each refresh. **David's discovered SignalK Pi connection "reset":**
SignalK is enum type 0 (unshifted), so the integer mechanism doesn't apply; a discovered connection is
LAN-only/ephemeral and `NSUserDefaults` survives updates — he's simply off the Pi's LAN. Real fix for
remote use is a manual connection (Tailscale/DDNS). **Did the "security" updates cause either? NO
(verified):** the merged security change is **#113** (`9eabaa55`, Keychain Surface 1) — a 14-line diff
that only strips `username`/`password`/`jwtToken` from the iCloud copy, only for `source=="manual"`
connections; it never touches `connectionType` and never runs for discovered connections. **#132
(Surfaces 2+3) is unmerged and its keychain code isn't in the shipped tree at all.** Offered (awaiting
David's go-ahead): a fix keying connection prefs by stable `uuid`/string constant instead of the
renumberable integer, a #137 regression test, and a Pi remote-access writeup.
## Current State (2026-06-07 evening → 06-08) — Anchor LA reliability, throttling fix, local-start fallback

A long live test of the anchor LA (David's TestFlight build vs the mini test bed) became a reliability + design pass. **Fixes landed across two repos:**
- **Plugin PR #13 (dglcinc/signalk-push-notifications):** atomic device-store write (`aa88622` — fixes an `fs.writeFile` truncate race causing parse errors / 404s / lost tokens / orphans; helps ALL push + alarm persistence); ignore replayed retained anchoring notifications on re-subscribe (`c20f75b` — a stale `ended=normal` was tearing the activity down → no updates); priority-10 updates on a 10s floor (`bd94aa3` — immediate delivery + low volume beats iOS throttling); skip push-to-start for devices with a running activity (`d1c027a` — dedup for local-start).
- **App PR #122 (sbender9/Wilhelm) — needs Scott's build:** `NSSupportsLiveActivitiesFrequentUpdates` plist key (`eefa3a6e`, Scott built from here); push-to-start status line on the Notifications page (`a71e87af`); **local-start fallback** (`dde60296` — `AnchorActivityManager.startLocalActivity()` via `Activity.request(pushType:.token)` on an in-app drop, hooked into `AnchorAlarmViewController`).

Full LA lifecycle validated end-to-end against the fixed plugin (drop→deploying→updates→set→green→drag→red→raise→end, all APNs-accepted). **Throttling fix still unverified on device** — blocked because the **iOS push-to-start budget (~10/device/short window, fixed, and NOT raised by the plist key — that key only affects the *update* budget) was exhausted** by repeated testing. The app only spawns the LA via server push-to-start in Release (the lone `Activity.request` was `#if DEBUG`), which is why the local-start fallback matters; and **a watch drop can't local-start the phone** (the watch posts `dropAnchor` to the server directly; WCSession can't wake a sleeping phone), so watch-first inherently needs push-to-start (fine for real single-drop use). Filed issues **#138** (units/localization propagation) + **#139** (Control Center controls' push tokens). **Feature value still in question** (drag alarm redundant with the anchoralarm onboard sound alarm + the existing push notification; watch mirror redundant with the accurate native gauge) — recommendation drafted for Scott in the local (git-excluded) `~/github/wilhelm/.claude/anchor-la-scott-writeup.md`: drop the watch mirror; decide phone-only ambient/live display vs shelve (keep the atomic-write fix regardless). **Next:** Scott rebuilds from the branch + updates the plugin on the server; restart the mini server (running `bd94aa3`) to load `d1c027a`; re-test via a phone-app drop once the budget resets.

## Current State (2026-06-07) — Backlog merged; Keychain + testing-plan PRs; advisory work

**Scott merged the bulk of the backlog today:** #123–#129 (crash + feature fixes), #131
(correctness quick wins), #130 (analysis refresh + Tier-1 status markers). This session opened
**#131** (3 correctness quick wins — MERGED), **#132** (connection credentials → shared Keychain,
Surfaces 2+3 — OPEN), **#137** (Tier 3 automated-testing & regression-defense plan, docs — OPEN),
and filed **issue #135** (modernize the Apple TV UI, Scott-requested).

**Keychain #132** (Surfaces 2+3, finishing #113's Surface 1): credentials move to a shared-access-
group Keychain read by app/widget/watch. Kept the in-memory connection-dict interface unchanged
(moved only the save/load persistence boundary), so ~20 credential read sites are untouched.
SecItem in `Settings.m` (no new file; WilhelmTV links Security.framework) + KeychainAccess on the
Swift side; service `com.scottbender.WilhelmSK`, account `cred.<name>.<field>`, no explicit access
group (defaults to the shared group the deviceToken uses). Added `keychain-access-groups` to both
watch entitlements. Migrate-on-read + delete; also strips VRM creds from iCloud (closes the #113
follow-up). Builds clean (Wilhelm + watch); **needs Scott's device/runtime verification** and a
decision on the migrate-delete rollback trade-off.

**Testing plan #137** (docs): risk-weighted Tier 3 program grounded by 4 subagents. The **W2k
regression is a class** — a `BoatDeviceType` value inserted mid-enum, deleted in the OBD cleanup,
renumbered later cases while `ConnectionSettingsViewController.m` still branched on the dead
constant (fixed `ed4c095e`); the plan locks it with enum-ordinal + capability tests. Highest crash
ROI = a malformed-server-input harness. **Local-first gates** (pre-push hook + optional self-hosted
runner) because the **private** repo makes GitHub-hosted macOS CI 10× costly. Phase 0 (new test
target/scheme/fastlane lane) to be aligned with Scott on Discord first.

**Advisory threads:** dropped the MetricKit→signalk-server crash-telemetry idea (Organizer already
shows aggregated MetricKit data free on App Store/TestFlight, gated on opt-in + privacy threshold;
programmatic access needs a coarse Access-to-Reports/Admin ASC key — David's is Developer-level,
for reviews). **Jordan #4 autopilot "undefined != standby":** server-side, single SK server on a
**Victron Ekrano (Venus OS Large)** — likely the `signalk-raymarine-autopilot` plugin, updatable
via the on-device SignalK appstore independent of Victron firmware (core SK version is firmware-
gated). Next: Jordan to confirm the plugin is installed + appstore loads. App-side #127 de-spam
merged; he can test on the boat next build.

## Current State (2026-06-07) — Anchor Live Activity on-device testing + fixes

Live-tested the anchor LA on a **TestFlight build** (David's iPhone, built by Scott from
`feature/anchor-live-activity`) against a **mini SignalK test server**. **Validated watch-first
end-to-end:** drop from the watch → LA deploys (yellow) → live distance updates → lock radius →
set. Reworked the lifecycle to **green-while-anchored** (stays green at set with no further
events, ends on raise) per David's point that an idle green activity costs nothing.

**Plugin fixes — sbender9/signalk-push-notifications#13** (pushed to dglcinc fork, latest
`e7e8e1e`): rebased on master; invoke the deployed lambda name **`sendLiveActivityPush`**;
**always subscribe to the anchor data feed** (fix: the LA wasn't updating live during deploy
because it only subscribed if a push-to-start token existed at plugin boot); **green-while-anchored**
lifecycle. **App:** PR **#134 MERGED** (`sendPOST` nullability crash — the Remote-Notifications
crash); PR **#136 OPEN** (settings no-exit, follow-up to #128). **AWS:** `sendLiveActivityPush`
lambda + IAM working (Scott). **Docs:** lambda runbook **wilhelmsk-lambda-push#2**; anchoring docs
**signalk-wilhelmsk-docs#53** (NEEDS UPDATE — behavior is now green-while-anchored, not end-at-set).

**Remaining (app-side → need a NEW TestFlight build from Scott to test):** orphaned-LA cleanup
(stuck LAs can't be ended remotely; app should clear stray activities on launch/fresh-drop);
dismiss garbage-error ("Server Returned Error -7562…", uninitialized code); confirm the watch-gauge
"not deployed"/lag is a real bug vs a desync artifact. **Signing:** David CANNOT self-sign (app
team `F5FEBHD6EF` = Scott's individual account; David's Apple ID on a different team) — app changes
need Scott's build; plugin changes are testable on the mini. **Test protocol:** David drives
drop/lock/raise; Claude drives ONLY the boat position (server-side anchor changes desync David's
devices). Full resume detail + mini test-bed restart procedure in the `session_state_wilhelm`
memory.

## Current State (2026-06-06 PM) — Crash + feedback triage + docs release (8 PRs + v0.1.7/v0.1.8)

Worked from Xcode Organizer **crash** screenshots and **Feedback** screenshots (in `~/Documents/`).
Opened **8 PRs** against `development` (all build-clean, awaiting Scott) and **released the docs
plugin twice**.

**Docs:** **#130** refreshes the in-repo docs — `ARCHITECTURE.md` (fixed stale auto-reconnect &
credential-sync claims; added Alerts toolbar, Anchor Live Activity, a Maps & Charts section) and
`.claude/analysis.md` (marked the OBD/ActiveCaptain/AWS dead-code cleanup DONE). The **user-guide
plugin** (dglcinc/signalk-wilhelmsk-docs) shipped **v0.1.7** (anchor Live Activity, alerts bulk
actions, Navionics orientation, two-finger map paging) and **v0.1.8** (reworked
"Anchoring and the Anchor Alarm" section, `{ #anchor-alarm }` id pinned). Both via OIDC
trusted-publish on a `vX.Y.Z` tag; GitHub Pages auto-deploys. Docs repo `origin` switched HTTPS→SSH.
Anchor-LA lifecycle verified plugin-driven (START on drop, END on raise, no manual stop).

The seven fix/feature PRs (#130 is the docs PR above):
- **#123** — four defensive crash guards (theme IBAction non-NSString sender; `GraphicGaugeView
  tapGesture:` parallel-array bounds; `StreamingBoat putPath:` nil path/value; `scrollToRowAtIndexPath:`
  stale index path).
- **#124** — push-provider **GCDAsyncSocket dealloc race** (`LocalPushReader` teardown serialized on
  main/delegate queue). This was the previously-unidentified "pending" crash: 12 devices, CFNetwork
  `Schedulables::_SchedulesInvalidateApplierFunction`, still live on 1.17.4.
- **#125** — gauge feedback: duplicate Gauge Options panel (re-entrancy guard in `selectGauge:`);
  stale green bar with Show-Old-Data off (`BarGaugeView refresh:` early-return ordering); engine-hours
  seconds option (`engineRuntimeHideSeconds`, default = show seconds).
- **#126** — deleted connection lingered in App Group store (`removeConnection:` made symmetric with save).
- **#127** — autopilot alert de-spam ("this will not go away"; confirmation logic untouched — safety).
- **#128** — no exit from Settings for a first-run user (Done-button fallback when no reveal controller).
- **#129** — two-finger swipe to page off a map (the map eats the one-finger pan).

**Crash confirmations:** #116 (Venus/MQTT over-leave) & #117 (NMEA2000 nil-array) already-fixed per the
Organizer stacks. **Still open:** `doesNotRecognizeSelector` (13 devices) needs "Open in Project"
symbolication (selector masked, Thread 0 empty); `demo.signalk.org` connect failure needs repro.
**Jaakko W2K-1 "no data"** = already fixed by `ed4c095e` (BoatDeviceType enum off-by-one, build 251);
he's on 241 → tell him to update. No simulator tap automation here, so #6 was reproduced by code tracing.

## Current State (2026-06-06 AM) — Detour: signalk-server architectural review

This session did **no Wilhelm code work**. It was a full architectural review of the upstream
**SignalK/signalk-server** codebase (the Node.js server WilhelmSK connects to), requested by
David. Deliverable: `~/github/signalk-server-architecture-review.md` (~44KB / ~700 lines) —
a loose file (`~/github/` is not a git repo, so uncommitted). Covers structure, performance,
scalability, extensibility, code evolution, and recommendations for governing the rising volume
of AI-assisted PRs (reviewed via CodeRabbit). Headline findings: ~123k LOC first-party; **~68%
of the core `src/` rewritten in 2026 alone** (a strict-TypeScript migration + React 19 admin-UI
rebuild); top liabilities are the central **`app` god-object** and a **plugin API that leaks the
whole `app`**; strong existing AI-PR governance, so the rec was to add a **CODEOWNERS** file +
**architecture-alignment criteria** for CodeRabbit rather than more style rules. Full findings in
the `signalk-server-architecture-review` memory file. **Wilhelm working tree is clean; all anchor
Live Activity state below is unchanged.**

## Current State (2026-06-05) — Anchor Live Activity (3 PRs open, cross-repo)

New Scott project: a DoorDash-style **ActivityKit Live Activity** for the anchor-deployment
process, **watch-first** (watchOS 11+ mirrors the iOS activity into the Smart Stack). Spec in
OneDrive "Live Activity anchor monitoring..." docx; full design in the local (git-excluded)
`ANCHOR-LIVE-ACTIVITY-PLAN.md` in the wilhelm repo root. Built on the **mini**; David came to the
**MacBook (M2)** to test on his phone.

**Built + 3 PRs open (all by David, build/type-check clean, all mergeable, awaiting Scott):**
- **sbender9/Wilhelm#122** (iOS, `feature/anchor-live-activity` off `development`):
  AnchorActivityAttributes + AnchorLiveActivity (lock-screen + Dynamic Island + static radar) +
  @objc AnchorActivityManager (push-to-start + per-activity tokens). Builds clean (sim). **Added
  `#Preview` blocks this session — committed `a145e37e`.**
- **sbender9/signalk-push-notifications#13** (from **dglcinc fork** — no direct push access):
  orchestrates start/update/end off anchoring.started/ended (anchoralarm **PR #87 merged**).
  `tsc` clean (`src/icon.ts` w/ AWS creds is git-ignored — stub locally).
- **sbender9/wilhelmsk-lambda-push#1** (David has push): `pushLiveActivityHandler`. **Scott must
  deploy** an AWS Lambda fn `sendLiveActivity` + invoke route (David has no AWS access).

**Cross-tier verification this session: CLEAN.** Checked every seam — endpoint paths app↔plugin,
`content-state`/`attributes` vs the Swift structs, Lambda invoke params + token shape, the
`…push-type.liveactivity` topic/pushType, and the `anchoring.started/ended/alert` + drag-alarm
state mapping against the **real** signalk-anchoralarm-plugin source. No code defects.

**Device test BLOCKED — signing (resolved 2026-06-05):** the planned `anchor-live-activity-devtest`
branch (Automatic signing all targets) **does not work** — David's Apple ID is on Scott's team
`1090917221`, but the app signs under **`F5FEBHD6EF` = Scott's INDIVIDUAL account**, which can't
add members. So David **can't** sign/debug on device. Dev now = **iOS Simulator** (no signing):
`#Preview` canvas for the views + a `#if DEBUG` `-wskDebugAnchorLA` hook that starts/cycles a
sample activity (kept local, not in #122; sim suspends backgrounded apps in ~30–60s so the live
island cycle is brief). Real-device end-to-end needs Scott's **ad-hoc** (UDID
`00008140-000928563A0B001C`, sandbox APNs) or **TestFlight** (prod APNs) build. The mini's
`~/wilhelm-spike/` APNs harness (`node anchor-spike.mjs start <hex>`) also needs a device token,
so it's likewise gated. **XcodeBuildMCP** installed (local scope; v2.x needs the `mcp` subcommand).

**Waiting on Scott:** review/merge the 3 PRs together · AWS-deploy the Lambda `sendLiveActivity` ·
provide an ad-hoc/TestFlight build for the real end-to-end test. (Also flagged via DM: the APNs
`.p8` key is committed in plaintext in `wilhelmsk-lambda-push/index.mjs`.)

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
