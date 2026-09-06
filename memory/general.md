# General - Cross-Project Conventions

## Writing & Naming Conventions

- **2026-05-14 — American English spelling and terminology.** Use "program" not "programme", "-ize" endings not "-ise", "-or" not "-our", "modeled" not "modelled", "modernization" not "modernisation". User caught British/Canadian spellings in a doc and asked for American going forward across all projects.

## Workflow Preferences

(Populate as you go — add things like: how you prefer to review work, commit message style)

## 2026-08-23 — Hardware part recommendations: always give both Digi-Key and Amazon links
When recommending any hardware part, give BOTH a Digi-Key link and an Amazon link, never one
alone. David sources from both and picks per part (Digi-Key for specs/stock/genuine parts,
Amazon for speed and prebuilt modules Digi-Key doesn't carry). Verify the Digi-Key page rather
than constructing the URL; flag SMD parts that need a breakout adapter.

- **2026-09-02 — Agent credentials live under `~/.config/`; look there before asking.** David stores API keys for Claude sessions as `~/.config/<service>-claude-agent.key` or `~/.config/<service>/claude-agent.key` (unifi, shelly, grafana so far), mode 600, usually mirrored on the Pi. He was annoyed at being asked for the Grafana admin password when a token could simply be minted and stored; the fix was a token file plus a CLAUDE.md pointer. When a service needs a credential that is missing: search `~/.config` on both machines, the palace, and CLAUDE.md first, then ask him to mint a token (never for a password), and record the file path in the project CLAUDE.md.
