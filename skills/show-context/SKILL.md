---
name: show-context
description: Display a summary of the currently loaded project context — branch, open PRs, session state, and next steps. Usage: /show-context
---

# /show-context

Display a snapshot of the current project context. No files are modified.

## Steps

### 1. Identify the active project

Infer the project name from what CLAUDE.md files are in context this session, or from the current working directory. If no project is loaded, report that and stop.

### 2. Check git state

```bash
git -C ~/github/<project> branch --show-current
git -C ~/github/<project> status --short
```

### 3. Check open PRs

```bash
GITHUB_TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token) \
  gh pr list --repo dglcinc/<project> --state open
```

### 4. Read session state

Read `~/.claude/projects/-Users-david-github-<project>/memory/session_state_<project>.md` if it exists.

### 5. Display the summary

Print a compact summary in this format:

```
## Context: <project>

**Branch:** <branch>
**Dirty files:** <count or "clean">
**Open PRs:** #123 — title (or none)

### Last session
<last_worked_on from session state, or "no session state found">

### Next steps
<numbered list from session state, or "—">

### Notes
<notes from session state, or "—">
```

Do not read or display the full project CLAUDE.md — this is a quick status view, not a full reload. If the user wants the full context, tell them to run `/set-context <project>`.
