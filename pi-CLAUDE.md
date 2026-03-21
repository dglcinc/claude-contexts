# Global Context — Raspberry Pi

This file lives at `~/CLAUDE.md` on the Pi. Claude Code reads it automatically
from the home directory whenever you work in any subdirectory (e.g. `~/github/pivac`).

**First-time setup:**
```bash
cd ~/github
git clone https://github.com/dglcinc/claude-contexts.git
cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
```

**To update after changes to this file:**
```bash
git -C ~/github/claude-contexts pull
cp ~/github/claude-contexts/pi-CLAUDE.md ~/CLAUDE.md
```

## This Machine

- Host: Raspberry Pi at `10.0.0.82` (local), `68lookout.dglc.com` (external)
- User: `pi`
- GitHub directory: `~/github/`
- Python venv for pivac: `~/pivac-venv/` — always activate before running pivac scripts

## Projects on This Pi

- `~/github/pivac` — HVAC/home monitoring daemon (main project)
- `~/github/claude-contexts` — Global Claude context files (keep pulled)

## Working Style

- **Execute without repeated check-ins.** Before a multi-step task, state the plan briefly and confirm once. Then carry out all steps without asking permission at each one.
- **Targeted edits, not rewrites.** When modifying an existing file, make surgical changes to the relevant lines. Do not rewrite or reorder content that isn't changing — it creates noise in diffs and risks dropping things accidentally.
- **PR workflow for code.** Always create a feature branch and open a pull request for code changes. Only push directly to the default branch for meta/context files (CLAUDE.md).
- **Keep context files current.** After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.
- **No unnecessary confirmation loops.** Don't ask "should I proceed?" or "does this look right?" mid-task. Finish the work, then summarize what was done.
- **Commit message quality.** Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.
- **Prose over bullets in explanations.** When explaining an approach or decision, write in sentences rather than fragmenting everything into bullet lists.

## GitHub Setup

- GitHub account: `dglcinc`
- Repos use HTTPS with token auth
- Always create feature branches and open pull requests for code changes
- Push directly to the default branch only for meta/context files (CLAUDE.md)

## Current Work

**Deploying pivac.Emporia module (PR #16 already merged into master)**

`~/github/pivac` is up to date on master. `pyemvue` is installed in `~/pivac-venv`.

**Blocked on:** PyEmVue API mismatch in `scripts/emporia-discover.py`. Authentication
succeeds but `populate_device_properties()` fails with:
```
AttributeError: 'list' object has no attribute 'device_gid'
```
This means the installed version of PyEmVue returns a different structure from
`get_devices()` than the script expects. Need to inspect the installed version's
API and fix `emporia-discover.py` and `pivac/Emporia.py` accordingly.

**Diagnosis starting point:**
```bash
source ~/pivac-venv/bin/activate
pip show pyemvue
python3 -c "
import pyemvue
vue = pyemvue.PyEmVue()
vue.login(username='david@dglc.com', password='NuAUf2VFwH!*')
devices = vue.get_devices()
print(type(devices))
print(type(devices[0]) if devices else 'empty')
print(devices[0] if devices else 'empty')
"
```

**After fixing the API mismatch, remaining steps:**
1. Run `emporia-discover.py` successfully to get device GIDs
2. Add `pivac.Emporia` block to `/etc/pivac/config.yml` with real GIDs and panel names
3. Test standalone: `python -c "import pivac.Emporia as m; import json; print(json.dumps(m.status(), indent=2))"`
4. Install service: `sudo cp scripts/systemd/pivac-emporia.service /etc/systemd/system/`
5. `sudo systemctl daemon-reload && sudo systemctl enable --now pivac-emporia`

**Note on password:** Password contains `!` — always use single quotes in bash: `--password 'NuAUf2VFwH!*'`
