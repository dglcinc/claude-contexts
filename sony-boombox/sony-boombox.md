# Sony Boombox — Context Summary

## Overview

Restore David's Sony CFD-G50 CD radio cassette-corder (US model, about 2000) to full working order. The set has been completely dead for about ten years. The work is diagnosis of the power fault, assessment and replacement of aged parts, and mechanical service of the tape deck and CD mechanism. The repo holds documentation only: the service manual PDF and a diagnosis and service plan under `docs/`.

## Current State

Branch `add-service-manual`, local only, three commits ahead of `main`, unmerged. The repo has no remote, so there are no PRs.

Copied Sony's CFD-G30/G50 service manual into `docs/` and reviewed it, reading the power, main-board and control schematics at 300 dpi and the CD, tape and tuner schematics at overview level. Wrote `docs/cfd-g50-diagnosis-and-service.md`: how the power circuit works, Sony's reference voltages and supply currents, tools, a staged diagnostic procedure (A to E), a servicing procedure listing all 74 electrolytics by board and value, and the optional adjustments. Filled in the project CLAUDE.md with the goal, the document map and how to read the raster schematic pages.

No measurements have been taken yet. The leading suspect is an open primary in transformer T901: the US model has no primary fuse, so the winding is energized whenever the set is plugged in. That is a hypothesis from the schematic, untested. AC-side figures and ESR thresholds in the plan are estimates and are marked as such.

## Next Steps

1. David reviews the plan and sets up his tools, then runs Stage A later in the week of 2026-09-28: plug-blade resistance with the cord in the set, then 12 V DC at the battery terminals with the cord removed, noting supply current before and after pressing POWER.
2. Interpret his Stage A readings against the table in section 4 of the plan and direct him to Stage C, D or E.
3. Fit the tape belt (Sony 3-933-020-01, ordered 2026-09-30) when it arrives; inspect the pinch roller (3-933-024-01) at the same time.
4. Record measurements and findings in the repo as they come in.
5. Merge `add-service-manual` into `main` when David wants it; a PR needs a GitHub remote, which he has deferred.
