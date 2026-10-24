# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

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
