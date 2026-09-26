> ### ▶ ACTIVE HANDOFF — Rev A boards bench-checked; new Pi arrives 09-26 for the swap; 2026-09-25, M2
>
> Session 72 (2026-09-25, M2). Bench-checked the first rev A INT and EXT boards on a fresh bench card
> (Trixie Lite, cloud-init `pibench`, user `pi`, password `pivac-bench`, M2 keys, SSH and I2C on,
> `io-board-test.py` in the home directory). INT: 37.1 V DC on TP1–TP2; nine channels proven end to
> end (ZV, DHW, BLR, BOS1, BOS2, DEHUM, SCALA, HPHEAT, SP-D). CHIL, SP-C and SP-E are unproven: the
> bench Pi (`dc:a6:32:19:12:ee`, the DS18B20 calibration Pi) has BCM 13, 16 and 25 dead on the bare
> header. EXT: DS2482 at 0x18, probe `0516a36816ff` on H1, H2 and H3, so JP2 is right. Merged #205,
> #207 (tone map `docs/rpi-io-boards-reva-tone-map.svg`, rev A map default in the test script, bench
> record, the off-Pi rule) and #208 (rev A is one plug position short; rev B keeps one COM per board).
> The Pi is at b6cce8d. Bench Pi shut down.
>
> **Next:**
> 1. New Pi 09-26: boot the bench card, read all twelve channel pins high bare, then prove CHIL, SP-C,
>    SP-E with the INT board (`--only 4`, `11`, `12`).
> 2. J8 pigtail (SP-C = `HPCOOL`, SP-E, COM) with strain relief, and the 5-way link cable. For a
>    pluggable pigtail try a 3-way PTSM header in the EXT proto field first (1.0 mm holes vs 1.1).
> 3. Housing swap per `rpi-io-boards-pcb-plan.md` §6 steps 6–8: J4.1 24 VAC hot, J4.2 return
>    (unlabelled), HPCOOL from J4.2 to J8 SP-C, J4.4 stays J4's COM. Freeze and clone first; prove
>    `HPCALL` on the first call and the 1-wire bus; check Sentry `decodeMargin`/`registrationScore`.
> 4. Carried: glycol top-up (premixed, record the date); `P52` = 2 pump check; pump-step sentinel;
>    exclude the 09-19 changeover firing; kids room duty and master setpoint gap; return transfer
>    plan (#198); first cold week record.
>
> **Notes:**
> - Every continuity check on an I/O board is made OFF the Pi: the SoC's protection diodes tone every
>   GPIO to ground on the header. Read a low pin on the bare Pi before blaming the board.
> - J4.2 has no silkscreen label. Transformer to J4.1/J4.2; neither is COM. A return on COM shorts the
>   transformer through a diode and the PTC (it survived several minutes of that).
> - Socket pins: bottom row 1–8 from the left, top row 9–16 from the RIGHT. C pins: U1 10 CHIL, 12
>   BLR, 14 DHW, 16 ZV; U2 10 SCALA, 12 DEHUM, 14 BOS2, 16 BOS1; U3 10 SP-E, 12 SP-C, 14 SP-D, 16 HPHEAT.
> - 11 relays vs 10 plug channel positions on rev A; J7 (VS, COM, +5V, GND) cannot carry channels;
>   J9 pads have no opto behind them. PTSM 0,5 takes 26–20 AWG.
> - Card writing on the M2: built-in reader `/dev/disk15`; `! sudo sh -c 'xz -dc … > /dev/rdisk15'`
>   from the prompt; `user-data`, `meta-data` (`instance-id`), `network-config` and the script onto
>   `/Volumes/bootfs`. Bench Pi `~/edges.py` logs pin edges (`setsid nohup … & disown`; never
>   `pkill -f edges.py` from an ssh command line that contains the name).
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

> ### ▶ ACTIVE HANDOFF — Rev A boards arrived; assembly bench sheet merged (PR #206); Pi still needs a pull; 2026-09-25, Mac Mini
>
> Session 71 (2026-09-25, Mac Mini). The rev A boards arrived from OSH Park. Wrote
> `docs/rpi-io-boards-assembly.md`, the bench sheet for populating them: order of work (flattest to
> tallest, EXT first, Pi socket last on the spare Pi as a jig), a three-column table per board of
> reference, invoiced part and location with the handling notes as a numbered list under it, the checks
> with rev A's values (12 kΩ per channel, about 35 V on VS), the link cable and the housing swap.
> `docs/rpi-io-boards-parts.md` now cites Mouser invoice 92489596 (shipped 2026-09-14, PDF in the
> OneDrive Claude folder), which carries the five MAL202138101E3 for INT C1 that the 09-12 cart lacked.
> Merged as PR #206 (7bb3321). PR #205 (changeover interlock deferred) is still open; the Pi is at 5078b76.
>
> **Next:**
> 1. Merge PR #205 and pull on the Pi (brings #206 too).
> 2. Assemble one INT and one EXT board per the sheet; bench-check on the spare Pi; make the 5-way link
>    cable; swap into the housing per `rpi-io-boards-pcb-plan.md` §6 steps 6–8. `HPCOOL` (BCM 13) is
>    `SP-C` on the J8 pads, a soldered wire; `SP-E` (BCM 16) is free for `Y2` logging. Check Sentry
>    `decodeMargin` and `registrationScore` after the visit.
> 3. Hydronic pressure 20.2–21.8 psi since the filter install: top up with premixed 30 % glycol, never
>    through the demineralised fill, and record the date.
> 4. `P52` = 2 has not stopped the pump (idle flow 6.9 L/min all day on 09-18); check a later day, then
>    ask Chiltrix support if it never stops.
> 5. Pump-step sentinel on each month's strainer check; decide whether it earns a panel or derived path.
> 6. Exclude the 09-19 12:45 changeover firing (power return) from the count; confirm valve wiring,
>    where `ZV` picks up, and the old CDP lockout on site.
> 7. Kids room duty baseline 09-18 (0.41 at 73.5 °F mean outdoor); master bedroom is the next
>    setpoint-gap question. Kids dehumidify never engaged on 09-18.
> 8. Return transfer plan (#198) re-read once the setpoint gap has data. `P12` stays 2. First cold week:
>    standby kWh, starts, defrosts (`r216`; `r217` = 1 unexplained). The 5.5 gal/min draw under the
>    09-17 16:40 shower is unexplained.
>
> **Notes:**
> - Rev A channel map: SP-D = BCM 19 = `DHWX` on J4.3; SP-C = BCM 13, SP-E = BCM 16 on J8; CHIL on J2.1 =
>   `HPCALL`. J9 carries none of the channel GPIOs, so the C-pin continuity check goes to the Pi header
>   pin (ZV 11, DHW 13, BLR 15, CHIL 22, BOS1 31, BOS2 29, DEHUM 32, SCALA 16, HPHEAT 18, SP-D 35, SP-C 33,
>   SP-E 36). EXT JP2 pads run left to right DATA · H3 · U2; the bus default is centre-to-left.
> - A requested "doc" is a `.md` in `docs/`, not a Claude Doc; short table cells, instructions listed
>   under the table.
> - Pressure analysis recipe: six measurements pulled one per `influx query --raw` with
>   `aggregateWindow(every: 1m, fn: mean)`, pandas on the Mini; a flow edge is `waterFlow` crossing
>   15 L/min (idle reads 6.9, never 0); step_on = mean of the first two minutes minus the three before;
>   fit `psi ~ flow²` and check the residual against the temperatures.
> - Analysis data pulls: one measurement per call with `aggregateWindow` on the Pi, tar to the Mac,
>   pandas in `~/pivac-venv` on the Mini; parse timestamps with `format='ISO8601'`. A 5-min `mean` of
>   `statenum` is duty; 1-min `min` gives call edges.
> - A boiler-room circuit outage: both Arduinos, their Shelly, the water meter, Sentry `waterTemp` and
>   `HPCOOL` all gone at once, chiller `switchOn` 1 with `compressorHz` 0 and `waterFlow` 6.9, five
>   staleness alerts at +30 min, and the changeover rule firing when `HPCOOL` returns.
> - Relays are stored as `electrical.ac.switch.utility.<NAME>.statenum`; the bare path returns nothing.
>   InfluxDB times are UTC. Leaving the Prestige installer menu restarts the staging.
> - Grafana: prove a rule fires by lowering the threshold in the Pi's /etc copy, restart, read
>   `/api/prometheus/grafana/api/v1/rules`, restore from the repo copy. Alert history:
>   `/grafana/api/annotations?type=alert`.
> - Session 65 notes still apply: Emporia backfill script; 782 sockets; Prestige installer path (Resideo
>   69-2490); RedLink `fan` statenum 0.5; PivacR uid `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

> ### ▶ ACTIVE HANDOFF — Boiler-loop pressure dip on chiller runs is the pump differential, recorded as a fouling sentinel; P52 = 2 has not stopped the pump; 2026-09-21, Mac Mini
>
> Session 69 (2026-09-20 to 09-21, Mac Mini). Settled why the boiler-loop pressure dips on every
> chiller run: the tank separates flow, never pressure, and the `.219` gauge sits on the suction side of
> the Chiltrix pump's path from the expansion tank connection. On 2026-09-18 (23 runs) the gauge stepped
> −1.23 psi (−1.00 to −1.56) in the first minutes at the 52.9 L/min startup plateau, climbed back about
> 0.5 psi as the chiller trimmed flow to 25–35 L/min, and took the rest back at the stop. Flow squared
> explains 63 % of the day's pressure variance; the residual has no relationship to `IN`, `LBT` or the
> chiller inlet, so thermal contraction of the chilled glycol is −0.19 psi net per run, at the noise
> level. Recorded in CLAUDE.md as a second fouling sentinel, baseline 1.0–1.6 psi at about 5 % screen
> coverage (5078b76, pushed to master and pulled on the Pi). The same record shows the flow meter at
> 6.9 L/min through all 588 idle minutes of 09-18 and never 0, so `P52` = 2 has not stopped the pump
> between runs and the 6.9 L/min trickle is the idle baseline.
>
> **Next:**
> 1. Hydronic pressure sits at 20.2–21.8 psi since the filter install, the floor of the 21–23 rule: top up
>    with premixed 30 % glycol, never through the demineralised fill, and record the date (moves the
>    `startupFlow` baseline and may move the pump-step baseline).
> 2. `P52` = 2 has not stopped the pump: idle flow read 6.9 L/min all day on 09-18. Check a later day
>    (09-20/21) for any zero; if the pump never stops, ask Chiltrix support whether `P52` = 2 needs a
>    restart or a companion parameter. `chiltrix-zero-flow` keeps its 7-minute window until then.
> 3. Pump-step sentinel: read `electrical.ac.arduinoThermPSI.psi` drop at the 52.9 L/min plateau on each
>    month's strainer check alongside `.startupFlow`. A Grafana panel or a derived path in
>    `pivac.ChiltrixModbus` would make it routine; decide whether it earns one.
> 4. Sentry after the 09-19 boiler-room visit: check `decodeMargin` and `registrationScore` (16 score
>    dips under 0.60 on 09-19 afternoon).
> 5. Exclude the 09-19 12:45 `hz432-mode-changeover` firing (panel power return) from the changeover
>    count; common → §7.1 interlock. Confirm on site: valve wiring, where `ZV` picks up, old CDP lockout.
> 6. Kids room duty comparison baseline is 09-18 (kids 74, family 75, gap 1 °F): 0.41 at 73.5 °F mean
>    outdoor. 09-19 is unusable. Master bedroom is the next setpoint-gap question (continuous 4 h calls
>    at 80 °F+ outdoor, room 1–2 °F over, already 1 °F above the kids room).
> 7. Fan-stage check is inconclusive from loop A ΔT; `Y2` logging on BCM 16 is the only way to see it.
> 8. Kids room dehumidify never engaged on 09-18 (RH 53–56 %, 142 min at or above 55 %, room never
>    below 74.0).
> 9. Return transfer plan (#198) re-read once the setpoint gap has data. `P12` stays 2. First real
>    bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1, `HPCALL` 0. Board swap: `HPCOOL` needs
>    `SP-C`/`SP-E` from J8 on rev A. First cold week: standby kWh, starts, defrosts (`r216`; `r217` = 1
>    unexplained). Plan §11 carried items. The 5.5 gal/min steady domestic draw under the 09-17 16:40
>    shower is unexplained.
>
> **Notes:**
> - Pressure analysis recipe: six measurements pulled one per `influx query --raw` with
>   `aggregateWindow(every: 1m, fn: mean)`, pandas on the Mini; a flow edge is `waterFlow` crossing
>   15 L/min (idle reads 6.9, never 0); step_on = mean of the first two minutes minus the three before;
>   fit `psi ~ flow²` and check the residual against the temperatures.
> - Analysis data pulls in general: one measurement per call with `aggregateWindow` on the Pi, tar to
>   the Mac, pandas in `~/pivac-venv` on the Mini; parse timestamps with `format='ISO8601'`. A 5-min
>   `mean` of `statenum` is duty; 1-min `min` gives call edges. Loop A ΔT ratio = ΔT ÷ (room − LOOPA_SUP)
>   in °F.
> - A boiler-room circuit outage looks like: both Arduinos, their Shelly, the water meter, Sentry
>   `waterTemp` and `HPCOOL` all gone at once, chiller `switchOn` 1 with `compressorHz` 0 and `waterFlow`
>   6.9, `IN` warming toward room temperature, five staleness alerts at +30 min, the watchdog logging a
>   failed cycle every 5 min, and the changeover rule firing when `HPCOOL` returns. With the HZ-432
>   unpowered both Chiltrix mode contacts are closed, so the chiller holds no mode (1.8 °F/h tank drift).
> - Relays are stored as `electrical.ac.switch.utility.<NAME>.statenum` (and `.state`); the bare path
>   returns nothing. InfluxDB times are UTC; the Pi's `date` gives EDT.
> - Leaving the Prestige installer menu restarts the staging and the equipment timers.
> - Grafana: no max/min across queries, pairwise `abs()` ORs; `notification_settings.repeat_interval`
>   works; prove a rule fires by lowering the threshold in the Pi's /etc copy, restart, read
>   `/api/prometheus/grafana/api/v1/rules`, restore from the repo copy. Alert state history:
>   `/grafana/api/annotations?type=alert`.
> - Session 65 notes still apply: Emporia backfill script; 782 sockets; Prestige installer path (Resideo
>   69-2490); RedLink `fan` statenum 0.5; PivacR uid `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

> ### ▶ ACTIVE HANDOFF — Load moved from the kids room to the family room; Caleffi demineralisation filter installed, boiler-room circuit dark 08:15–12:45; 2026-09-19, Mac Mini
>
> Session 68 (2026-09-18 evening and 09-19, Mac Mini). Analysed 09-18, the first full day under the 1 °F
> stage 2 differential, 2 cycles per hour, the family room lowered from 76 °F and the kids room at 74 °F.
> The midday load moved from the kids room to the family room and the house used the same chiller energy
> per cooling degree-hour: kids duty 0.67 → 0.41 on a day 6 °F warmer (longest call 161 → 24 min, cycles
> of 11 min on and 14.5 off), family room 0.02 → 0.55, master bedroom unchanged at 0.46 and now the
> full-demand zone (4 h 12 min call, 77 °F at 82 °F outdoor), chiller 0.147 → 0.108 → 0.101 kWh per
> degree-hour (base 65). The family room reads 75 since 09-17 20:35; the 74 °F setting lasted nine hours.
> On 09-19 David installed a Caleffi demineralisation filter; the boiler-room circuit was dark 08:15–12:45
> (Arduinos plug, water meter, Sentry camera and HZ-432 all off; Pi, chiller and 1-wire up). Hydronic
> pressure fell 23.3 → 21.0 psi at the same 50 °F tank, startupFlow unchanged at 52.9 L/min, the chiller
> held no mode with the panel dark and the tank drifted 47.6 → 55 °F, the master bedroom reached 79 °F,
> and `hz432-mode-changeover` fired on power return.
>
> **Next:**
> 1. Hydronic pressure sits at 20.2–21.8 psi since the filter install, the floor of the 21–23 rule: top up
>    with premixed 30 % glycol, never through the demineralised fill, and record the date (moves the
>    `startupFlow` baseline).
> 2. Sentry after the boiler-room visit: margin 64–84, misses 0, tracker moved the quad ~1 px with 16
>    score dips under 0.60 on 09-19 afternoon; check `decodeMargin` and `registrationScore` on 09-20.
> 3. Exclude the 09-19 12:45 `hz432-mode-changeover` firing (panel power return) from the changeover
>    count; common → §7.1 interlock. Confirm on site: valve wiring, where `ZV` picks up, old CDP lockout.
> 4. Kids room duty comparison baseline is 09-18 (kids 74, family 75, gap 1 °F): 0.41 at 73.5 °F mean
>    outdoor. 09-19 is unusable (four hours calling into dead equipment).
> 5. Master bedroom is the next setpoint-gap question: continuous 4 h calls at 80 °F+ outdoor with the
>    room 1–2 °F over; it already sits 1 °F above the kids room.
> 6. Fan-stage check (high fan only 1 °F over, drops at setpoint) is inconclusive from loop A ΔT: ratio
>    0.205 with the master at 76–77 vs 0.171 at 75, but ΔT stayed 5–6 °F after the display returned to
>    75 (whole-degree display, kids share loop A). `Y2` logging on BCM 16 is the only way to see it.
> 7. Kids room dehumidify: RH 53–56 % all of 09-18, 142 min at or above 55 %, room never below 74.0, so
>    the overcool never engaged or never bit.
> 8. `chiltrix-zero-flow` went Pending for a minute at 12:52 on 09-19 on the `P52` = 2 pump stop: decide
>    its window and compare `.startupFlow` across the change.
> 9. Return transfer plan (#198) re-read once the setpoint gap has data. `P12` stays 2. First real
>    bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1, `HPCALL` 0. Board swap: `HPCOOL` needs
>    `SP-C`/`SP-E` from J8 on rev A. First cold week: standby kWh, starts, defrosts (`r216`; `r217` = 1
>    unexplained). Plan §11 carried items. The 5.5 gal/min steady domestic draw under the 09-17 16:40
>    shower is unexplained.
>
> **Notes:**
> - Analysis data pulls: `influx query --raw` one measurement per call with `aggregateWindow` on the Pi,
>   tar to the Mac, pandas in `~/pivac-venv` on the Mini; parse timestamps with `format='ISO8601'`. A
>   5-min `mean` of `statenum` is duty; 1-min `min` gives call edges. Loop A ΔT ratio =
>   ΔT ÷ (room − LOOPA_SUP) in °F.
> - A boiler-room circuit outage looks like: both Arduinos, their Shelly, the water meter, Sentry
>   `waterTemp` and `HPCOOL` all gone at once, chiller `switchOn` 1 with `compressorHz` 0 and `waterFlow`
>   6.9, `IN` warming toward room temperature, five staleness alerts at +30 min, the watchdog logging a
>   failed cycle every 5 min, and the changeover rule firing when `HPCOOL` returns.
> - With the HZ-432 unpowered both Chiltrix mode contacts are closed, so the chiller holds no mode and
>   does no tank maintenance (1.8 °F/h drift).
> - Relays are stored as `electrical.ac.switch.utility.<NAME>.statenum` (and `.state`); the bare path
>   returns nothing. InfluxDB times are UTC; the Pi's `date` gives EDT.
> - Leaving the Prestige installer menu restarts the staging and the equipment timers.
> - Grafana: no max/min across queries, pairwise `abs()` ORs; `notification_settings.repeat_interval`
>   works; prove a rule fires by lowering the threshold in the Pi's /etc copy, restart, read
>   `/api/prometheus/grafana/api/v1/rules`, restore from the repo copy. Alert state history:
>   `/grafana/api/annotations?type=alert`.
> - Session 65 notes still apply: Emporia backfill script; 782 sockets; Prestige installer path (Resideo
>   69-2490); RedLink `fan` statenum 0.5; PivacR uid `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

> ### ▶ ACTIVE HANDOFF — High fan was ISU 3030 Comfort, now 1 °F on all five; kids room humidity step was a shower (#202–#204 merged); 2026-09-17, Mac Mini
>
> Session 67 (2026-09-17 afternoon, Mac Mini). The master bedroom and family room air handlers ran
> the high fan through hours-long calls with the display reading the setpoint: under ISU 3030 Comfort a
> continuous call holds stage 2 for its whole length. 3030 offers only Comfort or whole degrees from
> setpoint (the doc's "Economy" was wrong). David set every thermostat to a 1 °F stage 2 differential
> and 2 cycles per hour on both stages, heat and cool; by evening the calls ran on the low fan (#203,
> #204). The kids room's 52 → 59 % humidity step at 16:55 EDT was a shower: domestic flow 11–14.5
> gal/min 16:40–16:51 with `DHW` closed 16:40–17:15 and the other four zones flat; the room held
> 51–54 % on 47–54 °F loop A supply all day, so the 12 °C target stays. Its dehumidify call (55 %, 3 °F
> overcool, low fan) started after a ten-minute "waiting for equipment" hold and reads as ordinary
> cooling in RedLink. Shower rule in CLAUDE.md (RedLink). #202 merged. Pi and Mini on master 32e57d7.
>
> **Next:**
> 1. Hot afternoon check: the high fan returns only at 1 °F above setpoint and drops back at setpoint.
> 2. Kids room duty comparison now starts 2026-09-17 (family room 74 °F, dehumidify call and 1 °F
>    differential all landed that day); the family room's own duty should rise from 0.15.
> 3. Kids room: does the dehumidify call reach 55 % or its 71 °F floor first? RedLink cannot tell
>    the two calls apart, so read it from humidity against `statenum`.
> 4. Not checked: `hvac.chiller.chiltrix.waterFlow` at idle under `P52` = 2 (6.9 L/min trickle
>    seen); decide `chiltrix-zero-flow`'s window and compare `.startupFlow` across the change.
> 5. Return transfer plan (#198) re-read against the mixing finding once the setpoint gap has data.
> 6. Count `hz432-mode-changeover` firings; common → §7.1 interlock. Confirm on site: valve wiring,
>    where `ZV` picks up, old CDP lockout.
> 7. `P12` stays 2. First real bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1, `HPCALL` 0.
>    Board swap: `HPCOOL` needs `SP-C`/`SP-E` from J8 on rev A. First cold week: standby kWh,
>    starts, defrosts (`r216`; `r217` = 1 unexplained). Plan §11 carried items.
> 8. `Y2` logging (§4.6) is the only way to see the stage; BCM 16 is the free input with a wire run.
> 9. The 5.5 gal/min steady domestic draw under the 16:40 shower is unexplained (irrigation not checked).
>
> **Notes:**
> - Relays are stored as `electrical.ac.switch.utility.<NAME>.statenum` (and `.state`); the bare
>   path returns nothing. InfluxDB times are UTC; the Pi's `date` gives EDT.
> - Leaving the Prestige installer menu restarts the staging and the equipment timers, so a stage
>   drop right after a settings change proves nothing.
> - Zone analysis method: hourly `aggregateWindow` of `environment.inside.thermostat.<ZONE>.{statenum,coolset,temperature,humidity}`;
>   duty = clip(−statenum, 0, 1); `coolset`/`heatset` in °F, `temperature` in K. pandas in `~/pivac-venv` on the Mini.
> - Grafana: no max/min across queries, pairwise `abs()` ORs; `notification_settings.repeat_interval`
>   works; prove a rule fires by lowering the threshold in the Pi's /etc copy, restart, read
>   `/api/prometheus/grafana/api/v1/rules`, restore from the repo copy.
> - Session 65 notes still apply: Emporia backfill script; one measurement per `influx query --raw`;
>   782 sockets; Prestige installer path (Resideo 69-2490); RedLink `fan` statenum 0.5; PivacR uid
>   `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

> ### ▶ ACTIVE HANDOFF — Kids room long call is open-plan mixing, not ISU 3140 (#201 merged); zone setpoint spread alerts (#202 open); 2026-09-17, Mac Mini
>
> Session 66 (2026-09-17 morning, Mac Mini). The kids room called for 11 hours (15:56–02:39) after
> ISU 3140 went to 2; the record shows load, never the setting: the room held 73 °F, prior full-duty
> stretches of 9 and 10 h exist, and from 04:19 it cycled 12–22 min on / 10–18 off at 51 % duty (two
> cycles an hour). 3140 has a rate per cooling stage on a two-stage Prestige; David has both at 2 on
> kids and master. Loop A ΔT on kids calls follows fan stage and the tank band (ΔT ÷ (room − supply)
> 0.12 cycling, 0.16–0.22 at full demand; 2.0–2.5 °F on 55–57 °F supply, 3.6–4.9 °F on 50–52 °F).
> David's open-plan mixing theory holds: with the kids setpoint alternating 73/74 °F across all
> periods at matched outdoor temperature, duty at 73 is 1.5 × duty at 74 (0.72 vs 0.53 evenings), the
> ratio of the gaps to the family room's steady 76 °F, and the family room's duty drops when kids is
> at 73. All into Appendix J and the CLAUDE.md RedLink rule (#201, merged, 5b3b7a6). David set the
> family room to 74 °F on 09-17 (kids 74, master 75, great room 75, kitchen 76). House rule: zone
> setpoints within 2 °F. PR #202 (open) adds `zone-setpoints.yaml`: `zone-coolset-spread` /
> `zone-heatset-spread`, info, any pair > 2 °F for 2 h, gated on `HPCOOL` / `HPHEAT`,
> `repeat_interval: 24h`; tested on the Pi (inactive live, cooling pending at a 1 °F threshold) and
> the rule file is already live in `/etc/grafana/provisioning/alerting/`. Pi clone on master 5b3b7a6.
>
> **Next:**
> 1. Merge #202, then `git pull` on the Pi (rule file already deployed; nothing else to do).
> 2. After several days at family room 74 °F: kids room duty at matched setpoint, period and outdoor
>    temperature against the month to 09-17 (0.51 aft/eve, 0.42 morning, 0.37 night at 74 °F); family
>    room duty should rise from 0.15. Also the 15-on/15-off call-length distribution by compressor state.
> 3. Not checked last night: does `hvac.chiller.chiltrix.waterFlow` read 0 at idle under `P52` = 2?
>    Overnight samples showed 6.9 L/min at Hz 0, so the trickle may persist; confirm on a longer idle
>    gap, then decide on `chiltrix-zero-flow`'s window and compare `.startupFlow` across the change.
> 4. Return transfer plan (#198): a transfer path couples the kids room harder to the hallway, so close
>    the setpoint gap first and re-read the plan against the mixing finding.
> 5. Count `hz432-mode-changeover` firings over weeks; common → build the §7.1 interlock; rare →
>    bedrooms on one mode per day. Confirm on site: valve wiring, where `ZV` picks up, old CDP lockout.
> 6. `P12` stays 2; revisit next spring. 7. First real bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1,
>    `HPCALL` 0, `IN` toward the tank. 8. Board swap: `HPCOOL` needs `SP-C`/`SP-E` from J8 on rev A.
> 9. First cold week: standby kWh, starts, defrosts (`r216` candidate; `r217` = 1 unexplained).
> 10. Plan §11: rooms' drop during refused calls; ISU 9000/9070; ΔT panel limits; Sentry mount;
>     Y-strainer ~10-12; manual v1.9; carried items. Master bedroom 71 → 75 °F on 09-15 with no call.
> 11. Observations: no Grafana rule on `electrical.emporia.*`; Emporia re-logs in every cycle in an outage.
>
> **Notes:**
> - Zone analysis method: hourly `aggregateWindow` of `environment.inside.thermostat.<ZONE>.{statenum,coolset,temperature}`
>   over a month, duty = clip(−statenum, 0, 1); `coolset`/`heatset` are stored in °F, `temperature` in K.
>   One-minute "breaks" in a long call are missing RedLink samples (humidity absent the same minute).
>   pandas lives in `~/pivac-venv` on the Mini (system python3 has none).
> - Grafana math has no max/min across queries: pairwise `abs()` ORs. Per-rule `notification_settings`
>   accepts `repeat_interval`. Prove a rule can fire by lowering the threshold on the Pi's /etc copy,
>   restart, read state from `/api/prometheus/grafana/api/v1/rules`, then restore from the repo copy.
> - Prestige install guide: Resideo 69-2490 (lists each ISU once; per-stage fields appear on the screen).
> - Session 65 notes still apply: Emporia backfill script; one measurement per `influx query --raw`;
>   782 sockets (9–12 commons, 5–8 NO, 1–4 NC, 13/14 coil; pole 1 spare NO shares the Chiltrix common);
>   Prestige installer path; RedLink `fan` statenum 0.5; alert YAML test recipe; PivacR uid
>   `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

