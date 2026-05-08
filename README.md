# Test-Suite + Project Voltron

This project combines a hardware test suite with advanced battery diagnostics from Project Voltron.

## Features
- **CPU/RAM/Disk Stress Engines**: Standard hardware tests.
- **Peripheral Checks**: WiFi, Audio, USB, BT, GPU, Cam, Ethernet.
- **Advanced Battery Diagnostics (Voltron)**:
    - SMBus communication with Smart Batteries.
    - Detailed metrics: Temperature, Voltage, Cycle Count, Design Capacity.
    - Seal Status detection (Sealed, Unsealed, Full Access).
    - Permanent Failure (PF) bit detection.
    - **Surgery Mode**: Attempt to unseal batteries using default keys.

## Installation

Ensure you have the necessary dependencies installed:
```bash
# Install core dependencies
pip install smbus2 requests

# If using uv
uv add smbus2 requests
```

Note: Hardware-level SMBus communication may require `sudo` and the `i2c-dev` kernel module.

## Usage

Run the main test suite:
```bash
python3 src/main.py
```

Run in simulation mode (for testing without SMBus hardware):
```bash
python3 src/main.py --simulate
```

## Voltron Standalone
You can still run the Voltron diagnostics standalone:
```bash
PYTHONPATH=src python3 src/voltron/diagnostics.py
```

### Surgery Mode (Advanced)
To attempt battery unsealing via the standalone tool:
```bash
PYTHONPATH=src python3 src/voltron/diagnostics.py --surgery
```
*Warning: Surgery operations can potentially brick battery firmware. Use with caution.*
