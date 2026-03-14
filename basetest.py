import subprocess


class BaseTest:
    """Base class for all hardware tests"""

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def safe_shell(self, cmd):
        try:
            return subprocess.check_output(f"{cmd} 2>/dev/null", shell=True, text=True)
        except:
            return ""
