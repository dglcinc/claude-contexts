---
name: set-context
description: Load full context for a project. Reads per-project OneDrive context file, project summaries, session state, and project CLAUDE.md. Clones the repo if missing, otherwise runs git pull. Usage: /set-context <project-name>
---

# /set-context

Load full context for a project. Usage: `/set-context <project-name>`

## Input

The argument is the repo directory name under `~/github/` (e.g. `bowling-league-tracker`). If no argument was given, ask for it before proceeding.

## Steps

### 1. Pull claude-contexts
```bash
git -C ~/github/claude-contexts pull
```
This updates `global.md`, `pi-CLAUDE.md`, and all skills in place via their symlinks — no restart needed.

If this is the first time using this machine after the memory system was added, also run `~/github/claude-contexts/setup.sh` once to install the memory symlinks (`~/.claude/memory`, `~/.claude/hooks`) and merge the PreToolUse hook block into `~/.claude/settings.json`. Idempotent — safe to re-run any time. Requires `jq`.

### 2. Load cross-machine context (OneDrive)

Check for all files matching `~/OneDrive - DGLC/Claude/<project>*.md`. If none exist, skip silently.

If files exist: check their combined size:
```bash
ls ~/OneDrive\ -\ DGLC/Claude/<project>*.md 2>/dev/null | xargs wc -c 2>/dev/null | tail -1
```

- If combined size is **over 2,000 chars**: spawn an **Explore** subagent to read all matching files and return a structured brief covering: (1) infrastructure IPs and hostnames, (2) roadmap status — which phases are done and which are open, (3) any open data quality issues or pending actions. Keep the brief under 400 words. The subagent reads the full files; only the summary enters the main conversation.
- If combined size is **2,000 chars or under**: read the files directly.

### 3. Read project summaries
If `~/github/claude-contexts/<project>/` exists:
- Read `~/github/claude-contexts/<project>/<project>.md` — project context summary
- Read any other `*.md` files in that folder — supplemental plans and notes

### 4. Read session state
The per-project memory path is derived from `$HOME` (it differs by machine — `/Users/david`, `/Users/utilityserver`, `/home/pi`). Compute it with:
```bash
ENCODED=$(echo "$HOME/github/<project>" | tr '/' '-')
ls ~/.claude/projects/${ENCODED}/memory/session_state_<project>.md 2>/dev/null
```
If the file exists, read it — last session's branch, open PRs, next steps, and notes.

### 5. Sync local clone

Check whether `~/github/<project>/` exists.

- **If it exists**: run `git pull` in `~/github/<project>/` with `dangerouslyDisableSandbox: true`.
- **If it does not exist**: clone it. The token lives at `~/OneDrive - DGLC/Claude/.github-token`:
  ```bash
  TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token)
  git clone "https://dglcinc:${TOKEN}@github.com/dglcinc/<project>.git" ~/github/<project>
  git -C ~/github/<project> config user.email "dglcinc@users.noreply.github.com"
  git -C ~/github/<project> config user.name "David Lewis"
  ```
  If the clone fails (repo doesn't exist on GitHub, auth error, etc.), surface the error and stop — do not proceed to step 5. Note in the final summary whether the repo was pulled or freshly cloned.

### 6. Read project CLAUDE.md

First check if Claude Code is running from within the project directory:
```bash
[[ "$(pwd)" == "$HOME/github/<project>"* ]] && echo "IN_PROJECT" || echo "NOT_IN_PROJECT"
```

- If `IN_PROJECT`: the runtime has already auto-loaded `CLAUDE.md` — skip reading it and note "CLAUDE.md auto-loaded by runtime" in the summary.
- If `NOT_IN_PROJECT`: read `~/github/<project>/CLAUDE.md` — full project context: architecture, data model, routes, deployment.

### 7. Confirm and wait
Report what was loaded and the result of the git pull/clone in a brief summary. Include a one-line reminder: "Type `/rename <project>` to title your HUD session." Then **wait for the user's next instruction** — do not begin any work.

## On the Pi

Claude Code on the Pi reads `~/CLAUDE.md` (global) and `~/github/<project>/CLAUDE.md` (project) automatically from the working directory hierarchy — no `/set-context` needed. Start Claude Code from the project directory:

```bash
cd ~/github/pivac && claude
```
