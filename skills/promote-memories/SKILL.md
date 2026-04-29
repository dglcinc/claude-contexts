---
name: promote-memories
description: Review current project memory files and graduate stable knowledge into permanent CLAUDE.md files. Removes promoted memories from the memory folder and updates MEMORY.md.
---

# Promote Memories

Review the current project's memory files and graduate stable knowledge into
the appropriate permanent CLAUDE.md files. Removes promoted memories from the
memory folder and updates MEMORY.md.

## Instructions

### Step 1 — Locate memory folder

If a project name was passed as an argument (e.g. `/promote-memories bowling-league-tracker`),
derive the memory folder from `$HOME` (path differs by machine — `/Users/david`, `/Users/utilityserver`, `/home/pi`):
```bash
ENCODED=$(echo "$HOME/github/<project>" | tr '/' '-')
MEMDIR=~/.claude/projects/${ENCODED}/memory/
```

Otherwise, derive from the current working directory: replace `/` with `-`
(keeping the leading `-`), giving `~/.claude/projects/<slug>/memory/`. For example
`/Users/utilityserver/github/bowling-league-tracker` →
`-Users-utilityserver-github-bowling-league-tracker`.

Read all `.md` files in the memory folder and the `MEMORY.md` index.

### Step 2 — Classify each memory

For each memory file, determine the appropriate destination using these rules:

| Destination | Criteria |
|-------------|----------|
| **Stay local** (no promotion) | Machine-specific info: local IP addresses, SSH config, Pi-only commands, paths that differ per machine |
| **OneDrive** (`~/OneDrive - DGLC/Claude/CLAUDE.md`) | Sensitive info: personal names, private hostnames, credentials, anything that should not be on GitHub |
| **Project CLAUDE.md** (`~/github/<project>/CLAUDE.md`) | Project-specific knowledge safe for GitHub: workflow quirks, architecture decisions, key file locations, deployment commands using public hostnames |
| **Global Memory — `~/.claude/memory/general.md`** | Cross-project conventions and preferences: date formats, naming patterns, workflow style — facts about how the user works, not rules Claude must follow |
| **Global Memory — `~/.claude/memory/user.md`** | User profile, setup, working style — who the user is, their devices, their preferences |
| **Global Memory — `~/.claude/memory/tools/{tool}.md`** | Tool-specific config, CLI patterns, workarounds — one file per tool (e.g. `tools/jq.md`, `tools/gh.md`) |
| **Global Memory — `~/.claude/memory/domain/{name}.md`** | Domain knowledge accumulating toward eventual plugin promotion (e.g. HVAC monitoring, bowling-league scoring rules) — staging area, see lifecycle below |
| **claude-contexts CLAUDE.md** (`~/github/claude-contexts/CLAUDE.md`) | Cross-project workflow rules specific to this toolchain: context loading, MCP setup, tool quirks |
| **global.md** (`~/github/claude-contexts/global.md`) | Truly global preferences expressed as **rules Claude must follow**: working style, PR conventions, content perimeter rules |

**Memory vs rules — which tier?** If the content is a *fact about the user or their setup*, it belongs in Global Memory (general.md / user.md / tools/ / domain/). If it's *a rule Claude must apply*, it belongs in global.md or a project CLAUDE.md. Same content can drive both — the rule goes in CLAUDE.md, the underlying fact in memory.

**Domain Knowledge Lifecycle:** content in `~/.claude/memory/domain/{name}.md` is staging. When a domain matures enough to package, the next promotion step is a plugin/skill — at that point the memory file becomes a one-line pointer to the plugin and the body lives in the plugin repo. This step is out of scope for routine `/promote-memories` runs; flag the candidate to the user instead of attempting the plugin promotion automatically.

**Sensitivity check** — mark a memory as sensitive (→ OneDrive) if it contains:
- Personal names (people's real names, not generic role references)
- Private IP addresses or hostnames
- Credentials, tokens, or API keys
- File paths revealing personal information

### Step 3 — Present the plan

Show a table of every memory file with its proposed destination and one-line reason.
Ask for a single confirmation before proceeding. If the user disagrees with any
classification, adjust before executing.

### Step 4 — Execute promotions

For each memory being promoted:

1. **Read the target file** before editing.
2. **Integrate the content** — do not paste the memory verbatim. Synthesize it into
   the existing CLAUDE.md structure: add a new section if none fits, or append to
   the most relevant existing section. Remove memory-system metadata (frontmatter,
   `**Why:**` / `**How to apply:**` headers) and rewrite as direct prose or a
   concise rule that fits the target file's style.
3. **Delete the memory file** from the memory folder.
4. **Update MEMORY.md** to remove the entry for the promoted file.

### Step 5 — Commit

- Changes to `global.md` or `claude-contexts/CLAUDE.md`: commit directly to main in the `claude-contexts` repo.
- Changes to a project CLAUDE.md: commit directly to main in that project's repo.
- Changes to OneDrive CLAUDE.md: no git commit (personal perimeter).
- Never commit anything to GitHub that was classified as sensitive.

After committing, confirm what was promoted where and what was left in place.
