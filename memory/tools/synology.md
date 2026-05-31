---
name: Synology DSM rsync-over-SSH gate
description: DSM's modified rsync refuses SSH-rsync even with the toggle on (code 43)
type: tools
---

# Synology DSM — rsync over SSH gotchas

## Symptom

Direct `rsync` over SSH to a Synology fails immediately:

```
rsync error: rsync service is no running (code 43) at io.c(254) [Receiver=3.1.2]
```

Note the typo "is no running" — that's literally what DSM's modified rsync prints. Both the simple form (`rsync src root@nas:/path/`) and the explicit `rsync --server` invocation fail the same way.

## Root cause

DSM ships a modified rsync 3.1.2 with extra gating beyond the user-facing toggle. **Enabling Control Panel → File Services → rsync → "Enable rsync service" is necessary but not sufficient for the SSH path** — that toggle enables the rsync **daemon** (port 873). The SSH path additionally requires either:
- the SSH-authenticated user is in the **administrators** group, AND
- something writes/exists in DSM's internal rsync config that the wrapper is checking

In practice, even with the toggle on, root@DSM via SSH still fails.

## Workarounds (in order of preference)

1. **rsync as `nasadmin` with `sudo rsync` on the remote** — `nasadmin` is in `administrators`. Untested but recommended next try:
   ```
   rsync -e ssh --rsync-path='sudo rsync' -avS file nasadmin@nas:/volume1/path/
   ```
   Requires nasadmin's SSH pubkey in `~nasadmin/.ssh/authorized_keys` on the NAS, plus passwordless sudo for rsync.

2. **NFS + `cp --sparse=always` or `dd conv=sparse`** — bypasses rsync entirely. See `tools/rsync.md` for why rsync over NFS is also painful for sparse files; cp/dd avoid both gotchas.

3. **`scp -O`** for one-off files — `-O` forces legacy SCP protocol (modern openssh defaults to SFTP subsystem, which DSM also rejects with `subsystem request failed on channel 0`).

## Other DSM SSH gotchas

- **`scp` without `-O`** fails: `subsystem request failed on channel 0` — DSM rejects SFTP subsystem requests by default.
- Generic `ssh root@nas '<command>'` works fine — it's only rsync's and scp's specific session patterns that fail. `ssh ... 'whoami'` returns `root`, `ssh ... 'rm -f /path/x'` works.

## NFS+ACL note (separate gotcha for the same NAS)

A fresh DSM share has only `group:administrators` in its ACL. NFS exports with `no_root_squash` keep Pi-root as UID 0, but UID 0 isn't a member of `administrators` on the NAS, so `ls`/`touch` from the Pi appear to fail with permission-denied even though writes go through. Fix on the NAS:

```
synoacltool -add /volume1/<share> user:root:allow:rwxpdDaARWcCo:fd--
synoacltool -enforce-inherit /volume1/<share>
```
