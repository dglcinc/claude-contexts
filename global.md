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
