# Project Voltron SPEC.md

## Overview
Project Voltron is a specialized Python-based diagnostic service for Smart Battery forensics. It focuses on SMBus communication to detect firmware locks (PF Bits) and unseal status on laptop batteries, specifically targeting TI BQ series chips.

## Architecture
- **CLI Entry Point**: `diagnostics.py` - Manages the diagnostic flow, including bus scanning, data retrieval, and optional surgery.
- **Core Engine**: `core/smbus_engine.py` - Contains `BatteryDevice` for hardware communication and `MockBatteryDevice` for simulation.
- **Surgery Module**: `core/surgery.py` - Contains `BatterySurgery` for unsealing and resetting battery status.
- **Utilities**:
  - `utils/scanner.py`: I2C/SMBus bus discovery.
  - `utils/cloud_sync.py`: Reporting and remote synchronization.
- **Storage**:
  - `reports/`: JSON diagnostic logs.
  - `data/`: Internal project data.
  - `scripts/`: Operational scripts.

## API & Data Formats
Diagnostic reports are stored as JSON with the following structure:
```json
{
    "timestamp": "ISO8601",
    "bus_number": "int",
    "metrics": {
        "voltage_mv": "int",
        "current_ma": "int",
        "temperature_c": "float",
        "cycle_count": "int",
        "design_capacity_mah": "int"
    },
    "status": {
        "pf_bit_set": "bool",
        "seal_status": "string"
    }
}
```

## Known Issues
- Currently limited to TI BQ series register maps (0x51, 0x54).
- Cloud sync is optional and depends on environment variables.

## Future Roadmap
- Support for more battery chip manufacturers.
- Integration with a Vultr-based centralized dashboard.
