# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — the two Phoenix I/O boards as KiCad designs; PR #175 draft (2026-09-10/11, Mac Mini)
>
> Sentry after the 09-09 quad change: 229 warnings in 22 h against 964 the day before,
> `outdoorTemp` on 97 % of cycles, no gap over 15 min; #174 is ready to merge. Then the
> fabricated-PCB project: `docs/rpi-io-boards-pcb-plan.md` (OSH Park bare boards, hand assembly),
> the Phoenix STEP models parsed by `hardware/step-geometry.py` (the housing's restricted areas
> are modelled as a 0.02 mm solid on the solder face), and `hardware/gen-boards.py`, which places
> and nets both boards with pcbnew: 24 VAC sense supply on J4.1/J4.2 (PTC, four 1N4007, 220 µF,
> 12 kΩ 1/4 W for 2.8 mA at ~35 V), PTSM 0,5/5 link headers at both ends, a shadow column breaking
> out the free header pins, an unfitted 4-way power link; the EXT board keeps the built socket and
> link positions and adds an unfitted second DS2482 (0x19) and the rollback jumper.
> `hardware/route.py` routes with Freerouting 1.9.0 (2.4.1 writes an empty session file); both
> boards route completely with no electrical DRC errors. `hardware/gen-schematics.py` writes
> schematics from the shared `gen_tables.py`, ERC clean, netlists matching the boards pin for pin;
> `hardware/bom.py` exports the BOMs; `hardware/build.sh` chains it all. KiCad 10 lives in
> `~/Applications` on the Mini (copied from the DMG; the cask wants sudo), OpenJDK via Homebrew,
> Freerouting in `~/Applications/freerouting`.
>
> **Next:** David reviews renders and schematics and checks a spare PTSM plug at the INT board's
> bottom edge and the 12.5 mm capacitor against the cover; then Gerbers, 3D fit, the OSH Park
> order, and #175 out of draft. Merge #174 and pull on the Pi and M2. **Carried:** heating
> commissioning per plan §5; first heating week's energy balance; print the label; Loop B HIGH and
> 140 °F offsets; bus topology §7.2; re-measure glycol; Y-strainer mesh; Sentry LED swing; Wilhelm
> #155/#156; label the override relay; a plausibility floor for Sentry `air` (two 0 reads).
>
> **Notes:** decisions 2026-09-11 — the Pi stays on its USB-C adapter (no isolated 24 VAC-to-5 V
> part exists; plan §4.3 records the DDR-15L-5 two-part route), header pin 1 verified top-right
> component side up, transformers 75 VA, clearance assumed pending David's check. Header pins 9,
> 25, 39 (GND) are left open, the outer-column grounds ride a pre-routed edge bus. The DEV-KIT
> housing STEP is parts side by side, not an assembly. Plan §7 holds two model-vs-doc
> discrepancies (EXT 33 rows; INT column 3 holes).

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
