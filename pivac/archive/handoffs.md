> ### ▶ ACTIVE HANDOFF — Unico SCB serial live test, staged for the M2; 2026-10-24
>
> Goal: read and set the master bedroom Unico S.M.A.R.T. Control Board (SCB) ourselves, in place of
> Unico's Windows ECMConfig, then put the same serial tap on the air-handler node's rev B board.
> Everything is on pivac branch `feat/unico-scb-serial`, PR #251 (not merged):
> `docs/unico-scb-protocol.md` (the protocol from the decompiled ECMConfig 4.6, with harness pin maps),
> `scripts/unico-scb.py` (listen / decode / mirror / set), `tests/test_unico_scb.py` (14 checks, all
> pass) and `docs/unico-scb-live-test.md`, the procedure to follow. In short: 4800 8N1 through the
> A01470 USB board's FTDI chip (`/dev/cu.usbserial-*` on macOS, no driver needed). The SCB is bus
> master, sends a 51-byte `01 83` status frame unprompted, and treats every PC answer as a write, so
> stage 1 listens only, stage 2 answers with exactly the stored values, and stage 3 changes the fan-only
> (`G`) airflow by 25 CFM and restores it, each stage only after David's go-ahead. Never send the
> thermostat override bits or the test bytes. Run the tool as
> `uv run --no-project --with pyserial python scripts/unico-scb.py listen -v --raw scb-raw.txt`.
>
> Decided: the node keeps the UNO R4 WiFi (2.4 GHz accepted); rev B is the rev A shield PCB
> (`hardware/ah-board`, PR #242) plus an interface from the SCB data line to the UNO's `Serial1`. The
> live test must measure the data wires' levels (meter common on the data cable's black wire, then on
> the SCB's `C`) because the interface design waits on them. Data cable pins at the SCB header:
> 1 Blue, 2 Yellow, 3 Orange, 4 Black.
>
> Also open from the 2026-10-24 session (utilityserver Mac): the Sentry camera was recalibrated for
> David's closer mount (PR #252, lens radii 10/83, `led_ratio` 0.85, margin ~180); the Pi runs
> `fix/sentry-new-mount` until #252 merges, then goes back to master. The MBR remote sensor removed the
> morning solar overshoot (stat held 75 °F with no high fan on 10-24, against 77 °F and 2–3.5 h of high
> fan on 10-21 to 10-23); write that into assessment §5.10 on PR #250 after checking the afternoon.
>

> ### ▶ ACTIVE HANDOFF — MBR node installed and live; 2026-10-21, M2
>
> Session 83 (2026-10-20, M2). Bath calibration of the master bedroom air-handler node on the bench, then
> its install and deployment the same evening. The water pair is PA5 (PA5A `000000cb6e28` supply pipe,
> PA5B `0000001a8cda` return), three-point since today: offsets +0.280/+0.186 K at 55 °F (deployed) and
> +0.143/+0.295 K at 115 °F. The NTCs run `NTC_BETA` 3995 with `asup` −0.25 K and `aret` +0.03 K; A0 is
> supply air, A1 return air. David installed the node and `pivac-ah-mbr` went live at 23:34 EDT: all seven
> `environment.inside.hvac.ah.mbr.*` paths publish at a 5 s poll and reach InfluxDB,
> `ah-mbr-air-return-stale` is unpaused, and `LoopDelta` publishes `ah.mbr.water.deltaT` and
> `ah.mbr.air.deltaT` gated on `HPCALL` narrowed to `MASTER_BR` (return minus supply, negative in
> heating). Merged: pivac #240, #245, #246, #247. The node's first readings exposed a loose R and C pair in
> the master bedroom's RedLink EIM (the thermostat reported a heat call the HZ-432 never saw for 17 min);
> seated, the coil went 82 to 112 °F and the supply air 71 to 108 °F on the low fan, water ΔT about −3.1 K.
> Rule in CLAUDE.md under RedLink, timeline in `docs/operational-notes.md`. Arduino #12 merged too, so
> `AirHandler_MBR` on main is what the node runs. Plan §3.2 now asks for 20 AWG thermostat wire on its
> own run for the duct NTCs (#248, #249); Belden 8451 is only for a shared run, and the installed node is
> on it because it was on hand.
>
> **Next:**
> 1. Plan §6 steps 3–5: fan-on agreement of the pairs within 0.3 °F, sign check on the first cooling call
>    (`wret` above `wsup`, `asup` below `aret`), and Y2 within one poll on a high-fan call (this zone has no
>    W2, so Y2 is the only staged output; watch it on a call that runs long enough to stage).
> 2. Relay bank for the HZ-432 zone calls (David's wish, 2026-10-20): the rev C EXT has one spare input
>    (`SP-E`, J4.3), so five zones of W and Y need an MCP23017 on the DS2482's I2C bus behind 24 VAC
>    optocouplers or sense relays like SCALA's. It would also close the `LoopDelta` gap: a call that never
>    reaches the panel still opens the gate.
> 3. After a week with loop B on HIGH: great room alone was 7.8 °F ΔT on LOW, expect about 6.3;
>    LOOPB_SUP − IN −0.45 °F on LOW, −2 °F with both loops calling means MEDIUM.
> 4. From the Mini's session 83 (archived): watch the P1 count and `chiltrix-fault-latched` for a week or
>    two at the 48 °C heating target; loop at 19.4 psi chilled, back at the fill, optional regulator 2 psi
>    down, #236 to 19.3 on 17.0; outdoor coil after the first freezing night.
> 5. Carried: thermostats to Heat (David); cold nights at 30 °F; spare Pi model and MAC; sentry offline
>    registration; rev C §9; backup board set; palace redaction.
>
> **Notes:**
> - The node sends no sentinel: an unplugged sensor is simply absent from its line and its path goes stale.
> - Heating-season swap for the node: `wsup` +0.143, `wret` +0.295 K, with the loop probes' 140 °F values.
> - The node is not on the Arduinos Shelly; a `uptimeMs` reset with no WiFi message is a supply dropout.
> - Live config backup before the block was appended: `/etc/pivac/config.yml.bak-20261020` on the Pi.

> ### ▶ ACTIVE HANDOFF — P1 lockout; Devon's settings; 2026-10-20, Mini
>
> Session 83 (2026-10-20, Mac Mini; ran alongside the M2's session 82 below). The morning's low-flow alarm
> was a P1 lockout (`284` = 2, 08:30–09:42 EDT), not fouling; the strainer clean and breaker cycle at about
> 09:44 cleared it. #243 (pump-gated `.startupFlow`, `chiltrix-fault-latched` alert, P1 panel-log analysis)
> merged and deployed on the Pi. On Devon Powell's advice: heating target 48 °C (enter 119 °F), `P38` 15,
> `P39` 12, `P53` 50, set 12:23. Devon confirmed that a couple of P1s in a row lock the unit out until a
> power cycle (#244 merged).
>
> **Next:**
> 1. Watch P1 count and `chiltrix-fault-latched` for a week or two at 48 °C.
> 2. NTC calibration on the wired board: follow session 82's plan (sous-vide at 95 and 130 °F, reference
>    `0516a36816ff`, archive). The Mini session suggested an ice point with the PA5 pair; use the PA5 pair
>    only once its ROMs are on the bus.
> 3. Loop at 19.4 psi chilled, back at the fill; optional regulator 2 psi down. #236 to 19.3 on 17.0.
> 4. Outdoor coil after the first freezing night; session 82's install steps and carried items (archive).
>
> **Notes:**
> - °F entries truncate to whole °C; `P72` caps heating at 50 °C.
> - The HZ-432 went to cooling at 10:00 as the day warmed; tank chilled to about 50 °F.

> ### ▶ ACTIVE HANDOFF — MBR node bench-proven on WiFi at 10.0.0.180; NTC bath calibration pending; 2026-10-19, M2
>
> Session 82 (2026-10-18, M2). Bench-tested the master bedroom air-handler node (UNO R4 WiFi on the
> Olimex PROTO-SHIELD) with the Arduino #11 sketches, compiled on the M2 after installing Rosetta (the
> renesas core's compiler and bossac are x86_64). The shield is proved: spare DS18B20 `0516a36816ff` reads
> clean, both NTC dividers read 10.65 and 10.78 kΩ (74.4 and 74.0 °F against 72.05 °F on the probe), the
> Y2 input follows the relay (81 bounce edges on make, 3 on break). The node joins `redux` in about 2 s and
> answers at the UCG reservation 10.0.0.180 (MAC `e8:f6:0a:aa:a3:88`, client AirHandler-MBR). The 24 VAC
> converter is isolated and gives 4.65 V at the shield against 4.86 V from USB; David will install as is and
> watch `uptimeMs` for dropouts. Arduino #12 fixes a watchdog reboot loop (`WiFi.setHostname()` blocks past
> the 5 s WDT) and a −196.6 °F sentinel on a disconnected probe (double/float compare). pivac #240 adds
> `offset:` to ArduinoSensor with tests, `pivac-ah-mbr.service`, the backup lists, a paused
> `ah-mbr-air-return-stale` rule, the config sample block, and the bench record in plan §2/§4 and CLAUDE.md.
> The spare production Pi is recorded on master (81fba53).
>
> **Next:**
> 1. NTC two-point calibration in the sous-vide bath (plan §6 step 2); David will say when it is set up.
>    Suggested 95 and 130 °F with the bench 73 °F as a third point; reference is `0516a36816ff` on the bus
>    (`wsup` field while the ROMs are zero; subtract its +0.496 K); bundle both NTC tips against the probe
>    sheath, ten minutes per plateau. Same error at both points → `offset:` in config; a changing error →
>    adjust `NTC_BETA` in `AirHandler_MBR.ino` first. The CSV logger `airhandler-log.sh` in the M2 session
>    scratchpad polls .180 then .39 every 5 s into `airhandler-bench.csv`; restart one if it is gone.
> 2. PA5 pair on the bus: rescan (`AirHandlerBench`, 'r'), write the ROMs into `AirHandler_MBR.ino`, record
>    which probe is on which pipe (plan §3.1), split the pair offset into config.
> 3. Install: live `/etc/pivac/config.yml` block from the sample, copy and enable `pivac-ah-mbr.service`,
>    unpause the rule and verify in `alert_rule`; plan §6 steps 3–5.
> 4. David merges Arduino #12 and pivac #240 (#241, #236, #237 still open).
> 5. After a week with loop B on HIGH: great room alone was 7.8 °F ΔT on LOW, expect about 6.3;
>    LOOPB_SUP − IN −0.45 °F on LOW, −2 °F with both loops calling means MEDIUM.
> 6. Carried: thermostats to Heat (David); cold nights at 30 °F; spare Pi model and MAC for CLAUDE.md;
>    #236 pressure; handles; sentry offline registration; rev C §9; backup board set; palace redaction.
>
> **Notes:**
> - Homebrew `bossa` does not know the RA4M1 ("No device found"); use the core's bossac under Rosetta.
> - A faulted sensor is omitted from the node's line, so its path goes stale; no sentinels.
> - UCG fixed IP: scan `rest/user` fixed_ips and `stat/sta` leases for a free address first (.189 was taken).
> - The node is not on the Arduinos Shelly, so the watchdog cannot cycle it.
> - Y2 release is debounced 100 ms in the node sketch.

> ### ▶ ACTIVE HANDOFF — balance 30 °F; loop B HIGH; PR sweep; 2026-10-19, Mini
>
> Session 81 (2026-10-17 to 10-19, Mac Mini). HZ-432 balance point to 30 °F and loop B's pump to HIGH for
> heating, both in CLAUDE.md on master, the plan (#239, merged) and the assessment (#241, open). ST-25 DHW
> tank recorded at 60 psi precharge. Merged pivac #223, #234, #235 (DEHUM off the Relays panel) and #239,
> and Arduino #10 and #11 (bench and WiFi node sketches). Stale and merged branches deleted.
>
> **Next:**
> 1. Bench test the MBR shield on the M2, then WiFi on the transformer; UCG reservation and pivac config
>    with the board's IP (check #240, opened by another session).
> 2. After a week on HIGH: loop B ΔT great room alone 7.8 °F on LOW, expect about 6.3; LOOPB_SUP − IN
>    −0.45 °F on LOW, −2 °F with both loops calling means MEDIUM.
> 3. Cold nights at 30 °F: back to 35 °F above 95 % hourly duty or a 1 °F overnight droop.
> 4. Thermostats to Heat (David). #236 to 19.3 on 17.0 after the hot peak; #237 and handles.
>
> **Notes:**
> - LOW baseline: great room 65 % duty on a 38 °F night, held 72 °F; no boiler calls all week.
> - `r216` is not the defrost register. SSH to GitHub timed out on 10-18; `gh api` worked.

