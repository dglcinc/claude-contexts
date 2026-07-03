# arduino-cli on the Pi

- **2026-07-03** — Installed `arduino-cli` 1.5.1 on the Pi at `~/bin/arduino-cli`
  (not on PATH by default — invoke as `~/bin/arduino-cli`), with the
  `arduino:renesas_uno` 1.6.0 core (UNO R4 WiFi) and the `ArduinoGraphics` lib.
  **Why:** the M2 (the previous compile host, `david@10.0.0.83`) is a laptop and
  often unreachable; the Pi can now compile-verify UNO R4 sketches locally:
  `~/bin/arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi <SketchDir>`.
  Benign warning every build: "library WDT claims to run on renesas architecture(s)".
- **Placeholder secrets gotcha:** `~/github/Arduino/DomesticWater/arduino_secrets.h`
  on the Pi contains PLACEHOLDER WiFi creds (created 2026-07-03 just to satisfy the
  compile; the file is gitignored). Replace with the real SSID/PSK before flashing
  a board from the Pi, or it will never join WiFi.
- Flashing needs the board on USB wherever `arduino-cli upload` runs — the Pi works
  for that too now, if the board is plugged into it.
