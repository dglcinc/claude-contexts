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

## Current State (2026-05-26 pt.2, Scott's doc fixes + theme match)

`main` clean, no open PRs. **4 PRs merged this session.** **#42** implemented all six issues Scott filed
against the user guide (closes #36–#41): Digital Yacht RAW reframed as a **YDWG alias** (plain NMEA 0183,
not NMEA 2000); Actisense W2K **DS2-Server / N2K-ASCII** setup (port 60002) per the SK FAQ; Remote Access
**VPN/tunnel options** (Tailscale/ZeroTier/ngrok/remote.it); Watch Quirks corrected (**SignalK keeps
working when the phone is out of range** — watch caches token/connection details); plugin-dependency matrix
fixes (drop deprecated `signalk-zones` → zones built into server; vendor-agnostic `@signalk/signalk-autopilot`;
Fusion → `signalk-fusion-stereo`; track overlay → a Tracks-API plugin; Freeboard-SK → `freeboard-sk`; add
`signalk-wilhelmsk-plugin`); new **Shortcuts and Siri** section. Then matched the docs theme to
**wilhelmsk.com** over three iterations — **#43** (teal, wrong), **#44** (near-black + brass wordmark),
**#45** (**deep brown**, correct). Final palette in `docs/stylesheets/extra.css`: body `#574035`,
header/code `#382A23`, white text, brass accents `#CFB57C`, brass wordmark; dark scheme default. Pages
deployed and verified live. **Awaiting Scott's feedback.**

**Theme caveat:** it is **deep brown, not teal/near-black** — wilhelmsk.com's Wix near-black token `#061E20`
(faint cool cast) misled an early pass into teal. Verify rendered colors against what David sees. Color-only;
serif fonts (Enriqueta/Museo Slab) skipped (proprietary + offline serving). Two issue-wording corrections:
Fusion plugin is really `signalk-fusion-stereo`; `signalk-zones` has no successor (built into the server).

**History (pt.1, gauge-reference + automation):** #33 rewrote the Gauge Reference (5 missing gauges, paths
verified against `Wilhelm/gauges.json`); #34 released **0.1.6** + switched `verify-plugin-docs.yml` to
rebuild-and-commit; #35 added `publish.yml` (OIDC trusted publishing). Bundle auto-rebuild and hands-free
`v*`-tag publishing remain in place. Opened sbender9/Wilhelm#101.

## Next Steps

1. **Await Scott's feedback** on the content fixes + deep-brown/brass styling; fold in tweaks (e.g. brighten
   brass body links if dim on the brown — one line in `extra.css`).
2. **Mention sbender9/Wilhelm#101 to Scott on the Signal K Discord** (drop the dead picker line vs add the
   missing class — offered to PR either).
3. **Update the pi to 0.1.6** (`npm install signalk-wilhelmsk-docs@latest` + restart, or auto-update).
4. **Revoke the granular npm token** from the prior session — trusted publishing makes it unnecessary.
5. Optional: bump the pinned GitHub Actions off Node 20 (deprecation warning).
