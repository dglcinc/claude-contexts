# Claude Contexts — Tool Configuration

Tool-specific configuration and workflow quirks. Global working-style preferences live in `global.md` (symlinked to `~/.claude/CLAUDE.md`). To load a project: `/set-context <project>`.

## Machine Detection

The VM always reports `Linux` for `uname -s` regardless of host, and the session name in the VM path changes each session. Detect the machine by checking for a Mac-specific marker in the mounted folder:

```bash
ls /sessions/*/mnt/github/Arduino 2>/dev/null && echo "mac" || echo "pi"
```

The Arduino repo only exists in the Mac github clone; the Pi clone does not have it. To get the current session path:

```bash
ls /sessions/
```

| Mounted path visible at VM                          | Machine               | Host Claude top-level folder       | Host GitHub directory              |
|-----------------------------------------------------|-----------------------|------------------------------------|-------------------------------------|
| `/sessions/<session>/mnt/Claude/` (OneDrive-backed) | Mac (David's MacBook) | `~/OneDrive - DGLC/Claude`         | `~/github/`                         |
| `/sessions/<session>/mnt/github/` (Mac github dir) | Mac (David's MacBook) | `~/github`                         | `~/github/`                         |
| `/sessions/<session>/mnt/Claude/` (Pi home-backed)  | Raspberry Pi          | `/home/pi`                         | `/home/pi/github/`                  |

## Content Perimeter

Content is classified as either **infrastructure** (GitHub-managed) or **personal** (stays within David's personal devices and cloud tenants). Claude may freely read and write both, but must never move personal content outside the perimeter.

### Personal perimeter — never commit to GitHub or send to external services
- `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/dglcinc/` — personal Obsidian vault
- `~/OneDrive - DGLC/` — all of OneDrive (including the Claude working folder)
- Any file the user explicitly identifies as personal

### Infrastructure — GitHub-managed, may be public
- `~/github/claude-contexts/` — agentic infrastructure: CLAUDE.md files, project context, plans, skills
- All other repos under `~/github/` — project code and documentation

### Rules
- Never `git add`, commit, or push files from personal locations
- Never send personal content to external APIs, services, or third-party tools
- Never mix personal content into infrastructure files (e.g. do not paste personal notes into CLAUDE.md)
- Claude may read personal content to inform its work, but the output of that work must respect the same perimeter as the input

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code and documentation changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Git Workflow

### Mac (Cowork sessions)
Repos live at `~/github/` (outside OneDrive) and are mounted into the VM at `/sessions/<session>/mnt/github/`. The VM can create and modify files in this mount but **cannot delete files** — this is a VirtioFS security restriction, not a permissions issue.

**Practical consequences:**
- The VM cannot delete files by default. Before any `git pull` or `rm` operation, call `mcp__cowork__allow_cowork_file_delete` with a path inside the target folder. This unlocks deletion for the entire mounted folder for the session.
- Call it once per session per mounted folder — after that, `git pull`, `git commit`, `git push`, and file cleanup all work normally.

**Standard workflow on Mac:**
- At session start, call `mcp__cowork__allow_cowork_file_delete` for the github folder before attempting any git operations
- Edit files with Edit/Write tools in the VM, then commit and push with Bash git commands
- Repos are cloned at `~/github/<repo>/` with token auth embedded in the remote URL
- Token is stored at `~/OneDrive - DGLC/Claude/.github-token`
- Set up a new clone with: `git clone https://dglcinc:<token>@github.com/dglcinc/<repo>.git`
- Use `git config user.email "dglcinc@users.noreply.github.com"` and `user.name "David Lewis"` after cloning
- Feature branches + PRs for code changes; push directly to main for meta/context files

### Pi (Claude Code sessions)
Standard git works fine on the Pi. Repos live at `~/github/` on the Pi's local filesystem (not OneDrive-mounted), so `git pull`, `git push`, `git fetch`, and branch operations all work normally via Bash.

## MCP Servers

### Apple Mail
Binary: `/opt/homebrew/bin/apple-mail-mcp` (installed via `npm install -g apple-mail-mcp`, version 1.4.0)

Register for Claude Code CLI with:
```bash
claude mcp add apple-mail /opt/homebrew/bin/apple-mail-mcp
```
This writes to `~/.claude/settings.json`. The standalone `~/.claude/mcp.json` file is **not** read by Claude Code CLI — using that file alone silently fails. After registering and restarting, run `/mcp` to verify `apple-mail` shows as connected.

macOS permission required: Automation access to Mail.app (System Settings → Privacy & Security → Automation). If previously denied, reset with `tccutil reset Automation`.

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code.** Always create a feature branch and open a pull request for code and documentation changes. Only push directly to the default branch for meta/context files (CLAUDE.md).
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md (project and/or global) and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.
