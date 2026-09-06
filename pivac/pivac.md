# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

> ### ▶ ACTIVE HANDOFF — the Sentry LED coordinates drifted with the camera, and nothing was watching them (2026-09-06 19:00, M2)
>
> **Nothing is pending on the machine, and both repos are current on the M2** (that pull is no longer
> outstanding). Five pivac PRs merged and deployed this session: **#155** Sentry LED re-aim, **#157**
> I/O board pinout sheets, **#125** Chiltrix Modbus bring-up runbook, **#124** Sentry warp-search
> tool, **#94** storm-drain float spec. `pivac-sentry` restarted clean, all services active, journal
> silent. **One pivac PR left: #117**, rebased onto master and `MERGEABLE/CLEAN`.
>
> **David reported random on/off cycling on the LED-driven Sentry paths. The cause was geometry, not
> thresholds.** `leds:` and `indicators:` are **absolute frame coordinates that drift with the camera
> exactly as `display_warp` does**, but the recalibration recipe only ever re-aimed the quad. Left
> behind through the 07-28 and 08-23 recalibrations, all eight had absorbed the cumulative shift: the
> quad's TL had moved `(1156,655) → (1150,649)`, six left and six up, and the measured LED offsets
> were +4..+7 right and +6..+9 down — the same displacement. Every spot had slid off its lens onto
> the bright bezel below and right of it.
>
> **⚠️ The decisive test is the SWING, not the level, and idle data cannot produce it.** Across a real
> DHW call the lens-centred `burner` spot went **0.794 → 1.215 (+0.421)**, lit 10/10; the drifted spot
> went **1.039 → 1.052 (+0.012)**. A spot that does not move when the LED lights is reading the bezel,
> which the LED does not illuminate, so its output was **noise straddling the threshold rather than a
> measurement** — every `burnerOn` transition after the drift was manufactured, and the drifted
> `circ_aux` read the running DHW pump as **off for all ten samples**. The cycling indicators show the
> same thing without waiting for the boiler, since both their states appear in one capture
> (`water_temp` separation 0.090 → 0.394).
>
> **July's own fix set this up.** Dropping `led_ratio` 1.15 → 1.05 on 2026-07-20 correctly solved the
> IR/green-LED problem, but it also spent the margin that would have absorbed later drift; once the
> camera moved, 1.05 sat *inside* the compressed band rather than below it. **Lowering a threshold to
> fix a miss buys sensitivity by spending headroom.** `_low_margin` now warns when a spot's decision
> rested on noise — parking within 0.03 of the threshold, or switching on a separation under 0.15,
> which the majority test cannot catch because a cycling indicator is dark most of the cycle. Grep
> `lit-threshold` alongside `nothing decoded`.
>
> **⚠️ Do the frame captures from a Mac, not the Pi — I rebooted the Pi doing this.** Stacking 200
> full-res float64 frames is ~5.9 GB on a 3.8 GB machine. The camera is an ordinary LAN RTSP source
> and capturing from the M2 works *alongside* a running `pivac-sentry`. Crop at capture time, keep
> frames `uint8`. Everything recovered; it was avoidable.
>
> **#156 merged 68 s before #155**, both touching `CLAUDE.md` and `docs/sentry-cv-notes.md`. GitHub
> merged cleanly, but a clean *textual* merge proves nothing about coherence when two changes
> restructure the same section — checked by hand: rules appear once each, no duplicate headings, both
> suites pass. Worth repeating that check rather than assuming it.
>
> **Next:** decide **#117** — now purely two new docs, but written 2026-08-18 and overtaken in three
> places by the Modbus work (§4.2 treats the community register maps as an unresolved contradiction,
> §9 still asks whether the CX75 exposes Modbus RTU, §4 frames the feed as future work; the doc never
> mentions `ChiltrixModbus`, `startupFlow` or `docs/chiltrix-modbus.md`). A bounded ~60-line pass was
> offered against merging it as an August snapshot. Then **extend `sentry-warp-search.py` to the
> LED/indicator coords** — it searches the quad only, so recalibration is half automated and the
> manual half is the half that just failed; the methods that worked are dark-blob centroid for the LED
> lenses and temporal variance for the cycling indicators. **Carried:** confirm the 10:56 pushes
> reached the phone; device-test Wilhelm #155 and ship Wilhelm #155/#156; Arduino #10; Chiltrix tuning
> change 2 (12 °C target + `P12` = 3 as a pair, register 142 read back); confirm `r284` = 32 at the
> next lockout using **Error Reset, never Clear**; confirm `P65` on the panel; hot-day zone-droop
> check; loop-probe swing and strain-relief checks; board builds; LoopDelta gate on a real call.

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
