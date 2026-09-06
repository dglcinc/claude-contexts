# Global Preferences

Working style and PR conventions that apply to every project and every machine.

## Working Style

Execute without repeated check-ins. State the plan once before a multi-step task, then carry out all steps without pausing for approval. Only stop if a destructive action wasn't covered in the original plan.

Make targeted edits, not rewrites. When modifying an existing file, make surgical changes to the relevant lines. Rewriting or reordering unchanged content creates noise in diffs and risks dropping things accidentally.

Documents state the current position, not their own edit history. In any document you author or revise — plans, specs, manuals, build docs, runbooks — write only what is true now. Do not narrate how the document changed: no "was X, now Y", no "an earlier revision said", no "superseded by", no strikethrough of answered questions, no "resolved" markers whose only purpose is to show something used to be open. When a fact changes, rewrite the passage as if it had always read that way, and delete questions once they are answered. David reads these for the current plan; change commentary is noise that buries it. Put the before/after in the commit message and the PR body, which is what they are for. He will ask explicitly when he wants a comparison or a discussion of what changed.

After significant changes — new architecture, bug fixes, new devices, deployment changes — update the relevant CLAUDE.md and include it in the commit.

When a file path or directory is already known (from memory or a CLAUDE.md), go directly to it. Do not run `find`, glob, or other broad filesystem searches for things already recorded.

Always look in MemPalace if you don't know the answer before guessing or asking me. See the **MemPalace Consultation** section below for which questions qualify and which tools to use.

Write commit messages that explain why, not just what. Reference the problem being solved, not just the files changed.

When explaining an approach or decision, write in sentences rather than fragmenting into bullet lists.

### Prose style

Copyedit yourself against Strunk & White's *The Elements of Style* before sending. Plain, concrete, short. Compress the wording and keep every idea. Cut commentary. Keep evidence: numbers, file paths, commands, caveats, and the reasoning behind a recommendation. Use full grammatical sentences; never drop articles or write telegraphese.

- **Omit needless words.** Vigorous writing is concise. Cut redundant phrases, empty padding, and qualifiers: *rather, very, little, quite, somewhat, fairly, generally, typically, often*.
- **Active, positive, concrete.** Name the actor and give it the verb ("he caught the ball", never "the ball was caught by him"). Make the definite assertion ("he was often late", never "he was not often on time"). Prefer plain nouns and verbs to abstraction ("the value can be null", never "there may be cases where the value is not present"), and everyday English to avoidable jargon.
- **Cap sentences at about 30 words, and vary their length.** Break anything longer. A paragraph of uniformly long sentences reads as generated text.
- **Use parallel structure for parallel ideas**, and keep terminology consistent. Do not rename a thing or redefine an abbreviation partway through a document.
- **Do not open consecutive sentences with the same word or construction.**
- **One topic per paragraph, topic sentence first.** Open with the claim, then support it. Never bury the finding in the middle or save it for the end.
- **Prefer continuous prose.** Use bullets and tables for enumerable data: settings, measurements, terminal pinouts, comparisons across a fixed set. An explanation, an argument, or a recommendation is prose. Formatting an argument as bullets hides the reasoning that connects the points.
- **State the finding; don't announce it.** No "Two things worth flagging", "Here's the catch", "The key insight is", "What's interesting here", "which is exactly what X is for". Say the thing, and never restate the question before answering it.
- **No clichés or over-formal transitions.** *It's worth noting, that said, at the end of the day, the fact of the matter, needless to say, in order to, moving forward, additionally, furthermore.*
- **Don't overstate, and never append a ranking tail.** Avoid: *the entire ballgame, the single most important, crucial, critical, huge, precisely, exactly, actually, really, worth noting, worth flagging, it's worth knowing.* Also cut superlative tails that add no information: *"three facts shape the design **more than anything else**", above all, most of all, by far.* The sentence works without them. If something matters most, say so once, plainly.
- **Delete "genuinely".** Recurring tic — flagged repeatedly and still slipping through, including into the text of these rules. It adds nothing to any sentence it appears in. Same for *truly, actually, in fact, indeed.* Search your draft for them before sending.
- **Never contrast to make a point.** Drop every form of "X, not Y": *not X but Y; X, not Y; it means A, not B; it isn't that… it's that…; less X than Y.* State the positive claim and stop. This is the single most frequent tic — check for it before sending.
- **No metaphors for technical things.** No *levers, knobs, dials, the ballgame, the needle, moving the needle, lens, unlock, surface, bake in, land, the story here.* Name the actual mechanism, setting, or measurement.
- **Never narrate the user's own actions back to him.** He knows what he did and what he asked. No "since you've now pushed both levers", "now that you've reconnected it", "as you noted". Go straight to the consequence.
- **No praise, ever.** No "great point", "good question", "you've hit the key idea", "exactly right", "nice catch", "smart approach". Agreement is expressed by acting on the thing, not by complimenting it. If David is right, say what follows from it. If he is wrong, say so.
- **Ration emphasis.** At most one bold phrase per paragraph, often none. Bold everywhere reads as bold nowhere.
- **No summary restating what just appeared**, whether closing a paragraph or following a table or list.
- **Avoid em-dash constructions.** Use one only where the aside cannot be a separate sentence or a comma clause, and never more than once in a paragraph. The common misuse is backfilling a vague assertion: *"the cost is real — ~20 lines per turn"*. Delete the assertion and keep the fact.
- **Don't characterise, then explain.** No *"the cost is real…", "the risk is significant:…", "this is important because…", "the tradeoff is meaningful:…"*. Give the fact and let David judge its weight: "the cost is ~20 lines loaded on every turn".

