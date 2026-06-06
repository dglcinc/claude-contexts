---
name: apple-team-id-mapping
description: WilhelmSK Apple team has two IDs — alphanumeric Team ID F5FEBHD6EF (code signing) = numeric ASC team 10623714
metadata: 
  node_type: memory
  type: reference
  originSessionId: d162c627-e0f2-43ec-8b11-64c5cd6a0d2c
---

Scott's Apple Developer team for **WilhelmSK** (`com.scottbender.Wilhelm`) has two
identifiers that are **the same team, two Apple representations** — not a conflict:

- **`F5FEBHD6EF`** — 10-char alphanumeric **Team ID**. This is the **code-signing**
  value: `DEVELOPMENT_TEAM` in the Xcode project (14 configs on `development`) and the
  `teamId` in Scott's APNs Lambda key. *Not* hexadecimal (it contains `H`).
- **`10623714`** — the integer **App Store Connect team ID** for the same team (shows in
  ASC URLs, Users & Access, some API responses). This is the "integer developer number."

Code signing always uses the **alphanumeric** Team ID (`F5FEBHD6EF`); the integer never
goes in build settings. If someone questions "hex vs integer developer number," this is
the answer — same team.

David's own Apple ID is a **Developer-role member** of this team (Scott invited it
2026-06-03), which is sufficient to sign development device builds himself (no Scott ask
needed beyond logging the Apple ID into Xcode). See the M2's `appstore_connect_access`
note for the access details. Related: [[session-state-wilhelm]].
