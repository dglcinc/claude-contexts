# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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
