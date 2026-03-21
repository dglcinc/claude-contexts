# Global Claude Context

This file is read at the start of every session when setting project context. It applies to all projects.

## How to Set Project Context

When the user says "set context to X":
1. Run `uname -s` and `whoami` to detect which machine we're on (see Machine Detection below)
2. Confirm you've read this global file
3. Read `CLAUDE.md` from the project repo at `<github-dir>/X/CLAUDE.md`
4. Confirm what's been loaded and wait for the next prompt — do not start any work yet

The global CLAUDE.md is always in: `<github-dir>/claude-contexts/CLAUDE.md`

## Machine Detection

Run `uname -s` to determine the machine:

| `uname -s` | `whoami` | Machine            | Claude top-level folder                          | GitHub directory                                      |
|------------|----------|--------------------|--------------------------------------------------|-------------------------------------------------------|
| `Darwin`   | `david`  | Mac (David's MacBook) | `~/OneDrive - DGLC/Claude`                    | `~/OneDrive - DGLC/Claude/github/`                    |
| `Linux`    | `pi`     | Raspberry Pi       | `/home/pi`                                       | `/home/pi/github/`                                    |

The Mac path resolves to: `/Users/david/Library/CloudStorage/OneDrive-DGLC/Claude`

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
