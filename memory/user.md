---
name: David — user profile
description: Who David is, his setup, and how he likes to work
type: user
---
David is an experienced developer working primarily on Mac, with a Raspberry Pi for home automation/monitoring. Uses Claude Code CLI as his primary Claude interface. Remote access via Jump Connect from iPad.

Infrastructure is managed through GitHub (dglcinc). Personal content stays in iCloud (Obsidian dglcinc vault) and OneDrive. The separation between these two worlds is a core principle he cares about.

Projects: bowling league web app (Flask/Python, mlb.dglc.com), pivac (HVAC monitoring on Pi), MacDownToo (macOS markdown editor), Arduino sketches, WilhelmSK (iPad layouts).

Machines:
- **Mac Mini at `10.0.0.84`** runs the bowling app (gunicorn) under user **`utilityserver`** — there is no `david` user on this Mac. Pi → Mac SSH must target `utilityserver@10.0.0.84`.
- **Raspberry Pi at `10.0.0.82`** (`68lookout.dglc.com` externally) runs pivac, nginx TLS proxy, Grafana, InfluxDB, Signal K. User `pi`.
- **LookoutNas DS225+ at `10.0.0.3`** for backups. SSH as `root` from the Pi (via the pi user's RSA key). DSM admin account is `dlewis`.

Prefers clean, maintainable systems over clever ones. Thinks through architecture before building. Asks probing questions to understand tradeoffs before committing to an approach.

**Obsidian vault layout** (path + perimeter rules are in CLAUDE.md): `notes/` is organized **one folder per notebook** (Recipes, Paint Codes, Cars, Motorcycles, etc.), imported from Evernote in April 2026 via yarle. Resources (images, PDFs) live in per-note `_resources/` subfolders alongside the corresponding `.md`. When navigating or adding: don't flatten the notebook structure, and keep new resources in a sibling `_resources/` folder rather than a global assets dir.
