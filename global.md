# Global Preferences

Working style and PR conventions that apply to every project and every machine.

## Working Style

Execute without repeated check-ins. State the plan once before a multi-step task, then carry out all steps without pausing for approval. Only stop if a genuinely destructive action wasn't covered in the original plan.

Make targeted edits, not rewrites. When modifying an existing file, make surgical changes to the relevant lines. Rewriting or reordering unchanged content creates noise in diffs and risks dropping things accidentally.

After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.

When a file path or directory is already known (from memory or a CLAUDE.md), go directly to it. Do not run `find`, glob, or other broad filesystem searches for things already recorded.

Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.

When explaining an approach or decision, write in sentences rather than fragmenting into bullet lists.

## PR Workflow

All code and documentation changes require a feature branch and pull request. Only CLAUDE.md context files may be pushed directly to the default branch.

Open the PR at session end, even if the user doesn't explicitly ask. If a PR merges mid-session and work continues, start a new branch from the updated main.

When the goal is to fix something on `main`, confirm the PR's base branch is `main` before running `gh pr create`. Only target a feature branch as the base when building stacked changes that shouldn't land until the parent merges.

Add `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` to every commit in every repo. This applies to direct commits and PR commits alike.

## Skills

- **`/save-context`** (or type "save context"): Save session state, update CLAUDE.md files, commit. Run before `/clear`.
- **`/set-context <project>`**: Load full context for a project (OneDrive CLAUDE.md, project summaries, session state, project CLAUDE.md, git pull).
- **`/new-context <name>`**: Create a new project folder, CLAUDE.md template, and optional GitHub repo.
- **`/promote-memories`**: Graduate memory files to permanent CLAUDE.md destinations.

## Memory Management

Maintain a structured memory system rooted at .claude/memory/

### Structure

- memory.md — index of all memory files, updated whenever you create or modify one
- general.md — cross-project facts, preferences, environment setup
- domain/{topic}.md — domain-specific knowledge (one file per topic)
- tools/{tool}.md — tool configs, CLI patterns, workarounds

### Rules

1. When you learn something worth remembering, write it to the right file immediately
2. Keep memory.md as a current index with one-line descriptions
3. Entries: date, what, why — nothing more
4. Read memory.md at session start. Load other files only when relevant
5. If a file doesn't exist yet, create it
6. Before removing or modifying any existing memory entry, use AskUserQuestion to confirm
   with the user — show the current content and the proposed change

### Maintenance

To audit and clean up the memory system, run `/reorganize-memories`. The skill confirms each modification with `AskUserQuestion` before acting.

## Global Memory

Project MEMORY.md and this index are auto-injected before each tool call via PreToolUse hook
(~/.claude/hooks/pre-tool-memory.sh). Load specific topic files only when relevant.

Topic files:
- ~/.claude/memory/general.md — cross-project conventions and preferences
- ~/.claude/memory/tools/claude-hud.md — claude-hud statusLine setup quirks (GNU grep `\t` workaround)

## Global Memory Reference Rule

Whenever you work in a project and read (or create) its MEMORY.md, check that it contains a
## Global Memory section. If it does not, add it near the top, after the H1.

The section must be a SHORT POINTER only. Do NOT duplicate the topic file list into project
MEMORY.md. The list lives in CLAUDE.md (single source of truth). Project MEMORY.md has a
200-line budget — use it for project knowledge, not boilerplate.

Canonical template for project MEMORY.md:

```
## Global Memory

Read ~/.claude/CLAUDE.md for memory rules and topic files.
```

When a new file is added to ~/.claude/memory/:
- Add it to the ## Global Memory topic file list in ~/.claude/CLAUDE.md only
- Do NOT update individual project MEMORY.md files

## Repo Memory Auto-Init

At session start in any project, check for MEMORY.md in the project memory directory
(~/.claude/projects/{mapped-path}/memory/). If it does not exist, create it:

```
# {Project Name} - Project Memory

## Global Memory

Read ~/.claude/CLAUDE.md for memory rules and topic files.

## Project Notes

(Populated as you work in this project)
```

## Domain Knowledge Lifecycle

1. Staging — knowledge accumulates in ~/.claude/memory/domain/{name}/
2. Promotion — enough knowledge exists to package as a plugin/skill
3. Pointer — after promotion, the memory file becomes a pointer to the plugin;
   content lives in the plugin

When an update is needed to a promoted domain, note it in the memory file so an issue
can be created on the plugin repo.
