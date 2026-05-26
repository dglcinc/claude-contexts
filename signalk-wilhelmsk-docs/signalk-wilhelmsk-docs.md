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
  (auto-rebuilds `plugin/public/` and commits it back to the branch), `publish.yml` (npm OIDC
  trusted publishing on a `v*` tag push or manual run)

## Key Facts

- **Remote:** `https://github.com/dglcinc/signalk-wilhelmsk-docs.git` (HTTPS, dglcinc). Public.
- **Default branch:** `main`. Doc/code changes via feature branch + PR; self-merge OK (David sole reviewer).
- **Mount path:** SignalK auto-mounts a plugin's `public/` at `/<package-name>/`, so docs serve at
  `/signalk-wilhelmsk-docs/` (NOT the original `/wilhelmsk-docs/` — fixed in PR #5). Info endpoint:
  `/plugins/signalk-wilhelmsk-docs/info`.
- **Editing docs:** edit `docs/`, verify `mkdocs build --strict`, open a PR. CI (`verify-plugin-docs.yml`)
  rebuilds `plugin/public/` and **commits it back** to your branch — no manual `npm run build-docs`. (CI
  adds a `github-actions[bot]` commit, so `git pull` before adding more local commits.)
- **Releasing:** OIDC trusted publishing. Bump `plugin/package.json` + CHANGELOG, merge, then
  `git tag vX.Y.Z && git push origin vX.Y.Z` → `publish.yml` publishes to npm with no token/OTP.
- **MkDocs venv:** this repo now has its own `.venv/` — prefer `.venv/bin/mkdocs`.
- **Content direction (Scott's calls):** no public contributor docs; user guide leads with Connecting,
  with SignalK / Victron VRM / NMEA gateways as parallel subsections; tvOS, CarPlay, iKommunicate,
  Raymarine references removed.

## Current State (2026-05-26, gauge-reference + automation session)

`main` clean. **Published 0.1.6 to npm via OIDC trusted publishing** (no token, no OTP); tag `v0.1.6` pushed.
This session (PRs all merged): **#33** rewrote the user-guide **Gauge Reference** — added 5 missing gauge
types (StaticThermostat, Raymarine MFD, WavyTank, AWA Close-Hauled, Watch Grid), verified every gauge's
SignalK path against the WilhelmSK source (`Wilhelm/gauges.json`, 90 classNames) and fixed the wrong ones,
added a "Displays" description + a "SignalK Path(s) / Source" column to every section (controls vs
read-only marked), and a fixed-width table layout (`docs/stylesheets/extra.css` via `md_in_html`). **#34**
released 0.1.6 and switched `verify-plugin-docs.yml` from verify-and-fail to **rebuild-and-commit**
(ends the drift emails). **#35** added `publish.yml` for trusted publishing. Also opened
[sbender9/Wilhelm#101](https://github.com/sbender9/Wilhelm/issues/101) — the `AISTargetsTable` gauges.json
picker entry has no `GaugeConfig` class (the AIS table is actually embedded in the `AISTargets` gauge).

**Key automations now in place:** docs PRs auto-rebuild `plugin/public/` in CI (no manual step, no drift
emails); releases publish hands-free on a `v*` tag via OIDC (npm trusted publisher configured = repo +
`publish.yml`). GitHub Pages and the npm plugin bundle are decoupled channels — Pages updates on every
merge, plugin users only on a new release.

## Next Steps

1. **Mention sbender9/Wilhelm#101 to Scott on the Signal K Discord** (drop the dead picker line vs add the
   missing class — offered to PR either).
2. **Update the pi to 0.1.6** (`npm install signalk-wilhelmsk-docs@latest` + restart, or auto-update).
3. **Revoke the granular npm token** from the prior session — trusted publishing makes it unnecessary.
4. Optional: bump the pinned GitHub Actions off Node 20 (deprecation warning).
