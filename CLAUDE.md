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
- Repos are cloned at `~/github/<repo>/` over SSH — no token embedded in remote URLs
- Set up a new clone with: `git clone git@github.com:dglcinc/<repo>.git`
- `gh` (PRs, repo create) authenticates from its own config (`~/.config/gh/hosts.yml`); there is no plaintext token file
- Use `git config user.email "dglcinc@users.noreply.github.com"` and `user.name "David Lewis"` after cloning
- Feature branches + PRs for code changes; push directly to main for meta/context files

### Pi (Claude Code sessions)
Standard git works fine on the Pi. Repos live at `~/github/` on the Pi's local filesystem (not OneDrive-mounted), so `git pull`, `git push`, `git fetch`, and branch operations all work normally via Bash.

## Memory System

Structured memory lives in this repo and is symlinked into `~/.claude/` by `setup.sh`:

- `memory/` → symlinked to `~/.claude/memory/` — global cross-project memory (memory.md index, general.md conventions, user.md profile, tools/, domain/)
- `hooks/pre-tool-memory.{sh,py}` → symlinked to `~/.claude/hooks/` — PreToolUse hook that auto-injects project MEMORY.md + global index on the first tool call per session (PPID-flagged so it fires once per Claude Code process)

`setup.sh` also idempotently merges the hook registration into `~/.claude/settings.json` via `jq` (settings.json itself is per-machine — statusLine paths, plugin list, etc — so it can't be symlinked). Requires `jq` installed (`brew install jq` / `apt install jq`).

The actual memory rules (lifecycle, when to write, when to ask before modifying) live in `global.md` under the Memory Management, Global Memory, Repo Memory Auto-Init, and Domain Knowledge Lifecycle sections.

## MCP Servers

### Apple Mail
Binary: `/opt/homebrew/bin/apple-mail-mcp` (installed via `npm install -g apple-mail-mcp`, version 1.4.0)

Register for Claude Code CLI with:
```bash
claude mcp add apple-mail /opt/homebrew/bin/apple-mail-mcp
```
This writes to `~/.claude/settings.json`. The standalone `~/.claude/mcp.json` file is **not** read by Claude Code CLI — using that file alone silently fails. After registering and restarting, run `/mcp` to verify `apple-mail` shows as connected.

macOS permission required: Automation access to Mail.app (System Settings → Privacy & Security → Automation). If previously denied, reset with `tccutil reset Automation`.

### MemPalace (AI memory — centralized, deployed 2026-05-25)
Local AI-memory system (official `MemPalace/mempalace`). **One shared palace on the Mac Mini** (`utilityserver@10.0.0.84`) at `~/.mempalace` (ChromaDB; **never** sync this dir to OneDrive/iCloud — the live HNSW index corrupts). The MacBook and Pi are thin clients — no local palace; their Claude Code runs the host's MCP server over SSH. MCP is **stdio-only** (no HTTP transport), so remote access is SSH, never an nginx HTTP proxy.

- **Host:** `uv tool install mempalace` (→ `~/.local/bin/{mempalace,mempalace-mcp}`) + `claude plugin install mempalace@mempalace` (marketplace `MemPalace/mempalace`) — gives `plugin:mempalace:mempalace` MCP, auto-save Stop/PreCompact hooks, and the proactive skill.
- **Clients:** MCP via SSH wrapper — `claude mcp add -s user mempalace -- ssh utilityserver /Users/utilityserver/.local/bin/mempalace-mcp` (MacBook uses `bash ~/.ssh/mp-ssh …` to auto-pick LAN vs remote). Auto-capture hook `~/.mempalace-client/mempal-client-save-hook.sh` ships the transcript over SSH and runs `mempalace mine --mode convos` on the host every 15 human msgs. Hooks activate on next session start.
- **Remote (away) access:** mTLS SSH tunnel via the Pi's nginx `stream` on 8443 → `10.0.0.84:22` (server/client certs + CA in `pi:/etc/nginx/mempalace-tls` and `pi:~/mempalace-tls`; `ufw allow 8443`). Dormant until a router port-forward WAN tcp/8443 → `10.0.0.82:8443` is added; the MacBook uses the LAN path until then.
- **Backups:** Mac Mini LaunchAgent `com.dglc.mempalace-backup` (daily 03:30) cold-tars `~/.mempalace` and uploads via **cat-over-ssh** to NAS `root@10.0.0.3:/volume1/NetBackup/mempalace/` (14 kept; 3 local in `~/.mempalace-backups`). rsync/scp fail on this Synology's SSH (SFTP disabled, rsync `--server` returns 0 bytes) — cat-over-ssh is the proven method.

- **Direct CLI search:** an `mp` shell helper is installed on each machine (`~/.zshrc` on Macs, `~/.bashrc` on Pi, marker-guarded) — `mp "query"` searches, `mp status`/`mp wake-up` pass through; the MacBook/Pi route to the host over SSH (args shell-quoted so multi-word queries survive).

- **Knowledge-graph layer:** the palace has two layers — semantic-search **drawers** (auto-populated by the mining hooks) and **KG triples** (precise, temporal entity facts). **Mining does not populate the KG** — it stays empty until facts are added explicitly. KG ops are **MCP-tool-only** (no `mempalace kg` CLI): `mempalace_kg_add/query/invalidate/stats`; `invalidate` has no hard-delete (sets `valid_to`). Per `global.md`'s **MemPalace Consultation** rule, query the palace before answering about past sessions, infra/deployment facts, or people/projects (best-effort; skip if MCP unreachable).

- **Memory boundaries — keep the three systems non-overlapping (set 2026-05-25):** each system owns one job, so they don't mirror each other.
  - **Markdown memory** (`~/.claude/memory/` + project `MEMORY.md` + CLAUDE.md) = curated, version-controlled source of truth, loaded into context every session.
  - **MemPalace** = episodic recall — auto-mined conversation transcripts (`sessions` wing) + diary checkpoints — plus the **KG**, which is canonical for precise/temporal entity-fact queries.
  - **Beads** = work/task tracking (installed, not yet adopted).
  - **Do NOT `mempalace mine <repo> --mode projects` on claude-contexts** (or other curated-context repos). Project-mode mining clones version-controlled files into drawers that drift from the git source the moment you edit them. Only convo mining auto-runs (the Stop/PreCompact + client hooks); project-mode mining is a one-off manual action with no recurring job, so the rule is simply: don't run it on curated repos.
  - The original project-file mirror (`claude_contexts` wing, 321 drawers + 57 closets) was deleted 2026-05-25 — zero info loss, re-mineable from git if ever needed. `wing_contexts`/`wing_docs` were kept: despite the names they're episodic diary checkpoints, not file mirrors.

Per-machine specifics and verified facts live in this repo's Mac Mini project memory (`project_mempalace.md`); this section is the cross-machine reference.
