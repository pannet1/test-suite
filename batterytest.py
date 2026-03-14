import os
from basetest import BaseTest


class BatteryTest(BaseTest):
    def check(self):
        path = "/sys/class/power_supply/BAT0/"
        if not os.path.exists(path):
            return False

        def read_val(file):
            try:
                with open(path + file, "r") as f:
                    return int(f.read().strip())
            except:
                return 0

        # 1. Gather raw metrics
        # Some kernels use _full/_design, others use _full_design/_full
        now = read_val("energy_full") or read_val("charge_full")
        design = read_val("energy_full_design") or read_val("charge_full_design")
        cycles = read_val("cycle_count")

        # 2. Calculate Health Percentage
        health = 0
        if design > 0:
            health = int((now / design) * 100)

        # 3. Return a dictionary for the deep UI section
        return {
            "health": f"{health}%",
            "cycles": cycles,
            "raw": f"{now // 1000}/{design // 1000}mAh",
        }
