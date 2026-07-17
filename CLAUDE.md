# Claude Code Context: Raspberry Pi GPIO & Hardware Environment

This file provides the necessary hardware context, pin mappings, and system constraints for Claude Code to generate compatible script and configurations. Always adhere to the specifications defined below.

---

## 1. Target System & Constraints
* **OS Environment**: Highly stripped-down Embedded Linux built via Buildroot.
* **Available Shell**: BusyBox (Limited commands. No `apt`, `apt-get`, `man`, `nano`, `vim`).
* **File Deployment**: Transferred from host (Windows) via SFTP directly to `/root/projects/`.
* **Process Interruption**: Using `Ctrl + C` (`SIGINT`) to exit. All Python scripts MUST catch `KeyboardInterrupt` to clean up hardware states safely.

---

## 2. Python GPIO Environment
* **Primary Library**: `RPi.GPIO` (Version: `0.7.1`, manually compiled and installed).
* **Python Version**: `Python 3.8.2` (Executable: `python3`).
* **Coding Standard**: 
  * Always use **`GPIO.BOARD`** (Physical Pin Numbering) unless specified otherwise.
  * Always include `GPIO.setwarnings(False)` in the initialization phase.
  * Always execute `GPIO.cleanup()` inside the `except KeyboardInterrupt:` block.

---

## 3. Peripheral Hardware: TM1650 4-Digit Display
### 3.1 Physical Pin Mapping (BOARD Mode)
When writing scripts for the 4-digit display module (driven by TM1650), strictly use the following pin assignments:

| Module Pin | RPi 40-Pin Physical Number | Hardware Function Reference |
| :--- | :--- | :--- |
| **VCC** | **Pin 1** | 3.3V Power Supply |
| **GND** | **Pin 9** | System Ground |
| **SDA** | **Pin 3** | Data Line (Shared with hardware I2C1 SDA) |
| **SCL** | **Pin 5** | Clock Line (Shared with hardware I2C1 SCL) |

### 3.2 Low-Level Timing Protocol (Bit-Banging)
* Currently using software simulation (**Bit-Banging**) via `RPi.GPIO` outputs.
* Timing delays must utilize `time.sleep(0.001)` to ensure stable logic transitions for the TM1650 chip.
* **Register Addresses**: 
  * Control Register (Brightness/On/Off): `0x48`
  * 7-Segment Display RAM Addresses (Left to Right): `[0x68, 0x6a, 0x6c, 0x6e]`

---

## 4. Code Generation Directive
When I ask you to write a new feature or control script for this hardware:
1. **Never** include external package imports that require `apt` or `pip` installation (except for standard libraries or manually bundled local scripts).
2. **Always** implement full `try...except KeyboardInterrupt:` blocks to ensure the 7-segment display turns off (`0x00` written to all digit addresses) and `GPIO.cleanup()` is called when the user exits.
3. Keep the logic modular and well-commented so it can be directly piped or rewritten into `/root/projects/`.