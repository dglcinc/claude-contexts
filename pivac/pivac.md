# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — the flow decline may be the controller, not the plumbing (2026-08-28)
>
> **Nothing is pending on the machine.** `pivac-chiltrix` replaced `chiltrix-logger` and is writing
> **all 45 Chiltrix registers** to Signal K and InfluxDB under `hvac.chiller.chiltrix.*` every 30 s.
> The next physical work is David's strainer cleanout, and the record now spans it at full width.
>
> **⚠️ I read a 60% flow decline at matched compressor speed as a re-fouling strainer. David's
> counter — the controller adaptively re-trimming its pump — is currently better supported, and the
> question is open.** Three things favour it. The evaporator ΔT moved from 5–6 °F, *below* the
> Chiltrix 9 °F design value, to 9.5 °F, which is a controller converging on design. **The chiller
> modulates both pump and compressor off inlet water temperature**, so flow is a controlled output
> rather than an independent measurement. And the arithmetic runs backwards: **commissioning was
> 2026-08-04** and the first blockage 2026-08-22, **18 days**, against a claimed **6** for the
> second — on a loop that had just had its worst debris removed, where a fresh loop should foul
> fastest.
>
> **Both discriminating tests failed on instrument resolution; do not repeat them.** Register 256
> quantizes to 0.1 A (24 W) against a 22–200 W pump draw. Emporia's 60 s poll cannot isolate a
> ~70 s pump-only window inside a longer compressor-off period — several windows showing 45 L/min
> returned 9–10 W, the controls-only standby figure, impossible with the pump running. **Registers
> 248 and 260 are the candidate pump speeds**, and the cleanout is the physical test.
>
> **Two more fouling signals died this session.** `281` vs `142` meaned over hours does not
> separate (6 h mean 48.6–49.9 °F across both periods). Nor does end-of-cycle inlet — through a
> 354-minute run the unit still reached its normal 44.6 °F stop point. **Run duration separates
> where inlet temperature does not.** The one comparable flow measurement is the **startup
> plateau**: a flat 52.9 L/min from ~70 s before the compressor engages to ~140 s into the run,
> which David identified from the power profile. Published as `.startupFlow`.
>
> **⚠️ Two analysis traps.** Parsing a Modbus `TMO` as `0` made `hz or 0` read as compressor-off,
> splitting one 354-minute run into three fake "degraded cycles" — drop `TMO` rows before any
> state-machine analysis. And "pump-only flow reads hydraulic resistance" was an assumption, never
> a measurement.
>
> **The RPI-BC I/O board design is merged (#123) and parts-complete with no Digi-Key or Mouser
> order.** Three design assumptions died against the real panel: the 24 V is **AC**, the field wire
> count is **unchanged** (resistor and LED are board-mounted), and the commons converge **on the
> board**. Build values: 12 V wall wart measuring **14.7 V**, **4.7 kΩ** chosen to span the 25.9 VAC
> upgrade, supply on **J4 position 1** so the housing never opens, and **no components at all on the
> Pi side**. §2's wetting-current argument was wrong — seven channels have run at 66 µA for a year
> — and what survives is galvanic isolation.
>
> **The `chiltrix.yaml` alert rules are in the repo but deliberately NOT deployed.** They reference
> `pumpOnlyFlow`, which the module does not publish, and their thresholds come from a five-day-old
> screen. Rewrite against `startupFlow` after the cleanout.

*Updated 2026-08-28 (session 47 — the flow signal may be measuring the control loop; all 45
registers now recorded; the I/O board design finished against the real panel)*

> ### The fouling signal is not flow; the logger is fixed and collecting (2026-08-27)
>
> **Nothing is pending on the machine.** `chiltrix-logger.service` is running on the Pi and now
> actually writing. Read it with `python3 ~/chiltrix/tally_log.py [since_YYYY-MM-DD_HH:MM]`. The next
> physical work is David's CAT6 rewire.
>
> **⚠️ The recorded flow ÷ Hz candidate was wrong and is retired.** At a **constant 55 Hz** the flow
> ranged **42.5–52.9 L/min**, a 20% spread, giving flow ÷ Hz of **0.773–0.962**. Speed was pinned and
> flow moved anyway. Flow correlates **+0.96 with outlet temperature and −0.96 with ΔT**: the
> controller trims pump speed to hold an evaporator ΔT (`P53` floor 40%), with glycol viscosity
> pushing the same way as the water cools. The narrow 0.96–1.03 band came from reading only the
> ramp-down, where Hz and flow fell together; the ramp-*up* reaches **3.78**, because at 14–35 Hz the
> pump is already at full 52.9 while the compressor spools.
>
> **Build the alert on `281` vs `142` instead** — inlet water against the cooling target. A restricted
> chiller sits above its own return-water target, the documented signature of the August clog
> (52.4–54.4 °F against a 50 °F target for ten days). No flow scaling, no Hz gate, no ratio.
>
> **⚠️ The logger had run `active` for 18 hours having written ZERO rows**, with an empty journal.
> **Opening the port does not reset an UNO R4** — uptime survived repeated connects across 19.7 h — so
> a prior session had left the sketch in `watch`. A running watch consumes **exactly one character** to
> stop, so the service's `w 281 205 …` had its leading `w` eaten and the rest discarded. The read loop
> had no timeout and blocked forever. `logger.py` now quiesces the board to its prompt first and raises
> after 60 s of silence. **Any future serial client to this sketch needs both properties.**
>
> **The two WiFi pressure Arduinos come back to the Pi via the Modbus board's own ADC, not an
> ADS1115.** The R4's ADC reference is its own 5 V rail, so powering the transducers from that board
> keeps the measurement ratiometric and supply drift cancels in hardware — deleting the rail monitor,
> the dividers and the ratio arithmetic an ADS1115 needs purely to reconstruct it, and keeping the same
> conversion constants so **no scale step appears partway through the InfluxDB series**. This retires
> the `.61` Shelly, `arduino-watchdog.timer` and the `.219`-goes-dark failure mode outright; recovery
> becomes a USB reset instead of a mains cycle. **A serial port is exclusive, so it must be ONE pivac
> module and one service.** Keep the inverted `arduinoPSI` / `arduinoThermPSI` paths.
>
> **#121 stops being a blocker** — serial needs its own module regardless, and the DHW recirc probe
> moves to the 1-wire bus, leaving `ArduinoSensor` with no temperature consumers.
>
> **The CAT6 rewire has ~150 ft of spare capacitance budget**, so the outdoor probe goes back on and
> the lead-trimming task retires. **Do not share one cable between the 1-wire DQ and the pressure
> pairs.**

*Updated 2026-08-27 (session 46 — the flow ÷ Hz signal fell over, the logger had been silently dead
for 18 hours, and the pressure sensors get a route home that keeps them ratiometric)*

**The chiller answers.** `A3`/`B3` at 9600 8N1 slave 1, function 03, with no ground, no bias and no
terminator, because the chiller biases the pair itself at 3.18 V. Every documented register is now
confirmed against the unit rather than against a second document: 142 read 10 against the 50 °F
panel target, 202 read 23.9 °C against RedLink's outdoor sensor at 23.89 °C, 281 and 205 tracked
the controller's own displays to within 0.4 °F, and 227 and 256 fell to zero together when the
compressor stopped while inlet and outlet converged with the pump still running. The map predicts
the physics, which no document comparison can establish.

**Both scales the document leaves unstated are `÷10`, and both were measured.** Flow against the
panel's 1.8 gpm, current against Emporia's 2660.5 W. Raw flow would have published ten times high
and left the fouling alarm permanently unfireable, since 505 clears any threshold set against a
20 L/min trip.

**The link then lost two thirds of its frames the moment the compressor ran, and the cause was a
cable shield floating at both ends.** Grounding the drain at the Arduino end alone took running
loss from 65.3% to 0.0% across 635 reads at up to 55 Hz. Common mode was the wrong theory; the
controller's four-wire cable made the missing ground reference look like the difference. Two
methods carried the diagnosis: measuring under load rather than at idle, and printing `TMO` versus
`CRC` per failed read instead of a bare `--`.

**The alert signal is not raw flow.** Flow tracks compressor speed almost 1:1, so a fixed threshold
false-fires at part load on a clean strainer. `flow ÷ Hz` looks load-independent at 0.96–1.03 and a
logger is running on the Pi to confirm it over real cooling load.

*Updated 2026-08-26 (session 44 — Chiltrix's own Modbus document settles the register map; the
sketches are in version control for the first time)*

**Chiltrix's register map is now documented rather than guessed, and the guess was wrong.**
`cx34-123&cx50-2&cx35-1 Modbus User Document.docx` gives thirteen holding registers at 9600 8N1
slave 1, function 03. It **agrees with gonzojive (CX34) on all six addresses they share and
contradicts jasipsw (CX50-2) on all seven** — and jasipsw is what `ChiltrixModbus` was built on.
Six registers were wrong: 202 is ambient air rather than inlet water, outlet is 205, inlet is 281,
flow is 213 in L/min rather than 257 in tenths, and 256 is input AC current rather than power in
watts. The bridge would have published fresh, plausible, wrong numbers into Signal K, which is the
decoupled-DS18B20 and drifted-Sentry failure again.

**The addresses the document omits are dropped from the poll rather than kept on a guess** —
243/244 state and error, 258–260 speeds, 264 hours, 281 read as compressor starts. The scanner
keeps them as candidates. **The document has no fault-code register at all**, which is the gap
worth closing, and the only way to settle it is to read 243, 244 and 284 while the panel shows a
live P5 or E14.

**Two scales the document leaves unstated**, flow and current: it annotates "(to get C divide by
10)" on every temperature and says nothing on those two, so raw units are what it implies. Both sit
behind `FLOW_SCALE` and `CURRENT_SCALE` with the cross-check written down — `C13` in the pump-only
window for flow, the Emporia chiltrix circuit over 240 V for current. One digit off on flow turns
the strainer-fouling signal from useful into misleading.

**The three sketches are in `~/github/Arduino` for the first time** (PR #10), imported unchanged in
one commit so the corrections read as a diff in the next. They had lived only in
`~/OneDrive - DGLC/Claude/chiltrix-sketches/`, which is now a flash-convenience mirror with a README
pointing at the repo. **Nothing has been compiled or run** — there is no `arduino-cli` on the M4 —
so the checks are static only: delimiters, `snprintf` 18-for-18, payload 348 chars against a
640-byte buffer, and `%f` already proven in production by `ArduinoPSI_impl.h`.

**`pivac` PR #121 is now on the critical path.** `ArduinoSensor` rounds temperatures to whole
Kelvin, 1.8 °F, which is useless on a 4–5 °F evaporator ΔT — the same defect that made `IN − OUT`
meaningless before the 18 Aug precision fix.

**The `.114` DHW recirc firmware is not lost.** `ArduinoPSI_Domestic.ino` defines `ONE_WIRE_BUS 2`
on Arduino `main` and the shared impl header guards the DS18B20 code on it, so the Domestic build
emits `'temp'` and reflashing from the repo is safe. That retires a task carried since May and
corrects a warning in project `CLAUDE.md`.

**Both session-42 hardware faults are still open and untouched** — the two decoupled loop probes,
and the w1 bus going intermittent after the Pi-end connector was re-seated.

*Updated 2026-08-25 (session 43 — what the DS2482 migration is still worth now that the bus is
healthy)*

**The DS2482 is optional rather than indicated.** The bridge changes the master, and everything
downstream of its IO pin is the same copper with the same capacitance. What it buys is 1-Wire
timing generated in hardware instead of bit-banged through kernel interrupt jitter, plus an active
pull-up that drives the rising edge — which is what the 4.7 kΩ → 2.2 kΩ change already bought on
this bus.

**If it does go in, two things at the master end come out.** The **discrete pull-up**, because the
DS2482 supplies its own weak pull-up plus the active one and an external resistor fights it; and
the **driver-side 22–100 Ω series resistor**, whose whole job is softening a weakly driven edge and
which therefore works against the part's only contribution. Per-branch damping resistors at a hub
would survive a master swap untouched, since reflections are indifferent to what silicon drives the
line — but this bus is a chain and does not want them either way. Two wiring conditions carry over:
match the DQ rail to the sensors' **3.3 V**, which `w1-gpio` pinned for you and the bridge does
not, and flip `dtparam=i2c_arm=off` in `/boot/firmware/config.txt`.

**Master advanced four commits during this session**, so an answer read off the on-disk bus doc was
stale within the hour. Re-fetch before answering from a checkout on a long session.

*Updated 2026-08-25 (session 42 — all eight probes on the w1 bus; the 22 Aug collapse root-caused
to RC and fixed with a 2.2 kΩ pull-up; loop alerts live, panel 21 rebuilt as a ΔT panel)*

**The w1 bus carries all eight probes and the collapse is closed.** The fix was the pull-up, 4.7 kΩ
to 2.2 kΩ, and the cause was cable capacitance against pull-up strength rather than topology or a
bad probe. Measured: main loop **1.75 nF**, outdoor run **1.95 nF** bare. The inventory closes to
the digit — 45.5 ft of conductor at **112 pF/m** plus 200 pF of DS18B20 pins is the 1.75 nF read.

**The rise budget in the earlier analysis was the guaranteed worst case, not the operative one.**
A DS18B20 may sample a write slot anywhere from 15 to 60 µs after the falling edge and only the
15 µs end is promised; real parts sample near 30 µs, so the working budget is ~24 µs rather than 9.
Against 24 µs the history fits exactly: the configuration that ran for months needed 20.9 µs and
the one that died needed 24.3. Design to 9, expect failure near 24. David's objection that the old
four-sensor bus had included the outdoor run is what surfaced this — the arithmetic said it should
never have worked.

**Cable pairing is the variable, not category or gauge.** Jacketed 3-conductor puts DQ between VDD
and GND with both at AC ground, so it sees two grounded neighbours where a twisted pair gives it
one. That is 112 pF/m against ~50. CAT5e and CAT6 are identical here because `C = 1/(Z₀·v)` forces
both, so the old note calling thermostat wire an RC bargain was wrong.

**Topology was never the problem.** Three Phoenix ST 1,5/S QUATTRO headers distributed along the
run, trunk in and out, probes on spare terminals — a chain. So RC binds this bus rather than
reflection, and the 100 Ω damping resistors were never needed.

**Deployed:** #127 unpaused the four loop freshness rules (20 rules, 0 paused, verified in
`alert_rule`), and #128 rebuilt panel 21 as three ΔT lines — primary `OUT − IN` and `RET − SUP` per
loop, warm minus cold throughout, axis centred on zero and autoscaling so a winter inversion or a
backwards pair stays visible. All eight offsets verified *applied*, each within one LSB. **#126 is
open** with the doc corrections plus a health-measurement section and the planned end state.

