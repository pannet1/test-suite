from basetest import BaseTest


class WiFiTest(BaseTest):
    def check(self):
        # 1. Find the wireless interface name (e.g., wlan0)
        iface_raw = self.safe_shell("ls /sys/class/net | grep w")
        if not iface_raw:
            return False

        iface = iface_raw.strip().split("\n")[0]

        # 2. Get hardware capabilities (Standards & Bands)
        # We check if 'iw' is available for deep inspection
        iw_info = self.safe_shell(f"iw dev {iface} info")

        # 3. Get link quality if connected, or just device capabilities
        # We look for the 'bitrate' or 'link' status
        link_status = self.safe_shell(f"iw dev {iface} link")

        # 4. Fallback/Summary Logic
        if "Connected" in link_status:
            # Extract bitrate for capability proof
            import re

            bitrate = re.search(r"tx bitrate: (.+?)$", link_status, re.MULTILINE)
            speed = bitrate.group(1) if bitrate else "Link OK"
            return f"UP ({speed})"

        # If not connected, prove the hardware is functional by showing the standard
        hw_caps = self.safe_shell(f"iw phy | grep -E 'HT20|HT40|VHT|HE'")
        if "HE" in hw_caps:
            return "WiFi 6 (AX)"
        elif "VHT" in hw_caps:
            return "WiFi 5 (AC)"
        elif "HT" in hw_caps:
            return "WiFi 4 (N)"

        return "802.11 b/g" if iface else False
