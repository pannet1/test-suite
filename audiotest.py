import re
import os
from basetest import BaseTest


class AudioTest(BaseTest):
    def check(self):
        # 1. Force hardware volume up (The amixer "Scream")
        # We target Master and Speaker to bypass software mutes
        self.safe_shell("amixer sset Master unmute")
        self.safe_shell("amixer sset Master 100%")
        self.safe_shell("amixer sset Speaker unmute")
        self.safe_shell("amixer sset Speaker 100%")

        # 2. Extract the Codec name (The re.search part)
        # On Alpine, the codec files are in /proc/asound/cardX/codec#Y
        codec_data = self.safe_shell("cat /proc/asound/card*/codec#*")

        chip_name = "Generic"
        if codec_data:
            # We look for the line 'Codec: [Chip Name]'
            match = re.search(r"Codec:\s+(.+)", codec_data)
            if match:
                # We take the first part (e.g., 'Realtek') or the whole model
                chip_name = match.group(1).strip()

        # 3. Return the payload
        # This gives the UI the chip name and the command to fire the 1s tone
        return {
            "status": chip_name,
            "cmd": "speaker-test -t sine -f 1000 -l 1 > /dev/null 2>&1 &",
        }
