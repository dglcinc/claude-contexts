# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Sentry decode margin (PR #176) and the I/O boards ready to order (PR #175); 2026-09-12, Mac Mini
>
> **Sentry:** the 09-09 quad read every `6` as an `8` (its tens `b` rectangle sat in the top
> bar's IR bloom); a quad that fixed the cold display failed the hot one, and the lit bounding
> box was identical in both, so the digit content was the difference. `_SEGMENT_RECTS` now
> sample the middle of each segment, the quad is `TL(1102,564) TR(1263,559) BR(1253,628)
> BL(1095,636)`, 100 % clean with margin 64–70 at water 87, 149 and 116 °F. The reader publishes
> `decodeMargin`/`decodeMisses`, `sentry-decode-margin` alerts on an hour's mean under 20, and
> the bridge mails a capture + eyecheck on any firing `source: sentry` rule. The Pi runs the PR
> #176 branch. **Boards:** relaid to David's housing measurements — INT link headers in the
> right-hand slot (y 26–59), nothing over the Pi's USB stacks (plan A.3 maps the Pi 4B drawing
> at the 16 mm stack), every part ≤ 8 mm (axial capacitor flat between J4 and J6, PTC flat, MOV
> and proto field gone), silkscreen tidied, locked pre-routes; EXT J1 against the riser field
> so the housing opening stays clear. Both DRC clean; Gerbers, copper plots,
> `docs/rpi-io-boards-review.md` (designator tables, checks done) and
> `docs/rpi-io-boards-parts.md` (Phoenix 1778641/1778654/1778638/1778861/2202992, LTV-847,
> DS2482S-100+, MAL202138101E3, 60R010XU).
>
> **Next:** David orders from OSH Park with the Gerber zips in OneDrive `Claude/` (not the
> `.kicad_pcb`: OSH Park runs KiCad 9) and the parts list; then #175 out of draft and merged.
> Merge #176; on the Pi `git checkout master && git pull`, restart `pivac-sentry` and
> `grafana-graph-bridge`; `git pull` on the M2. After the boards: populate, test per
> `rpi-io-board-design.md` 7–8 and `ds18b20-bus-topology.md` §8, swap in, retire the build docs.
> **Carried:** heating commissioning per plan §5; first heating week's energy balance; print the
> label; Loop B HIGH and 140 °F offsets; bus topology §7.2; re-measure glycol; Y-strainer mesh;
> Wilhelm #155/#156; label the override relay; a plausibility floor for Sentry `air`.
>
> **Notes:** choose a Sentry quad on margin across ±1 px neighbours on captures from both
> thermal states; widening the rectangles makes both worse. Freerouting is stochastic (loop
> until DRC 0/0/0) and trims unlocked pre-routes; `build.sh` failures are silent when output is
> filtered; `gen-schematics` churns both boards' UUIDs. Pages: review
> https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 , Sentry eyecheck
> https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

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
