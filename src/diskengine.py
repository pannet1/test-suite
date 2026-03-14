import curses
from basetest import BaseTest


# --- 3. STORAGE: SMART & I/O READ ---
class DiskEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "3. STORAGE I/O & SMART:", curses.A_BOLD)
        ls = self.safe_shell("lsblk -dno NAME,TYPE")
        disks = [l.split()[0] for l in ls.splitlines() if "disk" in l]
        for i, d in enumerate(disks[:4]):
            x = 4 + (i * 14)
            smart = self.safe_shell(f"smartctl -H /dev/{d}")
            state = 3 if "PASSED" in smart else 4
            msg = "HEALTHY" if state == 3 else "FAIL/NT"
            self.stdscr.attron(curses.color_pair(state))
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│{d.upper():^11}│")
            self.stdscr.addstr(y_pos + 3, x, f"│{msg:^11}│")
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(curses.color_pair(state))