**⚠️ Two open hardware issues at hand-off.** First, **two loop probes are reading room air**:
`LOOPA_SUP` (`1ac0a9`, PA2A) and `LOOPB_RET` (`c99b56`, PA1B) sit at ~64 °F with 1.5 °F of swing
while the good probes swing 7–11 and track `IN`/`OUT` at 0.98. One supply and one return, one per
loop, so both loops are genuinely flowing. They worked correctly for 2.5 h after install and both
broke in the same 30-minute bucket at 01:00 EDT, during normal operation, while David was fastening
wire bundles to the wall — a cable tug sliding the tube out from under its worm clamp, invisible
under intact insulation. Chips, wiring, mounting quality and stagnation are all ruled out with
reasons; the fix is unmount, ice-test, re-seat, and strain-relieve at the probe.

Second, **the bus went intermittent after the cable was re-seated at the Pi** — a complete 6-minute
blackout of all eight sensors at 12:55–13:00 UTC on 25 Aug, self-recovered by the per-cycle rescan.
New since the previous night's 40/40 clean sweep. Re-seat the connector properly. It exposed two
monitoring holes: the freshness rules are 30-minute so a 6-minute outage never alerts, and
`pivac-1wire` logged no state change, leaving the InfluxDB gap as the only trace.

**Free headroom remains:** the eight untrimmed 2 ft leads are 16 ft of the 45.5 ft total, so
trimming plus de-slacking cuts ~37% and is most of what puts the outdoor probe back on this bus.
Backlogged by choice; the bus runs with margin as it stands (320 reads, 0 CRC failures, 40 of 40
clean ROM searches).

*Updated 2026-08-24 (session 41 — IN and OUT moved to calibrated probes; #122 merged, so ice-point
offsets are live on every 1-wire sensor on the Pi bus)*

**Every DS18B20 on the Pi's w1 bus is now a bench-calibrated PA-batch probe with its ice-point
offset applied.** The two primary-loop sensors bracketing the closely spaced tees were replaced on
the pipe with **PA4A → IN** (`28-000000c98b14`, +0.468 K) and **PA4B → OUT** (`28-0000001aa0a8`,
+0.143 K); UBT and LBT have been PA3A/PA3B since 22 Aug. The probes they replace, `0516a36332ff`
and `0516a365d8ff`, are off the bus. **PA5 is the only spare pair left**, which is what the outdoor
ambient restore now has to draw on.

**A probe swap fails silently in a way worth recognising.** Until the config was edited, `IN` and
`OUT` sat frozen in Signal K at their last values while the two new probes published under their
raw ROM IDs — the service was `active`, the journal clean, and the dashboards showed flat lines
rather than gaps. The recipe is unchanged: **config edit → `restart pivac-1wire` → `restart
signalk`**, the second restart being what drops the raw-ID paths.

**Check the sign after swapping a pair.** `IN − OUT` is the whole-system capacity measurement, and
a reversed pair inverts it without ever going stale. InfluxDB showed OUT running ~5 °F warmer than
IN across 21–23 Aug and it read 6.3 °F warmer straight after the swap, which is what ruled that out.

**PR #122 is merged (`7978d70`) and deployed**, so `offset` is live rather than inert. Verified on
the Pi by reading `/sys` and the Signal K value **in the same command** — sampled seconds apart,
loop drift swamps the correction and every sensor looks wrong by a common term. Agreement is within
one DS18B20 LSB (0.0625 °C) because the two are separate conversions. `sensor-freshness.yaml` is
deployed: **20 rules, the four loop rules paused as designed, no orphans**, so the `deleteRules:`
block is doing its job.

**Two limits on the calibration.** It is **single-point at the ice bath** while the loop runs near
45 °F, so slope is unverified. And **the DHW recirc probe is not calibrated at all** — it hangs off
the Arduino at `.114` and reaches Signal K through `pivac.ArduinoSensor`, which has no `offset`
support; the key exists only in `OneWireTherm`. Activating the offsets also puts a **+0.325 K
(+0.585 °F) step in `IN − OUT`** at 23 Aug, on top of the 18 Aug precision change.

