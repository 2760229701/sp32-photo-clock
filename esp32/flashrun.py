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
    raise TimeoutError("wait %r timeout" % (token,))


def open_port():
    s = serial.Serial(PORT, 115200, timeout=0.2, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    time.sleep(0.4)
    return s


def enter_raw(s):
    for _ in range(8):
        s.write(b"\r\x03")
        time.sleep(0.15)
        s.write(b"\r")
        time.sleep(0.2)
        s.write(b"\x01")
        t0 = time.time()
        buf = b""
        while time.time() - t0 < 2.0:
            buf += s.read(8)
            if b"raw REPL; CTRL-B to exit" in buf:
                read_until(s, b">", 3)
                return
        time.sleep(0.2)
    raise TimeoutError("raw repl fail")


def exec_raw(s, code, timeout=10):
    s.write(code.encode() + b"\x04")
    read_until(s, b"OK", 6)
    out = read_until(s, b"\x04", timeout)
    err = read_until(s, b"\x04", timeout)
    return out[:-1].decode("utf-8", "replace"), err[:-1].decode("utf-8", "replace")


def put(s, name):
    with open(DIR + "\\" + name, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    code = "import binascii\n_f=open(%r,'wb')\n" % name
    for i in range(0, len(data), 1000):
        code += "_f.write(binascii.a2b_base64('%s'))\n" % data[i:i + 1000]
    code += "_f.close()\nprint('wrote',%d)\n" % len(data)
    out, err = exec_raw(s, code, 15)
    print(name, out.strip()[-20:], err.strip()[-100:])


def main():
    script = sys.argv[1] if len(sys.argv) > 1 else "t1.py"
    s = open_port()
    s.reset_input_buffer()
    enter_raw(s)
    for f in ("st7789.py", script):
        put(s, f)
    s.write(b"\r\x02")
    time.sleep(0.3)
    s.write(b"\r\x03")
    time.sleep(0.3)
    s.reset_input_buffer()

    print("=== run %s ===" % script)
    s.write(("exec(open(%r).read())" % script).encode() + b"\r\n")
    t0 = time.time()
    out = b""
    while time.time() - t0 < 25:
        chunk = s.read(64)
        if chunk:
            out += chunk
            if b"done" in out and b">>> " in out[out.rfind(b"done"):]:
                break
        if b"ESP-ROM" in out:
            break
    print(out.decode("utf-8", "replace").replace("\r", ""))
    s.close()

    # always dump log.txt in a fresh connection
    time.sleep(1.0)
    s = open_port()
    s.reset_input_buffer()
    s.write(b"\r\x03")
    time.sleep(0.3)
    s.write(b"print(open('log.txt').read())\r\n")
    t0 = time.time()
    buf = b""
    while time.time() - t0 < 5:
        buf += s.read(64)
    print("=== log ===")
    print(buf.decode("utf-8", "replace").replace("\r", ""))
    s.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", repr(e))
        sys.exit(1)
