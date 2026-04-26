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
use `~/.claude/projects/-Users-david-github-<project>/memory/`.

Otherwise, derive the path from the current working directory: replace `/` with `-`
and drop the leading `/` (e.g. `/Users/david/github/bowling-league-tracker` →
`-Users-david-github-bowling-league-tracker`), giving:
`~/.claude/projects/<slug>/memory/`

Read all `.md` files in the memory folder and the `MEMORY.md` index.

### Step 2 — Classify each memory

For each memory file, determine the appropriate destination using these rules:

| Destination | Criteria |
|-------------|----------|
| **Stay local** (no promotion) | Machine-specific info: local IP addresses, SSH config, Pi-only commands, paths that differ per machine |
| **OneDrive** (`~/OneDrive - DGLC/Claude/CLAUDE.md`) | Sensitive info: personal names, private hostnames, credentials, anything that should not be on GitHub |
| **Project CLAUDE.md** (`~/github/<project>/CLAUDE.md`) | Project-specific knowledge safe for GitHub: workflow quirks, architecture decisions, key file locations, deployment commands using public hostnames |
| **claude-contexts CLAUDE.md** (`~/github/claude-contexts/CLAUDE.md`) | Cross-project workflow rules specific to this toolchain: context loading, MCP setup, tool quirks |
| **global.md** (`~/github/claude-contexts/global.md`) | Truly global preferences: working style, PR conventions, content perimeter rules — anything that should apply on every machine and every project |

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
