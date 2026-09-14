# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Chiltrix September findings and the loop drain-and-refill procedure (#181, #182 merged); 2026-09-14, Mac Mini
>
> Two weeks of Chiltrix data (08-29 → 09-13, 390 runs) reviewed and folded into the docs (#181):
> P95 5→3 raised the ≤26 Hz leaving-water floor 36.7→39.9 °F with no cycling effect; every near
> miss since is a surge-terminated run (25→47–60 Hz in the last 1–3 min, 5 % of runs, min 37.22 °F
> on 09-08 with r284 = 0) while steady running keeps 3 °F of margin; the start ramp is fixed at
> 50–52 Hz by minute 3, so night runs are 11 min with 36 min gaps; target still 10 °C and P12 still
> 2; cooling COP 4.9 all-in, 5.5–7.4 running, 0.82 kWh/°F of OAT above 48 °F; first heating run
> 09-08 (85 kBTU/h from 3.2 kW, cool-back 36 min / 1.13 kWh). Three sub-minute heating blips on
> 09-13 were mains outages (Pi reboots ~13:05 and ~20:48), now a rule. Then
> `docs/hydronic-drain-and-refill.md` (#182): the Pacific Hydrostar 65836 (120 ft head) fills to
> the attic coil (53 ft needed) with the 30 psi boiler relief as the thing to guard; zone valves
> open, high vents before low drains, air blow-down by zone, pre-mix 30 % PG in a drum, closed purge
> cart, `startupFlow` 51.7 L/min as the proof. Pi on master; docs only, no restart.
>
> **Next:** Chiltrix plan change 2 (target 12 °C in whole °C, read 142 back, then P12 3); if the
> loop is drained, follow the doc and record the new glycol reading; reconcile the `CHIL` contact
> with 17 % of starts occurring with it open; watch Sentry `registrationX/Y/Score` and add a panel;
> boards and parts arriving (populate, test on the spare Pi, swap in); Y-strainer around 10-12.
> **Carried:** heating commissioning per plan §5; first heating week's energy balance; print the
> label; Loop B HIGH and 140 °F offsets; bus topology §7.2; Wilhelm #155/#156; label the override
> relay; a plausibility floor for Sentry `air`.
>
> **Notes:** InfluxDB analysis is one measurement per query at 1 m over ssh, pandas on the Mac
> (`~/pivac-venv` on the Mini now has it). Water-side Q from the chiller's own sensors, ±10 %.
> Drain-and-refill facts to confirm on site: relief valve setting, CX75 drain plugs, zone-valve
> manual lever. Pages: review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ,
> Sentry eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

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
