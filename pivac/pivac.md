# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — rev B boards and parts ordered; PR #214 open; 2026-09-27, M2
>
> Session 75 (2026-09-26/27, M2). First `sd-clone.sh` run on the new Pi's spare card done
> (4 m 19 s, disk id `f9199e61`). Rev B went from plan to order: `docs/rpi-io-boards-revb-plan.md`,
> the layout SVG, `docs/rpi-io-boards-revb-review.md`, and `hardware/` regenerated (build.sh
> retries route+DRC until clean, exports gerbers, copper plots, schematic SVGs). Both boards
> DRC-clean, nothing unconnected. David ordered the boards from OSH Park and parts from
> Digi-Key/Amazon on 2026-09-27; gerber zips also in `~/OneDrive - DGLC/Claude/*-revB-gerbers.zip`.
>
> **Next:**
> 1. Merge PR #214 and pull the Pi.
> 2. Boards arrive: populate per plan §7, bench-prove per plan §9 step 4 with the retired Pi.
>    Not in the cart: four PTSM 0,5/4 headers for the new INT; check three spare 3-way headers.
> 3. Install per plan §9 step 5 (transformer to EXT J3, pigtail to the Pi, adapter removed,
>    PivacPower Shelly to the transformer outlet, J8 pigtail retired, label J4 row). Rev A is rollback.
> 4. Open: KiCad 3D fit check; David's rev A edge-alignment observation on the 3- and 5-way headers.
> 5. Carried: glycol top-up; `P52` pump check; pump-step sentinel; 09-19 changeover firing;
>    kids room duty and master setpoint gap; return transfer plan (#198); first cold week record.
>
> **Notes:**
> - Rev B: 24 VAC on EXT J3, F1 60R110XU, D1-D4, C3 470 µF, U3 TMR 12-4811WI (SIP-8, pins
>   1,2,3,6,7,8), J4 XH → USB-C pigtail into the Pi's USB-C; GH 7-way link (INT J6 side entry,
>   EXT J1 top entry, pin 1 at the bottom); INT J4 = HPCOOL 13, DHWX 19, SP-E 16, J8 gone.
> - Hand-laid tracks: INT GPIO6 (F), GPIO24 (B), GND J6.5→TP3; EXT VS C3→D1, U2.1↔U2.8.
> - GH is Digi-Key only; PA/PH are the through-hole fallbacks; XA does not fit INT.
> - Pages: layout https://claude.ai/artifact/M8sBqVoureWu6L9ia9s1DF ; renders and copper
>   https://claude.ai/artifact/XydsRbY9nMBgi673MQvSrw ; monogram https://claude.ai/artifact/SKAZqP4qcRNdWFSPCgBLPx

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
