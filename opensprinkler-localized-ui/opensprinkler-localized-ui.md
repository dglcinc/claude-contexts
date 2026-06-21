# opensprinkler-localized-ui — context summary

A fork of [`OpenSprinkler/OpenSprinkler-App`](https://github.com/OpenSprinkler/OpenSprinkler-App)
(repo: `dglcinc/opensprinkler-localized-ui`) that adds a **localization layer** so the
OpenSprinkler web UI shows irrigation flow in **gallons** instead of the upstream's
hard-coded liters. Self-hosted on the home Pi, points at the OpenSprinkler 3.2
controller at `10.0.0.17:5000`.

Full project context, the why, and deploy live in the repo's own `CLAUDE.md`. This file
exists for Mac-side sessions driving Pi operations.

## Why it exists

OpenSprinkler's firmware/API is SI-only (flow stored as `fpr` in liters/pulse, no unit
tag). The official app has an `isMetric` toggle but its **flow displays ignore it** and
hard-code `L`/`L/min`, so a US user can't get gallons. This fork wires the existing
`isMetric` flag into the flow display sites and converts liters→gallons at render time.
Sibling project **pivac** already reports the same flow in gallons to Grafana/WilhelmSK
independently; this fork is the *device's own control UI*, localized.

## Current state (2026-06-21, end of session — SHELVED)

v1 built, deployed reboot-savvy on the Pi, and **tested live (gallons confirmed)**. Also
fixed the Edit Options pulse-rate row to live-convert gal↔L on the isMetric/unit toggle.
**Then shelved:** the user reset the device to **`fpr=1` (L/pulse)** to keep the *stock*
phone app + Grafana as status quo, and will pick up the localized-UI / app-store path later.

> **⚠️ Before resuming the :8088 UI, set the device pulse rate back to `1 gal/pulse`**
> (stored ~3.78 = true liters). Under the current `fpr=1` the fork UI reads ~3.785× low.
> The stock app and this fork want opposite device settings; pivac/Grafana are correct
> under either. Next decisions: remote via `jsp` (same-origin, no rebuild) vs native build
> (Cordova — Android sideload easy, iOS needs Apple signing); then v2 (number/date formats).

## Current state (2026-06-21, mid-session)

- **v1 shipped + deployed + tested live.** Flow reads in gallons in the UI (confirmed).
  Centralized helpers in `www/js/modules/utils.js` (`volumeToDisplay`/`volumeUnit`/
  `flowRateUnit`), wired into all six flow display sites in `status.js`/`logs.js`.
  Merged to `master`.
- **Reboot-savvy install on the Pi (`10.0.0.82`):** served LAN-only, plain HTTP on
  **`http://10.0.0.82:8088/`** straight from `~/github/opensprinkler-localized-ui/www`
  via nginx (`os-localized-ui` site), ufw allows 8088 from `10.0.0.0/24`, nginx enabled
  on boot. Install/update codified in `deploy/install.sh` + `deploy/nginx-os-localized-ui.conf`.
- **Device requirement:** controller pulse rate set to **`1 gal/pulse`** in the app
  (stored as `fpr≈3.78` = true liters) so the UI's liters→gallons conversion is correct;
  "Use Metric" **off**. Does not affect pivac (reads raw `flcrt` with its own factor).
- `upstream` remote = `OpenSprinkler/OpenSprinkler-App` for rebasing. License **AGPL-3.0**.

## Next steps / open

1. **v2 localization (not built):** app-wide decimal comma/dot number formatting and
   date-format order. Design + canonical-units model in
   `~/github/pivac/docs/opensprinkler-gallons-ui-fork-scope.md`.
2. **Remote access (not set up):** would need solving the HTTPS→HTTP mixed-content
   issue (OS app expects the controller at a root URL, not a path prefix).
3. Optional: cherry-pick locale/translation updates from the actively-maintained
   `opensprinklershop/OpenSprinkler-App` fork (reference only; it still has the liter bug).
4. Optional upstream PR of the `isMetric`-aware flow fix to retire the fork.
