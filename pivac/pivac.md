# pivac — context summary

`pivac` is the HVAC/home-monitoring daemon running on the Raspberry Pi at `10.0.0.82` (external `68lookout.dglc.com`). Full project context, architecture, services, and remote-desktop setup live in:
- `~/github/pivac/CLAUDE.md` (project-specific, on the Pi)
- `~/github/claude-contexts/pi-CLAUDE.md` (Pi-wide infrastructure: backup procedure, journald, cursor fix, etc.)

This file exists for Mac-side Claude sessions that need to drive Pi operations remotely. The main thing it covers right now is the **backup runbook**.

---

## Current State

*Updated 2026-06-01 (session 4)*

**Last worked on (session 4)**: Ran down the ~03:00 Grafana **mlb-availability** alert.
It was self-inflicted — the monthly NAS image-backup (1st @ 03:00) stops `nginx`, blacking
out the `mlb.dglc.com` proxy 03:03–03:15. Separately, the backup itself was **failing with
ENOSPC**: RonR `image-backup` had sized `pivac.img`'s root partition to usage+margin at
creation (54.4 GiB), and live root had grown to 54.9 GiB. **Grew `pivac.img` on the NAS to
the full 128 GB card** (`truncate` → `parted resizepart 2 100%` → `e2fsck` → `resize2fs`;
now p2 = 118.7 GiB, ~63 GiB free, sparse 54 GB actual; restore is 1:1 to any ≥128 GB card),
and **restored the MBR disk id `0xf9199e61`** (parted regenerates it → would break
PARTUUID boot of a restore). Edited `nas-image-backup.sh` (PR #64, open): dropped `nginx`
from the stop list (mlb stays up during backups) and excluded the `/home/pi/thinclient_drives`
xrdp FUSE mount (root can't stat it → rsync exit 23). **Open:** confirm a clean exit-0 run
post-exclude, then merge PR #64. (David's live SD card was already fully expanded — fine.)

*Session 3 (2026-05-31):*

**Last worked on**: Shipped the **DHW recirc-loop temperature** feature end-to-end + several fixes. Generalized `pivac.ArduinoSensor` to multi-field (`type: temperature`→Kelvin), wired/flashed a DS18B20 on the DHW Arduino, deployed live (`environment.inside.hvac.dhw.recirc.temperature`, ~313 K), added a Grafana 2nd-axis panel, a `circ-temp-stale` freshness alert, and WilhelmSK iPad+iPhone gauges. Also: **corrected the inverted Arduino board/IP/role mapping** (DHW board = .114/`pivac.ArduinoPSI`, boiler = .219/`pivac.ArduinoThermPSI` — names are backwards vs role); **rotated the leaked GitHub PAT** (all `~/github` remotes→SSH, new fine-grained token in gh keyring on Mac+Pi, old `ghp_` revoked, 2027-05-17 rotation reminder scheduled); and **root-caused + hardened the Sentry** boiler-display "jumping values." Plan doc marked ✅ COMPLETE. PRs: pivac #59/#61/#62/#63, Arduino #4, wilhelm-sk #2 (all merged).

**Next steps**:
1. **Pump-health / "loop cold" alert — intentionally deferred** (plan §8.3): the recirc pump is on-demand/aquastat, so a static threshold false-alarms. Observe the duty cycle a few days, then build a "never reached hot in 24h" signal.
2. *(optional)* Round the HVAC In/CRW/Out WilhelmSK gauges to whole °F (recirc already done via `valueLabelFormat %0.0f`).
3. *(carryover)* NAS image-backup first auto-run check (`journalctl -u nas-image-backup.service`); physical card-swap boot test — needs hands at the Pi.

**Notes**:
- **Arduino board/IP/role mapping (was inverted in docs; now corrected in CLAUDE.md):** DHW board = MAC `c0:4e:30:11:6f:3c` = **10.0.0.114** = `pivac.ArduinoPSI` / `electrical.ac.arduinoPSI` / "Potable DHW PSI" / 200 PSI Domestic sketch (**recirc DS18B20 is here**). Boiler/hydronic = MAC `34:b7:da:66:1e:50` = **10.0.0.219** = `pivac.ArduinoThermPSI` / `electrical.ac.arduinoThermPSI` / "Hydronic PSI" / 100 PSI BoilerLoop sketch. Names kept (InfluxDB history); IPs DHCP-by-MAC.
- **Sentry CV depends on a locked camera mode:** Tapo C120 Night Vision must stay **Night** (+ Night Boost **off**), not Auto — Auto day/night switching causes 7-segment misreads. Module hardened (range-sanity + median debounce, PR #62).
- **GitHub auth on all machines is now SSH remotes + a fine-grained PAT** (gh keyring on Mac + Pi). The old broad `ghp_` classic token was leaked across configs and is revoked. New token expires ~2027-05-31.
- **Reader hardware:** Anker USB 3.0 Micro SD Card Reader, USB `05e3:0764` (Genesys Logic chipset). Replaced the 4-LUN Insignia NS-DCR30A2 on 2026-05-09. The Anker is a 2-LUN device but the same `size > 0` filter handles single- and multi-slot readers identically.
- **Why VID:PID, not SCSI model:** Anker's SCSI model string is `MassStorageClass` — too generic to match safely (any USB stick reports it). VID:PID is unique to the actual reader.
- **Both timers installed and enabled.** `nas-image-backup.timer` (monthly, 1st @ 03:00 EDT) and `sd-clone.timer` (weekly, Sun @ 02:00 EDT +/− 15m jitter). 1h gap prevents collision when the 1st of a month falls on a Sunday.
- **rpi-clone is live-safe** — no service stop, unlike `image-backup` which requires service quiesce. A weekly clone that captures live state is fine for hot-recovery; the monthly NAS image is the consistent backup.
- **rpi-clone install:** source at `~/github/rpi-clone/` (billw2/rpi-clone), copied to `/usr/local/sbin/` — see pi-CLAUDE.md.
- **No redeploy needed for sd-clone.sh changes:** `/etc/systemd/system/sd-clone.service` references the in-repo path `/home/pi/github/pivac/scripts/sd-clone.sh` directly, so `git pull` after merge is sufficient.
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
