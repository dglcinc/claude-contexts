# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Kids room long call is open-plan mixing, not ISU 3140 (#201 merged); zone setpoint spread alerts (#202 open); 2026-09-17, Mac Mini
>
> Session 66 (2026-09-17 morning, Mac Mini). The kids room called for 11 hours (15:56–02:39) after
> ISU 3140 went to 2; the record shows load, never the setting: the room held 73 °F, prior full-duty
> stretches of 9 and 10 h exist, and from 04:19 it cycled 12–22 min on / 10–18 off at 51 % duty (two
> cycles an hour). 3140 has a rate per cooling stage on a two-stage Prestige; David has both at 2 on
> kids and master. Loop A ΔT on kids calls follows fan stage and the tank band (ΔT ÷ (room − supply)
> 0.12 cycling, 0.16–0.22 at full demand; 2.0–2.5 °F on 55–57 °F supply, 3.6–4.9 °F on 50–52 °F).
> David's open-plan mixing theory holds: with the kids setpoint alternating 73/74 °F across all
> periods at matched outdoor temperature, duty at 73 is 1.5 × duty at 74 (0.72 vs 0.53 evenings), the
> ratio of the gaps to the family room's steady 76 °F, and the family room's duty drops when kids is
> at 73. All into Appendix J and the CLAUDE.md RedLink rule (#201, merged, 5b3b7a6). David set the
> family room to 74 °F on 09-17 (kids 74, master 75, great room 75, kitchen 76). House rule: zone
> setpoints within 2 °F. PR #202 (open) adds `zone-setpoints.yaml`: `zone-coolset-spread` /
> `zone-heatset-spread`, info, any pair > 2 °F for 2 h, gated on `HPCOOL` / `HPHEAT`,
> `repeat_interval: 24h`; tested on the Pi (inactive live, cooling pending at a 1 °F threshold) and
> the rule file is already live in `/etc/grafana/provisioning/alerting/`. Pi clone on master 5b3b7a6.
>
> **Next:**
> 1. Merge #202, then `git pull` on the Pi (rule file already deployed; nothing else to do).
> 2. After several days at family room 74 °F: kids room duty at matched setpoint, period and outdoor
>    temperature against the month to 09-17 (0.51 aft/eve, 0.42 morning, 0.37 night at 74 °F); family
>    room duty should rise from 0.15. Also the 15-on/15-off call-length distribution by compressor state.
> 3. Not checked last night: does `hvac.chiller.chiltrix.waterFlow` read 0 at idle under `P52` = 2?
>    Overnight samples showed 6.9 L/min at Hz 0, so the trickle may persist; confirm on a longer idle
>    gap, then decide on `chiltrix-zero-flow`'s window and compare `.startupFlow` across the change.
> 4. Return transfer plan (#198): a transfer path couples the kids room harder to the hallway, so close
>    the setpoint gap first and re-read the plan against the mixing finding.
> 5. Count `hz432-mode-changeover` firings over weeks; common → build the §7.1 interlock; rare →
>    bedrooms on one mode per day. Confirm on site: valve wiring, where `ZV` picks up, old CDP lockout.
> 6. `P12` stays 2; revisit next spring. 7. First real bridged call: `DHWX` 1, `ZV` 1, `BLR` 1, `DHW` 1,
>    `HPCALL` 0, `IN` toward the tank. 8. Board swap: `HPCOOL` needs `SP-C`/`SP-E` from J8 on rev A.
> 9. First cold week: standby kWh, starts, defrosts (`r216` candidate; `r217` = 1 unexplained).
> 10. Plan §11: rooms' drop during refused calls; ISU 9000/9070; ΔT panel limits; Sentry mount;
>     Y-strainer ~10-12; manual v1.9; carried items. Master bedroom 71 → 75 °F on 09-15 with no call.
> 11. Observations: no Grafana rule on `electrical.emporia.*`; Emporia re-logs in every cycle in an outage.
>
> **Notes:**
> - Zone analysis method: hourly `aggregateWindow` of `environment.inside.thermostat.<ZONE>.{statenum,coolset,temperature}`
>   over a month, duty = clip(−statenum, 0, 1); `coolset`/`heatset` are stored in °F, `temperature` in K.
>   One-minute "breaks" in a long call are missing RedLink samples (humidity absent the same minute).
>   pandas lives in `~/pivac-venv` on the Mini (system python3 has none).
> - Grafana math has no max/min across queries: pairwise `abs()` ORs. Per-rule `notification_settings`
>   accepts `repeat_interval`. Prove a rule can fire by lowering the threshold on the Pi's /etc copy,
>   restart, read state from `/api/prometheus/grafana/api/v1/rules`, then restore from the repo copy.
> - Prestige install guide: Resideo 69-2490 (lists each ISU once; per-stage fields appear on the screen).
> - Session 65 notes still apply: Emporia backfill script; one measurement per `influx query --raw`;
>   782 sockets (9–12 commons, 5–8 NO, 1–4 NC, 13/14 coil; pole 1 spare NO shares the Chiltrix common);
>   Prestige installer path; RedLink `fan` statenum 0.5; alert YAML test recipe; PivacR uid
>   `bdxar09dh34sgc`; relay rename recipe.
> - Pages: board review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ; Sentry
>   eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a ; an abandoned
>   Claude Doc "Kids Room Return Transfer Plan" can be deleted.

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
