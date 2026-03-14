import curses
from basetest import BaseTest


# --- 2. RAM: PATTERN VERIFICATION ---
class RAMEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "2. MEMORY DATA INTEGRITY:", curses.A_BOLD)
        raw = self.safe_shell("dmidecode -t memory")
        slots = []
        if raw:
            for dev in raw.split("Memory Device")[1:]:
                info = {"loc": "DIMM", "size": "EMPTY"}
                for line in dev.splitlines():
                    if "Locator:" in line:
                        info["loc"] = line.split(":")[1].strip()
                    if "Size:" in line and "No" not in line:
                        info["size"] = line.split(":")[1].strip()
                slots.append(info)

        for i, s in enumerate(slots[:4]):
            status = 1 if "B" in s["size"] else 2
            color = curses.color_pair(3 if status == 1 else 4)
            x = 4 + (i * 14)
            self.stdscr.attron(color)
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│{s['loc'][:9]:^11}│")
            self.stdscr.addstr(y_pos + 3, x, f"│{s['size']:^11}│")
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(color)
