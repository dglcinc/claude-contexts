#!/bin/bash
# Run once after cloning claude-contexts on a new machine.
# Creates symlinks for Obsidian vault config and Claude Code commands.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Obsidian vault config ---
VAULT=~/github
if [ -e "$VAULT/.obsidian" ]; then
  echo ".obsidian already exists at $VAULT — skipping"
else
  ln -s "$SCRIPT_DIR/.obsidian" "$VAULT/.obsidian"
  echo "Created: $VAULT/.obsidian → $SCRIPT_DIR/.obsidian"
fi

# --- Claude Code custom commands ---
# ~/.claude/commands must be a real directory (Claude Code does not follow a symlink here).
# Symlink each skill file individually instead.
mkdir -p ~/.claude/commands
for skill in "$SCRIPT_DIR/skills/"*.md; do
  name="$(basename "$skill")"
  target=~/.claude/commands/"$name"
  if [ -e "$target" ]; then
    echo "Command $name already exists — skipping"
  else
    ln -s "$skill" "$target"
    echo "Created: $target → $skill"
  fi
done

echo ""
echo "Setup complete."
echo "Open ~/github as a vault in Obsidian."
echo "Claude Code commands available: $(ls "$SCRIPT_DIR/skills/"*.md 2>/dev/null | xargs -I{} basename {} .md | tr '\n' ' ')"
