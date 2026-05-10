import curses
from basetest import BaseTest


class RAMEngine(BaseTest):
    def run(self, y_pos):
        self.stdscr.addstr(y_pos, 2, "2. MEMORY TOPOLOGY:", curses.A_BOLD)

        # Try DMI first
        raw = self.safe_shell("dmidecode -t memory")
        slots = []
        if raw and "Permission denied" not in raw:
            for dev in raw.split("Memory Device")[1:]:
                info = {"loc": "DIMM", "size": "EMPTY"}
                for line in dev.splitlines():
                    if "Locator:" in line:
                        info["loc"] = line.split(":")[1].strip()
                    if "Size:" in line and "No" not in line:
                        info["size"] = line.split(":")[1].strip()
                slots.append(info)

        # FALLBACK: If DMI failed, pull from Kernel MemInfo
        if not slots:
            with open("/proc/meminfo", "r") as f:
                mem = int(f.readline().split()[1]) // 1024  # KB to MB
            slots = [
                {"loc": "OS-DET", "size": f"{mem // 1024}GB"},
                {"loc": "SLOT1", "size": "UNK"},
            ]

        for i, s in enumerate(slots[:4]):
            color = curses.color_pair(3 if "B" in s["size"] else 4)
            x = 4 + (i * 14)
            self.stdscr.attron(color)
            self.stdscr.addstr(y_pos + 1, x, "┌───────────┐")
            self.stdscr.addstr(y_pos + 2, x, f"│{s['loc'][:9]:^11}│")
            self.stdscr.addstr(y_pos + 3, x, f"│{s['size']:^11}│")
            self.stdscr.addstr(y_pos + 4, x, "└───────────┘")
            self.stdscr.attroff(color)
