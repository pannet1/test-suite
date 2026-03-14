import os
from basetest import BaseTest


class SpecEngine(BaseTest):
    def get_laptop_identity(self):
        # Fallback to /sys/class/dmi/id/ which doesn't need root
        def read_sys(file):
            path = f"/sys/class/dmi/id/{file}"
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        return f.read().strip()
                except:
                    return None
            return None

        vendor = read_sys("sys_vendor") or "Generic"
        model = read_sys("product_name") or "System"
        tag = read_sys("product_serial") or "No Tag"

        return {
            "vendor": vendor.split()[0].upper(),  # e.g., DELL
            "model": model[:15],
            "tag": tag,
        }
