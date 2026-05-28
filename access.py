import tty
import sys
import termios
import os
import time

GREEN = "\033[92m"
RESET = "\033[0m"
BOLD = "\033[1m"

orig_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
os.system("clear")
sys.stdout.write("\033]0;System Status\a")


hack_font = r"""
           _____ _____ ______  _____ _____         _____ _____            _   _ _______ ______ _____  
     /\   / ____/ ____|  ____|/ ____/ ____|       / ____|  __ \     /\   | \ | |__   __|  ____|  __ \ 
    /  \ | |   | |    | |__  | (___| (___        | |  __| |__) |   /  \  |  \| |  | |  | |__  | |  | |
   / /\ \| |   | |    |  __|  \___ \\___ \       | | |_ |  _  /   / /\ \ | . ` |  | |  |  __| | |  | |
  / ____ \ |___| |____| |____ ____) |___) |      | |__| | | \ \  / ____ \| |\  |  | |  | |____| |__| |
 /_/    \_\_____\_____|______|_____/_____/        \_____|_|  \_\/_/    \_\_| \_|  |_|  |______|_____/ 
"""

try:
    while True:

        time.sleep(0.5)

        print(f"{GREEN}{hack_font}{RESET}")

        time.sleep(1)

        os.system("clear")

finally:
    # Restore settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    print(RESET)