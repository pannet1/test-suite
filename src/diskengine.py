import curses
import os
from basetest import BaseTest


class DiskEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "3. STORAGE INTERFACE:", curses.A_BOLD)
        # Find disks via /sys/block to avoid needing lsblk
        disks = [d for d in os.listdir("/sys/block/") if d.startswith(("sd", "nvme"))]

        for i, d in enumerate(disks[:4]):
            x = 4 + (i * 14)

            # Detect Type
            is_rotational = self.safe_shell(
                f"cat /sys/block/{d}/queue/rotational"
            ).strip()
            dtype = (
                "NVMe" if "nvme" in d else ("SSD" if is_rotational == "0" else "HDD")
            )

            # Health Fallback
            smart = self.safe_shell(f"smartctl -H /dev/{d}")
            msg = "HEALTHY" if "PASSED" in smart else "DETECTED"

            self.stdscr.attron(
                curses.color_pair(3 if "HEAL" in msg or "DET" in msg else 4)
            )
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│{d.upper():^11}│")
            self.stdscr.addstr(y_pos + 3, x, f"│{dtype:^11}│")  # Now shows SSD/NVMe!
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(curses.color_pair(3))
