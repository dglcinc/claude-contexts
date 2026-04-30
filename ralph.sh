#!/bin/zsh -i
# Canonical Ralph Wiggum loop driver.
#
# Usage: copy or symlink this script into a project directory that has a
# PLAN.md. Run it. Each loop iteration spawns a fresh `sclaude` to do the
# next unchecked `- [ ]` task in PLAN.md. The loop exits when claude prints
# `DONE` (i.e. no unchecked tasks remain).
#
# Optional finish hook: if `./ralph-finish.sh` exists and is executable in
# the cwd, it runs once after the loop exits. Use this for project-specific
# tail steps like deploying to prod, sending notifications, etc.
#
# Shebang is `zsh -i` so ~/.zshrc is sourced — aliases like `sclaude` and
# any PATH/env setup are inherited.

set -u
cd "$(pwd)"

if [[ ! -f PLAN.md ]]; then
  echo "ralph: no PLAN.md in $(pwd)" >&2
  exit 1
fi

while :; do
  output=$(sclaude -p <<'EOF' | tee /dev/tty
Read PLAN.md. Find the first unchecked `- [ ]` task. Do it.

For anything that would bloat your context — codebase exploration,
multi-file research, log digging, doc reading — spawn a subagent
(Explore for read-only search, general-purpose for heavier work) and
work from its summary. Don't read large files or grep widely yourself
unless the target is already known.

Follow the loop rules at the bottom of PLAN.md. When the task is done
(PR opened, box checked, PLAN.md committed to main), stop. If no
unchecked tasks remain, say "DONE" and stop. Don't ask questions —
make the call yourself and note the decision in the PR description.
EOF
)
  if echo "$output" | grep -qw DONE; then
    echo "ralph: DONE detected — exiting loop."
    break
  fi
done

if [[ -x ./ralph-finish.sh ]]; then
  echo "ralph: running ./ralph-finish.sh"
  ./ralph-finish.sh
fi
