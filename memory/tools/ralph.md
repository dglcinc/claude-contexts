---
name: ralph-loop
description: Ralph Wiggum loop — PLAN.md checklist driven by ralph.sh; each iteration spawns a fresh sclaude to complete one task
metadata:
  type: reference
---

**ralph.sh** lives at `~/github/claude-contexts/ralph.sh`.

A "ralph loop" is a project execution pattern:
1. Create a `PLAN.md` in the project directory with a `- [ ]` checklist of tasks
2. Include a **Loop Rules** section at the bottom telling each sclaude invocation: how to mark tasks done, commit/PR conventions, and what "DONE" means
3. Run `ralph.sh` from the project directory — it loops, spawning a fresh `sclaude -p` per task until Claude prints `DONE`
4. Optional `ralph-finish.sh` in the same dir runs once after the loop exits

**Why:** batch execution of multi-step tasks (doc writing, migrations, refactors) without manual intervention between steps.

**Key constraints:**
- Each task must be self-contained enough for one `sclaude` invocation
- Tasks should commit their own output (or the loop rules can batch-commit at end)
- PLAN.md itself should be excluded from version control (add to `.git/info/exclude`) when working in a third-party repo

**Reference:** used in bowling-league-tracker and other projects. [[ralph-loop]]
