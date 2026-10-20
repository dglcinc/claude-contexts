> ### ▶ ACTIVE HANDOFF — MBR node bench-proven on WiFi at 10.0.0.180; NTC bath calibration pending; 2026-10-19, M2
>
> Session 82 (2026-10-18, M2). Bench-tested the master bedroom air-handler node (UNO R4 WiFi on the
> Olimex PROTO-SHIELD) with the Arduino #11 sketches, compiled on the M2 after installing Rosetta (the
> renesas core's compiler and bossac are x86_64). The shield is proved: spare DS18B20 `0516a36816ff` reads
> clean, both NTC dividers read 10.65 and 10.78 kΩ (74.4 and 74.0 °F against 72.05 °F on the probe), the
> Y2 input follows the relay (81 bounce edges on make, 3 on break). The node joins `redux` in about 2 s and
> answers at the UCG reservation 10.0.0.180 (MAC `e8:f6:0a:aa:a3:88`, client AirHandler-MBR). The 24 VAC
> converter is isolated and gives 4.65 V at the shield against 4.86 V from USB; David will install as is and
> watch `uptimeMs` for dropouts. Arduino #12 fixes a watchdog reboot loop (`WiFi.setHostname()` blocks past
> the 5 s WDT) and a −196.6 °F sentinel on a disconnected probe (double/float compare). pivac #240 adds
> `offset:` to ArduinoSensor with tests, `pivac-ah-mbr.service`, the backup lists, a paused
> `ah-mbr-air-return-stale` rule, the config sample block, and the bench record in plan §2/§4 and CLAUDE.md.
> The spare production Pi is recorded on master (81fba53).
>
> **Next:**
> 1. NTC two-point calibration in the sous-vide bath (plan §6 step 2); David will say when it is set up.
>    Suggested 95 and 130 °F with the bench 73 °F as a third point; reference is `0516a36816ff` on the bus
>    (`wsup` field while the ROMs are zero; subtract its +0.496 K); bundle both NTC tips against the probe
>    sheath, ten minutes per plateau. Same error at both points → `offset:` in config; a changing error →
>    adjust `NTC_BETA` in `AirHandler_MBR.ino` first. The CSV logger `airhandler-log.sh` in the M2 session
>    scratchpad polls .180 then .39 every 5 s into `airhandler-bench.csv`; restart one if it is gone.
> 2. PA5 pair on the bus: rescan (`AirHandlerBench`, 'r'), write the ROMs into `AirHandler_MBR.ino`, record
>    which probe is on which pipe (plan §3.1), split the pair offset into config.
> 3. Install: live `/etc/pivac/config.yml` block from the sample, copy and enable `pivac-ah-mbr.service`,
>    unpause the rule and verify in `alert_rule`; plan §6 steps 3–5.
> 4. David merges Arduino #12 and pivac #240 (#241, #236, #237 still open).
> 5. After a week with loop B on HIGH: great room alone was 7.8 °F ΔT on LOW, expect about 6.3;
>    LOOPB_SUP − IN −0.45 °F on LOW, −2 °F with both loops calling means MEDIUM.
> 6. Carried: thermostats to Heat (David); cold nights at 30 °F; spare Pi model and MAC for CLAUDE.md;
>    #236 pressure; handles; sentry offline registration; rev C §9; backup board set; palace redaction.
>
> **Notes:**
> - Homebrew `bossa` does not know the RA4M1 ("No device found"); use the core's bossac under Rosetta.
> - A faulted sensor is omitted from the node's line, so its path goes stale; no sentinels.
> - UCG fixed IP: scan `rest/user` fixed_ips and `stat/sta` leases for a free address first (.189 was taken).
> - The node is not on the Arduinos Shelly, so the watchdog cannot cycle it.
> - Y2 release is debounced 100 ms in the node sketch.

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

