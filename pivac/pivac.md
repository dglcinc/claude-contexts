# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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

`nas-image-backup.timer` runs `image-backup` (no `-i`) against `/mnt/nas-pi-backups/pivac.img` on the 1st of each month at 03:00, stopping the disk-writing services first and restarting them on exit. `sd-clone.timer` runs `rpi-clone` to the spare card in the USB SD reader every Sunday at 02:00. Both are described under Backup Automation in `~/github/pivac/CLAUDE.md`.

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
