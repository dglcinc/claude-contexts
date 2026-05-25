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

## Current State (2026-05-25)

Through PR #18 squash-merged; `main` clean. This session: tested the plugin live on the pivac Pi
(installed + nginx proxy for the docs path); replaced the auth-gated `/plugins/.../info` route with
a static `public/info.json` (PR #17); documented the picker behavior (PR #18). On the iOS side
(upstream [sbender9/Wilhelm #99](https://github.com/sbender9/Wilhelm/pull/99), open, awaiting Scott)
added a reachability probe, fixed the unreachable picker (modal presentation), extracted a
`WSKDocsSource` resolver for future context-help, and made Help close return to the app.

**Detection:** `/signalk-wilhelmsk-docs/info.json` (static, unauthenticated). **Gotcha:** the
`signalk-webapp` keyword serves `public/` regardless of plugin enable state.

## Next Steps

1. Wait for Scott's review of upstream PR #99.
2. Pre-publish prep for npm / SignalK AppStore (signalk config block, displayName, appIcon, `npm publish`).
3. Context-help PR in Wilhelm — use `WSKDocsSource docsURLForAnchor:`, don't show the picker, default to web when source unset/None.
