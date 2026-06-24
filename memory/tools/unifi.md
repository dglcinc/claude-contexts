# UniFi UCG access (David's LAN)

**Gateway/controller = UCG Ultra at `https://10.0.0.1`.** As of 2026-06-16 the USG-3P was
replaced by a **UCG Ultra**, and the UniFi **Network controller now runs ON the gateway
itself** — *not* on the Mac-mini `UniFi OS Server.app` anymore (that path is stale; the app
isn't even running on `10.0.0.84`). Don't waste time on `10.0.0.84:11443`, SSH, or the
podman VM. **Go straight to `https://10.0.0.1`.**

## The credential (this is the part that was hard to find)

**API key file:** `~/.config/unifi/claude-agent.key` (on the Mac at `10.0.0.84` /
`utilityserver`, mode 600, 32 chars, created 2026-06-21 explicitly for the agent). Use it as
an `X-API-KEY:` header. No username/password, no cookie login, no SSH needed.

```bash
KEY=$(cat ~/.config/unifi/claude-agent.key)
# self-signed cert → always -k
curl -sk -H "X-API-KEY: $KEY" https://10.0.0.1/proxy/network/integration/v1/sites
```

The same key authenticates **both** API surfaces on the UCG:
- **Integration API (v1, read-mostly):** `https://10.0.0.1/proxy/network/integration/v1/...`
  e.g. `/sites`, `/sites/{siteId}/clients?limit=200`, `/sites/{siteId}/networks`.
  Site id = `88f7af54-98f8-306a-a1c7-c9349722b1f6` (internalReference `default`).
  NB integration IDs are different UUIDs than the classic API's `_id`s — don't mix them.
- **Classic controller API (read+write):** `https://10.0.0.1/proxy/network/api/s/default/...`
  The API key works here too (HTTP 200). This is where writes live (fixed IPs, etc.).

## Recipe: set a client's fixed IP (DHCP reservation)

Classic API, site `default`. LAN network classic `_id` = `63ab8c9d277b3e032baaa609`
(Default / corporate / 10.0.0.1/24).

1. Get the client's user `_id` by MAC (the bulk `rest/user` GET is capped ~3000 rows and
   may not include it — use the by-MAC path instead):
   `GET /proxy/network/api/s/default/stat/user/<mac>` → `data[0]._id`
2. PUT the reservation onto that `_id`:
```bash
B=https://10.0.0.1/proxy/network/api/s/default
curl -sk -X PUT -H "X-API-KEY: $KEY" -H 'Content-Type: application/json' \
  "$B/rest/user/<_id>" \
  -d '{"name":"Arduinos","use_fixedip":true,"fixed_ip":"10.0.0.61","network_id":"63ab8c9d277b3e032baaa609"}'
```
`meta.rc:"ok"` = done. (POST to `rest/user` to *create* a record errors `api.err.MacUsed`
if the client already exists — fetch its `_id` and PUT instead.)

## Notes
- DHCP reservation on the UCG keeps a device portable: leave the **device on DHCP** and pin
  the IP here, so moving it elsewhere needs no factory reset. (David's stated preference —
  done this way for the "Arduinos" Shelly plug at `10.0.0.61`, MAC `ac:eb:e6:f4:b9:30`.)
- The `/shelly` ARP-probe trick (find Shelly devices without creds) is separate; for the
  controller-side view (names, fixed IPs, uplink port) use this API key.
