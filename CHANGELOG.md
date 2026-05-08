# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Project Voltron Integration**: Merged advanced battery diagnostics into the test suite.
- **SMBus Battery Support**: Direct communication with Smart Batteries using `smbus2`.
- **Battery Surgery Mode**: Capability to attempt unsealing batteries using default keys.
- **Simulation Mode**: Added `--simulate` flag to `main.py` for testing without specialized hardware.
- **Enhanced UI**: Added Temperature and Seal Status display to the Battery section of the curses interface.
- **Relative Imports**: Refactored Voltron internals to work as a sub-package within `src/`.

### Changed
- Refactored `BatteryTest` to prioritize Voltron diagnostics over SysFS.
- Updated `src/main.py` UI layout to accommodate more detailed battery data.
- Standardized environment variables for simulation (`VOLTRON_SIMULATE`).
