# Bowling League Tracker — Session Context

## How to Load This Context

Tell Claude: "set context bowling-league-tracker"

Claude will:
1. Read this file
2. Read `~/github/bowling-league-tracker/CLAUDE.md` for the full data model and current state
3. Confirm context loaded and wait for instructions

## Project Location

- Repo: `dglcinc/bowling-league-tracker` (private, GitHub)
- Local clone: `~/github/bowling-league-tracker`

## What This Project Is

A Flask web app replacing the Mountain Lakes Men's Bowling League Excel scoring workbook.
Full stack: Python 3 / Flask / SQLAlchemy / SQLite, Bootstrap 5, Jinja2. No JS frameworks.

## Key Facts

- 26-week season (22 regular + 4 post-season tournaments), ~65 bowlers, 4 teams
- Handicap: `ROUND((200 - prior_week_avg) * 0.9)` for established bowlers (≥6 games)
- All stats computed on the fly from raw `MatchupEntry` rows — nothing derived stored

## Production Deployment (live as of 2026-04-11)

- URL: https://mlb.dglc.com
- Server: Mac Mini M4, `utilityserver@10.0.0.84`
- nginx reverse proxy + TLS: Pi at `pi@10.0.0.82`
- App: gunicorn via launchd (`com.dglc.bowling-app`), binds `0.0.0.0:5001`
- DB: `~/bowling-data/league.db` (local on utilityserver — NOT OneDrive; SQLite + cloud sync = corruption risk; backups handle redundancy)
- Restart: `pkill -f "gunicorn.*wsgi"` (launchd auto-restarts)
- Logs: `/tmp/bowling-app.log`, `/tmp/bowling-app.err`

## Current State (as of 2026-04-13)

- PRs #37–#69 all merged to main; no open PRs
- Mobile PWA complete: `/m/` blueprint, device detection, Home/Standings/Scores/Me/Schedule tabs, passkeys with conditional mediation, desktop home 3-column dashboard, navbar refactor
- Push notifications: Web Push/VAPID fully implemented and deployed (PR #65); Me tab has full onboarding flow; launchd timer running on utilityserver every 10 min
- Admin UI overhaul (PRs #66–#67): Weekly Alpha rename, All Bowlers removed, roster Active/All filter, Send Invite with configurable message, viewer access on Scores pages, YTD Alpha team filter, Reports button label bug fixed
- Historical import (PRs #68–#69): 13 seasons imported (2004-2005 through 2016-2017); 1st/2nd/3rd tournament placements captured with `place` field on TournamentEntry; unified roster All view (no separate "unrostered" section); `LAST_NAME_ALIASES` for Gosset→Gossett, Gradofsky→Grodofsky; all name disambiguation handled automatically via first-name data in sheets
- Next: season rollover wizard

## Git Workflow

CLAUDE.md pushes directly to main. All other code and documentation changes use feature branches + PRs. See global CLAUDE.md for full workflow.

For `gh` CLI: token is embedded in the remote URL — prefix commands with:
```bash
GITHUB_TOKEN=$(git remote get-url origin | sed 's/.*:\(.*\)@.*/\1/')
```
