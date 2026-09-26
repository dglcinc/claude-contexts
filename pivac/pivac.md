# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Rev A boards arrived; assembly bench sheet merged (PR #206); Pi still needs a pull; 2026-09-25, Mac Mini
>
> Session 71 (2026-09-25, Mac Mini). The rev A boards arrived from OSH Park. Wrote
> `docs/rpi-io-boards-assembly.md`, the bench sheet for populating them: order of work (flattest to
> tallest, EXT first, Pi socket last on the spare Pi as a jig), a three-column table per board of
> reference, invoiced part and location with the handling notes as a numbered list under it, the checks
> with rev A's values (12 kΩ per channel, about 35 V on VS), the link cable and the housing swap.
> `docs/rpi-io-boards-parts.md` now cites Mouser invoice 92489596 (shipped 2026-09-14, PDF in the
> OneDrive Claude folder), which carries the five MAL202138101E3 for INT C1 that the 09-12 cart lacked.
> Merged as PR #206 (7bb3321). PR #205 (changeover interlock deferred) is still open; the Pi is at 5078b76.
>
> **Next:**
> 1. Merge PR #205 and pull on the Pi (brings #206 too).
> 2. Assemble one INT and one EXT board per the sheet; bench-check on the spare Pi; make the 5-way link
>    cable; swap into the housing per `rpi-io-boards-pcb-plan.md` §6 steps 6–8. `HPCOOL` (BCM 13) is
>    `SP-C` on the J8 pads, a soldered wire; `SP-E` (BCM 16) is free for `Y2` logging. Check Sentry
>    `decodeMargin` and `registrationScore` after the visit.
> 3. Hydronic pressure 20.2–21.8 psi since the filter install: top up with premixed 30 % glycol, never
>    through the demineralised fill, and record the date.
> 4. `P52` = 2 has not stopped the pump (idle flow 6.9 L/min all day on 09-18); check a later day, then
>    ask Chiltrix support if it never stops.
> 5. Pump-step sentinel on each month's strainer check; decide whether it earns a panel or derived path.
> 6. Exclude the 09-19 12:45 changeover firing (power return) from the count; confirm valve wiring,
>    where `ZV` picks up, and the old CDP lockout on site.
> 7. Kids room duty baseline 09-18 (0.41 at 73.5 °F mean outdoor); master bedroom is the next
>    setpoint-gap question. Kids dehumidify never engaged on 09-18.
> 8. Return transfer plan (#198) re-read once the setpoint gap has data. `P12` stays 2. First cold week:
>    standby kWh, starts, defrosts (`r216`; `r217` = 1 unexplained). The 5.5 gal/min draw under the
>    09-17 16:40 shower is unexplained.
>
> **Notes:**
> - Rev A channel map: SP-D = BCM 19 = `DHWX` on J4.3; SP-C = BCM 13, SP-E = BCM 16 on J8; CHIL on J2.1 =
>   `HPCALL`. J9 carries none of the channel GPIOs, so the C-pin continuity check goes to the Pi header
>   pin (ZV 11, DHW 13, BLR 15, CHIL 22, BOS1 31, BOS2 29, DEHUM 32, SCALA 16, HPHEAT 18, SP-D 35, SP-C 33,
>   SP-E 36). EXT JP2 pads run left to right DATA · H3 · U2; the bus default is centre-to-left.
> - A requested "doc" is a `.md` in `docs/`, not a Claude Doc; short table cells, instructions listed
>   under the table.
> - Pressure analysis recipe: six measurements pulled one per `influx query --raw` with
>   `aggregateWindow(every: 1m, fn: mean)`, pandas on the Mini; a flow edge is `waterFlow` crossing
>   15 L/min (idle reads 6.9, never 0); step_on = mean of the first two minutes minus the three before;
>   fit `psi ~ flow²` and check the residual against the temperatures.
> - Analysis data pulls: one measurement per call with `aggregateWindow` on the Pi, tar to the Mac,
>   pandas in `~/pivac-venv` on the Mini; parse timestamps with `format='ISO8601'`. A 5-min `mean` of
>   `statenum` is duty; 1-min `min` gives call edges.
> - A boiler-room circuit outage: both Arduinos, their Shelly, the water meter, Sentry `waterTemp` and
>   `HPCOOL` all gone at once, chiller `switchOn` 1 with `compressorHz` 0 and `waterFlow` 6.9, five
>   staleness alerts at +30 min, and the changeover rule firing when `HPCOOL` returns.
> - Relays are stored as `electrical.ac.switch.utility.<NAME>.statenum`; the bare path returns nothing.
>   InfluxDB times are UTC. Leaving the Prestige installer menu restarts the staging.
> - Grafana: prove a rule fires by lowering the threshold in the Pi's /etc copy, restart, read
>   `/api/prometheus/grafana/api/v1/rules`, restore from the repo copy. Alert history:
>   `/grafana/api/annotations?type=alert`.
> - Session 65 notes still apply: Emporia backfill script; 782 sockets; Prestige installer path (Resideo
>   69-2490); RedLink `fan` statenum 0.5; PivacR uid `bdxar09dh34sgc`; relay rename recipe.
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
