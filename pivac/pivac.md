# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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
