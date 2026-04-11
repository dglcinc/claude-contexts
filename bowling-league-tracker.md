# Bowling League Tracker — Session Context

## How to Load This Context

Tell Claude: "set context bowling-league-tracker"

Claude will:
1. Read this file
2. Read `~/github/bowling-league-tracker/CLAUDE.md` for the full data model
3. Confirm context loaded and wait for instructions

## Project Location

- Repo: `dglcinc/bowling-league-tracker` (private, GitHub)
- Local clone: `~/github/bowling-league-tracker`
- VM mount: `/sessions/<session>/mnt/github/bowling-league-tracker`

## What This Project Is

A replacement/augmentation for the Mountain Lakes Men's Bowling League Excel scoring workbook. The source spreadsheet (`scoring 2025-2026 - Week 20.xlsx`) lives in `~/OneDrive - DGLC/Claude/` and is the reference for the data model.

## Key Facts

- 23-week season (October – March), ~65 bowlers, 4 teams
- Handicap formula: `INT(0.9 * (200 - current_average))`
- One Excel sheet per bowler; summary sheets: `wkly alpha`, `team scoring`, `indiv payout`, `Payout Formula`
- Stack: Flask + SQLAlchemy + SQLite, Bootstrap 5, Jinja2

## Production Deployment (live as of 2026-04-11)

- URL: https://mlb.dglc.com
- Server: Mac Mini M4, `utilityserver@10.0.0.84`
- nginx reverse proxy + TLS: Pi at `pi@10.0.0.82`
- App: gunicorn via launchd (`com.dglc.bowling-app`), binds `0.0.0.0:5001`
- DB: `~/OneDrive - DGLC/Claude/bowling-league-tracker/league.db` (OneDrive installed on server; auto-detected by config.py)
- Restart: `pkill -f "gunicorn.*wsgi"` (launchd auto-restarts)
- Logs: `/tmp/bowling-app.log`, `/tmp/bowling-app.err`

## Current PR Status (as of 2026-04-11)

- PRs #37–#40 merged to main
- **PR #41 `feature/otp-login` open** — replaces magic link email with 6-digit OTP code; 90-day sessions; PWA renamed to "MLC Bowling". Already deployed on production server; needs merge.

## Next Up

1. Merge PR #41
2. Season rollover wizard

## Git Workflow

CLAUDE.md pushes directly to main. All other code and documentation changes use feature branches + PRs. See global CLAUDE.md for full workflow.

For `gh` CLI: token is embedded in the remote URL — prefix commands with:
```bash
GITHUB_TOKEN=$(git remote get-url origin | sed 's/.*:\(.*\)@.*/\1/')
```
