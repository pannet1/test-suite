# Test-Suite SPEC.md

## Overview
The Test-Suite is a hardware audit engine designed to verify laptop components. It integrates **Project Voltron** for advanced battery diagnostics.

## Architecture
- **Entry Point**: `src/main.py` - Curses-based UI for running the audit.
- **Hardware Engines**:
  - `src/cpuengine.py`: CPU stress and verification.
  - `src/ramengine.py`: RAM capacity and stability.
  - `src/diskengine.py`: Disk health and performance.
  - `src/thermalengine.py`: Temperature monitoring.
- **Battery System (Voltron)**:
  - `src/batterytest.py`: Bridge between Test-Suite and Voltron.
  - `src/voltron/`: Sub-package for SMBus-level diagnostics.
- **Peripherals**: `src/wifitest.py`, `src/audiotest.py`, `src/othertests.py`.

## Configuration
- `VOLTRON_SIMULATE=1`: Enables mock battery data.
- `VOLTRON_API_ENDPOINT`: Optional cloud reporting.

## Directories
- `src/`: Python source code.
- `data/`: Local logs and temporary data.
- `scripts/`: Maintenance and verification scripts.
- `reports/`: Diagnostic JSON reports (inherited from Voltron).
