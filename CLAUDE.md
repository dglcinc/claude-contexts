# Global Claude Context

This file is read at the start of every session when setting project context. It applies to all projects.

## Context Setup by Tool

### Cowork (desktop app)
When the user says "set context to X":
1. Check the mounted folder to detect which machine we're on (see Machine Detection below)
2. Read this global file
3. Read `CLAUDE.md` from the project repo at `<github-dir>/X/CLAUDE.md`
4. Run `git pull` in `<github-dir>/X/` to pull the latest code from GitHub
5. Confirm what's been loaded and the result of the pull, then wait for the next prompt — do not start any work yet

The global CLAUDE.md for Cowork is: `<github-dir>/claude-contexts/CLAUDE.md`

### Claude Code (CLI, used on the Pi)
Claude Code automatically reads `CLAUDE.md` from the current directory and all
parent directories — no "set context" command is needed. To set up:
1. Copy `pi-CLAUDE.md` from this repo to `~/CLAUDE.md` on the Pi (one-time, re-run after updates):
   ```bash
   cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
   ```
2. Start Claude Code from the project directory:
   ```bash
   cd ~/github/pivac && claude
   ```
   Claude Code will automatically read `~/CLAUDE.md` (global) and `~/github/pivac/CLAUDE.md` (project).

## Machine Detection

The VM always reports `Linux` for `uname -s` regardless of host, and the session name in the VM path changes each session. Detect the machine by checking for a Mac-specific marker in the mounted folder:

```bash
ls /sessions/*/mnt/Claude/github/Arduino 2>/dev/null && echo "mac" || echo "pi"
```

The Arduino repo only exists in the Mac OneDrive clone; the Pi clone does not have it. To get the current session path:

```bash
ls /sessions/
```

| Mounted path visible at VM                          | Machine               | Host Claude top-level folder       | Host GitHub directory                        |
|-----------------------------------------------------|-----------------------|------------------------------------|----------------------------------------------|
| `/sessions/<session>/mnt/Claude/` (OneDrive-backed) | Mac (David's MacBook) | `~/OneDrive - DGLC/Claude`         | `~/OneDrive - DGLC/Claude/github/`           |
| `/sessions/<session>/mnt/Claude/` (Pi home-backed)  | Raspberry Pi          | `/home/pi`                         | `/home/pi/github/`                           |

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code and documentation changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Git Workflow

### Mac (Cowork sessions)
Local git via Bash works fine on the Mac — OneDrive-mounted repos can be cloned and used normally from the VM. This is the preferred approach as it is more token-efficient than the GitHub MCP (sends diffs rather than full file contents).

**Standard workflow on Mac:**
- Edit files with Edit/Write tools, then commit and push with Bash git commands
- Repos are cloned at `<mnt>/Claude/github/<repo>/` with token auth embedded in the remote URL
- Token is stored at `<mnt>/Claude/.github-token`
- Set up a new clone with: `git clone https://dglcinc:<token>@github.com/dglcinc/<repo>.git`
- Use `git config user.email "dglcinc@users.noreply.github.com"` and `user.name "David Lewis"` after cloning
- Feature branches + PRs for code changes; push directly to main for meta/context files

**Use the GitHub MCP only for:**
- Merging pull requests (`mcp__github__merge_pull_request`)
- Creating repos (`mcp__github__create_repository`)
- Operations on repos not cloned locally

### Pi (Claude Code sessions)
Local git on the Pi is unreliable when the working directory is OneDrive-mounted. All git operations on the Pi must use the GitHub MCP tools instead. Never run `git push`, `git pull`, `git fetch`, or branch operations locally on the Pi.

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code.** Always create a feature branch and open a pull request for code and documentation changes. Only push directly to the default branch for meta/context files (CLAUDE.md).
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md (project and/or global) and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.
