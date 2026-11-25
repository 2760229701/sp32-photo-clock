import sys
import time

import serial

PORT = "COM5"


def open_port():
    s = serial.Serial(PORT, 115200, timeout=0.2, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    time.sleep(0.3)
    return s


def wait_prompt(s, timeout=8):
    t0 = time.time()
    buf = b""
    while time.time() - t0 < timeout:
        buf += s.read(16)
        if buf.endswith(b">>> "):
            return True
    return False


def try_code(code, wait=8.0):
    s = open_port()
    s.reset_input_buffer()
    s.write(b"\r\x03")
    time.sleep(0.3)
    if not wait_prompt(s):
        s.write(b"\r\x03")
        time.sleep(0.3)
        wait_prompt(s)
    s.reset_input_buffer()
    s.write(code.encode() + b"\r\n")
    t0 = time.time()
    out = b""
    reset = False
    while time.time() - t0 < wait:
        chunk = s.read(64)
        if chunk:
            out += chunk
            if b"ESP-ROM" in out or b"TG1WDT" in out:
                reset = True
                break
    s.close()
    text = out.decode("utf-8", "replace")
    return reset, text


TESTS = [
    ("A: SPI(2) 默认引脚",
     "import machine\nprint('go')\ns=machine.SPI(2)\nprint('SPI2 ok')"),
    ("B: SPI(2) 只给 sck/mosi 无波特率",
     "import machine\nprint('go')\ns=machine.SPI(2, sck=machine.Pin(12), mosi=machine.Pin(11))\nprint('SPI2 pins ok')"),
    ("C: SPI(2) 带波特率5M",
     "import machine\nprint('go')\ns=machine.SPI(2, baudrate=5_000_000, sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))\nprint('SPI2 5M ok')"),
    ("D: SPI(1) 带引脚",
     "import machine\nprint('go')\ns=machine.SPI(1, baudrate=10_000_000, sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))\nprint('SPI1 ok')"),
]

if __name__ == "__main__":
    for name, code in TESTS:
        reset, text = try_code(code)
        clean = " ".join(text.replace("\r", " ").replace("\n", " ").split())
        print(("[HANG] " if reset else "[OK]   ") + name + " | " + clean[-120:])
        if reset:
            time.sleep(2)
