# WilhelmSK display-lag diagnosis — domestic water tiles (open, app-side)

**Status (2026-07-05):** Root-caused to the **WilhelmSK app**, not the data pipeline.
Handed off from a `pivac` session to be pursued in the `wilhelm` app codebase
(`sbender9/Wilhelm`, local clone `~/github/wilhelm`; David is a contributor).

## Symptom
On the iPhone/iPad main dashboard, the domestic-water tiles (`environment.water.domestic.*`
— GPM / Run Time / Gallons, added 2026-07-05) take **~20–40 s** to first update after water
starts flowing, and updates stay laggy. Slow-changing gauges (thermostats) never reveal it;
fast-changing flow does.

## Conclusion: the lag is inside the WilhelmSK app
Every hop *we* control delivers in ~1 s; the app renders 20–40 s late.

- Both **iPad and iPhone** lag identically → common app behavior, not a device/network fluke.
- The delta reaches WilhelmSK's **exact connection path** (WebSocket through nginx, same
  external host + hairpin NAT, `subscribe=all`) in **~1 s** every time — proven by a
  standalone WS subscriber on that same path.
- The tile renders **20–40 s later**, and the lag **grows with connection uptime**
  (~20 s right after a fresh app relaunch → ~40 s on an aged connection). That growing-backlog-
  on-a-trivial-input signature = an app-side processing inefficiency or leak, not our stack.
- **Not delta volume:** the idle `subscribe=all` stream is only **~7.6 deltas/s** total
  (thermostats 3.1, electrical.ac/PSI 1.5, emporia 1.1, water 0.9, boiler 0.6). A Python WS
  subscriber chews through it at zero cost; a modern iPad should absorb hundreds/s. Reducing
  our push rate would not help.
- WilhelmSK subscribes with `subscribe=all` (every self path) but only **displays ~20** paths.

### Hard evidence — synchronized four-point capture (fresh-reopen run)
Water opened ~17:24:47.9. Times each observer saw the flow:

