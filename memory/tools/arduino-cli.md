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
- **M2-over-SSH TCC gotcha (2026-07-03):** compiling on the M2 via SSH fails with
  `ArduinoGraphics.h: No such file` even though the lib is installed — macOS TCC
  blocks SSH sessions from reading `~/Documents/Arduino/libraries` ("Operation not
  permitted"). Local/GUI sessions are unaffected. Workaround: stage the lib outside
  Documents and pass it at compile time:
  `git clone --depth 1 https://github.com/arduino-libraries/ArduinoGraphics /tmp/ard-libs/ArduinoGraphics`
  then `arduino-cli compile ... --libraries /tmp/ard-libs <Sketch>`. Note `upload`
  does NOT accept `--libraries` — run upload plain after the compile.
- **DomesticWater node board (flashed 2026-07-03):** the spare third UNO R4 WiFi,
  USB serial/WiFi MAC `34:b7:da:65:99:1c` (`esp32s3-65991C`), UniFi-reserved to
  **10.0.0.188** (name "DomesticWater"). Meter-only sketch live, `GET /` verified.
