import os
from basetest import BaseTest

try:
    from core.smbus_engine import BatteryDevice, MockBatteryDevice
    from utils.scanner import find_battery_bus
    HAS_VOLTRON = True
except ImportError:
    HAS_VOLTRON = False


class BatteryTest(BaseTest):
    def check(self):
        # 1. Try Voltron SMBus first
        if HAS_VOLTRON:
            simulate = os.getenv("VOLTRON_SIMULATE") == "1"
            
            if simulate:
                battery = MockBatteryDevice(0)
                bus_number = 0
            else:
                bus_number = find_battery_bus()
            
            if bus_number is not None or simulate:
                try:
                    if not simulate:
                        battery = BatteryDevice(bus_number)
                    
                    full = battery.get_full_charge_capacity()
                    design = battery.get_design_capacity()
                    health = int((full / design) * 100) if design > 0 else 0
                    
                    return {
                        "health": f"{health}%",
                        "cycles": battery.get_cycle_count(),
                        "raw": f"{full}/{design}mAh",
                        "temp": f"{battery.get_temperature():.1f}C",
                        "status": battery.get_unseal_status(),
                        "voltron": True
                    }
                except:
                    pass

        # 2. Fallback to SysFS
        path = "/sys/class/power_supply/BAT0/"
        if not os.path.exists(path):
            return False

        def read_val(file):
            try:
                with open(path + file, "r") as f:
                    return int(f.read().strip())
            except:
                return 0

        # Gather raw metrics
        now = read_val("energy_full") or read_val("charge_full")
        design = read_val("energy_full_design") or read_val("charge_full_design")
        cycles = read_val("cycle_count")

        health = 0
        if design > 0:
            health = int((now / design) * 100)

        return {
            "health": f"{health}%",
            "cycles": cycles,
            "raw": f"{now // 1000}/{design // 1000}mAh",
        }
