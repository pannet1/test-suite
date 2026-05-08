# Project Voltron AGENTS.md

## Troubleshooting Checklist
- [ ] Verify I2C kernel modules: `lsmod | grep i2c`
- [ ] Check device permissions: `ls -l /dev/i2c-*`
- [ ] Confirm `smbus2` is installed in `.venv`
- [ ] Validate simulation mode: `uv run diagnostics --simulate`

## Issue Log

### issue: smbus2 dependency missing in simulation mode
- **status**: fixed
- **pre: scripts/check_smbus2.sh**: `pip show smbus2`
- **commit**: fix: decouple smbus2 for simulation
- **post: scripts/verify_sim.sh**: `python3 diagnostics.py --simulate`

### issue: no battery detected on WSL environment
- **status**: blocked
- **pre: scripts/check_i2c.sh**: checks for /dev/i2c-* nodes
- **findings**: Environment is WSL. Physical SMBus/I2C hardware is not exposed to WSL by default.
- **recommendation**: Use a native Linux installation or an external USB-to-I2C adapter (e.g., CP2112) with USBIP-win to pass it through to WSL.
