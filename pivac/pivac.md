# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — a chiller lockout nothing alerted on, and the alarm that now catches it (2026-09-06)
>
> **Nothing is pending on the machine.** `chiltrix-zero-flow` is merged (PR #154) and deployed:
> 23 rules and 0 paused in the `alert_rule` table, 23 Signal K notification paths, every service
> active, no warnings. Eight days of Chiltrix data were reviewed end to end — 10,396 minute-buckets,
> 212 compressor cycles, all 181 registers.
>
> **A closed isolation valve during Thursday's glycol top-up locked the chiller out for sixteen
> minutes (2026-09-03, 16:19–16:36 EDT) and no alert fired.** Inlet reached the 54.7 °F restart
> band, the controller commanded the pump to 100 %, flow read 54.0 for one cycle and **0.0** the
> next, register `284` went to **32**, the controller stopped the pump, and the loop coasted to
> **62.2 °F** before the unit released itself and restarted to 60 Hz. Zones held setpoint
> throughout, so there was no comfort consequence.
>
> **⚠️ The fouling alarm is structurally blind to a total loss of flow.** Through the whole
> lockout `startupFlow` published **54.0 L/min — the highest value of that week** — because the
> module captured the one 54.0 sample from the aborted start's plateau and then discarded every
> subsequent 0.0 as sub-floor idle trickle. **The 15 L/min floor that keeps the deep-idle trickle
> out of the plateau also throws away a genuine zero**, so a zero-flow fault reads as the healthiest
> possible state. Fouling is gradual and `startupFlow` catches it; a closed valve is instantaneous
> and only the new rule catches it.
>
> **⚠️ Guard on `max`, never `last`, when the guard is the device's own on/off state.** The
> controller switched *itself* off (register 140 → 0) for the last 4 minutes of its own lockout, so
> a `last` reducer would have disarmed the rule partway through the event it exists to catch.
>
> **`POST /grafana/api/v1/eval` with a back-dated `now` evaluates a whole expression chain without
> saving a rule.** That proved the rule before shipping — fires 16:28–16:37 on the real event,
> clears on recovery. Replayed over 12,370 minutes it fires eleven times, and **the ten before the
> 08-29 cleanout are the fouled regime rather than false positives**: with the strainer clogged the
> idle trickle fell under the meter's detection floor and read a clean 0.0 between cycles, through
> the very period the alarm set was silent. Reuse this endpoint for any rule with a math node.
>
> **Register `284` is the fault/lockout word** — 32 through the lockout, 0 for every other sample of
> the surrounding eight days. **The `P5` code was never confirmed and now cannot be**: the panel
> error log read empty on 09-06, already cleared. It rests on the mechanism plus CX65 IOM p70, which
> names insufficient flow **and air in the lines** as the two `P5` triggers — and a fill introduces
> air, so an open valve does not rule out an air lock. **No register latches a code and the panel log
> is erasable, so the InfluxDB record is the only durable evidence a chiller fault happened.**
>
> **⚠️ The antifreeze margin at the 10 °C target is zero, not 2.2 °F.** Forty running minutes came in
> at or below 38.5 °F leaving water, the minimum reaching **exactly the 37.40 °F `P59` trip** on
> 09-02. All are end-of-run at full flow, so they are the normal stop transient. **Widening `P12`
> before raising the target would push them under**, which makes the target raise a prerequisite.
> Adding glycol does not help: `P59` trips on a fixed temperature and knows nothing about concentration.
>
> **The glycol top-up moved the fouling baseline** 52.9 → 51.7 L/min, one quantization step. Four
> other measurements stepped with it at the same hour — idle trickle 6.9 → 5.7, flow lower at matched
> compressor speed in three of five Hz bands, evaporator ΔT one step wider. No single move means
> anything; five together in the direction viscosity predicts is the signal. **Read 51.7 as clean, and
> record the date of any top-up.**
>
> **`P95` 5 → 3 (made 08-30) has not moved starts/day**, matched on ambient (33.7 → 35.7, 41.6 → 38.1,
> 23.6 → 32.3). The pre-change window is only 25 h, so this is weak evidence rather than a refutation.
> The cycling reduction now rests on change 2.
>
> **Modbus link health is excellent** — 6 cycles below 181 registers out of ~8,400 in seven days.
> Cadence is `daemon_sleep: 60` giving ~70 s, not the ~6.8 s at 30 the docs had claimed.
>
> **Next:** tuning change 2 (12 °C target + `P12` = 3, as a pair, register 142 read back); confirm
> `r284` = 32 at the next lockout using **Error Reset**, never **Clear**; confirm `P65` on the panel
> (register 65 reads 14 against a documented 20); hot-day zone-droop check at the raised target; the
> carried-over probe swing/strain-relief checks; four open PRs (#94, #117, #124, #125).

This section holds one handoff. When `/save-context` adds the next, move this one to the top of `archive/handoffs.md`, newest first. `/set-context` reads only the `*.md` files in this folder, so the archive stays out of context.

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
