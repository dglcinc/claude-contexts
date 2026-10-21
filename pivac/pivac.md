# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — MBR node installed and live; 2026-10-20, M2
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
> `AirHandler_MBR` on main is what the node runs.
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
