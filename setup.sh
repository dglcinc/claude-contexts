#!/bin/bash
# Run after cloning claude-contexts on a new machine, or any time you want to
# verify/repair the managed symlinks. Idempotent and self-repairing for symlinks
# that point to the wrong place; refuses to delete regular files or directories
# (those may contain user data — manual cleanup required).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# link_or_repair <desired-target> <link-path>
#
# Cases:
#   - <link-path> doesn't exist        → create symlink
#   - <link-path> is a symlink → desired-target → no-op
#   - <link-path> is a symlink → other → remove and recreate
#   - <link-path> is a regular file/dir → warn, leave alone (user data risk)
link_or_repair() {
  local target="$1"
  local link_path="$2"

  if [ -L "$link_path" ]; then
    local current_target
    current_target=$(readlink "$link_path")
    if [ "$current_target" = "$target" ]; then
      echo "OK:        $link_path → $target"
    else
      echo "Repairing: $link_path was → $current_target"
      rm "$link_path"
      ln -s "$target" "$link_path"
      echo "           now → $target"
    fi
    return
  fi

  if [ -e "$link_path" ]; then
    echo "WARNING:   $link_path exists as a regular file/directory, not a symlink."
    echo "           Expected: symlink → $target"
    echo "           To repair: back up $link_path if it has content you need,"
    echo "                      then 'rm -rf $link_path' and re-run this script."
    return
  fi

  ln -s "$target" "$link_path"
  echo "Created:   $link_path → $target"
}

# --- Obsidian vault config ---
link_or_repair "$SCRIPT_DIR/.obsidian" "$HOME/github/.obsidian"

# --- Claude Code skills ---
# New skills added to the repo appear after /reload-plugins — no re-run needed.
link_or_repair "$SCRIPT_DIR/skills" "$HOME/.claude/skills"

# --- Global CLAUDE.md ---
# Edits to global.md take effect immediately via this symlink.
link_or_repair "$SCRIPT_DIR/global.md" "$HOME/.claude/CLAUDE.md"

# --- Pi: ~/CLAUDE.md symlink ---
# On the Pi, ~/CLAUDE.md is read via directory hierarchy and provides Pi-specific context.
# On Mac this file doesn't exist, so the symlink only makes sense on Pi.
if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "armv7l" ]; then
  link_or_repair "$SCRIPT_DIR/pi-CLAUDE.md" "$HOME/CLAUDE.md"
fi

# --- Global memory directory ---
# Cross-project memory (memory.md index, general.md conventions, tools/, domain/).
# Symlinked so edits sync across machines via git.
link_or_repair "$SCRIPT_DIR/memory" "$HOME/.claude/memory"

# --- PreToolUse memory hook ---
# Auto-injects project MEMORY.md and the global index on the first tool call per session.
link_or_repair "$SCRIPT_DIR/hooks" "$HOME/.claude/hooks"

# --- settings.json hook registration ---
# settings.json is per-machine (statusLine, plugin list differ), so we can't symlink it.
# Instead, idempotently merge the PreToolUse hook block. Requires jq.
SETTINGS="$HOME/.claude/settings.json"
HOOK_CMD="bash ~/.claude/hooks/pre-tool-memory.sh"
if ! command -v jq >/dev/null 2>&1; then
  echo "WARNING:   jq not found — cannot merge hook into settings.json."
  echo "           Install jq (brew install jq / apt install jq) and re-run."
elif [ ! -f "$SETTINGS" ]; then
  echo "WARNING:   $SETTINGS does not exist — start Claude Code once to create it,"
  echo "           then re-run this script."
elif jq -e --arg cmd "$HOOK_CMD" '[.hooks.PreToolUse[]?.hooks[]?.command] | any(. == $cmd)' "$SETTINGS" >/dev/null 2>&1; then
  echo "OK:        settings.json PreToolUse memory hook already configured"
else
  tmp=$(mktemp)
  jq --arg cmd "$HOOK_CMD" '
    .hooks //= {}
    | .hooks.PreToolUse //= []
    | .hooks.PreToolUse += [{matcher:"*",hooks:[{type:"command",command:$cmd,timeout:5}]}]
  ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
  echo "Added:     PreToolUse memory hook to settings.json"
fi

echo ""
echo "Setup complete."
echo "Open ~/github as a vault in Obsidian."
echo "Skills installed: $(ls -d "$SCRIPT_DIR/skills/"*/ 2>/dev/null | xargs -I{} basename {} | tr '\n' ' ')"
