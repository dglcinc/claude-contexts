# Carlson — Context Summary

## Overview

Builds of Mr Carlson's Lab Patreon projects. The first is the SIFT board from Video 49, a capacitor tester with an LM3914 bar display. Carlson's toner-transfer PDFs are converted into OSH Park Gerbers by `tools/sift2gerber.py` in `dglcinc/carlson`, a private repo because the design is Patreon-only.

## Current State

**Branch:** main. **Open PRs:** none (#1–#4 merged).

**Last worked on.** Checked the Amazon and Mouser carts against `PARTS.md`; both now cover the whole SIFT list. Merged PR #4, which names the off-board parts: the Alpha RV24AF-10-15R1-B100K-3LA pot (1/4 in round shaft, M8 bushing, 8 mm panel hole), the APEM MPKG50B1/4 set-screw knob, and the TT MFR4-120RFI resistor (0.5 W).

**Notes.** The datasheets for the pot, knob, resistor and toggles sit with the cart PDFs in `~/OneDrive - DGLC/Claude/Carlson/`. Three standoff holes are ground and one is isolated, so the metal standoffs are safe. The source PDFs are in `~/OneDrive - DGLC/Carlson/Video 49 - SIFT/`. The tools need shapely and `pdftocairo`.

## Next Steps

1. Place the Mouser and Amazon orders.
2. Upload the zip to OSH Park as a standard 1.6 mm, 1 oz board, compare its previews with `review/index.html`, and order 3.
3. Build and test.
