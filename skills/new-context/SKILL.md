---
name: new-context
description: Create a new project folder under ~/github/ with a CLAUDE.md template and claude-contexts subfolder. Optionally initializes git and creates a GitHub repo. Usage: /new-context <project-name>
---

# /new-context

Create a new project context. Usage: `/new-context <project-name>`

## Input

The argument is the new project's folder name under `~/github/` (e.g. `my-new-app`). If no argument was given, ask for it before proceeding.

## Steps

### 0. Guard against re-creating an existing project

If `dglcinc/<name>` already exists on GitHub, the user almost certainly meant `/set-context <name>` (which clones it). Abort `/new-context` rather than scaffolding over an existing remote.

```bash
GITHUB_TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token) \
  gh repo view dglcinc/<name> --json name 2>/dev/null && echo "EXISTS" || echo "NEW"
```

If `EXISTS`: stop and tell the user "`dglcinc/<name>` already exists on GitHub — use `/set-context <name>` to clone it locally. Aborting `/new-context`."

If `~/github/<name>/` already exists locally (regardless of remote), also stop and surface that.

### 1. Create the project folder
```bash
mkdir -p ~/github/<name>
```

### 2. Create a CLAUDE.md template
Write `~/github/<name>/CLAUDE.md` with this structure:

```markdown
# <Name> — Project Context

## Overview

<Brief description of what this project does.>

## Stack

<Languages, frameworks, key dependencies.>

## Current State

<What exists, what works, what's in progress.>

## Git Workflow

CLAUDE.md pushes directly to main. All other code and documentation changes use feature branches + PRs. See global CLAUDE.md for full conventions.
```

### 3. Create the claude-contexts subfolder
```bash
mkdir -p ~/github/claude-contexts/<name>
```

Write `~/github/claude-contexts/<name>/<name>.md` with a minimal summary:

```markdown
# <Name> — Context Summary

## Overview

<One paragraph describing the project.>

## Current State

<Current branch, open PRs, what's in progress.>

## Next Steps

1. ...
```

### 4. Create OneDrive cross-machine context file
Write `~/OneDrive - DGLC/Claude/<name>.md` with a minimal template:

```markdown
# <Name> — Cross-Machine Context

<Brief description of infrastructure context that needs to be shared across machines: server addresses, deployment commands, service names, credentials locations, etc. Leave blank if not yet known.>
```

Also add an entry for it in `~/OneDrive - DGLC/Claude/CLAUDE.md` under the `## Projects` section.

### 5. Initialize git
Ask: "Initialize a git repository? (y/n)"

If yes:
```bash
cd ~/github/<name>
git init
git add CLAUDE.md
git commit -m "Initial project setup with CLAUDE.md"
```

### 6. Create GitHub repo
If git was initialized, ask: "Create a GitHub repository under dglcinc? (y/n — and public or private?)"

If yes:
```bash
GITHUB_TOKEN=$(cat ~/OneDrive\ -\ DGLC/Claude/.github-token) \
  gh repo create dglcinc/<name> --<visibility> --source=. --remote=origin --push
```

Where `--<visibility>` is `--private` or `--public` based on the user's answer.

### 7. Confirm
Report what was created. Tell the user:
- To open a new Claude Code session in the project: `cd ~/github/<name> && claude`
- Or to load context in an existing session: `/set-context <name>`
