import os
import re
import curses
from basetest import BaseTest


class ThermalEngine(BaseTest):
    def get_temps(self):
        temps = []
        # Path for core thermal sensors in most Intel/AMD laptops
        hwmon_path = "/sys/class/hwmon/"
        if not os.path.exists(hwmon_path):
            return temps

        for h in os.listdir(hwmon_path):
            name_path = f"{hwmon_path}{h}/name"
            try:
                with open(name_path, "r") as f:
                    name = f.read().strip()

                # 'coretemp' is the standard for Intel Core i-series
                if name == "coretemp":
                    # Find all inputs (temp1_input, temp2_input, etc.)
                    for file in os.listdir(f"{hwmon_path}{h}/"):
                        if "input" in file:
                            with open(f"{hwmon_path}{h}/{file}", "r") as f:
                                # Values are in millidegrees C (e.g., 45000 = 45°C)
                                temps.append(int(f.read().strip()) // 1000)
            except:
                continue
        return sorted(temps)

    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "1.5 THERMAL MONITORING:", curses.A_BOLD)
        temps = self.get_temps()

        if not temps:
            self.stdscr.addstr(
                y_pos + 1, 4, "[ NO SENSORS DETECTED ]", curses.color_pair(4)
            )
            return

        for i, t in enumerate(temps[:4]):  # Show up to 4 core temps
            # Logic: Green < 60°C, Yellow 60-85°C, Red > 85°C
            color = 3 if t < 60 else (2 if t < 85 else 4)
            x = 4 + (i * 14)

            self.stdscr.attron(curses.color_pair(color))
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│ CORE {i:^4} │")
            self.stdscr.addstr(y_pos + 3, x, f"│  {t:^3}°C   │")
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(curses.color_pair(color))
