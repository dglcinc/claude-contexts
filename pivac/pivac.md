# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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
