# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — rev B INT + rev C EXT bench-proven and in production; boiler camera recalibrated; 2026-10-11, M2
>
> Session 76 (2026-10-11, M2). Prepped the `pibench` card from the M2's reader (`--revb` walk script
> from PR #228, `w1-proof.sh`, cloud-init instance bumped), bench-proved the rev B INT and rev C EXT
> set (5.09 V at J4, 35 V at TP1–TP2, COM open to GND, all twelve channels PASS, probe 40/40 clean on
> H1 and H2 through a replaced DS2482), then cut production over to it the same evening on the
> production Pi `88:a2:9e:3c:c3:73` and its own card: writers stopped 19:25, clone verified, Pi back
> 19:43, every path live, no alerts. Three harness faults on the way: pigtail black lead in `+5`
> (Pi survived), GH link mirrored 1↔7 (35 V on SDA killed GPIO2 on bench Pi `2c:cf:67:80:55:00`),
> 24 VAC plug seated in H1 with power on (killed the DS2482). The swap knocked the boiler camera
> ~200 px; David re-aimed by hand with a live readout, then the residual was registered offline
> against `/var/lib/pivac/sentry-registration.npz` (−65, −12 px), lenses re-aimed, search applied,
> reader back at margin 92. CLAUDE.md on master records all of it.
>
> **Next:**
> 1. David merges #232 (label, printable copy on the M2 Desktop), #231 (bench record, install note,
>    plug/link/pigtail corrections, Sentry notes, `w1-proof.sh`), #230 (test pads), #228 (`--revb`).
> 2. Order a backup board set.
> 3. Add an offline-registration option to `scripts/sentry-warp-search.py` (rebase quad and lenses
>    from the saved reference over a wide window) so the next large knock needs no ad-hoc code.
> 4. Next EXT revision (rev C plan §9): a 24 VAC connector that cannot enter a probe socket, labelled
>    test pads, pin-1 legend on the GH headers.
> 5. Carried: `P52` = 2 pump check; pump-step sentinel; exclude the 09-19 changeover firing; kids
>    room duty and master setpoint gap; return transfer plan (#198); first cold week record.
>
> **Notes:**
> - Bench Pis share the `pibench` card and take DHCP leases (find by MAC on the UCG): `2c:cf:67:80:55:00`
>   walks channels only (GPIO2 and GPIO26 dead); `dc:a6:32:19:12:ee` does I2C/1-wire (BCM 13, 25 dead,
>   16 pull-up dead).
> - On rev B INT the sense rail feeds the opto anodes; the 12 kΩ sits between cathode and plug.
> - A PTSM plug with fewer positions enters a larger socket.
> - `pkill -f "io-board-tes[t]"` in an ssh command line that also names the script kills the session.
> - Rev C EXT's probe sockets and 24 VAC entry sit at the opposite ends from the rev A board's; the
>   rev C orientation is the one to keep.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .
>>>>>>> Stashed changes

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
