# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

*Updated 2026-05-08 (later in the day)*

**Last worked on**: Both backup-architecture layers are now running. PR #44 (NAS image-backup timer) merged earlier in the session as `a80e251`. The USB SD reader + spare 128 GB card finally arrived, so the hot-recovery layer was wired up: installed billw2/rpi-clone to `/usr/local/sbin`, validated end-to-end with a full clone (29m 19s) plus an automated incremental (2m 7s), shipped `scripts/sd-clone.{sh,service,timer}` via PR #52 (squash-merged as `725b26e`). Updated pi-CLAUDE.md (direct push to claude-contexts main) and pivac/CLAUDE.md (in PR #52). Also resolved a separate OpenSprinkler-not-connecting issue — turned out to be an app-side config problem, not Pi-side.

**Next steps**:
1. **Physical card-swap boot test** — pull the live SD, drop the cloned spare in, confirm it boots. Needs hands at the Pi.
2. Verify the first scheduled SD clone run — Sun **2026-05-10** ~02:06 EDT via `journalctl -u sd-clone.service`. Should be incremental, ~2 min.
3. Verify the first scheduled NAS image-backup run — **2026-06-01** ~03:00 EDT via `journalctl -u nas-image-backup.service` and confirm `pivac.img` mtime advances on the NAS.
4. *(deferred)* Verify the `redlink-stale` Grafana alert fires the next time pivac-redlink is offline >30m.

**Notes**:
- **Both timers installed and enabled.** `nas-image-backup.timer` (monthly, 1st @ 03:00 EDT) and `sd-clone.timer` (weekly, Sun @ 02:00 EDT +/− 15m jitter). 1h gap prevents collision when the 1st of a month falls on a Sunday.
- **rpi-clone is live-safe** — no service stop, unlike `image-backup` which requires service quiesce. A weekly clone that captures live state is fine for hot-recovery; the monthly NAS image is the consistent backup.
- **Insignia NS-DCR30A2 reader is 4-LUN.** All four slots share the same model string; only the slot with media has non-zero size. The script picks by model + size > 0, refuses if multiple slots populated, refuses if target == booted disk.
- **rpi-clone install:** source at `~/github/rpi-clone/` (billw2/rpi-clone), copied to `/usr/local/sbin/` — see pi-CLAUDE.md.
- **Stacked-PR gotcha hit during PR #44 merge:** squash-merging a parent with `--delete-branch` auto-closes child PRs and blocks reopen. Recovery is cherry-pick onto new master + new PR. Documented globally in `~/.claude/memory/tools/gh-stacked-prs.md`.
- **OpenSprinkler `/sprinkler/` proxy** has no Basic Auth despite CLAUDE.md claiming it does — docs drifted, not blocking anything. Native OS app only works at root URL, not under a path prefix; if mobile-app access becomes important, set up `sprinkler.dglc.com` subdomain mirroring the bowling-app pattern.
- **Local SSD copy** at `/mnt/tempssd/pivac.img` retained as a cold spare; SSD unmounted by default.

---

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

Monthly cron will run `image-backup` (no `-i`) against `/mnt/nas-pi-backups/pivac.img` directly — incremental rsync of only changed files. The cron + service-stop wrapper script isn't yet written; create it as `/usr/local/bin/pivac-monthly-backup.sh` with the same stop/start service list as Phase 1, and add an entry to `/etc/cron.d/`.

A weekly `rpi-clone` backup to a USB SD reader + spare card is also planned but on hold until David buys the hardware.

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
