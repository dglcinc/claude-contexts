# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — Chiltrix option 2 relay control with HPCOOL, winter is HMI off, cooling-cold alarm (#186–#189 merged); 2026-09-14, Mac Mini
>
> Session 63 (2026-09-14 evening, Mac Mini): winter shutdown changed to controller off on the HMI with the
> breaker on (#186): the HZ-432 has no cooling lockout by outdoor temperature (69-2198 Table 5; `OT LOCKOUT`
> is a heating-stage lockout for non-dual-fuel panels), the CX's `P112`/`P42`/`P43` switch-over is unusable
> with `C`-`H`-`COM`, `P58` is −27 °C, `P00` = 1 keeps off through an outage, and the IOM names no crankcase
> heater. Then the tank-toggling problem: with one relay on `B`, a Checkout heat test ending put the unit back
> in cooling (09-08: mode 0 within a minute, 36 min / 1.13 kWh re-chill). IOM p. 40 contact logic: both open
> standby, `C` alone cool, `H` alone heat, both closed = wired controller (keeps last mode, maintains the
> tank); p. 41 option 2 = two normally closed relays. Plan §2/§4/§5 rewritten for `HPCOOL` (#187), David
> wired it (#188): 782 relay on `O`, NC pole holds `H`, the `H`-`COM` pair moved as a pair, spare pole on
> J4.2 `SP-C` = BCM 13; live config `13: HPCOOL`, baseDeltas order HPHEAT 4, HPCOOL 5, CHIL 6 … SCALA 10,
> Relays panel series (refId I, +.13, blue), label docx row regenerated, 70-782EL14-1 pinout verified (NC
> 1–4, NO 5–8, COM 9–12, coil 13/14, poles in columns 1·5·9 …), diagram `docs/hpheat-hpcool-wiring.svg`.
> Finding: `HPCOOL` read 1 without a break through calls and idle, so the HZ-432 holds `O`/`B` by mode
> (changeover-valve outputs, held to spare the reversing valve); `HPHEAT`/`HPCOOL` are mode indicators,
> the panel does the latching, both contacts closed only with the panel in neither mode; the one-relay
> version would have latched too but depends on `B` staying held below the balance point, which the
> guide does not say. New rule `chiltrix-cooling-cold` (#189, deployed 22:36): mode cooling + own ambient
> < 40 °F + max(switchOn) > 0 over 30 m, for 30 m. C7089 outdoor sensor fitted. As-built corrected
> everywhere: `CHIL` runs the Taco only. `signalk` restart took RedLink out ~2 min (normal).
>
> **Next:**
> 1. Read the overnight record (mode 141, `HPHEAT`, `HPCOOL`, `CHIL`, `BLR`, compressorHz, UBT/LBT): a heat
>    call should flip `HPCOOL` 0 / `HPHEAT` 1, 141 to 1, tank toward 122 °F, and hold after the call. Then
>    the §5 step 4 panel checks (`C64` 1 / `C63` 0 in cooling mode, swapped after the first heat call, 141
>    holding), print the label docx, cold-start WilhelmSK for the new switch.
> 2. Chiltrix plan change 2, second half: after two days at the 12 °C target (from 2026-09-14 17:00 EDT)
>    confirm the band at ~48 °F stop / ~58 °F restart and an outlet minimum near 41 °F, then P12 2 → 3 on
>    the panel and read register 12 back; expect starts/day to fall from 21–29 to ~15–18. Watch master BR
>    and kids-room RH on any warm day.
> 3. Chiltrix tech email (David composing): standby/off temperature protections, whether a cool call with
>    122 °F tank water trips a high-inlet limit. First cold week's log answers what standby freeze
>    protection runs; `P10` = 1 as a `C` blocker is untested and not needed.
> 4. If David drains and refills the loop, follow `docs/hydronic-drain-and-refill.md`; afterwards record
>    the glycol reading and date in CLAUDE.md (it moves the `startupFlow` baseline) and re-check pH.
> 5. HVAC System Manual v1.9 (issue #183): fall and spring procedures (now HMI off, thermostats on Heat),
>    Chiltrix description, relay meanings; source docx in OneDrive `Claude/` and `HVAC Documentation/`.
> 6. Sentry: watch registrationX/Y/Score for a week and add a Grafana panel; rigid camera mount; the
>    tracker does not follow scale; consider a plausibility floor for `air`.
> 7. Boards (OSH Park) and parts (Mouser), both ordered 09-12: populate, test on the spare Pi per
>    `docs/rpi-io-board-design.md` steps 7–8 and `docs/ds18b20-bus-topology.md` §8, swap in; at the swap
>    `HPCOOL` moves to J4.3 `SP-D` and the config pin to 19 (SP-C is on J8 pads on rev A).
> 8. Y-strainer re-inspection around 2026-10-12. Loop fluid pH retest in a month with a meter.
> 9. Carried: heating commissioning per plan §5 (register 143 read back, live-call proof, OT balance 40 °F;
>    watch `r284` on the first real heat-to-cool changeover); first heating week's energy balance replaces
>    the estimated COP; Loop B HIGH and 140 °F offsets; bus topology §7.2 as-built; Wilhelm #155/#156.
>
> **Notes:**
> - Manuals: the CX65/CX75 IOM (chiltrix.com/documents/CX65-1-IOM.pdf) and the HZ432 guide 69-2198
>   (honeywellmanual.com) both extract cleanly with `pdftotext`; WebFetch cannot read them. Relay pages are
>   IOM pp. 40–41 (rendered with `pdftoppm`). The 70-782EL14-1 socket datasheet is the Schneider legacy
>   sockets catalogue (mectronic mirror), p. 62.
> - Render an SVG with headless Chrome (`--screenshot --window-size=W,H`); `qlmanage -t` pads to a square.
> - The "override relay" of earlier plans was `HPHEAT`'s own NC pole holding `C`; there is no separate
>   bridging relay to label.

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
