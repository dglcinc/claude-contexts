#!/usr/bin/env python3
"""PreToolUse hook: inject the global memory index on the first tool call of this process.

The project MEMORY.md is not injected here: the harness already places it in the system prompt."""
import json
import os
import sys
from pathlib import Path


def main():
    # Use parent process ID as session identifier
    # PPID = Claude Code process — stable within a session, new for each subagent
    ppid = os.getppid()
    flag_path = Path(f"/tmp/claude-memory-loaded-{ppid}")

    # Already loaded for this process — exit silently (no output = no context injection)
    if flag_path.exists():
        sys.exit(0)

    # Mark as loaded for this process
    flag_path.touch()

    global_idx = Path.home() / '.claude' / 'memory' / 'memory.md'
    if not global_idx.exists():
        sys.exit(0)

    parts = ["=== Global Memory Index ===\n" + global_idx.read_text()]

    context = '\n\n'.join(parts)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
