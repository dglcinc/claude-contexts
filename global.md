# Global Preferences

Working style and PR conventions that apply to every project and every machine.

## Working Style

Execute without repeated check-ins. State the plan once before a multi-step task, then carry out all steps without pausing for approval. Only stop if a genuinely destructive action wasn't covered in the original plan.

Make targeted edits, not rewrites. When modifying an existing file, make surgical changes to the relevant lines. Rewriting or reordering unchanged content creates noise in diffs and risks dropping things accidentally.

After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.

When a file path or directory is already known (from memory or a CLAUDE.md), go directly to it. Do not run `find`, glob, or other broad filesystem searches for things already recorded.

Always look in MemPalace if you don't know the answer before guessing or asking me. See the **MemPalace Consultation** section below for which questions qualify and which tools to use.

Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.

When explaining an approach or decision, write in sentences rather than fragmenting into bullet lists.

### Asking, planning, and diagnosing

Two behavioral-analysis passes over how David directs work (claude-contexts mempalace-analysis, baseline + iteration-2, 2026-05-30) found the costliest friction is interaction mismatch, not bugs — but *which* mismatch depends on the operating mode. In **delegated/ralph builds** the plan gate dominates (≈75% of interrupts hit `ExitPlanMode`). In **attended work** the plan/ask gate rarely bites (1 of 9 interrupts); the recurring failure there is acting on the harder path before exhausting what was already knowable. These levers target both.

- **Before the harder path — or before asking — exhaust the local, known, and prior-session sources.** This is the most common attended-work interrupt (≈5 of 9): escalating to a remote/harder path, or starting fresh, when the answer was already readable in the repo, claude-contexts, a prior session, or the MemPalace palace — or verifiable by checking world-state (dependency currency, existing access, current versions). Over-asking is the *narrow* case of this: only ask when the answer is genuinely David's preference, and especially not when he has already given a direction.
- In a plan, fold in the obvious adjacent scope rather than offering a narrow one, and state the boundaries you are *assuming* (what the change does NOT touch), not just the steps. A narrow plan invites a redirect; an unstated boundary invites an interrupt to extract it. Never silently re-present a killed plan — change it or ask what should change. This lever pays off most in delegated/ralph builds, where the plan gate is nearly the only synchronous touchpoint.
- Treat a flat "no…" as a hard stop, not a detail to patch: re-derive the symptom from scratch, and when you assert a fix worked, state its expected observable for David to confirm rather than narrating a causal theory as established fact. (Strongly recurring — most redirects open with a flat "no…".)
- Read a precise→vague shift ("seems off", "still not right") as a change-tack signal **only when you are iterating your own fix across retries**: by the 2nd–3rd failed fix of one theory, propose abandoning it. This does *not* apply when David is vague about his own files or setup ("not sure where it'd be") or making a transient perceptual judgment on visual output ("looks a little off") — that's his information state, not a wrong-fix signal. In delegated/ralph builds corrections arrive as the next session's opening directive, so weight a prior session's closing diagnostic accordingly.
- When David is hand-driving an external system (npm, the App Store, a 2FA UI) and reporting its behavior, the failure is in that system, not your work — advise and wait; don't treat his precise status reports as bugs to chase.

## PR Workflow

All code and documentation changes require a feature branch and pull request. Only CLAUDE.md context files may be pushed directly to the default branch.

Open the PR at session end, even if the user doesn't explicitly ask. If a PR merges mid-session and work continues, start a new branch from the updated main.

When the goal is to fix something on `main`, confirm the PR's base branch is `main` before running `gh pr create`. Only target a feature branch as the base when building stacked changes that shouldn't land until the parent merges.

Add `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` to every commit in every repo. This applies to direct commits and PR commits alike.

## Skills

- **`/save-context`** (or type "save context"): Save session state, update CLAUDE.md files, commit. Run before `/clear`.
- **`/set-context <project>`**: Load full context for a project (OneDrive CLAUDE.md, project summaries, session state, project CLAUDE.md, git pull).
- **`/new-context <name>`**: Create a new project folder, CLAUDE.md template, and optional GitHub repo.
- **`/promote-memories`**: Graduate memory files to permanent CLAUDE.md destinations.

## Memory Management

Maintain a structured memory system rooted at .claude/memory/

### Structure

- memory.md — index of all memory files, updated whenever you create or modify one
- general.md — cross-project facts, preferences, environment setup
- domain/{topic}.md — domain-specific knowledge (one file per topic)
- tools/{tool}.md — tool configs, CLI patterns, workarounds

### Rules

1. When you learn something worth remembering, write it to the right file immediately
2. Keep memory.md as a current index with one-line descriptions
3. Entries: date, what, why — nothing more
4. Read memory.md at session start. Load other files only when relevant
5. If a file doesn't exist yet, create it
6. Before removing or modifying any existing memory entry, use AskUserQuestion to confirm
   with the user — show the current content and the proposed change

