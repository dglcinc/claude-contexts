---
name: prune-context
description: Review the current context load and produce specific, prioritized pruning recommendations — what to remove, trim, or consolidate, with estimated token savings for each.
---

# /prune-context

Audit the active context and produce a prioritized pruning action list. The goal is specific, actionable recommendations — not just "trim it" but exactly what to remove and how many tokens it saves.

## Steps

### 1. Identify the active project

Infer the project from what's loaded in this conversation (set-context output, CLAUDE.md references, or `pwd`). If no project is loaded, still proceed — some recommendations apply globally.

### 2. Measure all loaded sources

```bash
# Global CLAUDE.md
wc -c ~/.claude/CLAUDE.md 2>/dev/null

# Project CLAUDE.md
wc -c ~/github/<project>/CLAUDE.md 2>/dev/null

# Session state (per-project memory dir derived from $HOME — varies by machine)
ENC=$(echo "$HOME/github/<project>" | tr '/' '-')
wc -c ~/.claude/projects/${ENC}/memory/session_state_<project>.md 2>/dev/null

# OneDrive context files
ls ~/OneDrive\ -\ DGLC/Claude/<project>*.md 2>/dev/null | while read f; do wc -c "$f"; done

# claude-contexts project summaries
ls ~/github/claude-contexts/<project>/*.md 2>/dev/null 2>/dev/null | while read f; do wc -c "$f"; done

# MEMORY.md (auto-loaded by runtime, lives next to launch dir)
ENC_HOME=$(echo "$HOME/github" | tr '/' '-')
wc -c ~/.claude/projects/${ENC_HOME}/memory/MEMORY.md 2>/dev/null

# Transcript
PWD_ENCODED=$(pwd | tr '/' '-')
TRANSCRIPT=$(ls -t ~/.claude/projects/${PWD_ENCODED}/*.jsonl 2>/dev/null | head -1)
wc -c "$TRANSCRIPT" 2>/dev/null
```

### 3. Inspect large files for pruning opportunities

For each file above 3,000 chars, read its first 80 lines to assess what's in it. Look for:

- **OneDrive plan/roadmap files**: completed phases (marked Done, ✅, or described past tense). Completed phase prose can be removed — keep only the roadmap table row.
- **OneDrive context files**: content already present in CLAUDE.md (deployment commands, data model, routes). Anything already in CLAUDE.md should be removed from the OneDrive file to eliminate redundancy.
- **Project CLAUDE.md**: stale sections — resolved data quality items, one-time import notes, removed features. Verify "Still to build" is accurate.
- **Session state**: if all "Next steps" items are done or stale, recommend archiving or clearing the file.

### 4. Check auto-load opportunity

```bash
[[ "$(pwd)" == "$HOME/github/<project>"* ]] && echo "IN_PROJECT" || echo "NOT_IN_PROJECT"
```

If `NOT_IN_PROJECT` and the project CLAUDE.md is large (>8,000 chars): recommend starting Claude Code from `~/github/<project>/` so the runtime auto-loads CLAUDE.md without it appearing in the conversation transcript.

### 5. Check transcript size

If the transcript is over 80,000 bytes (~16,000 tokens): flag as high priority. Suggest `/save-context` then `/clear` before starting a new task.

### 6. Output recommendations

Number them most-impactful first. For each:
- **What**: file name + specific section or action
- **~Tokens saved**: estimate
- **How**: exactly what to do (delete section, move to CLAUDE.md, trim completed phases to table rows, run `/save-context` + `/clear`)

End with: `**Total estimated savings: ~N,NNN tokens**`

Do **not** implement any recommendations — report only, then wait for the user's instruction.
