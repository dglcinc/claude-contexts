---
name: save-context
description: Save current session state before clearing or switching projects. Updates memory, CLAUDE.md files, and commits changes. Also triggered by "save context" or "wrap". Always run before /clear. Accepts an optional project name argument (full or unambiguous partial — e.g. /save-context claude resolves to claude-contexts) to save to a different context than the one launched with.
---

# /save-context

Save everything before clearing or switching projects. Run this, then type `/clear`, then `/set-context <project>`.

Usage: `/save-context [project-name]`

If a project name is passed as an argument (available as `$ARGS`), use that as the target context instead of auto-detecting from loaded CLAUDE.md files. The argument may be a full directory name (e.g. `bowling-league-tracker`) or any unambiguous partial of one (e.g. `bowling`, `nas`, `claude`). This is useful when you've been doing work relevant to a different project than the one you launched with.

## Performance principle

The two dominant costs in `/save-context` are (1) sequential network round trips and (2) the model recomposing the same summary multiple times for redundant write targets. Always:
- Run all read-only checks in step 2 in **one parallel tool message**, not sequentially.
- Compose the summary **once** in step 3 and reuse the same text verbatim in steps 4–6.
- Skip optional write targets when their preconditions don't hold (claude-contexts mirror, OneDrive context, MEMORY.md update) instead of writing empty / redundant content.

## Steps

### 1. Identify the active project

If `$ARGS` is empty, look at what CLAUDE.md files were loaded this session. The project name is the repo subdirectory under `~/github/` (e.g. `bowling-league-tracker`). If no project was set, skip to step 7.

If `$ARGS` is non-empty, the argument may be partial. Resolve it to a full project name before proceeding.

```bash
ARG="$ARGS"
# Candidate set: directories under ~/github/ and ~/github/claude-contexts/
# (excluding claude-contexts itself, which is the infrastructure repo)
CANDIDATES=$(
  { ls -1 ~/github/ 2>/dev/null; ls -1 ~/github/claude-contexts/ 2>/dev/null; } \
    | grep -v '^claude-contexts$' \
    | sort -u
)
# Match rules, in order:
# 1. Exact match (case-insensitive) → use it.
# 2. Prefix match (case-insensitive) → if exactly one, use it.
# 3. Substring match (case-insensitive) → if exactly one, use it.
MATCHES=$(echo "$CANDIDATES" | grep -i -- "$ARG")
```

Decision:
- **Exact match** (case-insensitive) on a directory name: use it, preserving the on-disk casing.
- **Single prefix or substring match**: use it, and surface the autocomplete in the confirmation prompt (e.g. "Resolved `claude` → `claude-contexts`").
- **Multiple matches**: do not guess. Use `AskUserQuestion` to present the matches and let the user pick. Then proceed with the chosen name.
- **No matches anywhere locally**: stop and ask the user. Save-context writes to an existing project's state — a no-match argument is almost always a typo, and silently falling through would scatter session-state files into nonexistent project memory dirs. Show the candidate set and ask the user to retry with a real name (or confirm they really want to create a new one).

After resolving, confirm with the user: "Saving to context **`<resolved-project>`** (overriding the launched context). Continue?" If the argument was partial, include the autocomplete in the prompt.

### 2. Gather state in parallel

Run **every** read-only check in this step as a single message with multiple Bash tool calls running in parallel. Sequencing them is the biggest avoidable wall-clock cost in this skill. The set:

```bash
# A. git status
cd ~/github/<project> && git status

# B. current branch
git -C ~/github/<project> branch --show-current

# C. open PRs
GITHUB_TOKEN=$(git -C ~/github/<project> remote get-url origin | sed 's/.*:\(.*\)@.*/\1/') \
  gh pr list --repo dglcinc/<project>

# D. existing memory files (for the promote-memories nudge in step 12)
ENCODED=$(echo "$HOME/github/<project>" | tr '/' '-')
ls ~/.claude/projects/${ENCODED}/memory/ 2>/dev/null

# E. claude-contexts mirror existence (gates step 6)
[ -d ~/github/claude-contexts/<project> ] && echo MIRROR_EXISTS || echo NO_MIRROR

# F. git remote presence (gates step 10)
git -C ~/github/<project> remote -v
```

