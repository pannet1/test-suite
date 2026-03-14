import curses
import os
import time
from batterytest import BatteryTest
from cpuengine import CPUEngine
from diskengine import DiskEngine
from ramengine import RAMEngine
from wifitest import WiFiTest
from audiotest import AudioTest
from othertests import EthTest, BTTest, USBTest, GPUTest, CamTest
from specengine import SpecEngine


class TestSuite:
    def __init__(self, stdscr):
        self.stdscr = stdscr
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
        # 1. Fetch Identity
        idnt = SpecEngine(self.stdscr).get_laptop_identity()

        # 2. Draw Unified Header
        self.stdscr.addstr(
            1,
            2,
            "┌───────────────────────────────────────────────┐",
            curses.color_pair(1),
        )
        # This line now fits the trade-spec exchange format
        spec_line = f"{idnt['vendor']} {idnt['model']} | TAG: {idnt['tag']}"
        self.stdscr.addstr(2, 2, f"│{spec_line:^47}│", curses.color_pair(1))
        self.stdscr.addstr(
            3,
            2,
            "└───────────────────────────────────────────────┘",
            curses.color_pair(1),
        )

        # ... run Engines ...

        self.stdscr.addstr(
            1,
            2,
            "┌───────────────────────────────────────────────┐",
            curses.color_pair(1),
        )
        self.stdscr.addstr(
            2,
            2,
            "│   CHIP-LEVEL CLASS-BASED AUDIT ENGINE v8.2    │",
            curses.color_pair(1),
        )
        self.stdscr.addstr(
            3,
            2,
            "└───────────────────────────────────────────────┘",
            curses.color_pair(1),
        )

        # 1-3. Primary Stress Engines
        CPUEngine(self.stdscr).run(5)
        RAMEngine(self.stdscr).run(11)
        DiskEngine(self.stdscr).run(17)

        # 4. WIFI & 5. AUDIO
        self.stdscr.addstr(23, 2, "4. WIFI:", curses.A_BOLD)
        wifi = WiFiTest(self.stdscr).check()
        self.draw_box(
            24, 4, "WLAN0", str(wifi)[:11] if wifi else "OFF", 3 if wifi else 4
        )

        self.stdscr.addstr(23, 18, "5. AUDIO:", curses.A_BOLD)
        audio = AudioTest(self.stdscr).check()
        if isinstance(audio, dict):
            self.draw_box(24, 18, "ALSA", "PLAYING", 2)
            self.stdscr.refresh()
            os.system(audio["cmd"])
            time.sleep(1)
            self.draw_box(24, 18, "CODEC", audio["status"][:9], 3)

        # 6. BATTERY (The New Deep Section)
        self.stdscr.addstr(23, 34, "6. BATTERY:", curses.A_BOLD)
        bat = BatteryTest(self.stdscr).check()
        if isinstance(bat, dict):
            # Show health percentage in the box, and cycles in a log line below
            color = 3 if int(bat["health"].replace("%", "")) > 70 else 2
            self.draw_box(24, 34, "HEALTH", bat["health"], color)
            self.stdscr.addstr(28, 34, f"CYCLES: {bat['cycles']}", curses.A_BOLD)
        else:
            self.draw_box(24, 34, "BAT0", "NOT FOUND", 4)

        # 7-11. REMAINING BUS TESTS
        self.stdscr.addstr(30, 2, "7-11. REMAINING PERIPHERALS:", curses.A_BOLD)
        others = [
            ("USB", USBTest(self.stdscr).check()),
            ("BT", BTTest(self.stdscr).check()),
            ("GPU", GPUTest(self.stdscr).check()),
            ("CAM", CamTest(self.stdscr).check()),
            ("ETH", EthTest(self.stdscr).check()),
        ]
        for i, (name, res) in enumerate(others):
            color = curses.color_pair(3 if res else 4)
            self.stdscr.addstr(
                31, 4 + (i * 12), f"[{name}:{str(res)[:6] if res else '??'}]", color
            )

        self.stdscr.addstr(33, 2, "AUDIT COMPLETE. Press any key to exit.")
        self.stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(lambda stdscr: TestSuite(stdscr).execute())
