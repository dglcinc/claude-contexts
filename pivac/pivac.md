# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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

**Access notes**: M2 MacBook = `david@10.0.0.109` (SSH key from the Mini works; Arduino repo at `~/github/Arduino`, GUI IDE only). UniFi **APs** take SSH key auth as `dglcinc` (e.g. `KitchenAP` 10.0.0.78 — holds 2.4 GHz client logs); the **USG-3P** only takes username/password. This Mac's GitHub SSH had been broken — it caused a 25-commit-stale pivac checkout and repeated Arduino-mapping mislabeling; fixed by adding the Mini's `id_rsa` to GitHub. `gh` CLI token on the Mini is still invalid (HTTP 401).

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
