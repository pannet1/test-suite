import re
from basetest import BaseTest


class SpecEngine(BaseTest):
    def get_laptop_identity(self):
        # 1. Pull Manufacturer (e.g., Dell Inc.)
        vendor_raw = self.safe_shell("dmidecode -s system-manufacturer")
        vendor = vendor_raw.strip() if vendor_raw else "Unknown Vendor"

        # Clean up common names
        if "Dell" in vendor:
            vendor = "DELL"
        elif "HP" in vendor:
            vendor = "HP"
        elif "Lenovo" in vendor:
            vendor = "LENOVO"

        # 2. Pull Model Name (e.g., Latitude 5340)
        model_raw = self.safe_shell("dmidecode -s system-product-name")
        model = model_raw.strip() if model_raw else "System Model"

        # 3. Pull Serial/Service Tag (Vital for finding schematics/drivers)
        tag_raw = self.safe_shell("dmidecode -s system-serial-number")
        tag = tag_raw.strip() if tag_raw else "No Tag"

        return {"vendor": vendor, "model": model, "tag": tag}
