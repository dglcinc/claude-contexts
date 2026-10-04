# Sony Boombox — Context Summary

## Overview

Restore David's Sony CFD-G50 CD radio cassette-corder (US model, about 2000) to full working order. The set has been completely dead for about ten years. The work is diagnosis of the power fault, assessment and replacement of aged parts, and mechanical service of the tape deck and CD mechanism. The repo holds documentation only: the service manual PDF and a diagnosis and service plan under `docs/`.

## Current State

Branch `add-service-manual`, local only, six commits ahead of `main`, unmerged. The repo has no remote, so there are no PRs.

David ran the first power tests. A series lamp on mains stayed dark and the set stayed dead. With the cord out and 12 V (500 mA limit) on the pack-end contacts on the BATT board, there was no short and zero current before and after pressing POWER. An earlier "short" came from clipping across the BATT COM board, which is only the mid-string link. Results are in section 8 (Findings) of `docs/cfd-g50-diagnosis-and-service.md`.

Zero standby current means B+ never reaches IC502, so the break is ahead of the main-board circuits. The leading suspect is an open J901 changeover contact, since it would kill both supplies. An open T901 primary or F902 remains possible; the dark lamp fits either.

## Next Steps

1. Cycle the AC plug in and out of J901 a dozen times to wipe the changeover contact, then retest on 12 V, confirming zero current with a meter in series on mA.
2. If still dead, open the set (Stage B) and trace 12 V along the positive path: BATT board KH952, CNP902 BATT pin, J901 BATT contact and COM, CNP903 COM pin, KH321, C347 positive. Then trace the ground path. If both reach C347, the break is between C347 and IC502 pin 2.
3. While open, check F902 and the T901 primary (Stage C).
4. Fit the tape belt (3-933-020-01, ordered 2026-09-30) when it arrives; inspect the pinch roller.
5. Merge `add-service-manual` into `main` when David wants it; a PR needs a GitHub remote, which he has deferred.
