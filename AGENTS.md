# AGENTS.md

## Project Overview
Hardware diagnostics tool distributed via USB. Binary runs on target laptop, diagnostics stay local, report sent via WiFi.

## Architecture

```
USB Stick
├── alpine/              # Minimal Alpine setup
├── diag                 # Go binary (compiled, protected)
└── reports/             # Local fallback storage

Workflow:
1. Boot USB → Alpine → auto-login → run ./diag
2. WiFi gate: "Enter password" or exit
3. Connect to WiFi
4. Run hardware diagnostics
5. POST report to server
6. Self-clean and exit
```

## Distribution Model
- **Source** stays with you (private repo)
- **Binary** distributed via USB (hard to reverse)
- **Target** never sees diagnostic logic

## Core Behavior
- **WiFi provided** → Run diagnostics → Send report
- **WiFi skipped** → Exit cleanly, nothing happens

## WiFi Configuration
- User provides password at prompt
- Binary generates wpa_supplicant.conf
- Auto-select best interface
- Retry logic with timeout

## Report Format (JSON)
```json
{
  "device_id": "MAC or serial",
  "timestamp": "ISO8601",
  "wifi_connected": true,
  "diagnostics": {
    "battery": {...},
    "thermal": [...],
    "i2c": {...}
  }
}
```

## Build for Alpine
```bash
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o diag cmd/diag/main.go
```

## Dependencies (Alpine)
```bash
apk add i2c-tools acpi wpa_supplicant
# No Python needed for the Go binary
```

## Directories
- `src/` - Python source (for reference, not distributed)
- `cmd/diag/` - Go binary source
- `alpine/` - Shell scripts (reference only)
- `reports/` - Local report fallback