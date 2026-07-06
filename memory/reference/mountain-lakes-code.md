---
name: Mountain Lakes NJ municipal code — local KB
description: How to answer Mountain Lakes NJ code questions (water rates, zoning, building, etc.) — grep-indexed local corpus + distilled water/watering reference
type: reference
---

**David's town code (Borough of Mountain Lakes, NJ) is imported as a local, grep-indexed knowledge base** so any session can answer code questions (water rates, zoning, building, noise, pools, etc.) without loading the whole code into context.

**Corpus location:** `~/OneDrive - DGLC/Claude/mountain-lakes-code/` (present on David's Macs — M4 `utilityserver`, M2 `david`; syncs via OneDrive). Source: eCode360 **MO1514** (https://ecode360.com/MO1514), full general code Chapters 1–307, exported to PDF 2026-07-06 (the site's WAF blocks automated fetch — re-export from a browser to refresh).

**How to answer a code question (grep-first — do NOT read whole chapters; Ch 245 zoning alone is ~9,600 lines):**
1. Read `INDEX.md` (routing manifest: chapter table + "common question → chapter" map).
2. `grep -in "<term>"` across `chapters/` or `full-text.txt`.
3. `Read` only the matching lines. Cite as `§ <chapter>-<section>` (e.g. `§ 237-10A`).
4. Rebuild after any ordinance amendment: re-export PDF → `build/split_code.py` (pymupdf in the pivac venv).

**Water / irrigation cost + watering-schedule questions:** start at `water-schedule-reference.md` — tiered water & sprinkler-meter rates (§ 111-3C) and § 237-10 restrictions already distilled. Key facts:
- Billing is **quarterly**; rates are **tiered/rising with usage** (§ 111-3C(4)).
- A separate borough sprinkler/deduct meter is **NOT required** (§ 237-4C) — it's opt-in. **David has none**, so his irrigation is billed at **domestic tiers + the $0.6938/100 gal sewer charge** on his single meter (marginal upper tier ≈ **$1.19/100 gal**).
- Mandatory **June–Sept** outdoor-watering restriction (§ 237-10A): **alternate days by house-number parity**, only **12:01–10 a.m. and 6 p.m.–midnight**, none **Jul 31 / Aug 31**; Borough Manager can declare a full ban.

**David's home: 68 Lookout Road, Mountain Lakes, NJ 07046 → house #68 is EVEN → waters on even calendar days.** (Same "68" as `68lookout.dglc.com` / the pivac Pi.) 2026-07-06: set OpenSprinkler Program 1 restriction to **Even days** (native OS odd/even auto-skips the 31st) to comply + roughly halve irrigation volume; kept the compliant 1:00 a.m. start.

Ties into **pivac** (Pi HVAC/home monitoring): pivac meters real irrigation gallons (OpenSprinkler AS200U → InfluxDB `environment.water.irrigation.*`), so watering-cost questions can be answered against actual usage. See pivac project memory `[[mountain-lakes-code-kb]]` for the pivac-side detail.
