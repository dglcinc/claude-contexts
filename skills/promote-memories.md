# Promote Memories

Review the current project's memory files and graduate stable knowledge into
the appropriate permanent CLAUDE.md files. Removes promoted memories from the
memory folder and updates MEMORY.md.

## How to run

Invoked as `/promote-memories` in any Claude Code session. No arguments needed.

## Instructions

### Step 1 — Locate memory folder

Determine the current working directory and derive the memory path:
```
~/.claude/projects/<slug>/memory/
```
where `<slug>` is the working directory path with `/` replaced by `-` and
leading `/` dropped (e.g. `/Users/david/github/bowling-league-tracker` →
`-Users-david-github-bowling-league-tracker`).

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

Example format:
```
Memory                        → Destination          Reason
feedback_pr_workflow.md       → global.md            cross-project working style
feedback_no_personal_data.md  → bowling CLAUDE.md    project-specific rule
reference_m4_ssh.md           → OneDrive             contains IP address
feedback_git_sandbox.md       → bowling CLAUDE.md    project-specific workflow
reference_historical_import.md → OneDrive            contains player names
session_state_bowling.md      → bowling CLAUDE.md    project state, no sensitive data
reference_m4_ssh.md           → stay local           machine-specific SSH alias
```

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

- Changes to `global.md` or `claude-contexts/CLAUDE.md`: commit directly to main
  in the `claude-contexts` repo.
- Changes to a project CLAUDE.md: commit directly to main in that project's repo.
- Changes to OneDrive CLAUDE.md: no git commit (personal perimeter).
- Never commit anything to GitHub that was classified as sensitive.

After committing, confirm what was promoted where and what was left in place.
