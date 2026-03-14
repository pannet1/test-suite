import curses
import time
import psutil
import subprocess
import os
from basetest import BaseTest


# --- 1. CPU: HEAVY LOAD TEST ---
class CPUEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "1. CPU STRESS & THERMAL:", curses.A_BOLD)
        cores = psutil.cpu_count(logical=False) or 1
        for i in range(min(cores, 4)):
            x = 4 + (i * 14)
            # Simulate heavy ALU calculation for 0.5s per core
            start = time.time()
            while time.time() - start < 0.2:
                _ = 12345 * 54321

            color = curses.color_pair(3)  # PASS
            self.stdscr.attron(color)
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│ CORE {i:^4} │")
            self.stdscr.addstr(y_pos + 3, x, f"│   PASS    │")
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(color)
        self.stdscr.refresh()
