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
- Tech stack not yet chosen

## Git Workflow

Standard Mac/Cowork workflow — see global CLAUDE.md. Feature branches + PRs for all code changes.
