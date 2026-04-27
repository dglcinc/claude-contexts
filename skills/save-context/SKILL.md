---
name: save-context
description: Save current session state before clearing or switching projects. Updates memory, CLAUDE.md files, and commits changes. Also triggered by "save context" or "wrap". Always run before /clear. Accepts an optional project name argument (e.g. /save-context claude-contexts) to save to a different context than the one launched with.
---

# /save-context

Save everything before clearing or switching projects. Run this, then type `/clear`, then `/set-context <project>`.

Usage: `/save-context [project-name]`

If a project name is passed as an argument (available as `$ARGS`), use that as the target context instead of auto-detecting from loaded CLAUDE.md files. This is useful when you've been doing work relevant to a different project than the one you launched with.

## Steps

### 1. Identify the active project
If `$ARGS` is non-empty, use that value as the project name (e.g. `/save-context claude-contexts` → project = `claude-contexts`). Otherwise, look at what CLAUDE.md files were loaded this session. The project name is the repo subdirectory under `~/github/` (e.g. `bowling-league-tracker`). If no project was set, skip to step 6.

When using an argument-supplied project name, confirm with the user: "Saving to context **`<project>`** (overriding the launched context). Continue?"

### 2. Check git state
```bash
cd ~/github/<project> && git status && git branch --show-current
GITHUB_TOKEN=$(git remote get-url origin | sed 's/.*:\(.*\)@.*/\1/') \
  gh pr list --repo dglcinc/<project>
```

### 3. Update the session state memory file
Memory folder: `~/.claude/projects/-Users-david-github-<project>/memory/`
File: `session_state_<project>.md`

Write or overwrite with:
- `last_updated`: today's date
- `current_branch`: active branch or "main"
- `open_prs`: PR numbers and titles, or "none"
- `last_worked_on`: 2–4 sentences on what was done
- `next_steps`: remaining work in priority order
- `notes`: decisions, blockers, context future-Claude needs

### 4. Update the project CLAUDE.md
If meaningful changes happened (merged PRs, new architecture, new decisions), update the `## Current State` section in `~/github/<project>/CLAUDE.md`.

### 5. Update the claude-contexts project summary
Update `~/github/claude-contexts/<project>/<project>.md` `## Current State` section to match.

### 6. Update OneDrive cross-machine context
If infrastructure, deployment, or roadmap changed, update `~/OneDrive - DGLC/Claude/<project>.md`. If that file does not exist yet, create it (see `/new-context` step 4 for the template). Do not modify `~/OneDrive - DGLC/Claude/CLAUDE.md` — that is now an index only.

### 7. Update MEMORY.md index
If new memory files were created this session, add them to the memory folder's `MEMORY.md`.

### 8. Handle untracked files
Run `git status` in the project directory. If there are untracked files (beyond `.claude/`):
- List them for the user
- Ask which should be **committed**, which should be added to **`.gitignore`**, and which to leave alone for now
- Add a `.gitignore` entry for anything the user wants ignored
- Stage anything the user wants committed

### 9. Handle missing remote
Check whether a git remote exists (`git remote -v`). If there is no remote:
- Ask: "Do you want to create a GitHub repository for this project under dglcinc? (y/n — public or private?)"
- If yes, create it:
  ```bash
  GITHUB_TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token) \
    gh repo create dglcinc/<project> --<visibility> --source=. --remote=origin --push
  ```

### 10. Commit any CLAUDE.md changes
Push updated CLAUDE.md files directly to main (no PR needed for context files).

### 11. Check for promotable memories
Count the memory files in the current project's memory folder. If there are more than 3 non-session-state memories, remind the user:
> "You have N memory files that may be ready to promote. Run `/promote-memories` before `/clear` to graduate them to permanent CLAUDE.md files."

### 12. Confirm
Tell the user what was saved and where. Remind them to run `/clear` when ready to switch context.

---

## Session state file format

```markdown
---
name: Session State — <Project Name>
description: In-progress session state for <project>
type: project
---

**Last updated:** YYYY-MM-DD
**Branch:** <branch or "main">
**Open PRs:** #123 — title (or "none")

## Last worked on
<2–4 sentences>

## Next steps
1. ...

## Notes
<decisions, blockers, context>
```
