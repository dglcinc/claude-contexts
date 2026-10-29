> ### ▶ ACTIVE HANDOFF — Shield rev A powered and both inputs working; P1 seen at 6 s sampling; 2026-10-28, M4
>
> Session 88 (2026-10-27/28, M4). Air-handler shield rev A bring-up: U2 overheated and held the rail at
> 1.72 V because an ICM7555 from the Carlson parts sat in its place; the DS2482 is on and the board powers
> properly. W2 failed with one end of LED3 unsoldered (current only through D4, half the cycle); reflowed,
> W2 matches Y2. Build is U2 fitted, R15 off, JP1 open, LED1/R16 off (build sheet on #242). Wrote
> `OneWireBus.h` (DS2482 with D2 fallback) and ported AirHandler and AirHandlerBench (Arduino #14,
> compiled, not on hardware; `SHIELD_PCB` puts return air on A0). The faster Chiltrix sampling caught a P1:
> `raw.r284` = 2 at 02:47:51 EDT 10-28 for ~15 s, heating at 40 Hz, 54 °C leaving, 45 °F outdoors.
>
> **Next:**
> 1. Fit the shield headers, flash AirHandlerBench; expect `1-Wire master: DS2482 at 0x18`, ROMs `CRC ok`.
> 2. Order the TB1 plug (Phoenix MC 1,5/4, 1803594); 0805 LED kit ordered (Amazon B09Y1K1MFD).
> 3. Chiltrix P1: hold the 50 °C target until days in the low 30s / high 20s, then read every r284 ≠ 0
>    event and the 30 °F boiler cutover and recommend; no email wanted. Sooner if trips get frequent.
> 4. After a DHW call, confirm the Sentry's hundreds `1` and lit `burnerOn`/`circAuxOn`.
> 5. Flash UnicoSCBBench on the Feather; thermostats to Heat; Pico WH carrier.
> 6. Carried: spare Pi; sentry offline registration; rev C §9; backup board set; palace redaction.
>
> **Notes:**
> - Shield AC side is measured against COM (TB1 pad 3), never J1 GND; the Traco isolates them.
> - Test LEDs loose: LED1 fails the diode test in circuit through R16 and the rail.
> - r284 now samples every ~6 s, so P1 trips of 10–30 s show; the panel log still names the code.

> ### ▶ ACTIVE HANDOFF — Sentry recalibrated after the camera move; #256 merged; 2026-10-25 night, M4
>
> Session 87 (2026-10-25, M4). David moved the Sentry camera; the view shifted 6 px left and 22 px down,
> past the tracker's 15 px, so `waterTemp`/`outdoorTemp` went stale from 22:39 EDT at margin 12. Lens
> centroids from a 450-frame Mac capture fit the 10-24 spots by homography (≤1.2 px); the mapped quad,
> searched, read 100 % clean at margin 62 (61–64 on every ±1 px), water 88, air 57 (RedLink 49 + the 8 °F
> night offset), gas 0. Live config: corners TL(913,455) TR(1045,457) BR(1038,525) BL(905,521), LEDs
> (1073,453) (1073,479) (1074,505) (1073,529), indicators (910,541) (954,541) (997,544) (1041,544); backup
> `/etc/pivac/config.yml.bak-20261025-remount`. Live: margin 60, misses 0, tracker 0.947. CLAUDE.md on
> master (2bff806); notes in #256 (merged, 79fd0d1).
>
> **Next:**
> 1. After the first DHW call, check the Sentry for a hundreds `1` and lit `burnerOn`/`circAuxOn`
>    (`journalctl -u pivac-sentry | grep "nothing decoded\|lit-threshold"`); neither was in the capture.
> 2. Flash UnicoSCBBench on the Feather, plug it into the utility control box; expect a frame every ~850 ms.
> 3. Thermostats to Heat (MASTER_BR cools at 75 °F afternoons, KIDS_ROOM at 75 °F nights: ~2 changeovers
>    a day), or raise their cool setpoints.
> 4. Pico WH on the breadboard, then the carrier (session 84 steps 2–3 in archive/handoffs.md).
> 5. Read P1/P4 from the panel log, never `284` alone; keep watching `ah.utility.call.y2`.
> 6. Carried: cold nights at 30 °F; spare Pi; sentry offline registration; rev C §9; backup board set;
>    palace redaction.
>
> **Notes:**
> - The Mac's `~/pivac-venv` has OpenCV 5.0 (the Pi stays on 4.13); the warp search runs there with
>   `--config` pointing at a private copy of the live config. Delete that copy afterwards: it holds credentials.
> - Panel photos are in the Photos library originals (`~/Pictures/Photos Library.photoslibrary/originals/`, HEIC).
> - arduino-cli on the M4 has the rp2040 core and the `Pico PIO USB` library.

> ### ▶ ACTIVE HANDOFF — Loop B stays on HIGH; P1 3 in 119 at 48 °C; Feather SCB sketch written; 2026-10-25, M4
>
> Session 86 (2026-10-25, M4). Merged #254 and #255; the Pi pulled master and `pivac-scb-utility` runs at
> `daemon_sleep` 5. At the angled mount the Sentry `burnerOn`/`circAuxOn` followed `DHW` minute for minute
> through both overnight DHW calls. Loop B on HIGH measured 6.0 °F ΔT calling alone and 5.2 °F with both loops
> (8.4/7.2 on LOW), supply 0.45 °F under `IN`, so HIGH stays. The panel ERROR log photographed 08:20 holds
> P1s at 10-21 01:12, 10-21 23:41 and 10-24 22:37 plus the known 10-24 07:27 P4: 3 P1s in 119 heating starts
> (about 2.5 %, 4 % at 50 °C); `284` missed the 23:41 one. CLAUDE.md on master (77f1273, 640d382). Wrote
> `UnicoSCBBench` for the Feather RP2040 USB Host (Arduino PR #13): listen-only at 4800, ports of
> `split_frames`/`decode_status`, compiles, host test matches Python; not yet on hardware. The SCB shows one
> call since install (Y1+G, 10-24 18:03–18:07) and no y2.
>
> **Next:**
> 1. Flash UnicoSCBBench on the Feather, plug it into the utility control box; expect a frame every ~850 ms.
> 2. Thermostats to Heat (MASTER_BR cools at 75 °F afternoons, KIDS_ROOM at 75 °F nights: ~2 changeovers
>    a day). On 10-21 23:50 a kids room cool call chilled the tank to 54 °F and the great room fell 2 °F.
> 3. Pico WH on the breadboard, then the carrier (session 84 steps 2–3 in archive/handoffs.md).
> 4. Read P1/P4 from the panel log, never `284` alone; keep watching `ah.utility.call.y2`.
> 5. Carried: cold nights at 30 °F; spare Pi; sentry offline registration; rev C §9; backup board set;
>    palace redaction.
>
> **Notes:**
> - Panel photos are in the Photos library originals (`~/Pictures/Photos Library.photoslibrary/originals/`, HEIC).
> - arduino-cli on the M4 has the rp2040 core and the `Pico PIO USB` library.
> - The override has only been dry-run; guard word CALL-THE-PLANT.

> ### ▶ ACTIVE HANDOFF — Sentry at an angled IR mount; SCB at 5 s; 2026-10-24 evening, M4
>
> Session 85 (2026-10-24, M4). The Sentry camera went through three remounts after the shop lights went
> off at 19:40. The 10-diopter close-up bloomed in colour in the dark (97 read as 88, a false call with
> every light on); the 4-diopter face-on view reflected the camera's own infrared from every segment; the
> angled view reads in infrared (Night, Night Boost off) at margin 52–56 dark and 87–91 lit, tracker 0.82
> or better, no misses through the light changes. Live config: corners TL(911,434) TR(1051,435)
> BR(1048,501) BL(915,498), lens radii 4/25, `led_ratio` 1.05, `indicator_ratio` 1.15; backups
> `/etc/pivac/config.yml.bak-20261024-near` and `-skew`. CLAUDE.md rule on master, notes in PR #255.
> `pivac-scb-utility` dropped to `daemon_sleep: 5` live (it wrote ~1.4 M points/day at 1 s); PR #254
> also drains the serial buffer fully. The SCB had caught one Y1+G call (18:02–18:10, 300 CFM, 1078 rpm).
>
> **Next:**
> 1. Confirm the lit status-LED ratio on the next boiler or DHW call (dark 0.55–0.70 against 1.05);
>    check `burnerOn`/`circAuxOn` follow `BLR`/`DHW`.
> 2. Merge #254 and #255; pull on the Pi (it runs master).
> 3. Feather RP2040 USB Host bench sketch for the SCB (session 84 next steps 1–4 stand).
> 4. Watch `ah.utility.call.y2`; P1/P4 count at 48 °C; loop B HIGH review.
> 5. Carried: thermostats to Heat; cold nights at 30 °F; spare Pi; sentry offline registration; rev C §9;
>    backup board set; palace redaction.
>
> **Notes:**
> - The Tapo app shows no "Infrared" option; Night is the IR mode, and Auto drops to IR once the room is dark.
> - The 10-24 P4 (07:27 panel clock, ~07:30 Modbus) is written up in #253; no action.
> - The override has only been dry-run; guard word CALL-THE-PLANT.

> ### ▶ ACTIVE HANDOFF — Unico SCB proven, utility air handler publishing, rev B is a Pico carrier; 2026-10-24, M2
>
> Session 84 (2026-10-24, M2). The Unico SCB live test passed on the utility zone's M2430 (fw 3.21): the SCB
> sends a 36-byte frame every 0.85 s unanswered and the 51-byte frame only after a reply, the idle frame writes
> nothing, a set stores in under a second, no echo. `pivac.UnicoSCB` (protocol core `pivac/unico_scb_protocol.py`)
> runs on the Pi as `pivac-scb-utility.service` over USB (`/dev/serial/by-id/*unicousb*`) and publishes
> `environment.inside.hvac.ah.utility.{call.*,fan.airflow,fan.rpm,fan.stored.*,scb.*}` since 18:03 EDT. The tool
> has idle, backup, restore, override (a real zone call here: the SCB's relays are the HZ-432's W/Y) and the
> Air Cycle settings behind a typed guard. Merged #251, #252; #253 writes up the 10-24 P4 (not visible in `284`).
> Rev B: the UNO R4 cannot host USB, so the node becomes a Pico WH carrier plugged into the SCB's USB-B jack,
> in a CamdenBoss CNMB/6/KIT DIN module (PCB 86.5 × 103 mm), Würth 4065B push-in 5.08 mm blocks behind the
> guards, power and USB on the top face, sensors on the bottom (shield plan #242 §0). David ordered from
> Digi-Key: Feather RP2040 USB Host 5723 (the bench test), Pico WH, CNMB/6/KIT, 2× TMR 3-4811WI, 4× 2P and
> 3× 3P blocks, 2× USB-A jack 61400416021, 3× 20-pin sockets. HZ-432 relay bank is on the backlog.
>
> **Next:**
> 1. Feather: bench sketch (TinyUSB `serial_host_bridge` at 4800 + the frame decoder in C), plug into the
>    utility control box; decoded frames prove the route.
> 2. Pico WH on the breadboard: WiFi, DS2482/1-wire, NTCs at 3.3 V, HTTP line with the §7 fields.
> 3. Draw the carrier for the CNMB/6 base, review doc, OSH Park; chip parts from the rev A spares.
> 4. Pre-drilled guards (CNMB/3/TG508 ×4, TGUSB) from Newark if wanted; the kit's perforated ones serve.
> 5. Watch `ah.utility.call.y2`; P1/P4 count at 48 °C; loop B HIGH review.
> 6. Carried: thermostats to Heat; cold nights at 30 °F; spare Pi; sentry offline registration; rev C §9;
>    backup board set; palace redaction.
>
> **Notes:**
> - The override has only been dry-run; guard word CALL-THE-PLANT.
> - The DS2482 line added to the cart by mistake may be on the order; check the invoice.
> - Digi-Key and Amazon refuse the fetch agent; parts checks go through the Chrome extension.

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

