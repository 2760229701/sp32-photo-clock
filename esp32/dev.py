import base64
import sys
import time

import serial

PORT = "COM5"
DIR = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\esp32"


def read_until(s, token, timeout):
    t0 = time.time()
    buf = b""
    while time.time() - t0 < timeout:
        buf += s.read(1)
        if buf.endswith(token):
            return buf
    raise TimeoutError("wait %r timeout, got %r" % (token, buf[-200:]))


def enter_raw_repl(s):
    for _ in range(6):
        s.write(b"\r\x03")
        time.sleep(0.15)
        s.write(b"\r")
        time.sleep(0.25)
        s.write(b"\x01")
        t0 = time.time()
        buf = b""
        while time.time() - t0 < 2.0:
            buf += s.read(8)
            if b"raw REPL; CTRL-B to exit" in buf:
                read_until(s, b">", 3)
                return
        time.sleep(0.2)
    raise TimeoutError("cannot enter raw repl, last=%r" % buf[-200:])


def exit_raw_repl(s):
    s.write(b"\r\x02")


def exec_raw(s, code, timeout=10):
    s.write(code.encode() + b"\x04")
    r = read_until(s, b"OK", 6)
    out = read_until(s, b"\x04", timeout)
    err = read_until(s, b"\x04", timeout)
    return out[:-1].decode("utf-8", "replace"), err[:-1].decode("utf-8", "replace")


def soft_reset(s):
    exit_raw_repl(s)
    time.sleep(0.3)
    s.write(b"\r\x03")
    time.sleep(0.3)


def put(s, local_name, remote_name):
    with open(DIR + "\\" + local_name, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    code = "import binascii\n_f=open(%r,'wb')\n" % remote_name
    for i in range(0, len(data), 1000):
        code += "_f.write(binascii.a2b_base64('%s'))\n" % data[i:i + 1000]
    code += "_f.close()\nprint('wrote', %d)\n" % len(data)
    out, err = exec_raw(s, code, 15)
    print(remote_name, "->", out.strip()[-40:], err.strip()[-120:])


def main():
    s = serial.Serial(PORT, 115200, timeout=0.3, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    time.sleep(0.4)
    s.reset_input_buffer()
    enter_raw_repl(s)
    out, err = exec_raw(s, "print('hello from py', 1+1)")
    print("sync:", out.strip(), err.strip())
    soft_reset(s)
    enter_raw_repl(s)

    put(s, "st7789.py", "st7789.py")
    put(s, "main.py", "main.py")

    out, err = exec_raw(s, "import os\nprint(os.listdir())")
    print("fs:", out.strip(), err.strip())

    print("---- running main.py ----")
    out, err = exec_raw(s, "exec(open('main.py').read())", 25)
    print("OUT:\n" + out)
    print("ERR:\n" + err)
    exit_raw_repl(s)
    s.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", repr(e))
        sys.exit(1)
