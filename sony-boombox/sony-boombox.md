# Sony Boombox — Context Summary

## Overview

Restore David's Sony CFD-G50 CD radio cassette-corder (US model, about 2000) to full working order. The set has been completely dead for about ten years. The work is diagnosis of the power fault, assessment and replacement of aged parts, and mechanical service of the tape deck and CD mechanism. The repo holds documentation only: the service manual PDF and a diagnosis and service plan under `docs/`.

## Current State

Branch `add-service-manual`, local only, 26 commits ahead of `main`, unmerged. The repo has no remote, so there are no PRs.

The power fault is found: J901, the AC inlet, has both changeover contacts to COM (B+) failed open, which killed the set on batteries and mains. With a jumper from RECT.OUT to COM the set runs on mains, and the CD and radio work. The plan carries the Schottky diode-OR fallback (1N5822) for J901, the twelve capacitors to replace regardless of test, leakage checks, and glue guidance.

On a bench supply with no cells, the set powers up then shuts down with a battery warning; the battery check most likely reads the string's floating mid-point. David never uses batteries in this set.

## Next Steps

1. When Sony's substitute inlet 1-843-191-11 arrives, check that it has three switch pins and the same footprint, then fit it. If it lacks the switch, fit the Schottky fallback in plan section 5.4.
2. Capacitor service when the parts arrive: replace C909, C347, C349, C503, C504, C518, C953, C955, C959, C135, C235, C707 regardless; test the rest; record standby current and speaker DC before and after.
3. Fit the tape belt (3-933-020-01) when it arrives, then test tape and demagnetize the head.
4. Merge `add-service-manual` into `main` when David wants it.
