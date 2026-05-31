#!/usr/bin/env bash
# SessionEnd hook — remind if a session ended without running /save-context.
#
# Reads the SessionEnd JSON payload on stdin (transcript_path, cwd, reason).
# Strictly read-only: it never touches git or the model (the model is already
# gone by the time SessionEnd fires). When a meaningful session ends and no
# /save-context ran, it fires a macOS notification and appends a line to
# ~/.claude/unsaved-context.log. On non-macOS (Pi) the log line is the signal.
#
# Detection: a real /save-context leaves one of two STRUCTURAL markers in the
# transcript — `command-name>/save-context` (typed slash command) or
# `"name":"Skill","input":{"skill":"save-context"` (typed "save context"/"wrap").
# Neither appears from merely discussing save-context in prose, so no false
# positives. Registered into settings.json by setup.sh.

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  transcript=$(printf '%s' "$input" | jq -r '.transcript_path // empty')
  cwd=$(printf '%s' "$input" | jq -r '.cwd // empty')
else
  transcript=""; cwd=""
fi

# No usable transcript → nothing to check.
[[ -z "$transcript" || ! -f "$transcript" ]] && exit 0

# Already saved this session? Then stay silent.
if grep -qF -e 'command-name>/save-context' \
            -e '"name":"Skill","input":{"skill":"save-context"' "$transcript"; then
  exit 0
fi

# Only nag if there was real work. Count genuine human user turns: user-type
# lines minus tool_result payloads (which also carry "type":"user").
users=$(grep -c '"type":"user"' "$transcript" 2>/dev/null)
tools=$(grep -c '"tool_result"' "$transcript" 2>/dev/null)
: "${users:=0}"; : "${tools:=0}"
human=$(( users - tools ))
(( human < 3 )) && exit 0

project=$(basename "${cwd:-$PWD}")
msg="Ended without /save-context — ~${human} turns unsaved in ${project}."

printf '%s\t%s\t%s\n' "$(date '+%Y-%m-%dT%H:%M:%S')" "$project" "$transcript" \
  >> "$HOME/.claude/unsaved-context.log" 2>/dev/null

if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"${msg}\" with title \"Claude Code\" sound name \"Funk\"" 2>/dev/null
fi

exit 0
