---
name: apple-team-id-mapping
description: "WilhelmSK signs under F5FEBHD6EF = Scott's INDIVIDUAL Apple account (can't add members) — David CANNOT self-sign device builds; needs Scott's ad-hoc/TestFlight"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d162c627-e0f2-43ec-8b11-64c5cd6a0d2c
---

**Corrected 2026-06-05 by the M2 session's actual device-build attempt** (supersedes an
earlier claim that David could self-sign — that was from unverified 2026-06-03 notes).

WilhelmSK (`com.scottbender.Wilhelm`) signs under Team ID **`F5FEBHD6EF`**
(`DEVELOPMENT_TEAM` in the project; matches the `teamId` in Scott's APNs Lambda key).
`F5FEBHD6EF` is **Scott's INDIVIDUAL Apple Developer account** — individual accounts
**cannot add members**, so David's Apple ID can't be added to it. **Therefore David
CANNOT sign or debug WilhelmSK on a device.**

David's Apple ID *is* a member of a different Scott team (numeric **`1090917221`** per the
M2 device-build attempt), but the app doesn't sign under that team, so it doesn't help.

**Numeric IDs are muddled across sources — don't assert a clean mapping.** A 2026-06-03
note paired `F5FEBHD6EF` with "ASC team `10623714`"; the 2026-06-05 device attempt found
`1090917221` for the team David's on. Have **Scott confirm his account structure** rather
than trusting either number. `F5FEBHD6EF` (alphanumeric Team ID) is the only value that's
certain — it's what the build signs under and what code signing uses.

**Practical consequence:** real-device end-to-end testing of the anchor Live Activity needs
**Scott** to provide either an **ad-hoc build** (David's device UDID
`00008140-000928563A0B001C`, sandbox APNs) or a **TestFlight build** (prod APNs). The
`anchor-live-activity-devtest` branch (automatic signing) does **not** work for David, and
the `~/wilhelm-spike/` APNs harness is gated on a device token David can't generate. The
**iOS Simulator** (`#Preview` + a `#if DEBUG` hook) is the only no-signing dev path.
Related: [[session-state-wilhelm]].
