#!/bin/bash
# PreToolUse hook on Bash. Denies tool calls that pass dangerouslyDisableSandbox: true
# for commands already covered by sandbox.excludedCommands (git/ssh/docker/gh) — the
# bypass flag triggers an unnecessary permission prompt because the sandbox would
# already let those commands through.
#
# Edit the regex below to add/remove covered commands. Keep in sync with
# sandbox.excludedCommands in ~/.claude/settings.json.
exec jq 'if (.tool_input.dangerouslyDisableSandbox == true) and (.tool_input.command | test("^(git|ssh|docker|gh)([[:space:]]|$)")) then {hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: "git/ssh/docker/gh are in sandbox.excludedCommands — dangerouslyDisableSandbox is unnecessary and triggers a prompt. Retry without the flag."}} else empty end'
