> ### ▶ ACTIVE HANDOFF — balance 30 °F; loop B HIGH; PR sweep; 2026-10-19, Mini
>
> Session 81 (2026-10-17 to 10-19, Mac Mini). HZ-432 balance point to 30 °F and loop B's pump to HIGH for
> heating, both in CLAUDE.md on master, the plan (#239, merged) and the assessment (#241, open). ST-25 DHW
> tank recorded at 60 psi precharge. Merged pivac #223, #234, #235 (DEHUM off the Relays panel) and #239,
> and Arduino #10 and #11 (bench and WiFi node sketches). Stale and merged branches deleted.
>
> **Next:**
> 1. Bench test the MBR shield on the M2, then WiFi on the transformer; UCG reservation and pivac config
>    with the board's IP (check #240, opened by another session).
> 2. After a week on HIGH: loop B ΔT great room alone 7.8 °F on LOW, expect about 6.3; LOOPB_SUP − IN
>    −0.45 °F on LOW, −2 °F with both loops calling means MEDIUM.
> 3. Cold nights at 30 °F: back to 35 °F above 95 % hourly duty or a 1 °F overnight droop.
> 4. Thermostats to Heat (David). #236 to 19.3 on 17.0 after the hot peak; #237 and handles.
>
> **Notes:**
> - LOW baseline: great room 65 % duty on a 38 °F night, held 72 °F; no boiler calls all week.
> - `r216` is not the defrost register. SSH to GitHub timed out on 10-18; `gh api` worked.

