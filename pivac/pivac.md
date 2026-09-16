# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Chiltrix support answers in §9, P52 = 2 set, Emporia outage backfilled, kids room CPH 3140 = 2 (#195–#197 merged); 2026-09-16, Mac Mini
>
> Session 65 (2026-09-16 evening, Mac Mini). Chiltrix support's answers went into plan §9 (#195):
> `P52` = 2 concurred and set on the panel at 18:10 EDT (`raw.r52` reads 2), no slush at 30 %, `C17`
> runs the pump at full speed at the antifreeze temperature, cycle count and oil return no concern,
> `C16` reports defrost, register 143 read/write (pivac stays function 03), heating target stays 50 °C
> by David's decision. The module polls 215–217 as the `C16`/`C17` candidates on the 200 + n
> hypothesis (`C13` = 213); first readings `r215` 164, `r216` 0, `r217` 1. Emporia's cloud returned 400
> on `/customers` 13:11–15:52 EDT with RedLink normal (Emporia-side, self-healed, first 400 ever); the
> 162-minute gap was backfilled from the cloud through the module's own summing path with the new
> `scripts/emporia-backfill.py` (2,430 points, `main` within 0.7 W of the chart at the poller's
> one-minute lag) (#196). The kids room's cycling (51 calls/day, 10 on / 10 off at 50 % duty) was the
> Prestige's ISU 3140 = 3; David set it to 2 on kids and master; the coil is sound (3.7 °F loop A ΔT
> calling alone on warm tank water, zero droop); staging 3010 Advanced, 3020 No, 3030 Comfort, stage 2
> = air handler high fan, invisible in RedLink (#197). Pi on 0cef5d0, registerCount 184.
>
> **Next:**
> 1. Tonight: does `waterFlow` read 0 at idle under `P52` = 2 (first samples still 6.9)? If so
>    `chiltrix-zero-flow` fires ~10 min into each idle gap: widen its window to ~45 min (three pump
>    restarts) or change the signal; compare `.startupFlow` across the change.
> 2. After 09-18: kids room calls ~15 on / 15 off from `KIDS_ROOM.statenum`.
> 3. `P12` 2 → 3 (David's follow-up, due since 09-16 17:00 EDT); read register 12 back.
> 4. First real bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1, `HPCALL` 0, `IN` toward the tank.
> 5. Bedrooms fight in the shoulder season: both on Heat at night or raise the kids cool setpoint.
> 6. Board swap: `HPCOOL` needs `SP-C`/`SP-E` from J8 on rev A.
> 7. First cold week: standby kWh, starts, defrosts (`r216` candidate; `r217` = 1 unexplained).
> 8. Plan §11: rooms' drop during refused calls; ISU 9000/9070; ΔT panel limits; Sentry mount;
>    Y-strainer ~10-12; manual v1.9; carried items. 9. Master bedroom 71 → 75 °F on 09-15 with no call.
> 10. Observations: no Grafana rule on `electrical.emporia.*`; the module re-logs in every cycle during
>     a cloud outage.
>
> **Notes:**
> - Emporia backfill: `scripts/emporia-backfill.py --start/--end` (UTC, bounded by the last and first
>   live points), dry run then `--write`; a point at HH:MM:55 carries minute HH:MM−1.
> - Analysis: one measurement per `influx query --raw` over ssh (1 m, or 10 s/raw for toggles), CSV to
>   the scratchpad, pandas on the Mini; Emporia lags Modbus 1–2 min.
> - PivacR uid `bdxar09dh34sgc`; relay rename recipe: config `outname`, `baseDeltas.json` order,
>   LoopDelta `relay`, dashboard, docs; `restart pivac-gpio pivac-loop-delta` then `signalk`.
> - Prestige IAQ 2: Menu → Installer Options → date code → Installer Setup; 3140 needs 3010 Advanced.
> - RedLink `fan` statenum is 0.5. 782 sockets: A2 bus bar may be fitted, A1 bar must not.

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
