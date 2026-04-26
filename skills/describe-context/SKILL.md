---
name: describe-context
description: Show a token-estimate breakdown of everything currently loaded in context — CLAUDE.md files, session state, OneDrive context, memory, conversation transcript, and system overhead. Usage: /describe-context
---

# /describe-context

Estimate the token cost of everything currently loaded in context. Useful for diagnosing context bloat before a long session.

## Steps

### 1. Identify the active project

Infer the project name from what's been loaded in this conversation — set-context output, project CLAUDE.md references, or current working directory. If no project is loaded, still proceed and skip project-specific rows.

### 2. Gather file sizes

Run these commands. Use the actual project name in place of `<project>`.

```bash
# Global CLAUDE.md (auto-loaded by runtime)
wc -c ~/.claude/CLAUDE.md 2>/dev/null

# Project CLAUDE.md
wc -c ~/github/<project>/CLAUDE.md 2>/dev/null

# Session state
wc -c ~/.claude/projects/-Users-david-github-<project>/memory/session_state_<project>.md 2>/dev/null

# OneDrive context
wc -c ~/OneDrive\ -\ DGLC/Claude/<project>.md 2>/dev/null

# claude-contexts project summary
wc -c ~/github/claude-contexts/<project>/<project>.md 2>/dev/null

# MEMORY.md index (auto-loaded by runtime)
wc -c ~/.claude/projects/-Users-david-github/memory/MEMORY.md 2>/dev/null

# Any individual memory files that were explicitly read this session
# (check conversation history — only count files that were actually read)
```

### 3. Estimate conversation size

Find and measure the current session's transcript:

```bash
PWD_ENCODED=$(pwd | tr '/' '-')
TRANSCRIPT=$(ls -t ~/.claude/projects/${PWD_ENCODED}/*.jsonl 2>/dev/null | head -1)
wc -c "$TRANSCRIPT" 2>/dev/null
```

JSONL includes JSON framing overhead — divide the byte count by 5 (not 4) for a more accurate token estimate of actual message content.

### 4. Apply the token formula

- Text files (CLAUDE.md, session state, etc.): chars ÷ 4 ≈ tokens
- JSONL transcript: bytes ÷ 5 ≈ tokens
- System prompt + tool schemas: fixed estimate of **~12,000 tokens** (runtime-injected, not readable as files)

### 5. Display the breakdown

Print this table, omitting rows where files were not found:

```
## Context token estimate

| Source                       | Type         | ~Tokens |
|------------------------------|--------------|---------|
| System prompt + tool schemas | Runtime      |  ~12,000 |
| Global CLAUDE.md             | Auto-loaded  |    ~NNN |
| Project CLAUDE.md            | set-context  |    ~NNN |
| Session state                | set-context  |    ~NNN |
| OneDrive context             | set-context  |    ~NNN |
| claude-contexts summary      | set-context  |    ~NNN |
| MEMORY.md index              | Auto-loaded  |    ~NNN |
| Memory files (read this session) | Explicit |    ~NNN |
| Conversation transcript      | This session |    ~NNN |
|------------------------------|--------------|---------|
| **Total**                    |              | **~NNN** |

*Text files: chars ÷ 4. JSONL transcript: bytes ÷ 5. System overhead is a fixed estimate.*
*Context window: 200,000 tokens. Currently using ~NN%.*
```

After the table, add one sentence calling out the largest contributor if it's disproportionately large (e.g. conversation transcript growing across a long session).
