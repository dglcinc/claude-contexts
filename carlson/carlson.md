# Carlson — Context Summary

## Overview

Builds of Mr Carlson's Lab Patreon projects. The first is the SIFT board from Video 49, a capacitor tester with an LM3914 bar display. Carlson's toner-transfer PDFs are converted into OSH Park Gerbers by `tools/sift2gerber.py` in `dglcinc/carlson`, a private repo because the design is Patreon-only.

## Current State

**Branch:** main. **Open PRs:** none (#1 and #2 merged).

**Last worked on.** Converted the SIFT layout PDF into `gerbers/sift-oshpark.zip`, with drills, mask, and a silkscreen built from the component map. Replaced the discontinued LM3914V (PLCC-20) with the DIP-18 LM3914N-1 through a two-layer re-layout. `tools/verify_dip.py` confirms it matches Carlson's netlist: 48 nets, 242 pads, 8.8 mil minimum spacing. `PARTS.md` holds the parts list, buying plan and case hardware, and `review/index.html` renders the finished board.

**Notes.** The source PDFs are in `~/OneDrive - DGLC/Carlson/Video 49 - SIFT/`, and the photos and parts list are in `~/OneDrive - DGLC/Claude/Carlson/`. The tools need shapely and `pdftocairo`.

## Next Steps

1. Upload the zip to OSH Park, compare its previews with `review/index.html`, and order (about $38.15 for 3).
2. Order the LM3914N-1 (Amazon), the SMD kits and the Digi-Key or Mouser cart from `PARTS.md`.
3. Check the standoff length and test-clip type against the video.
4. Build and test.
