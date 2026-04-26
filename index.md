# dglcinc — Project Index

Central navigation for all active projects. Each project folder contains context files for Claude sessions and planning notes.

## Active Projects

| Project | Repo | Context |
|---------|------|---------|
| Bowling League Tracker | [dglcinc/bowling-league-tracker](https://github.com/dglcinc/bowling-league-tracker) | [Session context](bowling/bowling-league-tracker.md) · [iOS/PWA plan](bowling/bowling-ios-app.md) |
| pivac | [dglcinc/pivac](https://github.com/dglcinc/pivac) | [Overview](pivac/overview.md) |
| MacDownToo | [dglcinc/MacDownToo](https://github.com/dglcinc/MacDownToo) | [Overview](macdown/overview.md) |
| Arduino sketches | [dglcinc/Arduino](https://github.com/dglcinc/Arduino) | ad hoc |
| WilhelmSK layouts | [dglcinc/wilhelm-sk](https://github.com/dglcinc/wilhelm-sk) | ad hoc |

## Global Claude Context

- [CLAUDE.md](CLAUDE.md) — global instructions loaded at the start of every Claude session (Mac)
- [pi-CLAUDE.md](pi-CLAUDE.md) — global instructions for Claude Code on the Raspberry Pi

## Infrastructure

- **Mac Mini** `utilityserver@10.0.0.84` — hosts bowling app (gunicorn), mlb.dglc.com
- **Raspberry Pi** `pi@10.0.0.82` — nginx TLS proxy for mlb.dglc.com, pivac HVAC monitoring, Grafana
- **MacBook** — primary development machine
- **GitHub** account: `dglcinc`

## Archived / Dormant

[Old repos](archive/old-repos.md) — MLB, boat-scripts, HVAC-plc, HVAC-pi, wafapps
