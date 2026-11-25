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
    raise TimeoutError("wait %r timeout last=%r" % (token, buf[-120:]))


def wait_data(s, seconds):
    t0 = time.time()
    buf = b""
    while time.time() - t0 < seconds:
        buf += s.read(s.in_waiting or 1)
    return buf


def enter_raw(s):
    # 先安静等板子自己进到 >>> 提示符，别一上来就灌字节
    wait_data(s, 1.0)
    for _ in range(8):
        s.write(b"\r\x03")
        time.sleep(0.3)
        buf = wait_data(s, 0.6)
        if b">>> " in buf or buf.endswith(b">"):
            s.write(b"\x01")
            time.sleep(0.3)
            got = wait_data(s, 0.8)
            if b"raw REPL" in got:
                s.write(b"\r")
                time.sleep(0.2)
                return
    raise TimeoutError("raw repl fail")


def exec_raw(s, code, timeout=20):
    s.write(code.encode() + b"\x04")
    read_until(s, b"OK", 8)
    out = read_until(s, b"\x04", timeout)
    err = read_until(s, b"\x04", timeout)
    return out[:-1].decode("utf-8", "replace"), err[:-1].decode("utf-8", "replace")


def put(s, name):
    with open(DIR + "\\" + name, "rb") as f:
        raw = f.read()
    data = base64.b64encode(raw).decode()
    lines = [data[i:i + 1400] for i in range(0, len(data), 1400)]
    total = len(lines)

    out, err = exec_raw(s, "import binascii\n_f=open(%r,'wb')\n" % name)
    i = 0
    t0 = time.time()
    while i < total:
        batch = lines[i:i + 10]
        code = "".join("_f.write(binascii.a2b_base64('%s'))\n" % l for l in batch)
        out, err = exec_raw(s, code, 25)
        if err.strip():
            print("ERR", err.strip()[:200])
            return False
        i += len(batch)
        print("  %s %d/%d  %ds" % (name, i, total, int(time.time() - t0), ), flush=True)
    out, err = exec_raw(s, "_f.close()\nprint('size', %d)\n" % len(raw))
    print("  done:", out.strip(), err.strip()[:100])
    return True


def main():
    files = sys.argv[1:] or ["st7789.py", "config.py", "main.py"]
    s = serial.Serial(PORT, 115200, timeout=0.2, rtscts=False, dsrdtr=False)
    s.dtr = False
    s.rts = False
    time.sleep(0.4)
    s.reset_input_buffer()
    enter_raw(s)
    out, err = exec_raw(s, "print('sync')")
    print("sync:", out.strip(), err.strip()[:100])
    for f in files:
        if not put(s, f):
            break
    out, err = exec_raw(s, "import os\nprint([(x, os.stat(x)[6]) for x in os.listdir() if x.endswith(('.py','.bin'))])")
    print("fs:", out.strip())
    s.write(b"\r\x02")
    time.sleep(0.3)
    s.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAILED:", repr(e))
        sys.exit(1)
