# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — SP-E proven through the J8 pigtail; CHIL and SP-C wait for the new Pi or the meter; 2026-09-26, M2
>
> Session 73 (2026-09-26, M2). Proved SP-E on the rev A INT board through a PTSM-3 header in the
> EXT proto field wired to J8, on the old bench Pi (`dc:a6:32:19:12:ee`, `pibench`, 10.0.0.71) with
> the full INT+EXT assembly seated. Its BCM 16 has a dead pull-up only: driven high it holds, and two
> shorts of J8.2 to J8.3 pulled it low with no other pin moving, so the pigtail, R12, U3's SP-E
> channel and the trace to pin 36 are proven. BCM 13 and 25 are dead outright, so CHIL and SP-C
> stay unproven. Ten of twelve channels proven. PR #209 open (assembly doc bench record, meter
> procedure for CHIL and SP-C, refined dead-pad rule). The new Pi has not arrived.
>
> **Next:**
> 1. Merge #209.
> 2. CHIL and SP-C: the meter off the Pi (power J4, short J2.1 or J8.1 to COM, header pin 22 or 33
>    conducts to TP3 in diode mode while shorted), or the new Pi with `io-board-test.py --only 4`
>    and `--only 11`.
> 3. New Pi: boot the bench card, read all twelve pins high bare, run the full guided walk once.
> 4. J8 pigtail with strain relief (SP-C = `HPCOOL`, SP-E, COM) and the 5-way link cable.
> 5. Housing swap per `rpi-io-boards-pcb-plan.md` §6 steps 6–8: freeze and clone first; J4.1 24 VAC
>    hot, J4.2 return (unlabelled), HPCOOL to J8 SP-C, J4.4 stays J4's COM; prove `HPCALL` on the
>    first call, the 1-wire bus, Sentry `decodeMargin`/`registrationScore`.
> 6. Carried: glycol top-up (premixed, record the date); `P52` = 2 pump check; pump-step sentinel;
>    exclude the 09-19 changeover firing; kids room duty and master setpoint gap; return transfer
>    plan (#198); first cold week record.
>
> **Notes:**
> - `pkill -f <name>` from an ssh command line that contains the name anywhere kills the ssh
>   session. Kill in its own call with `pkill -f "j8watc[h]"`, start the script in a second call.
> - `~/j8watch.sh` on the bench Pi polls the twelve channel pins every 50 ms for four minutes and
>   logs changes to `~/j8.log` (`setsid nohup sudo ~/j8watch.sh > ~/j8.log 2>&1 < /dev/null & disown`).
> - Read a low pin on the bare Pi (`pinctrl set N ip pu`, `get`, then `op dh`) before blaming the
>   board; the dead pads read low with the board seated too.
> - Session 72 notes still apply: J4.2 unlabelled and never COM; socket pin order (bottom 1–8 from
>   the left, top 9–16 from the right); C pins U1 10 CHIL, 12 BLR, 14 DHW, 16 ZV; U2 10 SCALA, 12
>   DEHUM, 14 BOS2, 16 BOS1; U3 10 SP-E, 12 SP-C, 14 SP-D, 16 HPHEAT; 11 relays on 10 plug
>   positions; card writing on the M2 via `/dev/rdisk15`.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

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
