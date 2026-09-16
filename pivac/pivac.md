# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — First heat run analysed, HPCALL rename, DHWX bridge wired, chiller on all winter (#190–#194 merged); 2026-09-15, Mac Mini
>
> Session 64 (2026-09-15 evening, Mac Mini): first overnight heat run under option 2 analysed. Heat
> mode 04:37–09:04: the master's heat call flipped `HPHEAT` 1 / `HPCOOL` 0 / register 141 to 1 in the
> same minute; the panel held heat mode through calls and a 57-min idle (tank 130 → 125 °F, no run);
> the kids room (73–74 °F, on Auto) forced two changeovers by calling cool (05:12, 1.3 kWh wasted;
> 09:04, eight minutes of 100–118 °F water through its coil). Seven heat runs, 101 min, 6.4 kWh in,
> 29.9 kWh water-side, COP 4.7 at 54 °F (6.1 cold tank, 3.6–4.2 warm), 22–25 kW; heating band
> restart 116–119 °F return, stop 127–128 °F; tank tops 130–131 °F; changeovers 34 min / 2.0 kWh up,
> 33 min / 1.4 kWh down. Great room heat calls close `HPCALL` and run loop B: all five zones heat
> hydronically, kitchen and great room cool on Bosch. LoopDelta gained `heat_zones` and a fan-state
> fix (#190). Cooling band at 12 °C confirmed: stop 48.2–49.3 °F, restart 57.2–58.5, outlet min
> 40.6, ~18 starts/day. `CHIL` renamed `HPCALL` live and in the docs (#191; InfluxDB history under
> `CHIL`; `hardware/` keeps `CHIL`). DHW bridge designed and wired by David: `W1` through a `DHW`
> NC pole to the boiler, NO contact to a new `DHWX` relay closing the same Taco 503 input as
> `HPCALL` (`HPCALL` stays 0 on a bridged call); `DHWX` on J4.3 `SP-D` BCM 19, SwitchBank order 11,
> Relays series (J, +.15, green), LoopDelta primary `relay: [HPCALL, DHWX]`. `BLR` is `W1` upstream
> of the boiler (38 refused calls of 8–39 min last spring, circ LED dark). Heat-mode standby measured
> ~1,700 BTU/h at 60 °F (pump idling 8 L/min through the outdoor exchanger): ~$100 and ~1,400 idle
> starts plus defrost for a winter on. David decided the chiller stays on all winter; §9 rewritten,
> HMI off kept as the out-of-service procedure. The two `DHWX` presses at 22:43 reached the Pi (4 s,
> 2.5 s) but overlapped a kids-room cool call, so the pump start is unattributed on the record.
>
> Late: §9 corrected on defrost (#192), crankcase heater confirmed by Chiltrix support (#193), winter
> standby projection table from the measured UA with `P52` = 2 as the open question (#194); note to
> Chiltrix support drafted with three questions (`P52` = 2 and slush in the still coil, 16–24 short
> reheat runs a day and a lower standby target via register 143, the defrost `C` register).
>
> **Next:**
> 1. First real bridged call (below the balance point, heat + DHW call together): `DHWX` 1 and `ZV` 1
>    with `BLR` 1 and `DHW` 1, `HPCALL` 0, `IN` toward the tank temperature within a minute, chiller
>    restart on its band; `ZV` staying 0 means the old lockout is still in the path. Optional proof:
>    hold `DHWX` 90 s with no zone calling.
> 1a. Fold Chiltrix support's answers into plan §9; if `P52` = 2 is adopted, record the date.
> 2. Bedrooms fight in the shoulder season: both on Heat at night or raise the kids room cool
>    setpoint; one mode per day.
> 3. `P12` 2 → 3 after two days at 12 °C (from 09-14 17:00 EDT); read register 12 back.
> 4. Board swap: `DHWX` holds J4.3, so `HPCOOL` needs `SP-C`/`SP-E` from the J8 pads on rev A.
> 5. First cold week: standby kWh (Emporia, days without `Y1`), starts, defrosts; replaces the §9
>    estimate and the estimated heating COP.
> 6. Plan §11: rooms' drop during refused calls (RedLink record). ΔT panel soft limits vs −24 °F in
>    heating. Sentry registration panel and mount; Y-strainer ~10-12; manual v1.9 (#183); Chiltrix
>    tech email; carried items.
> 7. Unexplained: master bedroom 71 → 75 °F 09:00–10:00 on 09-15 with no call.
>
> **Notes:**
> - Analysis: one measurement per `influx query --raw` over ssh (1 m, or 10 s/raw for toggles), CSV to
>   the scratchpad, pandas on the Mini; Emporia lags Modbus 1–2 min.
> - PivacR uid `bdxar09dh34sgc`; Relays panel offsets series +.03 … +.15 with `byName` overrides on
>   `<measurement>.mean`; Grafana provisions ~45 s after a pull on the Pi's clone.
> - Relay rename recipe: config `outname`, `baseDeltas.json` order, LoopDelta `relay`, dashboard,
>   docs; `restart pivac-gpio pivac-loop-delta` then `signalk`; WilhelmSK cold start for a new tile.
> - RedLink `fan` statenum is 0.5. 782 sockets: A2 bus bar may be fitted, A1 bar must not.

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
