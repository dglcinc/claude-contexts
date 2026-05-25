# signalk-wilhelmsk-docs — Context Summary

## Overview

dglcinc-owned **public** monorepo holding the **WilhelmSK** documentation and the SignalK
plugin that serves it. Two outputs from one `docs/` source:

- **MkDocs site** → published to GitHub Pages: https://dglcinc.github.io/signalk-wilhelmsk-docs/
- **SignalK node-server plugin** (`plugin/`) → serves the same built site locally at
  `/signalk-wilhelmsk-docs/` so WilhelmSK can offer in-app help from a boat's own SignalK server.

Spun out of the third-party `sbender9/Wilhelm` iOS app (see the [wilhelm](../wilhelm/wilhelm.md)
context) by a Ralph loop (`~/github/wilhelm-docs-ralph/PLAN.md`, all 10 tasks complete). The
iOS app now ships a `HelpDocsViewController` picker (SignalK / GitHub / None) instead of a
bundled help viewer.

## Repo Layout (monorepo)

- `docs/` — MkDocs markdown sources (`index.md`, `user-guide.md`)
- `mkdocs.yml`, `requirements.txt` — at root
- `plugin/` — SignalK plugin: `package.json`, `index.js`, `public/` (committed built site), `README.md`
- `site/` — local MkDocs build output (gitignored)
- `.github/workflows/` — `deploy-pages.yml` (Pages on push to main), `verify-plugin-docs.yml`
  (fails PRs where `plugin/public/` is stale vs `docs/`)

## Key Facts

- **Remote:** `https://github.com/dglcinc/signalk-wilhelmsk-docs.git` (HTTPS, dglcinc). Public.
- **Default branch:** `main`. Doc/code changes via feature branch + PR; self-merge OK (David sole reviewer).
- **Mount path:** SignalK auto-mounts a plugin's `public/` at `/<package-name>/`, so docs serve at
  `/signalk-wilhelmsk-docs/` (NOT the original `/wilhelmsk-docs/` — fixed in PR #5). Info endpoint:
  `/plugins/signalk-wilhelmsk-docs/info`.
- **Editing docs:** any change under `docs/` or `mkdocs.yml` requires rebuilding the bundled site —
  `cd plugin && npm run build-docs` — and committing `plugin/public/`, or `verify-plugin-docs.yml` fails.
- **MkDocs venv:** reuses `~/github/wilhelm/.venv/` (no local venv in this repo yet).
- **Content direction (Scott's calls):** no public contributor docs; user guide leads with Connecting,
  with SignalK / Victron VRM / NMEA gateways as parallel subsections; tvOS, CarPlay, iKommunicate,
  Raymarine references removed.

## Current State (2026-05-25, publish session)

Through PR #23 squash-merged; `main` clean. **Published to npm (0.1.2) and live in the SignalK App Store.**
This session's PRs: #19 appstore metadata (`signalk` block displayName/appIcon/appSupport, 256px
`assets/icon.png`, README reworked as appstore page); #20 documented the doc-plugin in the user-guide
Server Plugins section; #21 README "Reading the docs" (direct browser access, no app) + appstore-listing
description; #22 tried a clickable config-page link via schema `description` (HTML) but it rendered as raw
tags; #23 reverted to plain text after verifying SignalK can't render links there, bumped to **0.1.2**.
Published 0.1.0 → 0.1.1 → 0.1.2 under the new **`dglcinc`** npm account; package indexed, appears as
"WilhelmSK Documentation".

**Publish auth gotcha:** `dglcinc` npm account has passkey-only 2FA + no classic/automation tokens →
publish with a **granular access token** inline: `npm publish "--//registry.npmjs.org/:_authToken=npm_…"`.
Registry read CDN lags ~1–2 min (verify with version-specific GET, not `npm view`); appstore lags further
(npm keyword indexing + SignalK server caches its Available list, restart to refresh). **Config-page link
NOT possible:** admin UI (`@rjsf/core` v5, custom `FieldTemplate` → `<p>{description}</p>`) renders the
schema `description` as plain text (HTML + markdown escaped) — the clickable entry point is the **Webapps
menu**. **Detection:** static `/signalk-wilhelmsk-docs/info.json`. **Gotcha:** `signalk-webapp` keyword
serves `public/` regardless of plugin enable state.

## Next Steps

1. **User: update server to 0.1.2** (`npm install signalk-wilhelmsk-docs@latest` + restart). Config page
   now clean plain text; clickable access via **Webapps → WilhelmSK Documentation**.
2. **User: revoke the granular npm token** pasted in chat.
3. Wait for Scott's review of upstream PR #99 (in-app docs picker); until merged + shipped, the in-app
   "Help → SignalK Server" path doesn't exist in the App Store build, but the plugin is useful standalone.
