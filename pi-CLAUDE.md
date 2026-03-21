# Global Context — Raspberry Pi

This file lives at `~/CLAUDE.md` on the Pi. Claude Code reads it automatically
from the home directory whenever you work in any subdirectory (e.g. `~/github/pivac`).

To install or update it:
```bash
cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
```

## This Machine

- Host: Raspberry Pi at `10.0.0.82` (local), `68lookout.dglc.com` (external)
- User: `pi`
- GitHub directory: `~/github/`
- Python venv for pivac: `~/pivac-venv/` — always activate before running pivac scripts

## Projects on This Pi

- `~/github/pivac` — HVAC/home monitoring daemon (main project)
- `~/github/claude-contexts` — Global Claude context files (keep pulled)

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code.** Always create a feature branch and open a pull request for code changes. Only push directly to the default branch for meta/context files (CLAUDE.md).
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Current Work

- **pivac PR #16** (`feature/emporia-module`): adds `pivac.Emporia` module for Emporia Vue Gen 2 power monitoring.
  After merging:
  1. `git pull` in `~/github/pivac`
  2. `pip install pyemvue --break-system-packages` (in pivac-venv)
  3. Run `scripts/emporia-discover.py` to get device GIDs
  4. Add `pivac.Emporia` block to `/etc/pivac/config.yml` with real GIDs
  5. Install and enable `pivac-emporia.service`
  See `CLAUDE.md` in the pivac repo for full details.
