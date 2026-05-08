# AGENTS.md

## Troubleshooting Checklist
- [ ] Ensure `.venv` is active: `source .venv/bin/python`
- [ ] Verify `smbus2` for hardware access: `uv pip list | grep smbus2`
- [ ] Check permissions for `/dev/i2c-*` if running battery tests.
- [ ] Run in simulation mode for quick UI verification: `uv run src/main.py --simulate`

## Issue Log

### issue: Integration of Project Voltron
- **status**: completed
- **commit**: feat: merge project-voltron for advanced battery diagnostics
- **findings**: Successfully integrated SMBus-level diagnostics into the main test suite. Added simulation support and updated UI.
