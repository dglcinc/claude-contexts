---
name: macOS gotchas
description: macOS platform quirks — hostname falling back to the gateway's reverse-DNS PTR
type: reference
---

## Hostname falls back to the gateway's reverse-DNS name

If a Mac's `hostname` shows something unexpected (e.g. `unifi`), the static `HostName` is unset and macOS is deriving a **transient** hostname from a reverse-DNS (PTR) lookup of its own IP against the DHCP/DNS server. On a UniFi LAN the gateway (`10.0.0.1`; `dig -x 10.0.0.1` historically resolved to `setup.ubnt.com`) answers `unifi.` as the PTR for clients without a registered DNS name, so the Mac adopts `unifi`.

`ComputerName` and `LocalHostName` (set via System Settings) can be correct while the Unix `HostName` is still unset — they're independent. Check all three:

```bash
scutil --get ComputerName
scutil --get LocalHostName
scutil --get HostName
```

Fix (persistent across reboots — writes to `/Library/Preferences/SystemConfiguration/preferences.plist`):

```bash
sudo scutil --set HostName UtilityServer-M4
```

Observed 2026-06-03 on the Mac Mini (UtilityServer M4, `10.0.0.84` — the MemPalace host). The gateway is now a UCG Ultra at `10.0.0.1` but the PTR behavior is the same.
