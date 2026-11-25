import base64
import sys
import time

import serial

PORT = "COM5"
DIR = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\esp32"


def read_all(s, seconds):
    t0 = time.time()
    buf = b""
    while time.time() - t0 < seconds:
        buf += s.read(s.in_waiting or 1)
    return buf.decode("utf-8", "replace")


def wait_prompt(s, timeout=6):
    t0 = time.time()
    buf = b""
    while time.time() - t0 < timeout:
        buf += s.read(8)
        if buf.endswith(b">>> "):
            return True
    return False


def main():
    s = serial.Serial(PORT, 115200, timeout=0.2, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    time.sleep(0.5)
    s.reset_input_buffer()
    s.write(b"\r\x03")
    time.sleep(0.4)
    wait_prompt(s)

    # upload diag.py via raw repl
    s.write(b"\r\x01")
    t0 = time.time()
    buf = b""
    while time.time() - t0 < 6:
        buf += s.read(8)
        if b"raw REPL; CTRL-B to exit" in buf:
            break
    s.write(b"\r")
    time.sleep(0.2)

    with open(DIR + "\\diag.py", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    code = "import binascii\n_f=open('diag.py','wb')\n"
    for i in range(0, len(data), 1000):
        code += "_f.write(binascii.a2b_base64('%s'))\n" % data[i:i + 1000]
    code += "_f.close()\nprint('ok')\n"
    s.write(code.encode() + b"\x04")
    print("upload:", read_all(s, 2).replace("\x04", "|")[-80:])

    s.write(b"\x04")
    time.sleep(0.2)
    s.write(b"\r\x02")  # exit raw
    time.sleep(0.3)
    s.write(b"\r\x03")
    time.sleep(0.3)
    s.reset_input_buffer()

    print("=== run diag ===")
    s.write(b"exec(open('diag.py').read())\r\n")
    print(read_all(s, 25))
    print("=== after ===")
    s.write(b"\r\x03")
    print(read_all(s, 1))
    s.write(b"print(open('log.txt').read())\r\n")
    print(read_all(s, 4))
    s.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", repr(e))
        sys.exit(1)
