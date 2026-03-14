import curses
import re
from basetest import BaseTest


class DiskEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "3. STORAGE I/O & SMART:", curses.A_BOLD)

        # 1. Target internal physical disks only (removable=0) [cite: 5]
        ls_cmd = "lsblk -dno NAME,RM,TYPE | grep ' 0 disk'"
        ls_out = self.safe_shell(ls_cmd)
        disks = [line.split()[0] for line in ls_out.splitlines()] if ls_out else []

        for i, d in enumerate(disks[:4]):
            x = 4 + (i * 14)
            dev_path = f"/dev/{d}"
            is_nvme = "nvme" in d  # [cite: 5]

            # 2. Use specialized utility for NVMe
            if is_nvme:
                # Get the SMART log directly from the controller
                nvme_data = self.safe_shell(f"nvme smart-log {dev_path}")

                # Check for hardware critical warnings
                if "critical_warning : 0" in nvme_data:
                    state, msg = 3, "NVMe-OK"
                else:
                    state, msg = 4, "NVMe-BAD"

                # Extract wear level (Percentage Used)
                wear_match = re.search(r"percentage_used\s+:\s+(\d+)%", nvme_data)
                sub_label = (
                    f"{100 - int(wear_match.group(1))}% LIFE" if wear_match else "NVMe"
                )

            else:
                # 3. Fallback to smartctl for SATA SSD/HDD [cite: 1, 5]
                smart = self.safe_shell(f"smartctl -H {dev_path}")
                state = 3 if "PASSED" in smart else 4
                msg = "SATA-OK" if state == 3 else "FAIL/NT"
                sub_label = "SATA"

            # 4. Draw the diagnostic box
            self.stdscr.attron(curses.color_pair(state))
            self.draw_disk_box(y_pos + 1, x, d.upper(), sub_label, msg)
            self.stdscr.attroff(curses.color_pair(state))

    def draw_disk_box(self, y, x, name, sub_label, status):
        self.stdscr.addstr(y, x, "┌───────────┐")
        self.stdscr.addstr(y + 1, x, f"│{name:^11}│")
        self.stdscr.addstr(y + 2, x, f"│{sub_label:^11}│")
        self.stdscr.addstr(y + 3, x, f"│{status:^11}│")
        self.stdscr.addstr(y + 4, x, "└───────────┘")
