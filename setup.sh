#!/bin/bash
# Run once after cloning claude-contexts on a new machine.
# Creates symlinks for Obsidian vault config and Claude Code skills.

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

# --- Claude Code skills ---
# ~/.claude/skills can be a symlink to the repo skills/ directory.
# New skills added to the repo appear after /reload-plugins — no re-run needed.
if [ -e ~/.claude/skills ]; then
  echo "~/.claude/skills already exists — skipping (remove it first to reset)"
else
  ln -s "$SCRIPT_DIR/skills" ~/.claude/skills
  echo "Created: ~/.claude/skills → $SCRIPT_DIR/skills"
fi

# --- Global CLAUDE.md ---
# ~/.claude/CLAUDE.md is a symlink to global.md so edits to global.md take effect immediately.
if [ -e ~/.claude/CLAUDE.md ]; then
  echo "~/.claude/CLAUDE.md already exists — skipping (remove it first to reset)"
else
  ln -s "$SCRIPT_DIR/global.md" ~/.claude/CLAUDE.md
  echo "Created: ~/.claude/CLAUDE.md → $SCRIPT_DIR/global.md"
fi

# --- Pi: ~/CLAUDE.md symlink ---
# On the Pi, ~/CLAUDE.md is read via directory hierarchy and provides Pi-specific context.
# On Mac this file doesn't exist, so the symlink only makes sense on Pi.
if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "armv7l" ]; then
  if [ -e ~/CLAUDE.md ]; then
    echo "~/CLAUDE.md already exists — skipping (remove it first to reset)"
  else
    ln -s "$SCRIPT_DIR/pi-CLAUDE.md" ~/CLAUDE.md
    echo "Created: ~/CLAUDE.md → $SCRIPT_DIR/pi-CLAUDE.md"
  fi
fi

echo ""
echo "Setup complete."
echo "Open ~/github as a vault in Obsidian."
echo "Skills installed: $(ls -d "$SCRIPT_DIR/skills/"*/ 2>/dev/null | xargs -I{} basename {} | tr '\n' ' ')"
