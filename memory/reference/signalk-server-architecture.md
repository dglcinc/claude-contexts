---
name: signalk-server-architecture
description: Architectural review of upstream SignalK/signalk-server — report location, the standing design liabilities, and the AI-PR governance recommendation
metadata:
  node_type: memory
  type: reference
---

A full architectural review of upstream **SignalK/signalk-server** — the Node.js marine-data
server that WilhelmSK, pivac and the docs plugin all talk to — was done 2026-06-06 against
`master` @ v2.28.0-beta.2.

**Deliverable:** `~/github/signalk-server-architecture-review.md` (~44KB, ~700 lines). It is a
loose file; `~/github/` is not a git repo, so the report is **not committed or backed up
anywhere**. Analysis used a full-history clone at `/tmp/signalk-server-loc` (ephemeral —
re-clone and `git fetch --unshallow` to reproduce).

**Scale, for orientation:** ~123k LOC first-party, split `src/` 49k, `server-admin-ui` 34k,
`server-api` 9k, `streams` 6k. A raw `git ls-files | wc -l` reports 356k and is misleading —
mostly `samples/*.log` replay data plus a vendored react-dom-16 bundle.

**The codebase churns hard.** Most of the current core was rewritten during 2025-2026, driven by
a strict-TypeScript migration (core now ~91% TS) and a React 19 + Vite + Zustand admin-UI
rebuild. Treat any specific file or line reference from the report as likely stale, and re-check
before relying on it. Bus factor is small: Teppo Kurki ~50% of commits, Scott Bender ~18%.

**Standing design liabilities** (these predate the rewrite and survived it):
- A central mutable **`app` god-object** — an 8-way `any`-typed intersection at
  `src/index.ts`, which the TypeScript migration never dissolved.
- **The plugin API leaks the whole `app`** via `_.assign({}, app)` in `plugins.ts`, so
  undocumented internals are de-facto public API and `app` cannot be refactored without
  breaking out-of-tree plugins.
- **Single-core**, no clustering or workers; plugins run in-process and trusted.
- **Bacon.js** FRP sits on the hot path.
- Oversized files — `serverroutes` ~2.5k lines, `tokensecurity` ~2k.

**Genuine strengths:** a real WebSocket/TCP backpressure system (latest-value coalescing plus
force-disconnect), hot-path performance rules codified in `AGENTS.md`, a typed v2
OpenAPI/Typebox API with provider registries, a WASM plugin SDK, and CI supply-chain hardening
(Socket.dev firewall, Trivy).

**AI-PR governance recommendation.** The project already has strong defences — `AGENTS.md`
guardrails, an anti-slop `.coderabbit.yaml`, and a PR template gating on "what problem does this
solve". The recommendation was therefore not "add a policy" but to close the two gaps automation
cannot: (1) a short **architecture-alignment checklist** mirrored into CodeRabbit
`path_instructions` — don't widen `app`, don't leak internals to plugins, declare a pruning
story for new per-context state, prove hot-path impact, extend v2 rather than fork it; and
(2) add a **`CODEOWNERS`** file (they have none) plus two-tier review keyed on whether sensitive
paths are touched rather than on diff size, because in-process plugins and whole-`app` exposure
mean a small diff can carry server-wide blast radius. Admission is framed on value and scope,
never on whether a human or an AI wrote it.

Related: [[signalk]] for operating the server and its plugins.
