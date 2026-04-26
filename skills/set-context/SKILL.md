---
name: set-context
description: Load full context for a project. Reads OneDrive CLAUDE.md, project summaries, session state, and project CLAUDE.md, then runs git pull. Usage: /set-context <project-name>
---

# /set-context

Load full context for a project. Usage: `/set-context <project-name>`

## Input

The argument is the repo directory name under `~/github/` (e.g. `bowling-league-tracker`). If no argument was given, ask for it before proceeding.

## Steps

### 1. Read cross-machine context
Read `~/OneDrive - DGLC/Claude/CLAUDE.md` — infrastructure details, private IPs, deployment state, roadmap.

### 2. Read project summaries
If `~/github/claude-contexts/<project>/` exists:
- Read `~/github/claude-contexts/<project>/<project>.md` — project context summary
- Read any other `*.md` files in that folder — supplemental plans and notes

### 3. Read session state
If `~/.claude/projects/-Users-david-github-<project>/memory/session_state_<project>.md` exists, read it — last session's branch, open PRs, next steps, and notes.

### 4. Read project CLAUDE.md
Read `~/github/<project>/CLAUDE.md` — full project context: architecture, data model, routes, deployment.

### 5. Pull latest
Run `git pull` in `~/github/<project>/` with `dangerouslyDisableSandbox: true`.

### 6. Confirm and wait
Report what was loaded and the result of the git pull in a brief summary. Then **wait for the user's next instruction** — do not begin any work.

## On the Pi

Claude Code on the Pi reads `~/CLAUDE.md` (global) and `~/github/<project>/CLAUDE.md` (project) automatically from the working directory hierarchy — no `/set-context` needed. Start Claude Code from the project directory:

```bash
cd ~/github/pivac && claude
```
