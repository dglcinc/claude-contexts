---
name: reorganize-memories
description: Audit and clean up the memory system — global memory and the current project's memory dir. Removes duplicates, fixes stale indexes, promotes cross-project knowledge to global memory, sorts entries, and updates the memory.md index. Always confirms each modification or removal with the user before acting.
---

# Reorganize Memories

Audit and clean up memory files. Operates on:

- **Global memory** at `~/.claude/memory/` (`memory.md` index, `general.md`, `user.md`, `tools/`, `domain/`)
- **Current project memory** at `~/.claude/projects/<encoded-cwd>/memory/` (project `MEMORY.md` + any auto-memory files)

Does **not** touch other projects' memory dirs unless the user passes a project name as an argument.

## Steps

### 1. Locate and read all memory files

Read every file under:

- `~/.claude/memory/` (depth-first, including `tools/` and `domain/`)
- `~/.claude/projects/${ENCODED}/memory/` where `ENCODED=$(echo "$HOME/github/<project>" | tr '/' '-')` — derive `<project>` from the argument if given, otherwise from the current working directory.

Note frontmatter `name`, `description`, `type`, and any `Last updated` dates.

### 2. Audit

Build a list of issues. Look for:

| Issue | What to look for |
|---|---|
| **Duplicates** | Same fact stated in two files (e.g. user profile in both project memory and global) |
| **Stale entries** | `Last updated` more than 60 days ago AND content references commits/branches/PRs that have moved on |
| **Orphans** | Files in a memory dir not listed in its `MEMORY.md` index |
| **Phantom index entries** | `MEMORY.md` rows pointing at files that no longer exist |
| **Misplaced content** | Project-memory file containing cross-project content (candidate for promotion to global), or global file containing project-specific content (candidate for demotion) |
| **Sprawl** | Single file covering 3+ unrelated topics that should be split |
| **Date order** | Index rows or in-file sections not in date order |
| **Missing pointer** | Project `MEMORY.md` lacking the `## Global Memory` section (per the Global Memory Reference Rule in `global.md`) |

Do not include session_state files in the dedup or staleness checks — they are operational state owned by `/save-context`. Only flag a session_state file if it is missing from its `MEMORY.md` index (orphan check applies).

### 3. Plan changes

Group findings into a small set of discrete changes. Each change must be one of:

- **Promote** — move content from project memory to global memory (and update both indexes)
- **Demote** — move project-specific content out of global memory into the relevant project's memory dir
- **Merge** — combine two files covering the same topic
- **Split** — break a sprawling file into focused files
- **Reindex** — fix `MEMORY.md` to match what's actually on disk (add orphans, remove phantoms, sort)
- **Delete** — remove a file that's confirmed stale or fully duplicated elsewhere
- **Add `## Global Memory` pointer** — for project `MEMORY.md` files that lack it

### 4. Confirm with user — required before any modification

Use `AskUserQuestion` to present the plan. Show:

- Each proposed change with the file path
- Current content vs proposed content (or "delete" / "create")
- A clear option to **approve all**, **approve subset**, or **skip**

Batch related changes into a single question where possible to keep interaction tight. Do not modify or delete any existing file before getting explicit approval — this is the rule from `global.md` Memory Management.

### 5. Execute approved changes

For each approved change:

1. Read the target file (always read before edit)
2. Make the change
3. Update affected `MEMORY.md` index(es) — both project and global where relevant
4. If a global file changed, bump its `Last updated` row in `~/.claude/memory/memory.md`

If the change involves files inside the `claude-contexts` repo (the global memory dir is symlinked to the repo), the change writes through to the repo automatically. Note this for the user — they'll need to commit and push.

### 6. Summary

Report:

- What was changed (one bullet per change)
- What was left alone and why
- Any follow-ups (e.g. "domain/hvac.md is approaching plugin-promotion size — flag for `/promote-memories` next session")
- Whether a git commit + push is needed for global memory changes

End with: "Done. Run `git -C ~/github/claude-contexts status` to confirm what needs committing."

## When NOT to use this skill

- If you only want to add a new memory entry — just write the file. Reorganization is for cleanup, not creation.
- If a session_state file is out of date — that's `/save-context`'s job, not this skill's.
- If you want to move stable knowledge from memory to a CLAUDE.md (rule layer) — that's `/promote-memories`.