*Updated 2026-08-23 (session 40 — the Modbus link's Arduino end proven good; the strainer cleaning
reviewed against InfluxDB and it qualifies #117's central finding)*

**The clogged Y-strainer sat underneath the water-temperature comparison, and cleaning it recovered
part of the gap on its own.** Matched 09:00–17:45 windows at the 50 °F target: pre-clean (12–20 Aug)
return water held **52.4–54.4 °F, mean 53.3**, with running power averaging **1593 W**; post-clean
(23 Aug) return water was **51.9 °F** on **1423 W** at a 75.4 °F outdoor average — the lowest of any
day in the window, on an above-median day. Runtime does not explain it, since 19 Aug ran longest
(513 min) and still returned warmer water than 23 Aug did at 446 min.

**A chiller meeting its load sits at target; this one ran 2.4–4.4 °F above it every afternoon.**
That is what restricted evaporator flow produces, so **part of the 6–8 °F gap #117 attributes to the
setpoint is the chiller failing to hold the setpoint it already had.** #117 now carries §6.4 saying
so, and **§7's target walk-down is gated on two weeks of clean-flow data at 50 °F.** The E14 lockout
reads differently too: low flow widens the evaporator ΔT onto the `P59` trip, so the restriction
likely contributed to the 21 Aug trip at 46 °F.

**Zone comfort shows no change yet, and the perception should not be trusted over the data.** All
three chiller zones sat on setpoint on 23 Aug as they did on 19–20 Aug; chiller-zone humidity against
the DX kitchen and great room as a control sits inside the pre-clean spread. Caveats: one post-clean
day, the tank probes were swapped 22 Aug, and zone temperatures before 18 Aug are truncated to whole
Kelvin.

**`C13` is the cheap recurring check** — read it in the 1–2 minute pump-only window at the start of a
call (>54 L/min after cleaning, `P65` trips at 20). The scale comes from the boiler side of a shared
loop, so it will foul again.

*Updated 2026-08-23 (session 39 — the Sentry warp drifted again and was recalibrated; the RPI-BC
relay-input rebuild designed; the 1-wire bus-topology doc written)*

**The `sentry-outdoor-divergence` alert was correct, and silencing it would have hidden a dead
reader.** The `display_warp` quad had drifted 4 px: **`water_temp` decoded 4.5 % clean (6/133) and
`air` nothing at all (0/153)**, while live `outdoorTemp` read 88–96 °F against RedLink's 68.
`gas_input` still read 155/155 because the idle-fill emits 0 regardless, which is exactly why the
service looked healthy from outside. New corners `TL(1150,649) TR(1318,641) BR(1307,717)
BL(1142,728)` give **99.8 % clean over 441 frames** and zero `nothing decoded` warnings.

**This drift recurs — twice in 26 days — and the camera mount is the fix.** Onset was ~Aug 21,
coinciding with the DS18B20 install and the Y-strainer work, so assume boiler-room work bumps the
camera and check the decode rate afterwards. Two techniques worth carrying: the `nothing decoded`
warning added after July **worked** (3,137 in three days dated the onset), and **day/night lock is
checkable with no Tapo credentials** — IR/Night is true greyscale, so colour-channel deltas of 0.00
rule out a mode flip. **PR #124** commits the tooling, which imports the module's own decode rather
than duplicating it, the flaw that left `scripts/sentry-calibrate.py` stale and misleading.

**The 1-wire hub is outside the enclosure.** The trunk leaves the extension board on one 3-position
header, so the enclosure side is already right and the branching happens at the first breakout —
inspect that node. The outdoor ambient run is a **second branch** and likely the longest cable, so
it dominates the RC budget; measure capacitance with it connected and restore that probe **last**.
`docs/ds18b20-bus-topology.md` (on #122) carries the daisy-chain rules, the verified DS2482
migration, and the fact that damping resistors work per branch and not on the trunk.

**PR #123** designs the RPI-BC relay inputs as **optoisolated** rather than resistor-conditioned —
GPIO 26 is already dead and no pull-up arrangement prevents that. 12 channels on four 4-position
PTSM connectors with a common each.

**Next:** bisect the w1 bus from PA1A; try the free fixes first (pull-up 2.2 kΩ, one 100 Ω at
GPIO 4 with the pull-up on the cable side); then order the DS2482s and LTV-847s.

*Updated 2026-08-22 (session 38 — the calibrated DS18B20s went on; the four loop probes took the
w1 bus down and came back off; PR #122 opened)*

**The buffer tank now carries bench-calibrated probes and the secondary loops do not, yet.** David
installed the PA1–PA5 set: **PA3A/PA3B replaced the two repurposed tank probes** (the former CRW and
outdoor AMB sensors, now decommissioned), and supply/return pairs went onto both secondary loops.
**Connecting the four loop probes took the whole bus down** — the kernel search enumerated 64
phantom devices and the count settled at **zero**, taking IN and OUT with it after six clean days.
They came back off for the night; the bus is stable at four.

**`w1_search: max_slave_count 64 reached` is an electrical fault, not 64 sensors.** The search walks
the ROM tree bit by bit, and on unreliable bit timing it takes both branches at every node until it
hits the ceiling. **Read the pin before assuming a short:** `raspi-gpio get 4` showed `level=1`, so
the line idled high and the pull-up was alive. Ranked causes when the device count doubles: one
4.7 kΩ pull-up no longer driving the added cable capacitance, star topology, or a probe with DQ and
VDD swapped. **The failure is silent in pivac** — the service stays `active` and logs only
`bus now has 0 sensor(s)`; the 30-minute freshness alerts are what reported it.

**PR #122** adds the `offset` key `OneWireTherm` never had, which is what made PR #120's calibration
unusable — a difference of a few degrees measured with probes that spread 1.4 °F. Stated in Kelvin,
with a dependency-free test asserting that correcting both ends of a pair moves the loop ΔT by the
pair's ice-point difference. Also a `Secondary Loop Supply / Return` panel and four loop freshness
alerts, **shipped paused** because an unpaused rule on a metric that has never existed emails on
every evaluation.

**Two naming traps worth carrying.** The probe pair numbers and the loop letters deliberately
differ: **pair PA1 serves loop B**, pair PA2 serves loop A. And **3A is upper, 3B is lower** on the
tank — they read within 0.11 °F, so the data cannot tell them apart.

**Next:** bisect the bus one probe at a time starting with PA1A (it logged `err=-5`); merge #122 and
pull on the Pi to activate the offsets; unpause the loop alerts once they publish.

*Updated 2026-08-22 (session 37 — the chiller's repeated P5 alarms traced to a clogged Y-strainer;
Modbus connection settled and a scanner sketch written; PR #121 opened)*

**The chiller was failing and it was a clogged strainer.** Repeated **P5 "indoor unit water flow
error"**, which is the **low-flow alarm**: `P65` sets the threshold at **20 L/min** on cx65/cx75,
`P64` selects the flow meter, and `C13` is the live readout. The Y-strainer came out **heavily
clogged with calcium-looking scale** migrating from the boiler side of the shared four-pipe loop.
**After cleaning, `C13` reads over 54 L/min.** The signature was unmistakable in InfluxDB: runtime
collapsed to **169 min against 626–1,012 min on each of the prior ten days**, the loop warmed from
~45 °F to **77 °F**, and only the chiller's zones drifted while the two DX zones held. Pressure held
21–23 psi throughout and the unit still made cold water when it ran, so capacity was fine and the
protection was stopping it. Margin is thin by design here — ~30,000 BTU/hr at the 9 °F design ΔT
needs ~25 L/min against a 20 L/min trip. **`C13` reads 0 at idle and that is normal**: the pump only
runs during a call, and the 1–2 minute pump-only window at the start of each run is when to read it.

**Do not raise the autofill to recover pressure.** On a glycol system the feed valve should stay
closed — an autofill carries in the calcium and oxygen that caused this, dilutes the glycol
silently, and hides leaks. Top up manually with premixed glycol to the usual 21–23 psi. The open
question is whether makeup water has been entering at all, and a week of the logged pressure trace
with the feed closed answers it.

**The Modbus feed is now unblocked.** The CX's BMS terminals are **`DA1` = A, `DA2` = B**, and
Chiltrix's own ProtoAir gateway guide gives **Modbus RTU 9600/N/8/1, Node-ID 1**. The chiller is a
**slave** on that port, so polling on demand works. **The two community register maps contradict
each other** — jasipsw (CX50-2) and gonzojive (CX34) disagree on nearly every address and neither
covers a CX75 — so §4.2 of the assessment now carries both plus the verification requirement. The
shortcut worth trying first: in the CX34 map **register 53 is `P53`**, so if parameter numbers are
register addresses the answer is exactly **40**.

**M2 task:** run `ChiltrixScan` (in `~/OneDrive - DGLC/Claude/chiltrix-sketches/`, compile-verified
for the UNO R4) — `d`, then `p`, then `k`. DFRobot **DFR0259** shield, both DIP switches **AUTO** and
**ON**. Cable has two conductors plus a drain outside the foil: **A and B only, drain at the chiller
end alone, nothing on the Arduino GND**. Then commit both sketches to `~/github/Arduino`, and
re-capture the .114 recirc sketch that still exists only on that machine.

**PR #121** fixes the last module emitting integer Kelvin (`ArduinoSensor`), which matters because
the Modbus inlet/outlet registers are 0.1 °C and the evaporator ΔT is the number that decides
whether `P59` needs touching. #117 remains **open and unmerged pending David's review**.

Four Chiltrix PDFs are now in `~/OneDrive - DGLC/Claude/HVAC Manuals/`. Chiltrix publishes no CX75
manual; the CX65 is the closest sibling.

*Updated 2026-08-22 (session 36 — bench-calibrated the ten DS18B20 secondary-loop probes end to end;
PR #120 open)*

Ten DS18B20 probes addressed, labelled **PA1A–PA5B**, ice-point calibrated, and cross-check verified
on the Mac (UNO R4 WiFi over USB, `arduino-cli`). Identified each by ice-water insertion, calibrated
against a Thermapen ONE in a circulating slush, then confirmed by pulling them out one at a time —
all ten removal IDs matched the insertion assignments. Record committed in **PR #120**
(`docs/ds18b20-PA1-5-calibration.md`): ROM/w1 map, offsets in °F and K, per-pair ΔT-zero corrections.
Pair A–B agreement reproducible to ~0.05 °F, absolute offsets to ±0.2 °F. Single-point (ice) only;
45 °F slope point deferred.

**Two things worth carrying forward.** The DS18B20 bus reads zero devices on a breadboard — diagnose
with a raw-OneWire sketch reporting the presence pulse and the pin's idle level (LOW idle = pull-up
not on the D2 node); a soldered/connector bus fixed it. And ice-bath calibration needs a *stable,
uniform* fixed point: loose probes and under-iced/stagnant baths gave 1.4–2.8 °F non-uniformity and
non-reproducible offsets (one run warmed 2.8 °F between captures while the Thermapen still read 32.0
— reference and probes in different water). A circulating chiller + packed crushed-ice slush, probes
bundled tips-together with the Thermapen co-located, gave a flat plateau (SD <0.06 °F) that
reproduced.

**On install:** verify each `28-…` under `/sys/bus/w1/devices/` on the Pi before trusting config,
apply offsets in **Kelvin** (pivac stores temps in K), mount on **copper at the tees, not PEX**.
`arduino-cli` lives on the Mac at `/opt/homebrew/bin` (renesas_uno + OneWire/DallasTemperature).

*Updated 2026-08-21 (session 35 — the colder-target experiment ran, worked, and locked the chiller
out on E14; root-caused to P59 and whole-°C setpoint rounding)*

**⚠️ Chiller incident, resolved.** David set P109 = 1 and dropped the return target to 46 °F at ~21:30
on 20 Aug. **E14 "System anti freeze level one twice" locked the chiller out at 19:01 on 21 Aug**, and
**the "Error reset" button did not clear it — a breaker power cycle was required.** Target is back at
**50 °F** and the chiller is running. **Cause: `P59` "AC anti-freezing temperature" defaults to 3 °C =
37.4 °F and watches *leaving* water**, and the unit runs ~9 °F below its *return* target, so the
lowest safe target is ~49 °F. **The controller also stores the target in whole °C**, so °F entries
land low — 50 °F = 10 °C exactly, but 48 °F = 8 °C = 46.4 °F, putting leaving water exactly on the
trip. **Set it in °C.** Order for any retry: **glycol → P59 → target**; P109 only opens the range.
`P53` (pump minimum 40 %) lets the ΔT widen at low demand, which is when it tripped. Recorded in
project `CLAUDE.md`.

**The experiment worked, which is the point.** The one usable afternoon: master-bedroom dew point
**56.5 → 54.7 °F while outdoor dew point ROSE** (73.3 vs 73.0/72.4), room temp pinned at 76.0 all
three days. And only part of the change landed — `IN` averaged 46.6 against a stored 44.6 target
because the protection clipped every cycle — so **1.2–3.6 °F of real water bought 1.7 °F of dew
point** and the full change has more to give. Kids zone: **read duty, not cycle count** — 48.8 % at
73.0 °F out → 40.5 % at 76.7 °F, but cycles got shorter and more numerous, which is arithmetic at
lower duty.

**No further target change until the Modbus feed can watch leaving water while it moves** (David's
decision). Registers 202/203 give the real part-load evaporator ΔT — the number that decides whether
P59 needs touching at all — and 257/260 show whether the pump drops to its P53 minimum at low demand.

Everything else from session 34 stands: the master-bedroom **Y2 goal** (Honeywell exposes no stage
data, verified against the raw payload, so Y2 needs a wire), the **old-UniChiller comparison** (loop
6–8 °F warmer at every matched outdoor band), and the **M2 bench task** —
`~/github/pivac/docs/ds18b20-provisioning.md` on branch `docs/unico-btu-monitoring-plan`, plus
re-capturing the .114 recirc sketch that exists only on that machine.

#117 remains **open and unmerged pending David's review**, now ~3,300 lines.


*Updated 2026-08-19 (session 34 — master-bedroom Y2 goal added to #117; the old UniChillers turn out
to be a controlled experiment and they indict the chilled-water temperature)*

**⚠️ If this session is on the M2 MacBook, the job is the DS18B20 bench work.** David has the four
secondary-loop probes and is addressing and calibrating them on an Arduino over USB. The procedure is
**`~/github/pivac/docs/ds18b20-provisioning.md`** on branch `docs/unico-btu-monitoring-plan` (pull it
first; it is not on master yet). It covers the enumeration sketch, tying each ROM to a physical probe
by hand-warming rather than by its printed tag, the CRC-8/Maxim check, the printed-ROM to w1-name
byte reversal, and two-point matched-pair calibration. **Fill in and commit the ROM map in §7 before
anything is installed.** Two probes go on Loop A supply/return and two on Loop B, mounted on copper
at the tees. While Arduino tooling is out on that machine, also **re-capture the .114 DHW board's
recirc-temperature sketch** — it exists only on the M2 and on the board, was never committed, and
reflashing that board from the repo would silently drop the recirc temperature.

**Plan David chose:** free and cheap steps first, **chiller setpoint deliberately deferred** to
collect more data. That is the right order — Y2 and the loop probes give a pre-change baseline that
would not exist if the setpoint moved first.

**The finding that reorders everything.** Two 5-ton Unico UniChillers ran the house until they failed
4 July, on/off, controlling **leaving** water at 38 °F with a 10 °F differential, so the loop
sawtoothed 38–48 °F. The same sensors logged them, which makes this a before/after on one house.
Binned by outdoor air, `IN` sampled only while the master bedroom called: the loop now runs **6–8 °F
warmer at every band**, the zone runs **46 % → 68 %** of the time in the 80–85 °F band, and it sits
**5–10 points wetter**. The new era is the *milder* of the two (90.1 °F peak vs 98.3 °F), and `IN`
barely moves with load in either era, so neither plant is capacity-bound — the gap is a setting.
Warmer water costs ~17 % of sensible capacity at every coil and lifts the coil outlet to the room dew
point, against a few per cent for the master coil's 74 %-of-design flow. **Water temperature is the
large term; distribution is the small one.**

**The remedy is one parameter, when he chooses to take it.** Chiltrix targets **return** water and
the fully mixed tank settles there. Set to **50 °F with a 2 °C restart hysteresis** (band 50–53.4),
and 50 °F is exactly the floor **P109=0** allows. **P109=1** opens the range to 41 °F, conditioned on
glycol not freezing at −10 °C — 25 % PG sits on that line, 30 % clears it, so the glycol top-up moves
off the heating-season list onto the critical path. A 42 °F target should put `IN` near 39–41 °F and
reproduce the old plant. Capacity falls with the target and the CX75 is 4.3 tons against the 5-ton
UniChiller, so step it and watch for `IN` rising above target.

**Y2 needs a wire; Honeywell has no stage data.** The Total Connect payload was read directly:
`EquipmentOutputStatus` is off/heat/cool only and `fanData` gives the user's fan mode. Y2 fraction
(stage-2 time over cooling-call time, denominator already logged as `statenum`) is a better metric
than droop, which reads a flat zero. Cheapest path is a 24 VAC relay on the spare pair to a free Pi
input under `pivac.GPIO`. **David's feedback-loop question is answered by the CX itself**: Dynamic
Humidity Control lowers the water target on room humidity (P114) or room temperature (P115) from one
indoor sensor, off from the factory — P115 covers what a Y2 feedback wire would carry, so Y2 stays a
measurement and pivac stays read-only.

Thermostat is a **THX9421R5021WW** (Prestige IAQ 2.0). Read **ISU 3010 first** — on Basic it hides
3020 (Finish With High Cool Stage), 3030 and 3140. Master fan mode is **circulate**, which re-wets
the room from a wet coil between calls. Appendices J and K of the assessment carry the ISU list and
the Chiltrix parameters.

#117 remains **open and unmerged pending David's review**, now ~3,160 lines.


*Updated 2026-08-18 (session 33 — #117 rewritten as an assessment with a verdict; hydraulics
settled from real topology, datasheets and live data)*

Master current, **#117 and #94 open**. **⚠️ #117 remains deliberately unmerged** — David reviews
first; do not duplicate its content into `CLAUDE.md` until it lands.

PR #117 is now an assessment rather than a build plan, renamed
`docs/unico-air-handler-btu-monitoring-plan.md` → **`docs/unico-cooling-assessment-and-tuning.md`**
(~2,460 lines, sections 1–9 + TOC, reference material in appendices A–I). Fifteen commits.

**Topology, David-confirmed.** Loop A = kids (M1218) → master (M2430, attic coil); Loop B = lower
family/utility (M2430) → kitchen (M3036) → great room (M3036). Kitchen and great room are **DX in
cooling** with hot-water hydronic modules for heat, so summer Loop A carries 2 chilled coils and
Loop B 1. **Four-pipe VCT37C tank** (37 gal = 304 BTU/°F, 8.6 gal/ton); chiller ↔ tank on the
CX75's **own modulating pump**; **the Taco 0015-MSF3-IFC is the DISTRIBUTION pump**, confirmed on
HIGH. Header 6 ft of 1½" copper; mains 1¼" PEX (ID ~1.07", frictions like 1" copper).

**The ΔT question is answered.** Primary flow is fixed at ~14.5 GPM, so `IN − OUT` reads house
load — 7.4 °F at the CX75's full rating, 4.3 °F at 2.5 tons. Measured 5.34 °F ≈ 3.1 tons on an
80 °F evening. **The 8–12 °F band arrives at design load and not before**, and chasing it means
cutting flow, which costs capacity and dehumidification.

**Every zone holds setpoint** (zero droop, chiller idle 54 %), so the measured shortfall is
humidity: 60 % MASTER_BR / 59 % KIDS_ROOM against 48.6 % in the DX kitchen. **The kids room is a
latent load, not a capacity shortfall** — laundry plus two full baths in a small space, highest
duty in the house (51.4 %) yet dead on setpoint. A *bigger* handler would be worse. Fixes are
lower CFM on that handler and bath/laundry exhaust.

**Pump settings from calculation** (Unico published coil ΔP + the UPS26-99FC curve): MEDIUM Loop A
(David set it), LOW Loop B summer, **HIGH Loop B winter** — LOW leaves the great room at 67 % of
design. **No pump purchase warranted**; primary and secondary are matched at 14.5–16.4 vs 15.8 GPM.

**Modbus register map found** ([jasipsw/homeassistant-chiltrix-modbus](https://github.com/jasipsw/homeassistant-chiltrix-modbus)):
203/202 water out/in, **257 flow**, 260 pump speed, 256 power, 281 compressor starts. **Register
257 means the flow meter stays off the list** — the tank decouples flow but conserves energy, so
`Q_house = Q_chiller − 304 × d(UBT)/dt` gives distribution flow to ±10 %. David is building the
feed this weekend.

**Next:** David reviews #117; Modbus feed; four DS18B20s on the secondary loops (**on the copper
at the tees, not the PEX**); kids-room CFM + exhaust; Loop B to HIGH before heating season with
the 25→30 % glycol top-up; restore leak detection (BCM 25 regression).


*Updated 2026-08-18 (session 32 — Grafana colour grouping; TWO temperature-precision bugs fixed; Unico/BOVA plan drafted and rewritten, #117 OPEN for review; global prose-style system added)*

Master current, Pi in sync, **#117 and #94 open**. **⚠️ #117 is deliberately unmerged — David
will review and suggest changes; do NOT duplicate its content into `CLAUDE.md` until it lands.**

**(1) Grafana colours** (#115/#116, deployed, verified in the `resource` table): House Power
regrouped by **load family** — blue for cooling (Chiltrix + both BOVAs), yellow for subpanels,
green for individual loads, grey catch-all, and `main` moved to **purple** so the unstacked
overlay cannot read as a fourth cooling series. Apartment Power matched. Explicit hex, because
adjacent Grafana named shades are not separable across ten bands.

**(2) Two temperature-precision bugs, both found mid-design and both fixed.**
`OneWireTherm` reads `Unit.KELVIN` for Signal K output and the live config held `rounding: 0`,
so every 1-wire temperature reached InfluxDB **quantised to 1.8 °F** (#118). `RedLink` was
worse: `int(ktemp)` at `RedLink.py:329` **truncated rather than rounded**, so every zone read up
to 1.8 °F cold, always downward, **biasing droop low** — and setpoints truncated the same way,
discarding Honeywell's half-degree steps (#119). Caught live: `MASTER_BR` stored 297 K (75.2 °F)
against `coolset` 76, reading as below setpoint when the true value was 76.0. Both merged,
deployed, verified; InfluxDB `_value` was already `double` in both cases so nothing orphaned.
**Not retroactive — quantitative ΔT and droop analysis starts 2026-08-18.**

**(3) The design plan** → `docs/unico-air-handler-btu-monitoring-plan.md` (1444 lines).
**David's objective: summer comfort + capacity for both the BOVAs and the Chiltrix; efficiency
secondary; heating monitor-only.** Architecture: boiler and chiller each carry **their own
primary pump** (boiler UP26-99F, chiller **Taco — model still pending**) into a header; two
secondary loops tap it via **closely spaced tees**, one UP26-99F each; **HZ-432 drives one zone
valve per zone, no dampers**; primary return goes to the boiler loop in heating and the buffer
tank in cooling, so **cooling is buffered and heating is not**. Taps: primaries **HIGH**,
secondaries **LOW**; **Loop B set LOW and must be raised before heating season** (1 zone summer
/ 3 winter), alongside the **25→30 % glycol** top-up (`fluid_k` ≈481→≈476). **Key structural
insight: `IN`/`OUT` bracket the tees**, so `IN−OUT` is whole-system capacity and, because tees
mix, **ΔT_primary/ΔT_secondary *is* GPM_secondary/GPM_primary** — the flow ratio from
thermometers alone, >1 being reverse mixing. Four DS18B20s + one *primary* flow meter therefore
beat a per-coil meter, and the Arduino node dropped to step 4.

**(4) BOVA findings, from the actual IOM** (text extracted locally with `pdftotext`). **`Y2`
appears zero times** — the outdoor block is `C Y B D/W` and the condenser takes one 24 V call,
staging internally. **But `Y2` drives the air handler's second-stage fan**, so a second-stage
call reaches the compressor *through airflow*. **David found the great room's setpoint loss: its
`Y2` fan wire had been disabled.** He reconnected it and raised base CFM, so **that complaint is
resolved** — but the zone now carries **three sensible-biased settings at once** (`Y2`, raised
CFM, `SW4-3` on), so **watch humidity there, not temperature**, and give `SW4-3` back first if
it reads clammy. Compressor speed modulates on evaporator pressure; SW4-3/SW4-4 are the only
adjustments and **both are already set**, so any remaining constraint is charge or airflow.
**Dynamic airflow is out** — the Smart Controller is USB-only and pauses on fan-speed change —
so **CFM is static and sets where the compressor operates**, reducing this to a two-setting
tuning exercise scored on droop and humidity.

**(5) A global prose-style system**, since David wants concise Strunk-and-White writing rather
than AI voice. A **19-bullet `### Prose style` section in `global.md`** plus a new **`/style`
skill** — both in this repo, so they reach every machine on pull (`~/.claude/CLAUDE.md` →
`global.md`, `~/.claude/skills` → `skills/`). Four rules merged from
[yzhao062/agent-style](https://github.com/yzhao062/agent-style). The whole plan was then
rewritten against them: bold spans **452 → 19**, em-dashes **237 → 3**, banned vocabulary
**60+ → 0**. That rewrite surfaced three real content errors, which argues for hand-rewriting
over word substitution.

**Next:** David reviews #117; run the zero-cost droop-vs-power-vs-humidity analysis (all three
cooling units are individually metered); two NTCs in whichever BOVA zone it identifies; four
DS18B20s on the secondary loops; **restore leak detection** (regression from the BCM 25
`SCALA`→`CHIL` rename); plus session-31 carryovers (channel 8 `dont_know` now reads 42.6 W;
verify House Power netting with the great-room BOVA running; #94; label the override relay).

*Updated 2026-08-13 (session 31 — Emporia CT rework end-to-end: two real module bugs fixed; Chiltrix idle misread diagnosed; chiller docs finished; HVAC manual v1.8 drafted)*

Master `11875a5`, Pi in sync, all services active, **only #94 open** (#95, #96, #99–#113 merged and
deployed). Three threads. **(1) Chiller documentation finished** — David corrected the physical
picture four times and the plan doc now reflects all of it: the BOS relays are a **parallel tap, not
a series element** (monitoring can't break cooling; no new conductors); **`CHIL` is the DEMAND side,
not the run command** — it means chilled water is being drawn from the buffer tank while the
Chiltrix starts its own compressor on an internal return-water thermostat, with a manual unlabeled
override relay able to run it with `CHIL` idle; **YOFF, YALT and CRWA are all decommissioned** so
winter shutdown is a **manual breaker-off** and the BCM 19 rewire is **cancelled** (it had been a
live "before heating season" item); and the **zone map** is Chiltrix→MBR/Dstrs-Fam/Kids,
BOS1→Kitchen, BOS2→Great Room. **(2) HVAC System Manual v1.8 drafted** (23 paragraphs text-only, all
38 images and the paragraph count preserved; figure-bearing sections left for David + new photos).
**(3) Emporia rework** after David re-arranged CTs — the substantive engineering. Two real bugs
fixed: **channel names were cached for the daemon's life**, so renames in the app never propagated —
and because the channel name *becomes the SK path*, it presents as a **stale sensor** rather than a
naming problem (now on an hourly TTL, keeps old names on API failure, logs renames); and
**`_sanitize` passed punctuation through**, where the latent case was a `.` silently nesting the SK
path an extra level. Diagnosed the **Chiltrix reading ~0 W idle**: 24h of InfluxDB showed 0 samples
≤0.5 W with min 1 W — the CT never truly read zero. **Single-CT-doubled is only valid for a balanced
240 V load**; the compressor is balanced but the pump/controls are 120 V on one leg, and the CT was
on the other. A merged pair now shows ~10 W idle. **Gotcha: reset the multiplier to 1.0 on a merged
pair.** House Power panel rebuilt: stacked, `main` excluded from the stack, `balance` plotted as
**"Everything else"** (without it the stack can't reach main), and the **great-room BOVA netted out
of the utility subpanel** since it's metered there. **Next:** identify channel 8 (`dont_know`,
~25 W); **verify the netting when the great-room BOVA actually runs** (0 W throughout, so untested);
merge #94 (expect a CLAUDE.md conflict like #96's); zone-by-zone BOS1/BOS2 test; label the override
relay; glycol 5.7 gal swap.

*Updated 2026-08-10 (session 30 — merged #99/#96/#95; chiller rework plan rewritten against reality; ≈86 gal loop volume + glycol; defect caught in #95)*

**⚠️ PICK UP HERE: master has undeployed changes.** The Pi is at `e6d0bf4`, master at `79afc21`
— PR **#95**'s `Sentry.py`, its service file (loglevel `ERROR`→`WARNING`) and a **new**
`sentry-boiler.yaml` alerting file are merged but **not on the Pi**. Merge **#100** first so the
fix ships in the same deploy, then pull + copy service + `daemon-reload` + `restart pivac-sentry`
+ copy alerting YAMLs (chown/chmod incl. `sentry-boiler`) + `restart grafana-server`, and
**verify the `alert_rule` table** (13 → 16) — provisioning is additive, so never trust the restart.

Merged **#99** (chiller rework plan + Phoenix Contact label docx — the branch had never been
pushed, so both were single-copy on the MacBook), **#96** (GPIO relay rename, repo catching up to
the live Pi config) and **#95** (Sentry calibration drift). Most of the session went into
rewriting `docs/cdp-chiller-rework-plan.md`, which described a scheme that was superseded before
it was built: shipped was `RCHL→BOS2` / `LCHL→BOS1` with **no CHIL Pi input**, not the planned
`RCHL→CHIL` / `LCHL→BOS2`. **David corrected three wiring assumptions in sequence**, each
invalidating more of the doc: (1) the BOS sense relays are a **parallel tap, not a series
element** — each air handler drives its compressor directly and its call relay separately
energizes the reclaimed CDP relay, so monitoring can't break cooling, there are **no new
conductors**, and the series records the *call* rather than proof the compressor ran; (2) the
**CHIL relay exists** (HZ432 Y → Chiltrix) and only its Pi input was dropped, with a **manual,
unlabeled override relay** bridging the same Y contacts because the Chiltrix maintains
buffer-tank temp on its **own internal return-water sensor**, independent of zone demand; (3)
**YOFF is retired entirely**, winter shutdown is now a **manual breaker-off**. That last one
killed the plan's highest-risk item and made several steps actively wrong to follow — and
**CLAUDE.md was carrying the BCM 19 rewire as a live "before heating season" deadline**, now
marked CANCELLED (`e2df235`). **Defect caught in #95 before deploying:**
`sentry-outdoor-divergence` queries `environment.outside.temperature`, retired on 08-06 when the
AMB probe became LBT — and with `noDataState: OK` it **fails quiet**, so it would have sat
provisioned and permanently silent while looking like coverage. **PR #100** repoints it at
RedLink (also Kelvin, so the K→°F math is unchanged). Also recorded **≈86 gal** post-conversion
loop volume (was 92) and the glycol move: **drain 5.7 gal, add 5.7 gal** of 100% inhibited PG to
go 25%→30%, which matters more now that the loop overwinters unpowered and static.
**Next:** merge #100 → deploy; merge #94 (expect a CLAUDE.md conflict like #96's); zone-by-zone
BOS1/BOS2 test (a crossed pair is invisible in config); label the override relay; glycol top-up.

*Updated 2026-08-06 (session 29 — CRW/AMB DS18B20s repurposed as buffer-tank UBT/LBT; outdoor 1-wire retired)*

David moved two DS18B20s onto the **buffer tank**: `0316a00f04ff` (was **CRW**) → **UBT** (upper)
and `0516a36816ff` (was the outdoor **AMB** probe) → **LBT** (lower). Bus is still 4 sensors —
IN, UBT, LBT, OUT. **There is no physical outdoor sensor any more:**
`environment.outside.temperature` is gone and outdoor air comes solely from RedLink's
`environment.outside.thermostat.temperature`. Shipped and deployed: pivac **#97** (config, alerts,
Grafana panel) + **#98**, and wilhelm-sk **#4/#5/#6** (3→4 HVAC gauges, iPhone column equalized,
iPad PSI stack equalized). All verified live — 13 services active, 0 WS re-logins; both `.wlyt`
files synced to OneDrive and **awaiting import on the devices** (the only step left).
**Diagnosis note:** David reported a "new" sensor, but its printed code decoded to the *existing*
AMB id — **the printed 8-byte ROM reverses its 6 serial bytes to form the w1 name**
(`28FF1668A316054F` → `28-0516a36816ff`). CRC-8 validation + 12 stable CRC-valid reads ruled out
a duplicate-address clone, and InfluxDB showed the outdoor path diverging 82→51 °F while the
thermostat held 80 °F.
**Two gotchas worth more than the work:** (1) **Grafana alert-rule provisioning is ADDITIVE** —
deleting a rule from the YAML does *not* remove it (it keeps evaluating with `provenance=file`,
uneditable in the UI). The table held 16 rules against a 7-rule YAML, and two dead
`noDataState: Alerting` rules would have emailed on every evaluation. A restart *looks* successful
because new rules do get created. Fix = a permanent top-level `deleteRules:` block; always verify
against the `alert_rule` table afterwards. (2) **`valueLabelPaddChars` centring trap** — a gauge
whose rendered string is shorter than the reservation gets padded and reads off-centre; do not
"fix" it by rounding sibling gauges, which spreads the problem.
**Next:** import the layouts; confirm UBT/LBT really are at different tank heights (both read
46.1 °F on install); merge #96/#95/#94; update `docs/cdp-chiller-rework-plan.md` + the label docx;
YOFF rewire before heating season.

*Updated 2026-08-02 (session 28 — GPIO relay roster reconfigured for the single-chiller conversion)*

Reconfigured the **relay array behind the WilhelmSK Control Relays tile** on both the iPad and
iPhone dashboards. Reclaimed **LCHL's pin (BCM 6) as `BOS1`** and **RCHL's (BCM 5) as `BOS2`** —
rename in place, no header wire moved — and dropped **Y2ON (13)**, **Y2FAN (16)** and the **old
BOS1 (24)**. Live `/etc/pivac/config.yml` updated + verified: Signal K returns exactly **7
relays** (ZV, DHW, BLR, BOS2, BOS1, DEHUM, SCALA), all 9 services active, WS re-logins 0/min.
**PR #96** carries `config.yml.sample`, the README example, both Grafana dashboards, a CLAUDE.md
note. **Two findings:** (1) **no `.wlyt` change is ever needed for a relay change** — both
SwitchBank widgets carry only `"path": "electrical.ac.switch.utility"` and enumerate children
dynamically, settling the session-27 "encoded SK paths" open question; (2) **retiring a relay
needs a `signalk` restart** — SK keeps a retired path frozen at its last value, so after
`restart pivac-gpio` alone the four dead names still sat in the API and would have shown on the
dashboards. Recipe: config edit → restart pivac-gpio → restart signalk. **Diverges from the
session-27 plan** (`RCHL→CHIL`, `LCHL→BOS2`): there is now **no CHIL relay** — deliberate, the
new chiller doesn't work in a way that gives it a call relay; the chiller's call state is
therefore unmonitored. **Next:** merge #96 → Pi pull; **update `docs/cdp-chiller-rework-plan.md`
+ the label docx** (both committed on `docs/rpi-relay-label`, no PR) since they still describe
the superseded scheme and would mislead the new-Pi build; merge #95/#94; YOFF rewire before
heating season.

*Updated 2026-07-23 (session 27 — CDP relay + RPi-label rework plan for the single-chiller conversion)*

Planning only, nothing built. David is decommissioning both old UniChillers for **one new chiller**
and adding a **BOS2** monitoring relay. Full plan: **`docs/cdp-chiller-rework-plan.md`** (branch
`docs/rpi-relay-label`). Key decisions: **CHIL** takes RCHL's pin (BCM 5/29, rename only — chiller
wire never moves); **BOS2** takes LCHL's pin (BCM 6/31, reclaim the LCHL relay *in place* and reuse
its existing contact wire); **YOFF** stays on BCM 26/37 (label typo "Y2OFF"→"YOFF"; new Pi silicon
fixes the old dead pad — ohm the wire to GND first); Y2ON/Y2FAN freed, **YALT relay removed**. Net:
9 active inputs, 3 spares, **zero header wires relocated**. Software: `pivac.GPIO` renames + delete
Y2ON/Y2FAN; fix `config.yml.sample`; rework `pivacr.json` + `chiller-time-r.json` Grafana panels.
**Highest risk:** YOFF's seasonal cutoff currently interrupts YALT — with YALT gone it must be
re-inserted into the new direct chiller call path or the winter cutoff fails **silently**; prove it
before closing the panel. Control-logic claims in plan §3 are inferences from HVAC Manual v1.7, not
live tracing — confirm at the panel. **Next:** David adds "other things" to the label docx → commit
+ open PR (base `master`) → build new Pi (capture eth0 MAC, DHCP-reserve to `.82`).

*Updated 2026-07-23 (session 26 — storm-drain clog-sensor spec + full Pi software update + fanless-Pi4 Sentry thermal retune)*

Two threads. **(1) New storm-drain clog-sensor node designed** (spec only): iterated live from
"contact sensor" → single binary threshold (clog is binary; standing water = the signal) →
**stainless M10 mini reed float in a 1½" PVC stilling well mounted to the 10×10" driveway grate**,
mounted **NC** so a cut cable self-alarms. Spec merged (**PR #93**); float lock-in **PR #94 OPEN**.
AG-1250E rejected (24 VAC solid-state — needs opto stage); SS2 condensate float + XKC-Y25 clamp-on
capacitive kept as documented alternatives. **(2) Full Pi software update + review:** 149 apt
packages incl. **kernel 6.12→6.18**, **Signal K 2.28-beta→2.30.0**, **Grafana 13.1.1**, **InfluxDB
2.9.1**, venv upgraded (**opencv HELD at 4.13** — the 4→5 major would risk the Sentry 7-seg CV;
verified fine under new numpy 2.5.1). Verified end-to-end: 14 services active, 0 errors, data
flowing, SK WS fix (PR #86) holding on 2.30.0, external Grafana OK, nginx manually restarted
(doesn't auto-start post-reboot). **nginx already latest stable** (`deb13u7`); recent 2026 CVEs
await a trixie backport that `unattended-upgrades` will auto-apply. **Key finding: the host is a
fanless Raspberry Pi 4** (not a Pi 5 as assumed) — Sentry's multi-core CV burst grazes the 80 °C
soft-limit no matter the config. Retuned live `/etc/pivac/config.yml`: `daemon_sleep: 30` +
`cycle_timeout: 20` (was 15/30; `cycle_timeout` had drifted to 30) → CPU ~1.6→~1.25 cores, floor
~76 °C, continuous throttle cleared; residual ~83 °C peaks are **benign** (< 85 °C hard limit) and
**cooling-bound — the only real fix is a fan**. CLAUDE.md thermal note on master `0252f5b`.
**Next:** merge PR #94; decide on a Pi cooling fan; build the storm-drain node (needs a NEW UNO R4
WiFi — all 3 deployed); carryover — YOFF rewire before heating season.

*Updated 2026-07-21 (session 25 — recovered a session lost to a power outage; merged the stranded work)*

A **power outage** (~14:50 EDT 2026-07-21) interrupted work before a save, so the saved state
falsely read "master / no PRs" while three commits sat unmerged (and live) on
`fix/sentry-gas-idle-fill`. Reconstructed from git + reflog + Pi state: **(1) Sentry gas idle-fill**
(`pivac/Sentry.py` emits `gasInputValue=0` every cycle when the burner LED is off but the display
didn't rotate to gas mode — kills a 14–19 min idle gap that looked stale; never fabricates while
firing); **(2) two Grafana flow-panel axis fixes** (drop custom units so ticks fit the pinned
`axisWidth`, size axes to real data gal/min ~12 / gal/hr ~700 — still gross flow). Opened **PR #92**,
squash-merged → master **`cf135d0`**; Mac + Pi back on master. **No restart** — squash was
byte-identical to the branch already running live. **Post-outage recovery clean this time:** all 3
Arduino boards rejoined WiFi (watchdog + `initial_state=on`; contrast Jul-15's 16h `.219` stale),
signalk WS re-logins 0, all 13 services active. **Next:** YOFF rewire before heating season; confirm
the watchdog fires on a real outage; verify irrigation volume halved after the Jul-6 even-day change.

*Updated 2026-07-20 (session 24 — Sentry LED misread root-caused + fixed; Grafana Sentry→TimeSeries alignment; water net-of-irrigation + hourly bars; Arduino watchdog)*

Big session, all merged to master `7e4a9e8`. **(1) Sentry boiler LED misread fixed (PR #90):**
burner/pump read 0 for most of every DHW call — camera locked in IR/Night dims the green LEDs to
~1.13× bg, under the 1.15 threshold. Split into `led_ratio=1.05` (dim green status LEDs) +
`indicator_ratio=1.15` (bright indicators); proved via `gasInputValue>0` cross-check + live lit-LED
measurement during a forced hot-water call. **(2) Grafana (PRs #89/#91):** Sentry Boiler Status →
aligned **Time Series** (colored stepped lines + legend); pinned `axisWidth=50` on every panel +
dropped the DHW panel's `PSI + °F` axis label → all time axes line up. Water: **Domestic shown NET
of irrigation** on the three "Used" stats + new bottom panel **"Water consumption by hour — last 7
days"** (stacked hourly bars, green domestic-net / yellow irrigation). **(3) Arduino watchdog (PR
#88):** freshness alerts for both pressure boards + `arduino-watchdog.timer` auto-power-cycles the
`.61` Shelly on a >15m board outage (root-caused a 16h `.219` stale after a Jul-15 power failure).
**Key infra learned:** Grafana is on **port 4000** sub-path `/grafana/`; live dashboards live in the
`resource` table of grafana.db (legacy `dashboard` table is stale); Grafana InfluxQL cross-measurement
math needs joinByField+calculateField with both aggregates forced to one `GROUP BY time(3650d)` bucket.
**Next:** optionally net the flow-rate panels 18/19; YOFF rewire before heating season; watch the
watchdog fire on a real outage.

*Updated 2026-07-16 (session 23 — stale hydronic root-caused to a power failure; added freshness alerts + an auto-recovery watchdog for the pressure Arduinos)*

Hydronic boiler PSI (`.219` board, `electrical.ac.arduinoThermPSI.psi`) was stale ~16h. Root
cause = a **mains power failure ~17:15 EDT Jul 15** (confirmed by David) that cycled both
Shelly-powered pressure Arduinos and rebooted the Pi; `.114` rejoined WiFi, `.219` didn't, and
the pressure boards had **no freshness alert**, so it failed silently. Power-cycled the `.61`
Shelly to recover it. Full log review otherwise clean (SignalK WS re-logins 0/hr = PR #86 fix
holding; all 9 services healthy; no other stale sensors). **PR #88 (merged, deployed live):**
(1) two Grafana freshness alerts `arduino-{dhw,hydronic}-psi-stale` → graph-bridge email at 30m;
(2) `arduino-watchdog.timer` — polls both boards every 5m and auto-power-cycles the `.61` Shelly
when either is unreachable >15m (rate-limited ≤1/hr, state in tmpfs, only touches the Arduinos'
plug). All watchdog branches tested; both repos on master `7358343`; timer active+enabled.
**Next:** confirm the watchdog/alerts fire on a real outage; carryover — verify irrigation volume
halved after the Jul-6 even-day change, review OpenSprinkler weather level (149%), YOFF rewire
before heating season.

*Updated 2026-07-06 (session 22 — town-code KB import + OpenSprinkler watering-schedule optimization; no pivac code change)*

Non-pivac-code session. **Imported the Mountain Lakes NJ municipal code (eCode360 MO1514) as a grep-indexed local KB** at `~/OneDrive - DGLC/Claude/mountain-lakes-code/` (70 chapter files + `INDEX.md` + distilled `water-schedule-reference.md` + rebuild script; eCode360's WAF blocks automated fetch → browser PDF export → pymupdf split). Promoted it to **global memory** (`reference/mountain-lakes-code.md`, synced via the claude-contexts symlink) so any session can answer town-code questions via INDEX→grep→cite-§. Used it to **optimize irrigation**: confirmed a borough sprinkler/deduct meter is **not required** (§ 237-4C) — David has none, so irrigation bills at domestic tiers **+ sewer** (marginal ≈ $1.19/100gal); and the § 237-10A restriction (June–Sept alternate-days-by-house-#, only 12:01–10am & 6–12pm, none Jul31/Aug31) was **being violated** by an every-day program. Fix: **set OpenSprinkler Program 1 restriction = Even days** (house #68 even; OS even/odd auto-skips the 31st), kept the compliant 1:00am start — David applied it in the app. Expect ~50% volume cut (was ~830 gal/run-day, 8,486 gal/30d via the AS200U → InfluxDB). Also saved David's **home address (68 Lookout Rd)** to `user.md`. **Next:** verify the volume halves in ~2 weeks; review the 149% weather level (manual vs Zimmerman); optional — put the text corpus in the repo for Pi access. Pivac carryover unchanged: **merge PR #86** then Pi master pull + restart.

*Updated 2026-07-05 evening (session 21 — WilhelmSK water-tile lag CORRECTED: it was pivac, not the app; fixed in PR #86)*

**The ~20–40 s "WilhelmSK display lag" was NOT the app — root cause was `pivac-provider.py`, fixed in PR #86 (open, deployed live on the Pi from the branch).** Signal K's ws interface heartbeats every client each `wsPingInterval` (30 s default) and terminates any that hasn't ponged by the next sweep; Python `websocket-client` only auto-pongs inside `recv()`, and the provider was **send-only, never reading its socket**. So every one of the **9 pivac services** had its WS connection heartbeat-killed ~60 s after connect, then silently discarded up to ~30 s of deltas (the unread server close frame left writes error-free) before `Broken pipe` forced a re-login — a chronic ~90 s connect/blackout/reconnect cycle (~6 re-logins/min in the signalk journal, all day). Invisible on slow thermostat paths; glaring on the 1 Hz water tiles. Fix: a daemon reader thread per connection drains the socket (pongs sent, close detected immediately). Verified live: 0 re-logins / 0 broken pipes for the 6 min after restart; gap-free 1 Hz water stream; tiles now track within the ~4–7 s physics floor (0.1 gal/pulse meter + 1 Hz poll + ~1 Hz app refresh — David measured ~6 s). Evidence: an instrumented WilhelmSK sim build showed deltas arriving 0.01 s + tiles rendering ≤1 s, while InfluxDB showed the SAME ~34 s gaps as the sim (server had nothing for ANY consumer during blackouts). **Regression signature:** `journalctl -u signalk | grep -c auth/login` climbing ~6/min. NB some pre-fix RedLink "Honeywell flakiness" 30–60 s path gaps were likely these blackout windows. WilhelmSK app fully exonerated. **Next: David merges PR #86, then Pi `git checkout master && git pull` + restart services** (Pi runs the branch until then). Diagnosis doc updated: `claude-contexts/wilhelm/water-tile-lag-diagnosis.md` (RESOLVED header).

*Updated 2026-07-05 (session 20 — domestic-water run timer + per-flow gallons + WilhelmSK tiles; display-lag root-caused to the WilhelmSK app)*

Built out **domestic water monitoring** end-to-end. **(1)** Reflashed the UNO R4 node
(`10.0.0.188`, Arduino#9) with a **low-lag per-pulse flow model** — `flowing`/run-timer fire on
the **first meter pulse** instead of a 10 s tumbling window (detection now ~1–3 s at fixture flow,
the meter's physical floor of 1 pulse/0.1 gal), EMA inter-pulse `flowRate`, 10 s stop-tail. **(2)**
Three new SK values: `environment.water.domestic.runDuration` (s) + `.runningFor` (mm:ss string,
node-emitted `run_s`/`runtime`) and **`.runVolume`** (gallons of the current draw, **held after
flow stops**, computed **Pi-side**). `pivac.DomesticWater` is now a **real module**
(`pivac/DomesticWater.py`) wrapping `ArduinoSensor` + appending `runVolume`; live config dropped
the `module:` override and runs `daemon_sleep: 1` (1 Hz). **(3)** Added **WilhelmSK tiles** (Water
GPM / Run Time / Gallons) to both iPad (three-across in the freed Outside row; whole row
redistributed to equal widths) and iPhone (relays column shortened for three stacked boxes; the
four water-temp gauges equalized to 77 px so DHW Recirc's font matches) — `dglcinc/wilhelm-sk` #3,
copied to `~/OneDrive - DGLC/Claude/{ipad,iphone}.wlyt`. **(4) Root-caused the ~20–40 s WilhelmSK
display lag to the app itself** — a 4-point synchronized monitor proved the delta reaches
WilhelmSK's exact WebSocket path (through nginx, `subscribe=all`) in ~1 s while the tile renders
20–40 s later (worsens with connection uptime); ruled out node/pivac/SignalK/nginx and delta
volume (~7.6/s). Handed off to the **wilhelm** context — see
`claude-contexts/wilhelm/water-tile-lag-diagnosis.md`. Added `proxy_buffering off` +
`proxy_read_timeout 3600s` to nginx `/signalk/` (correct for WS, didn't fix the app lag). **All
PRs merged** (Arduino #8/#9, pivac #83/#84/#85, wilhelm-sk #3); zero open. **Next:** pursue the
lag in `~/github/wilhelm`; import the layouts; sanity-check the meter registers under sustained
flow (froze at 905.0 in one test).

*Updated 2026-07-04 (session 19 — post-outage recovery + Emporia paired-CT half-scale ROOT-CAUSED and fixed; all PRs merged)*

Overnight power outage (~21:00 Jul 3 → ~15:30 Jul 4; generator flapping = 5 Pi
boots). Recovered: 1-wire IN/CRW stuck at the DS18B20 **85 °C power-on value**
(fresh `w1_slave` reads + `restart pivac-1wire`); hydronic Arduino `.219` never
rejoined WiFi (cycled the Arduinos Shelly plug `10.0.0.61` — both boards back in
seconds). **Emporia root-cause fix (PR #82, merged + live)**: David set dipswitch
3 ON on the 32x40 BOVA (runs 75–77 Hz), clamp read 9.4–9.5 A/leg ≈ 2.27 kW vs
Emporia ~1.15 kW — the house panel's four 240 V circuits (`utility_sub_panel`,
`hall_subpanel`, `wall_oven`, `bosch_bova`) use **two CTs, one per leg** (correct
hardware, mult 1.0), and `pivac.Emporia` emitted per channel so the second leg
overwrote the first at the same SK path → half scale. Fix = sum same-named
channels; energy balance closes; live step verified 16:21 EDT (bosch_bova 1.31 →
2.65 kW). **Do not set app ×2 on those circuits** (apartment `air_cond` single-CT
×2 is correct as-is). Pre-fix InfluxDB history stays half-scale. **Session-18
zone analysis rescales: both BOVAs were ~75% max on hot days, not ⅓** — the
32x40 zone now looks capacity/airflow-limited (and it has 23–24 Unico outlets,
≥ recommended, so outlets aren't the constraint). Merged #75/#81/#82, closed
stale #68, merged Arduino #7 (`28a66bf`) — **both repos clean, zero open PRs**.
**Next:** watch the 32x40 zone on a hot afternoon at full Hz (if it still
drifts: blower CFM tap, outlet audit, subcooling); quiet-house flush retest;
leak-threshold tuning; YOFF rewire before heating season.

*Updated 2026-07-03 (session 18 — MJ-75a register calibration VERIFIED + Bosch BOVA zone analysis; no code changes)*

Diagnostics/analysis session on the Pi. **(1) Meter node calibrated against its
mechanical register**: register 79.056 ↔ Arduino `volume` 75.5 → **offset 3.556
gal**; a ~6.2 gal bucket draw showed register delta 6.206 vs Arduino 6.3 — within
one 0.1 gal pulse (pickup chain fully verified, no dropped/doubled pulses; details
in Pi project memory `domestic-water-register-calibration.md`). A **Grundfos Scala2
booster sits immediately downstream of the meter** — shapes flow-rate traces, can't
affect totals. **Open item:** a toilet flush measured 2.9 gal (expected 1.2–1.6)
but both flush tests had concurrent household draws — retest quiet-house; if it
holds, inspect the toilet (gpf stamp / flapper), not the meter. **(2) HVAC 2-zone
analysis** (2× BOVA-36HDN1-M18M + Unico 3036; 32x40 zone loses setpoint to 77 on
hot days while 20x32 holds 75): Emporia shows both condensers at ~1.3 kW (~⅓ max)
with matching ramps — `house.bosch_bova` = 20x32 (confirmed), `utility_sub_panel`
plateau = almost certainly the 32x40's unit. Per the BOVA IOM the compressor
modulates on suction pressure only (Y2 never reaches the condenser; open-loop on
room temp), and both units already have SW4-4 accelerated ON → the lagging zone is
**control-limited, not capacity-starved**. Subpanel mapping since **confirmed by
David** (utility subpanel = 32x40 BOVA + fridge + shop outlets only). Plan:
**Force Mode** test on a hot afternoon (expect ~1.3 → ~3.5 kW +
room recovery), then Unico CFM/outlet audit, subcooling check, lower-zone-cooler
stairwell trick, pre-cooling. **Next:** merge #81/#75/Arduino #7, close #68 (all
unchanged from 17b).

*Updated 2026-07-03 (session 17b — domestic water meter COMPLETE end-to-end: plumbed, deployed into pivac, leak alerts live)*

David plumbed the MJ-75a and the full pipeline is **live and verified**: real draw
showed flow 0→3.0 gpm with the totalizer tracking. Deployed the Pi side (all on
**PR #81**, already running): `pivac-domestic-water.service` + `pivac.DomesticWater`
config (→ `pivac.ArduinoSensor`, `ipaddr: 10.0.0.188`, `daemon_sleep: 15`) →
`environment.water.domestic.{flowRate,consumption,flowing}` confirmed in Signal K
**and** InfluxDB. **Irrigation-aware leak alerts deployed + verified provisioned**
(`grafana/provisioning/alerting/domestic-water.yaml` → graph-bridge email):
continuous-flow 3h (suppressed if OpenSprinkler ran in-window — sprinkler water flows
*through* this meter), burst = **net** (domestic − irrigation) > 12 gpm/15m (stays
armed during runs), 30m freshness; irrigation NoData→0 so a down sprinkler service
can't disarm leak alerting. CLAUDE.md fully updated. **Next:** merge #81/#75/Arduino
#7, close stale #68; tune the 12 gpm / 3h thresholds after a usage baseline; optional
register-vs-`consumption` accuracy check (±1.5%).

*Updated 2026-07-03 (session 17a — domestic water node: valve deferred, meter-only sketch FLASHED + verified)*

David **dropped the shutoff valve from scope** — the domestic water node is now
**meter-only**. Stripped the valve from `DomesticWater.ino` (Arduino **PR #7**,
`5b46997`: no D7 relay, no `/valve/*`, no valve EEPROM; status dict =
`{'flow','volume','flowing','uptime_ms'}`; **USB power only**) and updated the build
spec to match (pivac **PR #75**; valve sections kept as marked reference; valve-era
sketch stays in branch history). **Flashed the spare UNO R4 WiFi** (MAC
`34:b7:da:65:99:1c`) from the M2 over SSH, **verified live** (`GET /` returns the
dict), and **UniFi-reserved it to `10.0.0.188`** ("DomesticWater"). LED matrix shows
whole-gpm flow (reads 0 with no meter). Wiring = reed leads → **D2 + GND** (no
polarity) + USB power. Installed **arduino-cli on the Pi** (`~/bin`, renesas_uno
core) for local compile-verify. Gotchas recorded in `tools/arduino-cli.md`: M2-over-SSH
compiles hit macOS TCC on `~/Documents` libs (use `--libraries /tmp/ard-libs`); the
Pi clone's `arduino_secrets.h` is a placeholder. Also corrected M2 network memory:
**`.83` fixed wired = canonical**; Wi-Fi now **reserved `.95`** (mDNS resolves to the
Wi-Fi addr — not a moved host). **Pick up here:** plumb meter + wire reed → add
`pivac.DomesticWater` config (`ipaddr: 10.0.0.188`, spec §6) + service → Grafana
monitor-only alerts → merge #75 + Arduino #7, decide stale #68. YOFF rewire
(session 16) still pending before heating season.

*Updated 2026-07-01 (session 16 — YOFF stuck pin root-caused: GPIO 26 silicon is dead; 1-wire recovery)*

Root-caused the stuck YOFF input: **GPIO 26 (physical pin 37) is permanently dead** —
floating it reads 0 under both pulls and even output-drive-HIGH can't raise it
(internally shorted to ground). Killed by the 2026-06-23 power event (Shelly plug
move): unpowered Pi + connected live field wiring. The Jun 23→Jul 1 YOFF "active"
plateau in InfluxDB was dead-pin fabrication — **purged**. **YOFF is now disabled**
(commented out in `/etc/pivac/config.yml`); the wire is physically still on dead
pin 37 (move deferred). YOFF is **winter-only** (disables A/C), so 0 is its true
state all summer — **rewire deadline = before heating season**: move wire to
**pin 35 (GPIO 19, verified healthy)**, uncomment config, restart pivac-gpio. Also
planned: ~1 kΩ series resistor per sense line (Pi end) against the
unpowered-Pi-transient failure mode. Separately, recovered 1-wire after David's
hard-reset experiment: service had started with pins disconnected → empty sensor
list at import → silent no-publish; `systemctl restart pivac-1wire` fixed it (no
reboot). Diagnostic recipes documented in pivac CLAUDE.md (`6afa447`, `5bf7025`).
Water-node work below (session 15) remains the active resume target.

*Updated 2026-06-28 (session 15 — domestic water node: sketch built + wiring spec — ACTIVE RESUME TARGET)*

Built the **domestic water node firmware** on the M2:
`~/github/Arduino/DomesticWater/DomesticWater.ino` (Arduino branch `feat/domestic-water-node`,
**PR #7**) — DAE **MJ-75a** reed on **D2** (ISR + 3 ms debounce, 0.1 gal/pulse), EEPROM
totalizer (5-min persist + magic marker), 10 s rolling flow window, and a **DPDT relay on
D7** for the **Variant-A reverse-polarity bistable valve** (David confirmed he has Variant A
in hand). Reuses the `ArduinoPSI_*` WiFi/RA4M1-watchdog/bounded-HTTP scaffolding; serves the
single-quoted `ast.literal_eval` dict + `/valve/open|/valve/close|/reset?confirm=1`.
**Compiles clean for the R4 WiFi (30 % flash); NOT flashed — no board was connected.**
Also **expanded the build spec's §4 wiring** (pivac **PR #75**) with the detailed
**12 V-to-board+valve power path** and **crossed-contact DPDT reverse-polarity** wiring (the
detail still owed), and resolved the §1 decisions (valve A, monitor-first, board R4). Sketch
defaults the relay **active-LOW** so D7-idle-HIGH = OPEN (fail-open); persists commanded valve
state to EEPROM so a watchdog reset holds position. **Pick up here:** flash the board when
connected → bench-test (incl. power-loss-stays-open) → DHCP-reserve MAC → add
`pivac.DomesticWater` config + `pivac-domestic-water.service` on the Pi → plumb + calibrate +
Grafana monitor-only alerts. Stale pivac **#68** (old camera plan) still open — candidate to close.

*Updated 2026-06-28 (session 14b — domestic water node: started scaffolding, moved to M2)*

**Resuming on the M2** (`david@10.0.0.83` — fixed IP, wired; Arduino repo at `~/github/Arduino` — NOT on
utilityserver). Building the **domestic water node** to replace the retired camera-CV
`pivac.WaterMeter`. David has the **DAE MJ-75a** meter (0.1 gal/pulse, 2-wire reed) + a
**motorized shutoff valve** in hand; spare board confirmed **UNO R4 WiFi**. **Verified via the
`dglcinc/Arduino` GitHub tree that no domestic-water sketch exists yet** (only the two pressure
sketches; `ArduinoPSI_Domestic` is the DHW *pressure* board, not a meter; branch
`feat/cc1101-watermeter-test` = abandoned RF approach). **Source of truth = the build spec**
`docs/domestic-water-node-build-spec.md` on **PR #75** (read via
`git show origin/docs/domestic-water-node-build-spec:docs/domestic-water-node-build-spec.md`) —
it has the full BOM, wiring tables (§4), firmware skeleton (§5), pivac config (§6), and deploy
checklist (§11).

**Pick up here (in order):** (1) **confirm the valve variant** — A = 2-wire reverse-polarity
(bistable, holds on power loss, no feedback, needs **DPDT** relay; *spec primary*) vs B = "Normally
Open" 5-wire (needs continuous hold power + 2 feedback inputs via divider/opto). (2) **Scaffold the
sketch** in `~/github/Arduino` reusing the `ArduinoPSI_*` WiFiS3/HTTP/watchdog scaffolding — adds
**D2** reed ISR (`INPUT_PULLUP`, `FALLING`, ~3 ms debounce), EEPROM totalizer (save every 5 min),
10 s rolling flow window, **D7** valve relay, `GET /` status + `GET /valve/open|/valve/close`.
Status line is a **single-quoted Python literal, NOT JSON** (ArduinoSensor uses `ast.literal_eval`):
`{'flow' : 2.50, 'volume' : 12345.6, 'flowing' : 1, 'valve' : 1}` (`volume = pulses × 0.1`).
(3) **Still owe David the "how to get 12 V to the valve" wiring detail** — single 12 V/1–2 A adapter
→ board VIN + relay COM; valve motor current flows **only through the relay contacts**, never an
Arduino pin; common ground; RC snubber; DPDT reverses polarity to the 2 motor leads for Variant A.
(4) **pivac config:** add `pivac.DomesticWater` (`module: pivac.ArduinoSensor`) →
`environment.water.domestic.{flowRate,consumption,flowing,shutoffValve}`; clone a
`pivac-arduino-*.service` → `pivac-domestic-water.service`. (5) DHCP-reserve the board IP by MAC.
MJ-75a K-factor is factory-known (0.1 gal/pulse ±1.5%) — no fudge factor; start **monitor-only**,
defer autonomous shutoff until a Grafana baseline.

*Updated 2026-06-28 (session 14a — Sentry phantom-hundreds root-cause fix + Pi gh token recovery)*

**Last worked on**: Root-caused and fixed the **Sentry boiler water-temp jitter**
(idle ~84 °F intermittently read as 184/183/134, during idle *and* DHW). First
attempt was a cross-cycle jump-guard with physics assumptions; David pushed back —
correctly — and the real fix went into the **recognition layer**: `_read_display`
was computing the lit/off threshold **per-digit-crop**, so a **blank** hundreds
digit (any temp < 100) had its bar set by its own IR-glare noise and manufactured
a phantom "1". Replaced with **one display-wide threshold** `bg + factor*(p99-bg)`
anchored to a genuinely-lit segment, applied to every digit → blank stays blank.
Also **vote LED states across the cycle's frames** (burnerOn/status stop
flickering). **PR #80 merged** (`501f000`), deployed live. New config keys
`digit_threshold_factor` (0.65, display-wide) + `display_bg_percentile` (40).
A Pi-local one-shot **`sentry-phantom-check.timer`** emails PASS/FAIL at 07:00
2026-06-29 after an overnight idle period (definitive observable). Also **recovered
the Pi's invalid gh token** by pulling the valid PAT from the **M4 Mac Mini**
(`utilityserver@10.0.0.84`) hosts.yml and piping into `gh auth login` (M2 `.83`
fails host-key from the Pi — use M4; recipe saved to `~/.claude/memory/tools/gh.md`).
**Next:** check the 7 AM email; water-meter PRs #75/#68 still open; optional
`pivac.Shelly` module.

*Updated 2026-06-23 (session 13 — Shelly plugs + UCG API access + MemPalace cleanup)*

**Last worked on**: LAN-infra + memory, no pivac code. Set up **two Shelly Plug US Gen4** —
**Arduinos** `10.0.0.61` (MAC `ac:eb:e6:f4:b9:30`; the two UNO-R4 pressure boards plug into it
→ remote power-cycle) and **PivacPower** `10.0.0.118` (MAC `ac:eb:e6:f6:45:20`) — each pinned
with a **UCG DHCP reservation** (left on DHCP so portable), names aligned across app/local-RPC/UCG
(app/cloud label is rename-in-app-only). **Found + documented UCG API access** (was hard to
find): the UniFi Network controller now runs **on the UCG Ultra at `https://10.0.0.1`** (not the
Mac mini anymore), full-admin key at `~/.config/unifi/claude-agent.key` (`X-API-KEY`, works on
both the v1 Integration and legacy Network APIs) → wrote `~/.claude/memory/tools/unifi.md` +
index + `global.md` (pushed). **Cleaned 5 stale pre-migration UniFi drawers** from MemPalace
(read IDs from the Chroma SQLite, deleted via MCP) that were misleading semantic search; added an
authoritative drawer + KG facts. Also **configured the Shelly Cloud key** (`~/.config/shelly/cloud.key` +
`.../cloud.server`) for off-LAN read/control — verified via `/device/all_status`; confirmed the
key **cannot** rename a device (Control API is status+relay only, rename is app-session-only).
Late in the session, **moved the Pi's power onto the PivacPower plug** (`10.0.0.118`): graceful
shutdown (stop pivac→signalk→influxdb→nginx, `sync`, `shutdown -h now`), watched for boot,
restarted nginx (doesn't auto-start) — all services + external Grafana confirmed back. **Set
both plugs `initial_state="on"`** (were `off`) so a mains outage auto-restores power and the
Pi + Arduinos reboot unattended. **Next:** optional `pivac.Shelly` module (W/Wh via
`/rpc/Switch.GetStatus` → `electrical.*`); water-meter PRs #75/#68 still open. **Gotcha:** editing an already-mined memory note leaves the OLD drawers in
the palace — fix is manual delete via Chroma-SQLite ID lookup.

*Updated 2026-06-21 (session 12 — OpenSprinkler localized-UI fork, spun off + shelved)*

**Last worked on**: Spun off a **new project, `dglcinc/opensprinkler-localized-ui`** — a
fork of OpenSprinkler-App that localizes the web UI to show irrigation flow in **gallons**
(upstream hard-codes liters). v1 built, deployed reboot-savvy on the Pi (LAN-only nginx site
`os-localized-ui` on :8088), **tested live (gallons confirmed)**, then **shelved** — user set
the device to `fpr=1` (L/pulse) to keep the status quo (stock phone app + Grafana). On pivac:
root-caused the OS liters/gallons confusion (firmware SI-only, no unit tag), added Grafana
irrigation **Used** totals (PR #76, merged), and merged a UI-fork scope doc
(`docs/opensprinkler-gallons-ui-fork-scope.md`, PR #77). **Pick up via
`/set-context opensprinkler-localized-ui`.** ⚠️ Resuming the fork UI needs the device set
back to `1 gal/pulse`; pivac/Grafana are unaffected either way.

*Updated 2026-06-20 (session 11b — irrigation meter installed + calibrated)*

**Last worked on**: Completed the **irrigation flow-meter swap end-to-end**. Installed the
**DAE AS200U-75P** (¾", 1 gal/pulse) on OpenSprinkler (`SN1`+`GND`, 2-wire reed, no power);
a clean **meter-register calibration confirmed pivac `fpr=1.0`** — 28.0 gal over ~5.1 min ≈
5.5 gpm matched pivac's 5.4–5.57 gpm (~1%). Purged **all** GREDIA-era data: InfluxDB
irrigation measurements (~12k pts) **and** the full OpenSprinkler device log (`/dl?day=all`),
and set the OS **device `fpr=1.00`** — so device / Grafana / pivac all agree from a clean
slate. CLAUDE.md updated + pushed to master (`71ad5de`). Reusable calibration: clean zone run,
read register before/after, `fpr_new = fpr × (true_gpm ÷ pivac_gpm)`. **Next:** build the
**domestic** node (PR #75) when MJ-75a + valve arrive; decide PR #68.

*Updated 2026-06-20 (session 11 — water-meter hardware selection)*

**Last worked on**: Settled the **hardware path** to replace the retired camera-CV domestic
water meter with real **pulse-output meters**. Chose **DAE** meters — **AS200U-75P** (¾", 1
gal/pulse) for **irrigation** → OpenSprinkler, and **MJ-75a** (¾", 0.1 gal/pulse) for
**domestic** → the spare **UNO R4 WiFi** — plus a **U.S. Solid** motorized shutoff valve.
Wrote the full domestic-node build spec (`docs/domestic-water-node-build-spec.md`, **PR #75**,
open). Both meters **ordered**. **Key facts:** OS `fpr` resolution is 0.01, so a 1 gal/pulse
meter (`fpr=1.00`) kills the contaminated `0.0025` override and makes OS app + Grafana agree;
the GREDIA hall sensor was both too fine and >50 Hz over its range (bad for OS). Commercial
units (Moen Flo/Phyn/Flume) rejected as cloud-only / iPerl-incompatible; local Arduino path
chosen (pivac stays read-only — valve control + leak logic on the Arduino). **Next:** decide
3 open spec items (valve variant, monitor-first vs auto-shutoff, confirm board is R4 WiFi);
on arrival, wire AS200U → OS SN1+GND + `fpr=1.0`, then build the domestic node; decide PR #68.

*Updated 2026-06-16 (session 10 — planning)*

**Last worked on**: Planned the **camera/OCR water-meter** front end around `jomjol/AI-on-the-edge-device`. **Mid-session pivot:** discovered PR #68's branch already has a **validated custom-CV pipeline** reading the iPerl LCD (Tapo at `10.0.0.85`, reading `0626984.29 Gal`; warp → illumination-flatten → whole-glyph template-match, flow-aware decimals, monotonic guard). So the open question is **hardware form-factor, not software** — David's complaint is physical (the Tapo is bulky and its ~10″ USB light bar is clumsy in a tight pit). Wrote `docs/water-meter-camera-hardware-options.md` (on the PR #68 branch, commit `4dd8ed7`): AI-on-the-edge (compact ESP32-CAM, **flash-on-capture** = no permanent light) vs. keeping the validated Tapo+CV with a small off-axis LED. **Key catch:** the reflective LCD needs **off-axis diffused** light (proven in PR #68 §1), but the ESP32-CAM's flash is **on-axis** → glare is the hard gate for the compact all-in-one. Recommendation: cheap ~$12 **AI-Thinker ESP32-CAM** prototype gated on the glare test; Path B (validated CV + compact off-axis light) is the proven fallback.

**Key facts**: AI-on-the-edge stable firmware = **original ESP32** (ESP32-S3 still experimental); needs **microSD + flash LED + ≥4 MB PSRAM + OV2640** (FREENOVE Wrover-CAM has no SD → no good). Purpose-built **"AI-On-The-Edge-Cam" ESP32-S3 PoE** board (Amazon **B0FVMFBG22**, ~$28) has a **WS2812B ring light** (best anti-glare) but experimental firmware. Meter unit = **US gallons**, not m³ (the m³ was an EU-wM-Bus artifact of the retired RF plan). RF approach retired (US iPerl = FlexNet 900 MHz encrypted). Two clarifiers before buying: is the bulk the camera or the light bar? Is there ethernet at the meter (→ PoE board)?
*Updated 2026-06-17 (session 10 — implementation; supersedes the planning note above)*

**Last worked on**: Domestic + irrigation **water monitoring**. Built `pivac.WaterMeter` (Tapo camera reading the Sensus iPerl LCD at `10.0.0.85` via custom CV) — but it **doesn't generalize** across digit positions on the low-contrast LCD (read `627713` as `627177`), so it was **retired and the service STOPPED**; bad domestic data was deleted from InfluxDB. Built + deployed `pivac.Sprinkler` (OpenSprinkler irrigation flow via local HTTP API, auth = md5(device password)), added a Grafana "Domestic Water" row (flow gal/min + gal/hr Domestic-vs-Irrigation overlay, adaptive usage bars, totals, sane scales). **Decided the domestic main-meter path is an AI-on-the-edge ESP32-CAM** (`docs/water-meter-camera-hardware-options.md`, on PR #68). **Next:** buy an AI-Thinker ESP32-CAM (~$12), flash `jomjol/AI-on-the-edge-device`, prove on-axis glare is beatable, then rewrite `pivac.WaterMeter` as a `/json` poller. Irrigation `fpr=0.0025` (approx from 1042 gal overnight / 416046 pulses) — refine with an isolated run later. PRs merged: #69–#74; **#68 open** (camera plan superseded + hardware-options doc). Radio wM-Bus plan #67 stays as zero-CV fallback.

*Updated 2026-06-16 (session 9)*

**Last worked on**: Ran down a full Pi outage that presented as "pivac hung again" but was the **whole host off the network** (ping "Host is down", ARP `incomplete`). Root cause: **WiFi power-save on a weak 2.4 GHz link** → association drop → DNS failures across all modules → host off the wire (needed a power-cycle). **Fix: migrated the Pi from WiFi to wired ethernet.** Final state: `eth0` **primary** (MAC `d8:3a:dd:b1:ad:4d`, UniFi-reserved → `10.0.0.82`, metric 100); `wlan0` **fallback** (`10.0.0.130`, SSID `redux` locked to **5 GHz** on a new utility-room AP @ ≈-45 dBm, power-save off, metric 600, auto-failover). Also recovered RedLink (stale in WilhelmSK was collateral from the DNS window — a clean `systemctl restart pivac-redlink` republished all 5 thermostats once DNS resolved). PR #67 (water-meter plan) **merged**. CLAUDE.md updated (Remote Access + Known Operational Behaviours). **Caveat:** port-forwards target `.82`/eth0 only — WiFi fallback keeps the Pi alive + SSH + collecting data, but external access wouldn't auto-fail-over. Late in the session the WiFi fallback dropped and didn't self-heal (NM `failed (reason 'no-secrets')`); reconnected it and verified the durable fix — the `redux` profile's PSK/`band=a`/`powersave=2` are persisted to its on-disk keyfile (`Wireless connection 1.nmconnection`), so it can now autoconnect unattended. Natural test: the weekly Sunday-00:00 reboot should bring `wlan0` back on `.130` by itself.

*Updated 2026-06-15 (session 8)*

**Last worked on**: Wrote `docs/water-meter-monitoring-plan.md` (**PR #67, open**) — a plan to add **domestic water consumption monitoring** from the **Sensus iPerl** meter. Research established it's **wM-Bus** (T1, 868.95 MHz, AES-128-CBC, factory key), decoded by `wmbusmeters` — not NA SCM/rtlamr. Iterated the receiver across 5 revisions; **chosen = a remote UNO R4 WiFi node** (dumb radio forwarding raw telegrams over WiFi; `wmbusmeters` decodes on the Pi), picked for **$0** (parts on hand) over the lowest-effort-but-$100 Würth AMB8465-M USB dongle. **Next:** write the Arduino sketch + `pivac.WaterMeter` module (not started), then bench-test the on-hand **433** CC1101 (band-mismatched for 868 — test up close, may need an 868 module). **No code written / nothing deployed yet** — plan only.

**Key facts**: CC1101 band trap (chip does 315/433/868/915, board matching is fixed per-band; 433 board ≈10–20 dB down at 868). Pi-direct GPIO rejected (header in use + would require opening the production Pi). US dongle source = Würth AMB8465-M, DigiKey PN 1917-1022-ND (iM871A is EU-only). SK path `environment.water.domestic.consumption`. ⚠️ `~/github/Arduino` not cloned on utilityserver.

*Updated 2026-06-03 (session 7)*

**Last worked on**: Grafana DHW panel polish. Made DHW pressure and recirc-loop
temp share **one** y-axis on the "Potable DHW Loop — Pressure & Recirc Temp"
panel (`pivacr.json` id 5). **PR #65** moved recirc temp off the right axis to
the left (target view can't render right-side axis labels), relabeled the axis
`PSI + °F`, and dropped the temp `fahrenheit` unit. **PR #66** fixed the residual
two-stacked-left-axes problem — PSI on `axisPlacement: auto` vs temp override
`left` don't dedupe in Grafana, so it drew two independently auto-scaled left
axes — by setting the panel default to explicit `left` and removing the
per-series override. Both merged, pulled on the Pi, confirmed live (one shared
scale). **Gotcha worth keeping:** Grafana only merges series onto one y-axis if
they share the *same explicit* placement (+ matching unit grouping); `auto` ≠
`left`. No open work.

*Updated 2026-06-02 (session 6)*

**Last worked on**: **Closed out the Arduino firmware deployment (`dglcinc/Arduino#6`, now MERGED).** Flashed both UNO R4 WiFi pressure boards with the hardened firmware (RA4M1 watchdog + escalating WiFi reconnect with `NVIC_SystemReset()` fallback + bounded HTTP + `uptime_ms`; DHW board also gets the compile-guarded DS18B20) via `arduino-cli` on the M2, fixed the inverted IP/MAC columns in the Arduino repo `CLAUDE.md` hardware table, merged PR #6 to `main`, and **verified end-to-end on the Pi**: recirc temp `environment.inside.hvac.dhw.recirc.temperature` = **310 K** and DHW pressure `electrical.ac.arduinoPSI.psi` = **64 PSI** both flowing fresh into Signal K. No open work on either repo.

**Flashing how-to (M2 = `David-M2.local`)**: `arduino-cli` 1.4.1 flashes fine — **not GUI-only**. Board identity = USB serial = WiFi MAC, so the connected board self-identifies which firmware it needs: `.219`/`usbmodem34B7DA661E50*` = BoilerLoop 100 PSI (boiler); `.114`/`usbmodemC04E30116F3C*` = Domestic 200 PSI + DS18B20 (DHW). Compile: `arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi --libraries ArduinoPSI_BoilerLoop/libraries <SketchDir>` (OneWire/DallasTemperature come from global user libs; Domestic only). A board flashed on the bench (not reinstalled) reads `temp` = `-196.6 °F` = `-127 °C` `DEVICE_DISCONNECTED_C` and a floating `psi` — bench artifact, not a fault. The M2 can `ssh pi@10.0.0.82`. (Correction to session 5: the Arduino `gh`/SSH path works from the M2 now.)

*Updated 2026-06-02 (session 5)*

**Last worked on**: Diagnosed a DHW-Arduino stale-data alarm — both pressure Arduinos dropped off 2.4 GHz WiFi and self-recovered ~2 h later. Proved via UniFi U6-Pro AP logs (`KitchenAP`, 10.0.0.78) + USG DHCP logs that the recovery was a WiFi re-association, **not** a reboot/power cycle (board sent `DHCPREQUEST`, kept its IP; a reboot sends `DHCPDISCOVER`, which both boards did at a *separate* ~12:23 PM power blip). Hardened the Arduino firmware (RA4M1 watchdog + escalating reconnect with `NVIC_SystemReset()` fallback + bounded HTTP + `uptime_ms`), recovered the weekend DS18B20 DHW-recirc temp firmware from the M2, merged both into one branch, and consolidated PRs → **Arduino `dglcinc/Arduino#6`** (open). Flash still pending. (Board mapping below — `.114`=DHW, `.219`=boiler — re-confirmed.)

**Access notes**: M2 MacBook = `david@10.0.0.83` (fixed IP, wired USB-ethernet; the `.109` originally recorded here was a Wi-Fi DHCP lease — Wi-Fi is now reserved to `.95` (2026-07-03), and `.83` remains the canonical SSH target. SSH key from the Mini works; Arduino repo at `~/github/Arduino`, GUI IDE only). UniFi **APs** take SSH key auth as `dglcinc` (e.g. `KitchenAP` 10.0.0.78 — holds 2.4 GHz client logs); the **USG-3P** only takes username/password. This Mac's GitHub SSH had been broken — it caused a 25-commit-stale pivac checkout and repeated Arduino-mapping mislabeling; fixed by adding the Mini's `id_rsa` to GitHub. `gh` CLI token on the Mini is still invalid (HTTP 401).

*Updated 2026-06-01 (session 4)*

**Last worked on (session 4)**: Ran down the ~03:00 Grafana **mlb-availability** alert.
It was self-inflicted — the monthly NAS image-backup (1st @ 03:00) stops `nginx`, blacking
out the `mlb.dglc.com` proxy 03:03–03:15. Separately, the backup itself was **failing with
ENOSPC**: RonR `image-backup` had sized `pivac.img`'s root partition to usage+margin at
creation (54.4 GiB), and live root had grown to 54.9 GiB. **Grew `pivac.img` on the NAS to
the full 128 GB card** (`truncate` → `parted resizepart 2 100%` → `e2fsck` → `resize2fs`;
now p2 = 118.7 GiB, ~63 GiB free, sparse 54 GB actual; restore is 1:1 to any ≥128 GB card),
and **restored the MBR disk id `0xf9199e61`** (parted regenerates it → would break
PARTUUID boot of a restore). Edited `nas-image-backup.sh` (PR #64, open): dropped `nginx`
from the stop list (mlb stays up during backups) and excluded the `/home/pi/thinclient_drives`
xrdp FUSE mount (root can't stat it → rsync exit 23). **Validated:** patched script ran
clean **exit 0 in 125 s**, mlb stayed up (HTTP 302) throughout, all 10 services active
after; fresh image timestamped 07:24, 56 G actual on the NAS (2.4 T free). **Done:** PR #64
merged, Pi back on master. Also **pruned all stale branches** — 9 local + 29 merged remote
branches deleted; repo is now just `master` (local + origin) with zero open PRs. (David's
live SD card was already fully expanded — fine.) **No open pivac work.**

*Session 3 (2026-05-31):*

**Last worked on**: Shipped the **DHW recirc-loop temperature** feature end-to-end + several fixes. Generalized `pivac.ArduinoSensor` to multi-field (`type: temperature`→Kelvin), wired/flashed a DS18B20 on the DHW Arduino, deployed live (`environment.inside.hvac.dhw.recirc.temperature`, ~313 K), added a Grafana 2nd-axis panel, a `circ-temp-stale` freshness alert, and WilhelmSK iPad+iPhone gauges. Also: **corrected the inverted Arduino board/IP/role mapping** (DHW board = .114/`pivac.ArduinoPSI`, boiler = .219/`pivac.ArduinoThermPSI` — names are backwards vs role); **rotated the leaked GitHub PAT** (all `~/github` remotes→SSH, new fine-grained token in gh keyring on Mac+Pi, old `ghp_` revoked, 2027-05-17 rotation reminder scheduled); and **root-caused + hardened the Sentry** boiler-display "jumping values." Plan doc marked ✅ COMPLETE. PRs: pivac #59/#61/#62/#63, Arduino #4, wilhelm-sk #2 (all merged).

**Next steps**:
1. **Pump-health / "loop cold" alert — intentionally deferred** (plan §8.3): the recirc pump is on-demand/aquastat, so a static threshold false-alarms. Observe the duty cycle a few days, then build a "never reached hot in 24h" signal.
2. *(optional)* Round the HVAC In/CRW/Out WilhelmSK gauges to whole °F (recirc already done via `valueLabelFormat %0.0f`).
3. *(carryover)* NAS image-backup first auto-run check (`journalctl -u nas-image-backup.service`); physical card-swap boot test — needs hands at the Pi.

**Notes**:
- **Arduino board/IP/role mapping (was inverted in docs; now corrected in CLAUDE.md):** DHW board = MAC `c0:4e:30:11:6f:3c` = **10.0.0.114** = `pivac.ArduinoPSI` / `electrical.ac.arduinoPSI` / "Potable DHW PSI" / 200 PSI Domestic sketch (**recirc DS18B20 is here**). Boiler/hydronic = MAC `34:b7:da:66:1e:50` = **10.0.0.219** = `pivac.ArduinoThermPSI` / `electrical.ac.arduinoThermPSI` / "Hydronic PSI" / 100 PSI BoilerLoop sketch. Names kept (InfluxDB history); IPs DHCP-by-MAC.
- **Sentry CV depends on a locked camera mode:** Tapo C120 Night Vision must stay **Night** (+ Night Boost **off**), not Auto — Auto day/night switching causes 7-segment misreads. Module hardened (range-sanity + median debounce, PR #62).
- **GitHub auth on all machines is now SSH remotes + a fine-grained PAT** (gh keyring on Mac + Pi). The old broad `ghp_` classic token was leaked across configs and is revoked. New token expires ~2027-05-31.
- **Reader hardware:** Anker USB 3.0 Micro SD Card Reader, USB `05e3:0764` (Genesys Logic chipset). Replaced the 4-LUN Insignia NS-DCR30A2 on 2026-05-09. The Anker is a 2-LUN device but the same `size > 0` filter handles single- and multi-slot readers identically.
- **Why VID:PID, not SCSI model:** Anker's SCSI model string is `MassStorageClass` — too generic to match safely (any USB stick reports it). VID:PID is unique to the actual reader.
- **Both timers installed and enabled.** `nas-image-backup.timer` (monthly, 1st @ 03:00 EDT) and `sd-clone.timer` (weekly, Sun @ 02:00 EDT +/− 15m jitter). 1h gap prevents collision when the 1st of a month falls on a Sunday.
- **rpi-clone is live-safe** — no service stop, unlike `image-backup` which requires service quiesce. A weekly clone that captures live state is fine for hot-recovery; the monthly NAS image is the consistent backup.
- **rpi-clone install:** source at `~/github/rpi-clone/` (billw2/rpi-clone), copied to `/usr/local/sbin/` — see pi-CLAUDE.md.
- **No redeploy needed for sd-clone.sh changes:** `/etc/systemd/system/sd-clone.service` references the in-repo path `/home/pi/github/pivac/scripts/sd-clone.sh` directly, so `git pull` after merge is sufficient.
- **Stacked-PR gotcha hit during PR #44 merge:** squash-merging a parent with `--delete-branch` auto-closes child PRs and blocks reopen. Recovery is cherry-pick onto new master + new PR. Documented globally in `~/.claude/memory/tools/gh-stacked-prs.md`.
- **OpenSprinkler `/sprinkler/` proxy** has no Basic Auth despite CLAUDE.md claiming it does — docs drifted, not blocking anything. Native OS app only works at root URL, not under a path prefix; if mobile-app access becomes important, set up `sprinkler.dglc.com` subdomain mirroring the bowling-app pattern.
- **Local SSD copy** at `/mnt/tempssd/pivac.img` retained as a cold spare; SSD unmounted by default.

---

## Backup Runbook (drivable from a Mac Claude session)

The Pi backs up to LookoutNas (DS225+ at `10.0.0.3`) using RonR's `image-utils` (rsync-based, produces a directly bootable `.img`). Architecture and one-time infrastructure (NFS mount, ACL fix, share setup) are documented in `pi-CLAUDE.md`'s `## Backup` section — that work is already done. What follows is the procedure to actually run a backup.

### Connection

The Mac has passwordless SSH to the Pi as user `pi` (`ssh pi@10.0.0.82`). The Pi has passwordless SSH **as root** to the NAS (`ssh root@10.0.0.3`).

### Phase 1 — bootstrap initial image to the temp SSD (one-time, ~15 min)

**Preconditions to verify before running:**
- Temp SSD is plugged into the Pi and mounted at `/mnt/tempssd` (1.8 TB SanDisk Extreme, ext4). Check: `ssh pi@10.0.0.82 'df -h /mnt/tempssd'`
- image-utils is at `/home/pi/github/RonR-RPi-image-utils/`
- No backup has been run yet (the `/mnt/tempssd/pivac.img` file does not exist — `-i` will refuse to overwrite)

**Run from the Mac, inside `tmux` for resilience** (RDP/SSH drop kills foreground commands):
```bash
ssh pi@10.0.0.82
tmux new -s backup
sudo systemctl stop pivac-1wire pivac-redlink pivac-gpio pivac-arduino-psi pivac-arduino-therm-psi pivac-emporia pivac-sentry signalk influxdb nginx
sudo /home/pi/github/RonR-RPi-image-utils/image-backup -i /mnt/tempssd/pivac.img
sudo systemctl start nginx signalk influxdb pivac-1wire pivac-redlink pivac-gpio pivac-arduino-psi pivac-arduino-therm-psi pivac-emporia pivac-sentry
```
Detach tmux: `Ctrl-b d`. Reattach: `tmux attach -t backup`.

**Expected output**: image-backup creates partitions inside the .img file, formats them, then rsyncs the live system into the loopback-mounted partitions. ~10–15 min for ~53 GB to local ext4 (~50–100 MB/s). The script prints rsync progress.

**Success signals:**
- Final line of `image-backup` says something like "image-backup completed successfully"
- `ls -la /mnt/tempssd/pivac.img` shows a ~119 GB file (sparse — actual usage close to the source's 53 GB)
- All systemd services come back up: `systemctl status pivac-* signalk influxdb nginx | grep "Active:"` all show `active (running)`
- Grafana dashboards resume updating once Signal K + InfluxDB are back

### Phase 2 — ship the bootstrap .img to the NAS

```bash
sudo mount /mnt/nas-pi-backups   # uses the noauto fstab entry
sudo rsync -avS --progress /mnt/tempssd/pivac.img /mnt/nas-pi-backups/
sudo umount /mnt/nas-pi-backups
```
`-S` preserves sparse-ness so we don't transmit empty bytes. ~10–20 min on gigabit (sequential — best case for NFS).

Alternative if NFS-mount is unhappy: `sudo rsync -avS --progress /mnt/tempssd/pivac.img root@10.0.0.3:/volume1/pi-backups/` (uses the existing root SSH key).

### Phase 3 — verify

```bash
sudo mount /mnt/nas-pi-backups
sudo /home/pi/github/RonR-RPi-image-utils/image-info /mnt/nas-pi-backups/pivac.img
ls -la /mnt/nas-pi-backups/pivac.img
sudo umount /mnt/nas-pi-backups
```
`image-info` should show two valid partitions (boot vfat + root ext4). Size should match what was on the SSD.

### Phase 4 — detach the temp SSD

David needs the SSD back. After Phase 2 completes:
```bash
sudo umount /mnt/tempssd
sudo eject /dev/sda
```
Then David physically unplugs.

### Going forward

Monthly cron will run `image-backup` (no `-i`) against `/mnt/nas-pi-backups/pivac.img` directly — incremental rsync of only changed files. The cron + service-stop wrapper script isn't yet written; create it as `/usr/local/bin/pivac-monthly-backup.sh` with the same stop/start service list as Phase 1, and add an entry to `/etc/cron.d/`.

A weekly `rpi-clone` backup to a USB SD reader + spare card is also planned but on hold until David buys the hardware.

### Restore (for reference, not part of bootstrap)

To restore from a `.img` on the NAS:
1. Mount the NAS share on a Mac (or any machine with Raspberry Pi Imager)
2. In Pi Imager: "Use Custom" → select `pivac.img` → write to a fresh SD card (≥ 128 GB)
3. Insert the new SD into the Pi and boot. The first boot will auto-expand the root filesystem to the full card.
4. To pick a specific historical version, mount the matching DSM snapshot of the `pi-backups` share before reading the .img.

### Known gotchas

- Run inside `tmux` — xrdp/SSH drops will SIGHUP a foreground rsync.
- The first time you `mount /mnt/nas-pi-backups`, all NAS access must be done as root (`sudo`). The share's ACL only grants `user:root` and `group:administrators`. Non-root Pi users get permission-denied even though the unix bits look open. This is by design.
- If image-backup ever complains about missing `parted`, `losetup`, `kpartx`, or `rsync`: install with `sudo apt install -y parted kpartx rsync` (all should already be present on Raspberry Pi OS).
