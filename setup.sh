#!/bin/bash
# Run once after cloning claude-contexts on a new machine.
# Creates the Obsidian vault config symlink at ~/github/.obsidian.

VAULT=~/github
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/.obsidian"

if [ -e "$VAULT/.obsidian" ]; then
  echo ".obsidian already exists at $VAULT — skipping (remove it first if you want to reset)"
  exit 0
fi

ln -s "$CONFIG" "$VAULT/.obsidian"
echo "Created: $VAULT/.obsidian → $CONFIG"
echo "Open ~/github as a vault in Obsidian."
