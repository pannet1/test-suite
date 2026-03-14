from basetest import BaseTest
import os


# --- COMPACT BUS CLASSES ---
class USBTest(BaseTest):
    def check(self):
        res = self.safe_shell("lsusb")
        count = len(res.strip().split("\n")) if res else 0
        return f"{count} Devs" if count > 0 else False


class BTTest(BaseTest):
    def check(self):
        res = self.safe_shell("hciconfig --all") or self.safe_shell("bluetoothctl show")
        if res:
            match = re.search(r"Name: '(.+?)'", res)
            return match.group(1)[:8] if match else "Found"
        return False


class GPUTest(BaseTest):
    def check(self):
        res = self.safe_shell("lspci | grep -i vga")
        if res:
            if "Intel" in res:
                return "Intel"
            if "NVIDIA" in res:
                return "Nvidia"
            return "Found"
        return False


class CamTest(BaseTest):
    def check(self):
        return "Video0" if os.path.exists("/dev/video0") else False


class EthTest(BaseTest):
    def check(self):
        return (
            "Gbe OK" if "Gigabit" in self.safe_shell("lspci | grep -i ether") else False
        )
