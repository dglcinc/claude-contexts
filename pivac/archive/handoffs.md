> ### ▶ ACTIVE HANDOFF — balance point 30 °F; MBR node sketches; ST-25 DHW tank; 2026-10-18, Mini
>
> Session 81 (2026-10-17 to 10-18, Mac Mini). The heating review of the 35 °F week (no boiler heat calls,
> 75–87 % duty on a 38 °F night, overall COP 2.94 at 33–36 °F) led David to set the HZ-432 balance point to
> 30 °F; the panel does not offer 32. CLAUDE.md on master records it, and plan §3/§5/§8/§9 follow in #239.
> The ST-25 DHW expansion tank (since 10-17) holds 51.5–69 psi; 60 psi precharge is right and a 3–5 psi
> recovery rise is expected. The MBR node shield drawings name every lead hole and scale to one page (#223).
> Arduino #11 adds the bench sketch and the WiFi node sketch, both compiled with arduino-cli under Rosetta.
>
> **Next:**
> 1. Bench test on the M2 with `AirHandlerBench`, then `AirHandler_MBR` on the transformer over WiFi; with
>    the board's IP, make the UCG reservation and add the pivac config (plan §5.2).
> 2. Cold nights at 30 °F: back to 35 °F if an hour exceeds 95 % duty or a room falls 1 °F overnight.
> 3. Thermostats to Heat (David). Merge #239 and #234–#237 on approval.
> 4. Carried: #236 to 19.3 psi on 17.0 after the hot peak; handles on arrival; rev C §9, sentry offline
>    registration, palace redaction.
>
> **Notes:**
> - `r216` stayed 0 through the first defrosts, so it is not the defrost register.
> - DHW precharge cannot be read or set without isolating and draining the water side.

