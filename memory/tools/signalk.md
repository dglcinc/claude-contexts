---
name: SignalK server admin
description: SignalK-server plugin admin — install topology (bundled vs ~/.signalk), force-disabling un-toggleable built-ins, minting an admin JWT, and reading in-app-browser issues from the access log
type: tools
---

# SignalK server — plugin administration

Operational notes for managing plugins on a self-hosted SignalK server. Reference box: the
pi at `pi@10.0.0.82` (host `pivac`), server 2.28.0-beta.2, global install at
`/usr/lib/node_modules`, data dir `~/.signalk`. The techniques generalize to any SignalK
server (incl. Victron Venus OS Large, where the SK **core** version is firmware-gated but
**plugins** are still installed/updated through the SignalK appstore on-device).

## Install topology — why the admin UI hides Disable/Remove

A plugin's enable/remove options depend on **where its package physically lives**:

- **Bundled in the server distro** (`/usr/lib/node_modules/signalk-server/node_modules/`):
  npm owns these as part of `signalk-server`, so the Appstore shows **no Remove**.
  Examples: `signalk-n2kais-to-nmea0183`, `@signalk/set-system-time`,
  `@signalk/udp-nmea-plugin`, `@signalk/n2k-signalk`, `@signalk/nmea0183-signalk`.
- **Installed in `~/.signalk/node_modules/`** (listed in `~/.signalk/package.json` deps):
  Appstore-managed, **removable** via `cd ~/.signalk && sudo npm uninstall <pkg>`.
- **Dual-installed** (both places): the `~/.signalk` copy wins module resolution; uninstalling
  it just falls back to the bundled copy. Seen for `@signalk/signalk-to-nmea0183` and
  `signalk-to-nmea2000`.

**Plugin id ≠ package name.** e.g. id `sk-to-nmea0183` = pkg `@signalk/signalk-to-nmea0183`;
id `sk-to-nmea2000` = pkg `signalk-to-nmea2000`; id `udp-nmea-sender` = pkg
`@signalk/udp-nmea-plugin`.

## Disabling a plugin the UI won't let you toggle

The UI toggle only appears once a plugin has a persisted state. Each plugin's state lives in
`~/.signalk/plugin-config-data/<id>.json` as `{"enabled": <bool>, "configuration": {}}`.
Built-in plugins that have **never been configured** report `enabled: none` in the API and
show no toggle. Force-disable by writing the file directly:

```bash
ssh pi@10.0.0.82
printf '%s' '{"enabled": false, "configuration": {}}' \
  > ~/.signalk/plugin-config-data/<id>.json
sudo systemctl restart signalk
```

When uninstalling a plugin, also delete its orphaned `~/.signalk/plugin-config-data/<id>.json`.

## Querying the authenticated /skServer/plugins API

`/skServer/plugins` is admin-only (401 for readonly). Mint a short-lived admin JWT from the
server's own `secretKey` (HS256, payload `{"id":"admin"}`) — legit on a box you own:

```python
# sudo python3 - reads /home/pi/.signalk/security.json secretKey, signs JWT, calls API
import json,hmac,hashlib,base64,time,urllib.request
sec=json.load(open("/home/pi/.signalk/security.json")); key=sec["secretKey"].encode()
b64=lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")
now=int(time.time())
hdr=b64(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
pl=b64(json.dumps({"id":"admin","iat":now,"exp":now+600}).encode())
sig=b64(hmac.new(key,hdr+b"."+pl,hashlib.sha256).digest())
tok=(hdr+b"."+pl+b"."+sig).decode()
req=urllib.request.Request("http://localhost:3000/skServer/plugins",
    headers={"Authorization":"Bearer "+tok})
data=json.load(urllib.request.urlopen(req,timeout=10))
# each entry: id, data.enabled (true/false/none = never configured)
```

This pi: single `admin` user, `allow_readonly: true`. **Don't `signalk-server -v` over ssh —
it boots the server and hangs.** Read the version from
`/usr/lib/node_modules/signalk-server/package.json` instead.

## Debugging in-app-browser issues — read the access log first

When an in-app browser (e.g. WilhelmSK's "?" help) renders a page differently than desktop
Safari (unstyled/serif, no scroll, stuck at "Skip to content"), **check the SignalK server
access log early** — `journalctl -u signalk` shows morgan-style request lines with the exact
URLs and status codes, which ends the guessing fast. A real case: a malformed `…/user-guide//`
(double-slash) URL made the page's relative `../assets/…` CSS/JS resolve one level too deep and
**404**, so it rendered unstyled with no JS — invisible in the URL bar but obvious in the log as
404s on every asset. Lesson generalizes: a 200 on the page but 404s on its assets = a path/base
problem, not fonts/cache/HSTS.
