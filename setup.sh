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
if [ -e ~/.claude/commands ]; then
  echo "~/.claude/commands already exists — skipping (remove it first if you want to reset)"
else
  ln -s "$SCRIPT_DIR/skills" ~/.claude/commands
  echo "Created: ~/.claude/commands → $SCRIPT_DIR/skills"
fi

echo ""
echo "Setup complete."
echo "Open ~/github as a vault in Obsidian."
echo "Claude Code commands available: $(ls "$SCRIPT_DIR/skills/"*.md 2>/dev/null | xargs -I{} basename {} .md | tr '\n' ' ')"