### Maintenance

To audit and clean up the memory system, run `/reorganize-memories`. The skill confirms each modification with `AskUserQuestion` before acting.

## Global Memory

Project MEMORY.md and this index are auto-injected before each tool call via PreToolUse hook
(~/.claude/hooks/pre-tool-memory.sh). Load specific topic files only when relevant.

Topic files:
- ~/.claude/memory/general.md — cross-project conventions and preferences
- ~/.claude/memory/tools/claude-hud.md — claude-hud statusLine setup quirks (GNU grep `\t` workaround)
- ~/.claude/memory/tools/ralph.md — Ralph loop pattern (PLAN.md + ralph.sh driver for batch task execution)
- ~/.claude/memory/tools/mempalace.md — MemPalace auto-mines via plugin Stop/PreCompact hooks (not settings.json); palace = mined own content
- ~/.claude/memory/tools/gh-stacked-prs.md — squash-merging a parent PR with --delete-branch auto-closes child PRs (reopen blocked); cherry-pick to recover
- ~/.claude/memory/tools/nfs.md — D-state stuck procs survive SIGKILL; lazy-unmount + reboot to recover; fstab pattern for non-blocking boot
- ~/.claude/memory/tools/rsync.md — rsync starves over NFSv4 on large sparse files (use cat|ssh|dd or cp); rsync 3.4 → older server needs `--old-args`
- ~/.claude/memory/tools/synology.md — DSM rsync-over-SSH gate (code 43); nasadmin + `--rsync-path='sudo rsync'` workaround; NFS+ACL recipe
- ~/.claude/memory/tools/m365-graph.md — modern M365 tenants disable SMTP AUTH; use MSAL + Graph `sendMail` with client-credentials
- ~/.claude/memory/tools/signalk.md — SignalK-server plugin admin: install topology, force-disable un-toggleable built-ins, mint an admin JWT, read in-app-browser 404s from the access log
- ~/.claude/memory/tools/unifi.md — UCG access: controller now ON the UCG Ultra at `https://10.0.0.1` (not the Mac mini); API key `~/.config/unifi/claude-agent.key` via `X-API-KEY`; integration + classic API paths; client fixed-IP recipe

## Global Memory Reference Rule

Whenever you work in a project and read (or create) its MEMORY.md, check that it contains a
## Global Memory section. If it does not, add it near the top, after the H1.

The section must be a SHORT POINTER only. Do NOT duplicate the topic file list into project
MEMORY.md. The list lives in CLAUDE.md (single source of truth). Project MEMORY.md has a
200-line budget — use it for project knowledge, not boilerplate.

Canonical template for project MEMORY.md:

```
## Global Memory

Read ~/.claude/CLAUDE.md for memory rules and topic files.
```

When a new file is added to ~/.claude/memory/:
- Add it to the ## Global Memory topic file list in ~/.claude/CLAUDE.md only
- Do NOT update individual project MEMORY.md files

## Repo Memory Auto-Init

At session start in any project, check for MEMORY.md in the project memory directory
(~/.claude/projects/{mapped-path}/memory/). If it does not exist, create it:

```
# {Project Name} - Project Memory

## Global Memory

Read ~/.claude/CLAUDE.md for memory rules and topic files.

## Project Notes

(Populated as you work in this project)
```

## Domain Knowledge Lifecycle

1. Staging — knowledge accumulates in ~/.claude/memory/domain/{name}/
2. Promotion — enough knowledge exists to package as a plugin/skill
3. Pointer — after promotion, the memory file becomes a pointer to the plugin;
   content lives in the plugin

When an update is needed to a promoted domain, note it in the memory file so an issue
can be created on the plugin repo.

## MemPalace Consultation

The MemPalace palace is a separate memory system from the file-based `.claude/memory/`
above. Only the file-based MEMORY.md + index is auto-injected each session; the palace
(semantic-search drawers and the knowledge-graph triples) is **not** loaded automatically
and must be queried on demand.

Before answering a question whose answer plausibly lives in stored memory rather than in
the current conversation, query the palace first instead of guessing. This applies to:
past-session decisions and history, infrastructure and deployment facts (hosts, IPs,
topology, commands), and details about specific people or projects. Use `mempalace_search`
for prose/semantic recall and `mempalace_kg_query` for specific entity facts.

Scope guard: only reach for the palace when the answer is genuinely stored knowledge and
is not already available in the current context, the auto-injected file memory, the
codebase in front of you, or general knowledge. Do not search reflexively for things you
can already answer.

Best-effort: the palace lives on the Mac Mini behind the SSH MCP wrapper. If it is
unreachable (e.g. off-LAN with the remote tunnel dormant), say so and answer from what is
available rather than blocking.
