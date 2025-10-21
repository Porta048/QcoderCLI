"""ASCII art banner for QCoder CLI."""

import sys
import os


QCODER_BANNER = r"""
  ██████╗  ██████╗ ██████╗ ██████╗ ███████╗██████╗
 ██╔═══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
 ██║   ██║██║     ██║   ██║██║  ██║█████╗  ██████╔╝
 ██║▄▄ ██║██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
 ╚██████╔╝╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
  ╚══▀▀═╝  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""

ORANGE = "\033[38;5;208m"
RESET = "\033[0m"


def print_banner() -> None:
    """Print the QCoder ASCII art banner in orange."""
    # Configure Windows console for UTF-8
    if sys.platform == "win32":
        try:
            # Enable ANSI escape sequences on Windows
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            # Set console output to UTF-8
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # Print banner with orange color
    try:
        print(f"{ORANGE}{QCODER_BANNER}{RESET}")
    except UnicodeEncodeError:
        # Fallback to plain ASCII if Unicode fails
        fallback_banner = r"""
   ___   ____ ___  ____  _____ ____
  / _ \ / ___/ _ \|  _ \| ____|  _ \
 | | | | |  | | | | | | |  _| | |_) |
 | |_| | |__| |_| | |_| | |___|  _ <
  \__\_\\____\___/|____/|_____|_| \_\
"""
        print(f"{ORANGE}{fallback_banner}{RESET}")