Capture the results — every later step references one of these.

### 3. Draft the summary once

Compose **one** summary block now, before writing any files. The same text is used verbatim in steps 4, 5 (when applicable), and 6 (when applicable). Drafting once instead of three or four times is the largest token-cost win in this skill.

Draft three short blocks:
- **Last worked on** (2–4 sentences): what was actually done this session.
- **Next steps** (numbered list): remaining work in priority order.
- **Notes** (free prose): decisions, blockers, surprises, context that would be lost if not written down.

Keep it tight — this content lands in the session-state file as the source of truth. Steps 5 and 6, when they run, paste it into a `## Current State` section.

### 4. Write the session-state memory file

```bash
ENCODED=$(echo "$HOME/github/<project>" | tr '/' '-')
MEMDIR=~/.claude/projects/${ENCODED}/memory/
mkdir -p "$MEMDIR"
```

File: `${MEMDIR}/session_state_<project>.md`

Write or overwrite using the format at the bottom of this skill, populating the three blocks from step 3 plus `last_updated` (today's date), `current_branch` (from step 2B), and `open_prs` (from step 2C, or "none").

### 5. Update the project CLAUDE.md (only if meaningful changes happened)

Skip this step entirely unless the session produced one of: merged PRs, new architecture, new deployment behavior, new external integrations, new data-quality finding, new operational gotcha. Routine in-progress work belongs in the session-state file (step 4), not in CLAUDE.md.

If the bar is met: drop the **Last worked on** + **Notes** content from step 3 into the relevant subsection of `~/github/<project>/CLAUDE.md` (typically `## Current State` or a deployment / known-notes block). Use Edit, not Write.

### 6. Update the claude-contexts mirror (only if it exists)

Skip silently if step 2E reported `NO_MIRROR`. Most projects do not have a mirror — only those created via `/new-context` after the convention was introduced (currently `arch-as-code`, `archive`, `nas-cleanup`).

If the mirror exists (`~/github/claude-contexts/<project>/<project>.md`): paste the same step-3 summary into its `## Current State` section. Use Edit.

### 7. Update OneDrive cross-machine context (only if cross-machine state changed)

Skip unless the session changed something other machines need to know about: production IPs, hostnames, deployment commands, infrastructure topology, secrets locations, roadmap status. Routine app changes do not qualify.

If the bar is met: update `~/OneDrive - DGLC/Claude/<project>.md`. Create it from the `/new-context` step 4 template if it does not exist. Do not modify `~/OneDrive - DGLC/Claude/CLAUDE.md` — that is now an index only.

### 8. Update the MEMORY.md index (only if new memory files were added this session)

If you wrote new memory files this session (other than `session_state_<project>.md`), add one-line entries for them to the project memory folder's `MEMORY.md`.

### 9. Handle untracked files

From step 2A's `git status`, if there are untracked files (beyond `.claude/`):
- List them for the user.
- Ask which should be **committed**, which should be added to **`.gitignore`**, and which to leave alone for now.
- Add a `.gitignore` entry for anything the user wants ignored.
- Stage anything the user wants committed.

### 10. Handle missing remote

From step 2F: if there is no remote, ask: "Do you want to create a GitHub repository for this project under dglcinc? (y/n — public or private?)"

If yes:
```bash
GITHUB_TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token) \
  gh repo create dglcinc/<project> --<visibility> --source=. --remote=origin --push
```

### 11. Commit and push (in parallel where possible)

Two repos may need pushes:
- The project repo (if step 5, 8, 9, or 10 changed tracked files).
- The `claude-contexts` repo (if step 6 changed the mirror).

When both need pushes, run them as **two parallel Bash calls** in one message, not sequentially. Direct pushes to main are fine for context files (CLAUDE.md, memory files, mirror summaries).

### 12. Check for promotable memories

From step 2D's `ls`, count non-session-state memory files. If > 3:
> "You have N memory files that may be ready to promote. Run `/promote-memories` before `/clear` to graduate them to permanent CLAUDE.md files."

### 13. Confirm

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
