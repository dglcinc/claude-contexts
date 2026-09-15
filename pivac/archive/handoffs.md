> ### ▶ ACTIVE HANDOFF — Chiltrix September findings and the loop drain-and-refill procedure (#181, #182 merged); 2026-09-14, Mac Mini
>
> Two weeks of Chiltrix data (08-29 → 09-13, 390 runs) reviewed and folded into the docs (#181):
> P95 5→3 raised the ≤26 Hz leaving-water floor 36.7→39.9 °F with no cycling effect; every near
> miss since is a surge-terminated run (25→47–60 Hz in the last 1–3 min, 5 % of runs, min 37.22 °F
> on 09-08 with r284 = 0) while steady running keeps 3 °F of margin; the start ramp is fixed at
> 50–52 Hz by minute 3, so night runs are 11 min with 36 min gaps; target still 10 °C and P12 still
> 2; cooling COP 4.9 all-in, 5.5–7.4 running, 0.82 kWh/°F of OAT above 48 °F; first heating run
> 09-08 (85 kBTU/h from 3.2 kW, cool-back 36 min / 1.13 kWh). Three sub-minute heating blips on
> 09-13 were mains outages (Pi reboots ~13:05 and ~20:48), now a rule. Then
> `docs/hydronic-drain-and-refill.md` (#182): the Pacific Hydrostar 65836 (120 ft head) fills to
> the attic coil (53 ft needed) with the 30 psi boiler relief as the thing to guard; zone valves
> open, high vents before low drains, air blow-down by zone, pre-mix 30 % PG in a drum, closed purge
> cart, `startupFlow` 51.7 L/min as the proof. Later: `CHIL` corrected in CLAUDE.md (it is the
> Taco primary call; the chiller is always enabled, `HPHEAT` only selects mode); winter shutdown
> section §9 in the shoulder-season plan (#184); manual update backlogged as issue #183; **David
> raised the cooling target to 54 °F at 17:00 EDT, stored 12 °C, register 142 read back** (#185
> open). Pi on master; docs only, no restart.
>
> **Next:** merge #185; after two days at 12 °C confirm the band (~48 stop / ~58 restart, outlet
> min ~41 °F) then P12 2 → 3 and expect starts/day ~15–18; if the loop is drained, follow the doc
> and record the glycol reading; watch Sentry `registrationX/Y/Score` and add a panel;
> boards and parts arriving (populate, test on the spare Pi, swap in); Y-strainer around 10-12.
> **Carried:** heating commissioning per plan §5; first heating week's energy balance; print the
> label; Loop B HIGH and 140 °F offsets; bus topology §7.2; Wilhelm #155/#156; label the override
> relay; a plausibility floor for Sentry `air`.
>
> **Notes:** InfluxDB analysis is one measurement per query at 1 m over ssh, pandas on the Mac
> (`~/pivac-venv` on the Mini now has it). Water-side Q from the chiller's own sensors, ±10 %.
> Drain-and-refill facts to confirm on site: relief valve setting, CX75 drain plugs, zone-valve
> manual lever. Pages: review https://claude.ai/code/artifact/b0e30280-ffbe-4e69-b9a5-24dcec8be736 ,
> Sentry eyecheck https://claude.ai/code/artifact/577a962a-3a1b-410c-bedb-1322883c809a .

