---
name: NFS operational gotchas
description: D-state stuck procs and lazy-unmount recovery
type: tools
---

# NFS gotchas

## D-state stuck processes survive SIGKILL

When the NFS server hangs mid-RPC (server overload, network blip, server reconfigured during a transfer), client processes block in **uninterruptible kernel sleep (D state)** waiting for replies that never come. SIGKILL cannot reach D-state processes — the kernel only delivers signals when a process is in interruptible sleep or running.

**Symptom:** `ps` shows old `ls`/`stat`/`cat`/`rsync` processes from earlier attempts. `kill -9 <pid>` does nothing. New transfers on the same mount run at ~100 KB/s because every operation is contending with the stuck queue.

**Recovery (in order):**

1. `sudo umount -l /mnt/path` — **lazy unmount.** Detaches the mountpoint from the namespace immediately, even with active references. New processes won't see the mount; existing stuck procs are still in D-state but new work can continue.
2. `sudo umount -f /mnt/path` — force unmount, sometimes needed if `-l` doesn't dislodge.
3. Reboot — only way to actually reap the D-state procs and recover all kernel resources they're holding. Should be done before the next clean transfer attempt; otherwise the contamination persists.

**Don't:** layer more transfer attempts on top of stuck D-state procs. Every accumulated stuck process holds NFS slots and degrades throughput further. Stop, unmount, retry — and reboot if the count is non-trivial.

## fstab pattern for non-blocking boot

Use `noauto,_netdev` so a missing NFS server doesn't block boot. Mount on demand:

```
10.0.0.X:/volume1/share  /mnt/share  nfs4  noauto,vers=4.1,rw,hard,timeo=600,retrans=2,_netdev  0  0
```

`hard` matters — soft mounts return EIO mid-write and silently corrupt large transfers. Hard mounts wait, which is also painful but at least doesn't lie.

## See also

- `tools/rsync.md` — why `rsync -S` is a bad idea over NFS for large sparse files (use cat|ssh|dd or cp instead).
