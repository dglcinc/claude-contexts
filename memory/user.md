---
name: David — user profile
description: Who David is, his setup, and how he likes to work
type: user
---
David is an experienced developer working primarily on Mac, with a Raspberry Pi for home automation/monitoring. Uses Claude Code CLI as his primary Claude interface. Remote access via Jump Connect from iPad.

Infrastructure is managed through GitHub (dglcinc). Personal content stays in iCloud (Obsidian dglcinc vault) and OneDrive. The separation between these two worlds is a core principle he cares about.

Projects: bowling league web app (Flask/Python, mlb.dglc.com), pivac (HVAC monitoring on Pi), MacDownToo (macOS markdown editor), Arduino sketches, WilhelmSK (iPad layouts).

Machines (David names Macs by Apple-silicon generation — "M4" = the Mac Mini, "M2" = the MacBook Pro; do not confuse with the network):
- **Mac Mini "M4" at `10.0.0.84`** (hostname `UtilityServer-M4`, Apple M4, `Mac16,10`) runs the bowling app (gunicorn) and is the **MemPalace host**, under user **`utilityserver`** — there is no `david` user on this Mac. SSH targets `utilityserver@10.0.0.84`. Often David is physically on the MacBook SSH'd into here, so a session reporting as M4 can mean he's at M2.
- **MacBook Pro "M2" at `10.0.0.83` (FIXED — canonical)** (hostname `david-m2`), user **`david`** (`/Users/david`). The fixed IP is on the **USB ethernet adapter (`en7`, wired)**. The **Wi-Fi (`en0`) carries a second address, now also pinned: reserved to `10.0.0.95`** (David set the reservation 2026-07-03; the live lease still showed the old `.42` until renewal/reconnect — `.109`/`.42` were pre-reservation leases). **mDNS `David-M2.local` resolves to the Wi-Fi address, so don't treat a non-`.83` sighting as "the IP changed."** Always SSH `david@10.0.0.83` (key auth from the Pi verified 2026-07-03). Thin MemPalace client. David's primary hands-on machine — a laptop, so sometimes asleep/off-LAN.
- **Raspberry Pi "pivac" at `10.0.0.82`** (`68lookout.dglc.com` externally) runs pivac, nginx TLS proxy, Grafana, InfluxDB, Signal K. User `pi`.
- **LookoutNas DS225+ at `10.0.0.3`** for backups. SSH as `root` from the Pi (via the pi user's RSA key). DSM admin account is `dlewis`.

Prefers clean, maintainable systems over clever ones. Thinks through architecture before building. Asks probing questions to understand tradeoffs before committing to an approach.

**Obsidian vault layout** (path + perimeter rules are in CLAUDE.md): `notes/` is organized **one folder per notebook** (Recipes, Paint Codes, Cars, Motorcycles, etc.), imported from Evernote in April 2026 via yarle. Resources (images, PDFs) live in per-note `_resources/` subfolders alongside the corresponding `.md`. When navigating or adding: don't flatten the notebook structure, and keep new resources in a sibling `_resources/` folder rather than a global assets dir.