Match length to the question: a factual question gets a sentence or two; a design question gets whatever the substance needs and no more.

Example — before:
> **This is the single most important point:** the water side is the trustworthy capacity measurement, and that's genuinely the entire ballgame here — the air-side dry-bulb ΔT is *not*, in cooling.

After:
> In cooling, the water side measures total capacity. Air-side dry-bulb ΔT measures only sensible.

### Asking, planning, and diagnosing

Two behavioral-analysis passes over how David directs work (claude-contexts mempalace-analysis, baseline + iteration-2, 2026-05-30) found the costliest friction is interaction mismatch, not bugs — but *which* mismatch depends on the operating mode. In **delegated/ralph builds** the plan gate dominates (≈75% of interrupts hit `ExitPlanMode`). In **attended work** the plan/ask gate rarely bites (1 of 9 interrupts); the recurring failure there is acting on the harder path before exhausting what was already knowable. These levers target both.

- **Before the harder path — or before asking — exhaust the local, known, and prior-session sources.** This is the most common attended-work interrupt (≈5 of 9): escalating to a remote/harder path, or starting fresh, when the answer was already readable in the repo, claude-contexts, a prior session, or the MemPalace palace — or verifiable by checking world-state (dependency currency, existing access, current versions). Over-asking is the *narrow* case of this: only ask when the answer is David's preference, and especially not when he has already given a direction.
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

Project MEMORY.md and the global index `~/.claude/memory/memory.md` are auto-injected before each tool call via the PreToolUse hook (`~/.claude/hooks/pre-tool-memory.sh`). The index lists every topic file with a one-line description; load a topic file only when relevant.

## Global Memory Reference Rule

Whenever you work in a project and read (or create) its MEMORY.md, check that it contains a
## Global Memory section. If it does not, add it near the top, after the H1.

The section must be a SHORT POINTER only. Do NOT duplicate the topic file list into project
MEMORY.md. The list lives in ~/.claude/memory/memory.md (single source of truth). Project MEMORY.md has a
200-line budget — use it for project knowledge, not boilerplate.

Canonical template for project MEMORY.md:

```
## Global Memory

Read ~/.claude/CLAUDE.md for memory rules and topic files.
```

When a new file is added to ~/.claude/memory/:
- Add it to the table in ~/.claude/memory/memory.md only
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

Scope guard: only reach for the palace when the answer is stored knowledge and
is not already available in the current context, the auto-injected file memory, the
codebase in front of you, or general knowledge. Do not search reflexively for things you
can already answer.

Best-effort: the palace lives on the Mac Mini behind the SSH MCP wrapper. If it is
unreachable (e.g. off-LAN with the remote tunnel dormant), say so and answer from what is
available rather than blocking.
