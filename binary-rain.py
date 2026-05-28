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
sys.stdout.write("\033]0;Binary Exploit\a")

index = 0

fake_output = [
    "01010111 01100101 01101100 01100011 01101111 01101101 01100101 00100000 01110100 01101111",
    "00100000 01110100 01101000 01100101 00100000 01100101 01110000 01101001 01100011 00100000",
    "01101101 01100001 01110011 01110100 01100101 01110010 00100000 01101000 01100001 01100011",
    "01101011 01100101 01110010 00100000 01100011 01101100 01110101 01100010 00100001 00100001",
]

try:
    while True:


        if index >= len(fake_output):
            index = 0

        print(f"{GREEN}{fake_output[index]}{RESET}")

        index += 1
        time.sleep(0.01)

finally:
    # Restore settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    print(RESET)