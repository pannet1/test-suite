# Test-Suite SPEC.md

## Overview
Hardware diagnostics tool distributed via USB. Binary runs on target laptop, diagnostics stay local, report sent via WiFi.

## Distribution Model

| Component | Location | Notes |
|-----------|----------|-------|
| Source code | Private repo | Never distributed |
| Go binary | USB stick | Compiled, protected |
| Report endpoint | Your server | HTTPS POST |
| Local fallback | USB/repo | If no WiFi |

## Architecture

```
USB Stick (distributed)
├── alpine/              # Minimal Alpine boot
├── diag                 # Go binary (compiled)
└── wpa_supplicant.conf  # Template (no credentials)

Target Laptop (runs binary)
├── Boot from USB
├── Enter WiFi password → connect
├── Run diagnostics (local)
├── POST report to server
└── Clean up and exit
```

## Core Behavior

### WiFi Gate
- Binary prompts: "Enter WiFi password (or press Enter to skip)"
- If skipped → exit cleanly, no diagnostics
- If provided → connect, proceed

### Diagnostics (local, no internet needed)
- Battery health (sysfs + SMBus if available)
- Thermal zones
- I2C bus scan
- Storage health (smartctl)
- WiFi capabilities
- CPU/RAM info

### Report Delivery
- **Connected**: POST JSON to endpoint
- **Not connected**: Save locally, exit

## Build Requirements

### Go Binary
- Static compilation
- Target: Linux amd64 (Alpine)
- CGO disabled

### Alpine Packages (pre-installed on USB)
```bash
apk add i2c-tools acpi wpa_supplicant
```

## Report Schema
```json
{
  "device_id": "string",
  "mac_address": "string",
  "timestamp": "ISO8601",
  "wifi": {
    "connected": true,
    "ssid": "string"
  },
  "diagnostics": {
    "battery": {
      "present": true,
      "capacity_percent": 85,
      "health_percent": 92,
      "cycles": 156,
      "voltage": 12300,
      "temperature": 32
    },
    "thermal": [
      {"zone": "x86_pkg", "temp_c": 45},
      {"zone": "pch", "temp_c": 38}
    ],
    "i2c": {
      "devices": ["0x18", "0x1a", "0x68"]
    }
  }
}
```

## Security
- Binary obfuscation (Go + UPX if needed)
- No source distributed
- Report includes device MAC for identification
- Optional: signed reports with pre-shared key

## Directories
- `src/` - Python (reference, not distributed)
- `cmd/diag/` - Go binary source
- `alpine/` - Shell scripts (reference)
- `reports/` - Local fallback storage