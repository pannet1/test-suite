import os
import logging

logger = logging.getLogger(__name__)

try:
    import smbus2
except ImportError:
    smbus2 = None

def find_battery_bus():
    """
    Scans all /dev/i2c-* devices to find which one has a device at 0x0B.
    Returns the bus number if found, else None.
    """
    if smbus2 is None:
        logger.warning("smbus2 not installed. Bus scanning is disabled.")
        return None

    for i in range(256):  # Check up to 256 buses
        bus_path = f"/dev/i2c-{i}"
        if os.path.exists(bus_path):
            try:
                bus = smbus2.SMBus(i)
                # Quick scan: try to write a dummy byte or just check for existence
                # SMBus 'quick command' is often used for scanning
                bus.write_quick(0x0B)
                bus.close()
                return i
            except Exception:
                # If it fails, the device is likely not there or bus is busy
                continue
    return None

def format_report(data):
    import json
    return json.dumps(data, indent=4)
