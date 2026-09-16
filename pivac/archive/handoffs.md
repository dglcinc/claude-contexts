> ### ▶ ACTIVE HANDOFF — Chiltrix option 2 relay control with HPCOOL, winter is HMI off, cooling-cold alarm (#186–#189 merged); 2026-09-14, Mac Mini
>
> Session 63 (2026-09-14 evening, Mac Mini): winter shutdown changed to controller off on the HMI with the
> breaker on (#186): the HZ-432 has no cooling lockout by outdoor temperature (69-2198 Table 5; `OT LOCKOUT`
> is a heating-stage lockout for non-dual-fuel panels), the CX's `P112`/`P42`/`P43` switch-over is unusable
> with `C`-`H`-`COM`, `P58` is −27 °C, `P00` = 1 keeps off through an outage, and the IOM names no crankcase
> heater. Then the tank-toggling problem: with one relay on `B`, a Checkout heat test ending put the unit back
> in cooling (09-08: mode 0 within a minute, 36 min / 1.13 kWh re-chill). IOM p. 40 contact logic: both open
> standby, `C` alone cool, `H` alone heat, both closed = wired controller (keeps last mode, maintains the
> tank); p. 41 option 2 = two normally closed relays. Plan §2/§4/§5 rewritten for `HPCOOL` (#187), David
> wired it (#188): 782 relay on `O`, NC pole holds `H`, the `H`-`COM` pair moved as a pair, spare pole on
> J4.2 `SP-C` = BCM 13; live config `13: HPCOOL`, baseDeltas order HPHEAT 4, HPCOOL 5, CHIL 6 … SCALA 10,
> Relays panel series (refId I, +.13, blue), label docx row regenerated, 70-782EL14-1 pinout verified (NC
> 1–4, NO 5–8, COM 9–12, coil 13/14, poles in columns 1·5·9 …), diagram `docs/hpheat-hpcool-wiring.svg`.
> Finding: `HPCOOL` read 1 without a break through calls and idle, so the HZ-432 holds `O`/`B` by mode
> (changeover-valve outputs, held to spare the reversing valve); `HPHEAT`/`HPCOOL` are mode indicators,
> the panel does the latching, both contacts closed only with the panel in neither mode; the one-relay
> version would have latched too but depends on `B` staying held below the balance point, which the
> guide does not say. New rule `chiltrix-cooling-cold` (#189, deployed 22:36): mode cooling + own ambient
> < 40 °F + max(switchOn) > 0 over 30 m, for 30 m. C7089 outdoor sensor fitted. As-built corrected
> everywhere: `CHIL` runs the Taco only. `signalk` restart took RedLink out ~2 min (normal).
>
> **Next:**
> 1. Read the overnight record (mode 141, `HPHEAT`, `HPCOOL`, `CHIL`, `BLR`, compressorHz, UBT/LBT): a heat
>    call should flip `HPCOOL` 0 / `HPHEAT` 1, 141 to 1, tank toward 122 °F, and hold after the call. Then
>    the §5 step 4 panel checks (`C64` 1 / `C63` 0 in cooling mode, swapped after the first heat call, 141
>    holding), print the label docx, cold-start WilhelmSK for the new switch.
> 2. Chiltrix plan change 2, second half: after two days at the 12 °C target (from 2026-09-14 17:00 EDT)
>    confirm the band at ~48 °F stop / ~58 °F restart and an outlet minimum near 41 °F, then P12 2 → 3 on
>    the panel and read register 12 back; expect starts/day to fall from 21–29 to ~15–18. Watch master BR
>    and kids-room RH on any warm day.
> 3. Chiltrix tech email (David composing): standby/off temperature protections, whether a cool call with
>    122 °F tank water trips a high-inlet limit. First cold week's log answers what standby freeze
>    protection runs; `P10` = 1 as a `C` blocker is untested and not needed.
> 4. If David drains and refills the loop, follow `docs/hydronic-drain-and-refill.md`; afterwards record
>    the glycol reading and date in CLAUDE.md (it moves the `startupFlow` baseline) and re-check pH.
> 5. HVAC System Manual v1.9 (issue #183): fall and spring procedures (now HMI off, thermostats on Heat),
>    Chiltrix description, relay meanings; source docx in OneDrive `Claude/` and `HVAC Documentation/`.
> 6. Sentry: watch registrationX/Y/Score for a week and add a Grafana panel; rigid camera mount; the
>    tracker does not follow scale; consider a plausibility floor for `air`.
> 7. Boards (OSH Park) and parts (Mouser), both ordered 09-12: populate, test on the spare Pi per
>    `docs/rpi-io-board-design.md` steps 7–8 and `docs/ds18b20-bus-topology.md` §8, swap in; at the swap
>    `HPCOOL` moves to J4.3 `SP-D` and the config pin to 19 (SP-C is on J8 pads on rev A).
> 8. Y-strainer re-inspection around 2026-10-12. Loop fluid pH retest in a month with a meter.
> 9. Carried: heating commissioning per plan §5 (register 143 read back, live-call proof, OT balance 40 °F;
>    watch `r284` on the first real heat-to-cool changeover); first heating week's energy balance replaces
>    the estimated COP; Loop B HIGH and 140 °F offsets; bus topology §7.2 as-built; Wilhelm #155/#156.
>
> **Notes:**
> - Manuals: the CX65/CX75 IOM (chiltrix.com/documents/CX65-1-IOM.pdf) and the HZ432 guide 69-2198
>   (honeywellmanual.com) both extract cleanly with `pdftotext`; WebFetch cannot read them. Relay pages are
>   IOM pp. 40–41 (rendered with `pdftoppm`). The 70-782EL14-1 socket datasheet is the Schneider legacy
>   sockets catalogue (mectronic mirror), p. 62.
> - Render an SVG with headless Chrome (`--screenshot --window-size=W,H`); `qlmanage -t` pads to a square.
> - The "override relay" of earlier plans was `HPHEAT`'s own NC pole holding `C`; there is no separate
>   bridging relay to label.

> ### ▶ ACTIVE HANDOFF — Chiltrix September findings and the loop drain-and-refill procedure (#181, #182 merged); 2026-09-14, Mac Mini
>
> Two weeks of Chiltrix data (08-29 → 09-13, 390 runs) reviewed and folded into the docs (#181):
> P95 5→3 raised the ≤26 Hz leaving-water floor 36.7→39.9 °F with no cycling effect; every near
> miss since is a surge-terminated run (25→47–60 Hz in the last 1–3 min, 5 % of runs, min 37.22 °F
> on 09-08 with r284 = 0) while steady running keeps 3 °F of margin; the start ramp is fixed at
> 50–52 Hz by minute 3, so night runs are 11 min with 36 min gaps; target still 10 °C and P12 still
> 2; cooling COP 4.9 all-in, 5.5–7.4 running, 0.82 kWh/°F of OAT above 48 °F; first heating run
> 09-08 (85 kBTU/h from 3.2 kW, cool-back 36 min / 1.13 kWh). Three sub-minute heating blips on
> 09-13 were mains outages (Pi reboots ~13:05 and ~20:48), now a rule. Then
> `docs/hydronic-drain-and-refill.md` (#182): the Pacific Hydrostar 65836 (120 ft head) fills to
> the attic coil (53 ft needed) with the 30 psi boiler relief as the thing to guard; zone valves
> open, high vents before low drains, air blow-down by zone, pre-mix 30 % PG in a drum, closed purge
> cart, `startupFlow` 51.7 L/min as the proof. Later: `CHIL` corrected in CLAUDE.md (it is the
> Taco primary call; the chiller is always enabled, `HPHEAT` only selects mode); winter shutdown
> section §9 in the shoulder-season plan (#184); manual update backlogged as issue #183; **David
> raised the cooling target to 54 °F at 17:00 EDT, stored 12 °C, register 142 read back** (#185
> open). Pi on master; docs only, no restart.
>
> **Next:** merge #185; after two days at 12 °C confirm the band (~48 stop / ~58 restart, outlet
> min ~41 °F) then P12 2 → 3 and expect starts/day ~15–18; if the loop is drained, follow the doc
> and record the glycol reading; watch Sentry `registrationX/Y/Score` and add a panel;
> boards and parts arriving (populate, test on the spare Pi, swap in); Y-strainer around 10-12.
> **Carried:** heating commissioning per plan §5; first heating week's energy balance; print the
> label; Loop B HIGH and 140 °F offsets; bus topology §7.2; Wilhelm #155/#156; label the override
> relay; a plausibility floor for Sentry `air`.
>
> **Notes:** InfluxDB analysis is one measurement per query at 1 m over ssh, pandas on the Mac
> (`~/pivac-venv` on the Mini now has it). Water-side Q from the chiller's own sensors, ±10 %.
> Drain-and-refill facts to confirm on site: relief valve setting, CX75 drain plugs, zone-valve
> manual lever. Pages: review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ,
> Sentry eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

