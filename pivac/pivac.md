# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — heating changeover built; assessment merged; CAT6 trunk (2026-09-08 evening, M2)
>
> The Unico assessment was refreshed against the Modbus feed, the loop probes and the clean-flow
> week and merged (#117): chiller band 54.3 → 44.8 °F at the inlet, evaporator ΔT 6.3 °F median
> with zero antifreeze margin at the end of a run, loop supplies on `IN` within 0.1 °F, distribution
> flow 8.8–13.1 GPM from the tank energy balance. The shoulder-season heating plan is merged
> (`docs/chiltrix-shoulder-season-heating-plan.md`): HZ-432 dual fuel with an outdoor balance
> temperature, the Chiltrix C-H-COM contacts, and one relay named HPHEAT on the panel's `B`
> terminal steering the `CHIL` contact between the cooling and heating pairs. David configured the
> panel (heat pump, dual fuel, conventional thermostats), wired and test-mode-proved the relay, and
> its spare pole is live on J3.3 / BCM 24 as `HPHEAT`; label regenerated, Relays panel updated
> (#170). The 1-wire trunk is CAT6 (a swapped conductor found and fixed; 8/8 probes, clean CRCs).
> A Pi restart on 09-07 19:40 was a power-on reset from bumping the power during the rewire.
> The Tapo camera was knocked in the same pull; the Sentry reader was recalibrated from 600
> frames captured on the M2 (display 58 px left / 87 px up, quad 99.3 % clean, air 68 vs RedLink
> 68.0, all eight LED/indicator spots re-aimed) and #166 records it. #167 left one full-width
> gal/min flow-rate panel on PivacR.
>
> **Next:** print the label; heating commissioning per the plan's §5 (factory C7089U sensor 09-09,
> override relay open or on the HPHEAT relay common, target 50 °C confirmed, live-call proof, OT
> balance 40 °F to start; Loop B HIGH and 140 °F probe offsets before heating season); bus
> topology §7.2 as-built; re-measure glycol. **Carried:** Chiltrix target direction (assessment vs
> cycling plan, DHC reconciles) next cooling season; old Pi shelved to ~09-21;
> Sentry LED swing on the next DHW call; `r284`/`P65`; Wilhelm #155/#156; label the override relay.
>
> **Notes:** register 111 does not track `P111` (panel is the reference; enabled). HZ-432 has
> separate `O` and `B` equipment terminals (`O` in cooling, `B` in HP heating). The override relay
> is holding the `C` call today (16 % of starts with `CHIL` open). EXT board hangs solder side out:
> H plugs read GND · DATA · VCC from the front. InfluxDB analysis: one measurement per query.
> The ACOL DN32 Y-strainer screen reads ~60–70 mesh from a full-res photo, so it likely meets
> Chiltrix's ≥60 mesh (0.25 mm) already; confirm with a ruler (24 wires/cm) and record the
> basket OD and length at the next cleaning. Rule and the exchanger's ~1.2 mm blocking limit are
> in CLAUDE.md.

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
