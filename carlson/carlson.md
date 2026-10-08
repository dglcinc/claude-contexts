# Carlson — Context Summary

## Overview

Builds of Mr Carlson's Lab Patreon projects. The first is the SIFT board from Video 49, a capacitor tester with an LM3914 bar display. Carlson's toner-transfer PDFs are converted into OSH Park Gerbers by `tools/sift2gerber.py` in `dglcinc/carlson`, a private repo because the design is Patreon-only.

## Current State

**Branch:** main. **Open PRs:** none (#1, #2 and #3 merged).

**Last worked on.** Converted the SIFT layout PDF into `gerbers/sift-oshpark.zip`, with the discontinued LM3914V replaced by the DIP-18 LM3914N-1 (verified against Carlson's netlist by `tools/verify_dip.py`). Worked through the parts order and merged PR #3: both panel toggles are the Dailywell 1AD1T2B1M1QES (DPDT, power uses one pole), the coax is a Superbat RG-316 20 ft roll, the standoffs are M3 × 25 mm metal, and every SMD passive is a Mouser cut-tape line in place of the Amazon kits.

**Notes.** Three standoff holes are ground and one is isolated, so metal standoffs are safe. The source PDFs are in `~/OneDrive - DGLC/Carlson/Video 49 - SIFT/`; the photos, parts list and Dailywell datasheet are in `~/OneDrive - DGLC/Claude/Carlson/`. The tools need shapely and `pdftocairo`.

## Next Steps

1. Upload the zip to OSH Park as a standard 1.6 mm, 1 oz board, compare its previews with `review/index.html`, and order 3.
2. Place the Mouser order from `PARTS.md`; use TS5A3159DBVT or TS5A3159ADBVR if the DBVR is out.
3. Order the LM3914N-1 and the coax from Amazon, and a panel-mount 100K linear pot with solder lugs.
4. Build and test.