| Observer | Saw flow at | Lag |
|----------|-------------|-----|
| WS through nginx (WilhelmSK's exact path) | 17:24:49.5 | ~instant |
| WS direct to Signal K (bypass nginx) | 17:24:49.5 | ~instant |
| Node (`10.0.0.188`, 1 s poll) | 17:24:49.7 | ~1 s |
| Signal K REST model | 17:24:50.9 | ~2 s |
| **iPad + iPhone tile** | ~17:25:09 | **~20 s (fresh) / ~40 s (aged)** |

Workaround: a fresh force-quit + relaunch of WilhelmSK roughly **halves** the lag (resets
whatever accumulates), but does not fix it.

## What was ruled out (all in the pivac/infra stack — do NOT re-investigate these)
- **Node firmware / pivac poll** — reacts on first pulse; pivac `daemon_sleep: 1` (1 Hz). ~1 s.
- **Signal K broadcast** — REST model + both WS subscribers update in ~1 s.
- **nginx WebSocket proxy** — added `proxy_buffering off` + `proxy_read_timeout 3600s` to the
  `/signalk/` block; the WS-through-nginx subscriber proves frames pass in ~1 s regardless.
- **Delta volume** — ~7.6/s idle, trivial.
- **Hairpin NAT / external host path** — the WS-through-nginx test used the same
  `wss://68lookout.dglc.com` hairpin and was instant.

## Next steps (in the WilhelmSK app — `~/github/wilhelm`)
The lag grows with connection uptime on an ~8/s stream, so look for per-delta work that scales
with app state, or an unbounded structure:
1. How does the app handle the `subscribe=all` delta stream? Does each incoming delta trigger
   O(n) work across all gauges / the whole data model rather than a keyed lookup?
2. Is there an unbounded buffer/history/queue that grows over connection lifetime (would explain
   fresh ≈20 s → aged ≈40 s)?
3. Is gauge redraw happening on the main thread per-delta (a redraw storm)?
4. Does subscribing to only the **displayed** paths (vs `subscribe=all`) change it? (Test via a
   modified subscription; if the app forces `subscribe=all`, that itself is the lever.)
5. Check the app version — confirm it's current (older builds had unrelated bugs; see wilhelm.md).

## Reproduce / re-measure (scripts were in /tmp, preserved here)

Needs `pip install --user websocket-client requests`. Endpoints: node `http://10.0.0.188/`;
Signal K direct `http://10.0.0.82:3000`; WilhelmSK path `wss://68lookout.dglc.com/signalk/v1/stream`.

**Four-point synchronized monitor** (`sync_test.py`) — run it, then open a tap and note when the
iPad tile moves; compare timestamps:

```python
import threading, time, json, datetime, re, ast, requests, websocket
LOG="/tmp/water-sync-test.log"; lock=threading.Lock(); stop=threading.Event()
def now(): return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
def log(src,msg):
    with lock, open(LOG,"a") as f: f.write(f"{now()}  [{src:8}] {msg}\n")
def node_poll():
    while not stop.is_set():
        try:
            r=requests.get("http://10.0.0.188/",timeout=2)
            d=ast.literal_eval(re.findall(r"\{.*\}",r.text)[0])
            log("NODE",f"flow={d['flow']} flowing={d['flowing']} vol={d['volume']}")
        except Exception as e: log("NODE",f"err {e}")
        stop.wait(1)
def sk_poll():
    u="http://10.0.0.82:3000/signalk/v1/api/vessels/self/environment/water/domestic/flowRate"
    while not stop.is_set():
        try:
            j=requests.get(u,timeout=2).json(); log("SK-REST",f"flowRate={j.get('value')} sk_ts={j.get('timestamp')}")
        except Exception as e: log("SK-REST",f"err {e}")
        stop.wait(1)
def on_msg(tag):
    def f(ws,m):
        try:
            for u in json.loads(m).get("updates",[]):
                for v in u.get("values",[]):
                    if v.get("path","") in ("environment.water.domestic.flowRate","environment.water.domestic.flowing"):
                        log(tag,f"{v['path'].split('.')[-1]}={v['value']}")
        except Exception: pass
    return f
def ws_run(tag,url):
    while not stop.is_set():
        try:
            websocket.WebSocketApp(url,on_open=lambda w:log(tag,"CONNECTED"),on_message=on_msg(tag),
                on_error=lambda w,e:log(tag,f"err {e}"),on_close=lambda w,*a:log(tag,"closed")).run_forever(ping_interval=20)
        except Exception as e: log(tag,f"run err {e}")
        if not stop.is_set(): time.sleep(1)
open(LOG,"w").close(); log("START","open a tap now")
q="?stream=delta&subscribe=all&sendMeta=none"
for t in [threading.Thread(target=node_poll,daemon=True),threading.Thread(target=sk_poll,daemon=True),
          threading.Thread(target=ws_run,args=("WS-DIRECT","ws://10.0.0.82:3000/signalk/v1/stream"+q),daemon=True),
          threading.Thread(target=ws_run,args=("WS-NGINX","wss://68lookout.dglc.com/signalk/v1/stream"+q),daemon=True)]:
    t.start()
time.sleep(150); stop.set(); time.sleep(1); log("END","done")
```

**Delta-rate breakdown** (`delta_breakdown.py`) — quantify the stream the app must process:

```python
import websocket, json, threading, time
from collections import Counter
c=Counter()
def on_message(ws,m):
    try:
        for u in json.loads(m).get("updates",[]):
            for v in u.get("values",[]):
                c[".".join(v.get("path","").split(".")[:2]) or "(meta)"]+=1
    except: pass
ws=websocket.WebSocketApp("wss://68lookout.dglc.com/signalk/v1/stream?stream=delta&subscribe=all&sendMeta=none",on_message=on_message)
threading.Thread(target=lambda:(time.sleep(15),ws.close()),daemon=True).start()
ws.run_forever()
for p,n in c.most_common(): print(f"  {n/15:5.1f}/s  {p}")
print(f"  TOTAL {sum(c.values())/15:.1f}/s")
```
