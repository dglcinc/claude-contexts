---
name: wrap
description: Session wrap-up — save context, update CLAUDE.md files, and capture session state so the next session starts with full context. Also triggered by "save context".
---

# /wrap — Session Wrap-Up ("save context")

Capture the current session state so the next session starts with full context.
This is also the implementation of the "save context" shortcut.

## When to use

Run `/wrap` (or say "save context") at the end of any work session, especially when
working on a named project (bowling-league-tracker, etc.).

## What to do when invoked

### 1. Identify the active project context
Look at what CLAUDE.md files were loaded this session. The project name is the
subdirectory under `~/github/` (e.g. `bowling-league-tracker`).

### 2. Check git state in the project repo
```bash
cd ~/github/<project> && git status && git branch --show-current
GITHUB_TOKEN=$(git remote get-url origin | sed 's/.*:\(.*\)@.*/\1/') \
  gh pr list --repo dglcinc/<project>
```

### 3. Update the session state memory file
Read then rewrite:
`~/.claude/projects/-Users-david-github-claude-contexts/memory/session_state_<project-slug>.md`

Include:
- `last_updated`: today's date
- `current_branch`: active branch (or "main")
- `open_prs`: PR numbers and titles, or "none"
- `last_worked_on`: 2–4 sentences describing what was done this session
- `next_steps`: what remains, in priority order
- `notes`: important decisions, blockers, or context future-Claude needs

### 4. Update the project CLAUDE.md
If the session produced meaningful changes (merged PRs, new architecture, completed
features, new decisions), update the `## Current State` section in
`~/github/<project>/CLAUDE.md` to reflect the new reality.

### 5. Update the claude-contexts summary file
Update `~/github/claude-contexts/<project>.md` (e.g. `bowling-league-tracker.md`)
`## Current State` section to match.

### 6. Update the OneDrive cross-machine context
If infrastructure, deployment, or roadmap changed, update
`~/OneDrive - DGLC/Claude/CLAUDE.md` so the other machine picks it up.

### 7. Update MEMORY.md if new memory files were written
If new memory files were created this session, add them to:
`~/.claude/projects/-Users-david-github-claude-contexts/memory/MEMORY.md`

### 8. Confirm
Tell the user what was saved and where, and note anything that still needs doing.

---

## Session state file format

```markdown
---
name: Session State — <Project Name>
description: In-progress session state for <project>; what was last worked on, open PRs, next steps
type: project
---

**Last updated:** YYYY-MM-DD
**Branch:** <branch or "main">
**Open PRs:** #123 — title (or "none")

## Last worked on
<2–4 sentences>

## Next steps
1. ...
2. ...

## Notes
<important context>
```
