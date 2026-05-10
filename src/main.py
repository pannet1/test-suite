import curses
import os
import time
import argparse
from checks.batterytest import BatteryTest
from checks.othertests import EthTest, BTTest, USBTest, GPUTest, CamTest
from checks.audiotest import AudioTest
from checks.wifitest import WiFiTest
from engines.cpuengine import CPUEngine
from engines.diskengine import DiskEngine
from engines.ramengine import RAMEngine
from engines.thermalengine import ThermalEngine
from specengine import SpecEngine


class TestSuite:
    def __init__(self, stdscr, simulate=False):
        self.stdscr = stdscr
        self.simulate = simulate
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    def draw_box(self, y, x, title, status_text, color_pair):
        self.stdscr.attron(curses.color_pair(color_pair))
        self.stdscr.addstr(y, x, "┌───────────┐")
        self.stdscr.addstr(y + 1, x, f"│ {title:^9} │")
        self.stdscr.addstr(y + 2, x, f"│{status_text:^11}│")
        self.stdscr.addstr(y + 3, x, "└───────────┘")
        self.stdscr.attroff(curses.color_pair(color_pair))

    def execute(self):
        if self.simulate:
            os.environ["VOLTRON_SIMULATE"] = "1"

        # Check terminal size
        rows, cols = self.stdscr.getmaxyx()
        if rows < 42 or cols < 50:
            self.stdscr.addstr(0, 0, "ERROR: Terminal too small (need 42x50 min)")
            self.stdscr.refresh()
            self.stdscr.getch()
            return

        y_pos = 1  # Starting row

        # 1. Fetch & Draw Identity Header
        idnt = SpecEngine(self.stdscr).get_laptop_identity()
        spec_line = f"{idnt['vendor']} {idnt['model']} | TAG: {idnt['tag']}"

        self.stdscr.addstr(
            y_pos,
            2,
            "┌───────────────────────────────────────────────┐",
            curses.color_pair(1),
        )
        self.stdscr.addstr(y_pos + 1, 2, f"│{spec_line:^47}│", curses.color_pair(1))
        self.stdscr.addstr(
            y_pos + 2,
            2,
            "└───────────────────────────────────────────────┘",
            curses.color_pair(1),
        )
        y_pos += 3  # Move down past header

        # 2. Draw Version/Engine Header
        self.stdscr.addstr(
            y_pos,
            2,
            "┌───────────────────────────────────────────────┐",
            curses.color_pair(1),
        )
        self.stdscr.addstr(
            y_pos + 1,
            2,
            "│   CHIP-LEVEL CLASS-BASED AUDIT ENGINE v8.2    │",
            curses.color_pair(1),
        )
        self.stdscr.addstr(
            y_pos + 2,
            2,
            "└───────────────────────────────────────────────┘",
            curses.color_pair(1),
        )
        y_pos += 4  # Spacing before primary tests

        # 3. Primary Stress Engines (Mutating y_pos)
        CPUEngine(self.stdscr).run(y_pos)
        y_pos += 6

        ThermalEngine(self.stdscr).run(y_pos)
        y_pos += 6

        RAMEngine(self.stdscr).run(y_pos)
        y_pos += 6

        DiskEngine(self.stdscr).run(y_pos)
        y_pos += 7

        # 4. WIFI & 5. AUDIO (Side-by-Side row)
        self.stdscr.addstr(y_pos, 2, "4. WIFI:", curses.A_BOLD)
        self.stdscr.addstr(y_pos, 18, "5. AUDIO:", curses.A_BOLD)

        wifi = WiFiTest(self.stdscr).check()
        self.draw_box(
            y_pos + 1, 4, "WLAN0", str(wifi)[:11] if wifi else "OFF", 3 if wifi else 4
        )

        audio = AudioTest(self.stdscr).check()
        if isinstance(audio, dict):
            self.draw_box(y_pos + 1, 18, "ALSA", "PLAYING", 2)
            self.stdscr.refresh()
            os.system(audio["cmd"])
            time.sleep(1)
            self.draw_box(y_pos + 1, 18, "CODEC", audio["status"][:9], 3)

        # 6. BATTERY (Shared row with Wifi/Audio)
        self.stdscr.addstr(y_pos, 34, "6. BATTERY:", curses.A_BOLD)
        bat = BatteryTest(self.stdscr).check()
        if isinstance(bat, dict):
            health_val = int(bat["health"].replace("%", ""))
            color = 3 if health_val > 70 else 2
            self.draw_box(y_pos + 1, 34, "HEALTH", bat["health"], color)
            self.stdscr.addstr(y_pos + 5, 46, f"CYCLES: {bat['cycles']}", curses.A_BOLD)

            if bat.get("voltron"):
                self.stdscr.addstr(y_pos + 6, 46, f"TEMP: {bat['temp']}", curses.color_pair(color))
                self.stdscr.addstr(y_pos + 7, 46, f"STATUS: {bat['status'][:10]}", curses.color_pair(1))
        else:
            self.draw_box(y_pos + 1, 34, "BAT0", "NOT FOUND", 4)

        y_pos += 9  # Move past the row of boxes and extra Voltron info

        # 7-11. REMAINING BUS TESTS
        self.stdscr.addstr(y_pos, 2, "7-11. REMAINING PERIPHERALS:", curses.A_BOLD)
        y_pos += 1
        others = [
            ("USB", USBTest(self.stdscr).check()),
            #("BT", BTTest(self.stdscr).check()),
            ("GPU", GPUTest(self.stdscr).check()),
            ("CAM", CamTest(self.stdscr).check()),
            #("ETH", EthTest(self.stdscr).check()),
        ]
        for i, (name, res) in enumerate(others):
            color = curses.color_pair(3 if res else 4)
            self.stdscr.addstr(
                y_pos, 4 + (i * 12), f"[{name}:{str(res)[:6] if res else '??'}]", color
            )

        y_pos += 2
        # Cap y_pos to stay within terminal bounds
        rows, cols = self.stdscr.getmaxyx()
        y_pos = min(y_pos, rows - 3)
        self.stdscr.addstr(y_pos, 2, "AUDIT COMPLETE. Press any key to exit.")
        self.stdscr.getch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chip-Level Class-Based Audit Engine")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    args = parser.parse_args()

    curses.wrapper(lambda stdscr: TestSuite(stdscr, simulate=args.simulate).execute())
