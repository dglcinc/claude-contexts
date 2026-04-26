# Global Preferences

Working style and PR conventions that apply to every project and every machine.

## Working Style

Execute without repeated check-ins. State the plan once before a multi-step task, then carry out all steps without pausing for approval. Only stop if a genuinely destructive action wasn't covered in the original plan.

When a file path or directory is already known (from memory or a CLAUDE.md), go directly to it. Do not run `find`, glob, or other broad filesystem searches for things already recorded.

## PR Workflow

All code and documentation changes require a feature branch and pull request. Only CLAUDE.md context files may be pushed directly to the default branch.

Open the PR at session end, even if the user doesn't explicitly ask. If a PR merges mid-session and work continues, start a new branch from the updated main.

When the goal is to fix something on `main`, confirm the PR's base branch is `main` before running `gh pr create`. Only target a feature branch as the base when building stacked changes that shouldn't land until the parent merges.
