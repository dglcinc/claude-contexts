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

- PRs #37–#86 all merged to main; no open PRs
- Mobile PWA complete; push notifications deployed (PR #65); admin UI overhauled (PRs #66–#67)
- Historical import (PRs #68–#69): 13 seasons imported (2004-2005 through 2016-2017)
- Tournament data corrections (PRs #70–#73): bulk email, placement fixes, historical tournament winner repair
- Bowler merges + tournament year shift (PR #75): Brywlaski, Kincey, Oakley, Graf duplicates merged; Mike Schmitt/Tucker names corrected; Martorana first name filled in; all tournament placement entries shifted one year earlier (2004-05 through 2016-17 were each carrying prior year's winners); 2003-04 stub season created (id=23)
- UI improvements + club championship (PR #76): ClubChampionshipResult model + admin entry; sortable column headers (wkly_alpha, ytd_alpha, bowler_dir, records); bowler_detail breadcrumb back nav; Flask-Caching on Records and Bowler Directory (10 min, busted on score entry)
- Post-season score entry fixes (PRs #82–#83): null team guards in score_position_night + position_entry; season selector now navigates correctly on admin pages (/seasons/ URL pattern)
- Sortable columns extended (PRs #84, #86): bowler_detail (all 3 tables), Records By Season tab (flattened header)
- Club championship finalists rule (PR #85): if same team wins both halves, finalists are that team + second-place second-half team
- Next: season rollover wizard; enter historical club championship winners via Admin → Tournament Placements

## Git Workflow

CLAUDE.md pushes directly to main. All other code and documentation changes use feature branches + PRs. See global CLAUDE.md for full workflow.

For `gh` CLI: token is embedded in the remote URL — prefix commands with:
```bash
GITHUB_TOKEN=$(git remote get-url origin | sed 's/.*:\(.*\)@.*/\1/')
```
