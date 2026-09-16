> ### ▶ ACTIVE HANDOFF — First heat run analysed, HPCALL rename, DHWX bridge wired, chiller on all winter (#190–#194 merged); 2026-09-15, Mac Mini
>
> Session 64 (2026-09-15 evening, Mac Mini): first overnight heat run under option 2 analysed. Heat
> mode 04:37–09:04: the master's heat call flipped `HPHEAT` 1 / `HPCOOL` 0 / register 141 to 1 in the
> same minute; the panel held heat mode through calls and a 57-min idle (tank 130 → 125 °F, no run);
> the kids room (73–74 °F, on Auto) forced two changeovers by calling cool (05:12, 1.3 kWh wasted;
> 09:04, eight minutes of 100–118 °F water through its coil). Seven heat runs, 101 min, 6.4 kWh in,
> 29.9 kWh water-side, COP 4.7 at 54 °F (6.1 cold tank, 3.6–4.2 warm), 22–25 kW; heating band
> restart 116–119 °F return, stop 127–128 °F; tank tops 130–131 °F; changeovers 34 min / 2.0 kWh up,
> 33 min / 1.4 kWh down. Great room heat calls close `HPCALL` and run loop B: all five zones heat
> hydronically, kitchen and great room cool on Bosch. LoopDelta gained `heat_zones` and a fan-state
> fix (#190). Cooling band at 12 °C confirmed: stop 48.2–49.3 °F, restart 57.2–58.5, outlet min
> 40.6, ~18 starts/day. `CHIL` renamed `HPCALL` live and in the docs (#191; InfluxDB history under
> `CHIL`; `hardware/` keeps `CHIL`). DHW bridge designed and wired by David: `W1` through a `DHW`
> NC pole to the boiler, NO contact to a new `DHWX` relay closing the same Taco 503 input as
> `HPCALL` (`HPCALL` stays 0 on a bridged call); `DHWX` on J4.3 `SP-D` BCM 19, SwitchBank order 11,
> Relays series (J, +.15, green), LoopDelta primary `relay: [HPCALL, DHWX]`. `BLR` is `W1` upstream
> of the boiler (38 refused calls of 8–39 min last spring, circ LED dark). Heat-mode standby measured
> ~1,700 BTU/h at 60 °F (pump idling 8 L/min through the outdoor exchanger): ~$100 and ~1,400 idle
> starts plus defrost for a winter on. David decided the chiller stays on all winter; §9 rewritten,
> HMI off kept as the out-of-service procedure. The two `DHWX` presses at 22:43 reached the Pi (4 s,
> 2.5 s) but overlapped a kids-room cool call, so the pump start is unattributed on the record.
>
> Late: §9 corrected on defrost (#192), crankcase heater confirmed by Chiltrix support (#193), winter
> standby projection table from the measured UA with `P52` = 2 as the open question (#194); note to
> Chiltrix support drafted with three questions (`P52` = 2 and slush in the still coil, 16–24 short
> reheat runs a day and a lower standby target via register 143, the defrost `C` register).
>
> **Next:**
> 1. First real bridged call (below the balance point, heat + DHW call together): `DHWX` 1 and `ZV` 1
>    with `BLR` 1 and `DHW` 1, `HPCALL` 0, `IN` toward the tank temperature within a minute, chiller
>    restart on its band; `ZV` staying 0 means the old lockout is still in the path. Optional proof:
>    hold `DHWX` 90 s with no zone calling.
> 1a. Fold Chiltrix support's answers into plan §9; if `P52` = 2 is adopted, record the date.
> 2. Bedrooms fight in the shoulder season: both on Heat at night or raise the kids room cool
>    setpoint; one mode per day.
> 3. `P12` 2 → 3 after two days at 12 °C (from 09-14 17:00 EDT); read register 12 back.
> 4. Board swap: `DHWX` holds J4.3, so `HPCOOL` needs `SP-C`/`SP-E` from the J8 pads on rev A.
> 5. First cold week: standby kWh (Emporia, days without `Y1`), starts, defrosts; replaces the §9
>    estimate and the estimated heating COP.
> 6. Plan §11: rooms' drop during refused calls (RedLink record). ΔT panel soft limits vs −24 °F in
>    heating. Sentry registration panel and mount; Y-strainer ~10-12; manual v1.9 (#183); Chiltrix
>    tech email; carried items.
> 7. Unexplained: master bedroom 71 → 75 °F 09:00–10:00 on 09-15 with no call.
>
> **Notes:**
> - Analysis: one measurement per `influx query --raw` over ssh (1 m, or 10 s/raw for toggles), CSV to
>   the scratchpad, pandas on the Mini; Emporia lags Modbus 1–2 min.
> - PivacR uid `bdxar09dh34sgc`; Relays panel offsets series +.03 … +.15 with `byName` overrides on
>   `<measurement>.mean`; Grafana provisions ~45 s after a pull on the Pi's clone.
> - Relay rename recipe: config `outname`, `baseDeltas.json` order, LoopDelta `relay`, dashboard,
>   docs; `restart pivac-gpio pivac-loop-delta` then `signalk`; WilhelmSK cold start for a new tile.
> - RedLink `fan` statenum is 0.5. 782 sockets: A2 bus bar may be fitted, A1 bar must not.

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

