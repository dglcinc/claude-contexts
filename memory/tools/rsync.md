---
name: rsync — large-sparse-file pathology over NFS, and 3.4 → older compat
description: Don't rsync large sparse files over NFS; rsync 3.4 has compat regressions with older servers
type: tools
---

# rsync gotchas

## 1. Large sparse files over NFSv4 starve

**Symptom:** `rsync -avS` of a multi-GB sparse `.img` to an NFSv4 mount starts at gigabit-class throughput (~30 MB/s), then collapses to KB/s and stays there. Long-run rate ~750 KB/s for a 50 GB file = ~18 hours.

**Why:** rsync's sparse handling does many small `lseek`+`write` syscalls per block. NFSv4 sync semantics make every one a round trip. The instantaneous rate `--progress` shows is misleading — between bursts, rsync is blocked on individual sync acknowledgements.

**Workarounds (NFS-mounted destination):**

| Tool | Speed | Notes |
|---|---|---|
| `cp --sparse=always src dst` | ~3–10 MB/s | Sequential read+write, sparse-skipping for output. Better than rsync; still NFS-bound. |
| `dd if=src of=dst bs=4M conv=sparse status=progress` | ~similar | Same as `cp --sparse` mechanically; useful when you want explicit progress. |
| `cat src \| ssh nas 'dd of=dst conv=sparse bs=4M'` | gigabit-class | **Fastest.** Bypasses NFS entirely — raw bytes via SSH, sparse-skip on the receiving end. The wire still carries the zero blocks (no compression by default), but disk write is sparse. |

For very large transfers, prefer the SSH pipe even if NFS is mounted. Don't use `rsync -S` for one-shot fresh transfers of large sparse files — its protocol benefits don't pay for the NFS sync overhead.

## 2. NFS-stuck D-state procs survive SIGKILL

When NFS misbehaves mid-transfer, `ls`/`stat`/`cat`/`rsync` processes go into uninterruptible kernel sleep (D state) waiting on RPCs that never return. **`SIGKILL` cannot reach D-state processes.** They show in `ps` indefinitely; the only fix is `umount -l /mnt/path` (lazy unmount) followed by a reboot to actually clear them. Do not try to layer more rsync attempts on top — every accumulated stuck proc holds NFS resources and contaminates new transfers.

## 3. rsync 3.4 → older rsync server compat

**Symptom:** `rsync -av src user@host:/dest/` from a 3.4.x client to a 3.1.x server (e.g. Synology) fails immediately:

```
rsync: connection unexpectedly closed (0 bytes received so far) [sender]
rsync error: error in rsync protocol data stream (code 12) at io.c(232) [sender=3.4.1]
```

**Root cause:** rsync 3.4 introduced "secluded args" (CVE-2024-12084 hardening) that older servers don't speak.

**First-line fix:** `--old-args` on the client. If that still fails, suspect a server-side gate (e.g. Synology DSM — see `tools/synology.md`). `--protocol=31` does **not** fix this — it's an args-passing change, not a protocol change.

```
rsync --old-args -avS file user@host:/dest/
```
