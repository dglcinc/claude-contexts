# Global Claude Context

This file is read at the start of every session when setting project context. It applies to all projects.

## Context Setup by Tool

### Cowork (desktop app)
When the user says "set context to X":
1. Check the mounted folder to detect which machine we're on (see Machine Detection below)
2. Read this global file
3. Read `CLAUDE.md` from the project repo at `<github-dir>/X/CLAUDE.md`
4. Confirm what's been loaded and wait for the next prompt — do not start any work yet

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

The VM always reports `Linux` for `uname -s` regardless of host, so detect the machine by checking the mounted folder path instead:

```bash
ls /Users/david/Library/CloudStorage/OneDrive-DGLC/Claude/github 2>/dev/null && echo "mac" || echo "pi"
```

| Mounted path visible at VM                                      | Machine               | Host Claude top-level folder       | Host GitHub directory                        |
|-----------------------------------------------------------------|-----------------------|------------------------------------|----------------------------------------------|
| `/sessions/eager-modest-noether/mnt/Claude/` (OneDrive-backed) | Mac (David's MacBook) | `~/OneDrive - DGLC/Claude`         | `~/OneDrive - DGLC/Claude/github/`           |
| `/sessions/eager-modest-noether/mnt/Claude/` (Pi home-backed)  | Raspberry Pi          | `/home/pi`                         | `/home/pi/github/`                           |

To distinguish Mac vs Pi when both mount to the same VM path, check for a Mac-specific marker:
```bash
ls /Users/david/Library/CloudStorage/OneDrive-DGLC/Claude/github/Arduino 2>/dev/null && echo "mac" || echo "pi"
```
(The Arduino repo only exists in the Mac clone; the Pi clone does not have it.)

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code and documentation changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code.** Always create a feature branch and open a pull request for code and documentation changes. Only push directly to the default branch for meta/context files (CLAUDE.md).
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md (project and/or global) and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.
