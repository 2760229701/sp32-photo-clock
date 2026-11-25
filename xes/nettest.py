import os, tempfile, time, urllib.request

url = "https://dl.espressif.com/dl/esp-idf/downloads/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf-esp-15.2.0_20251204-x86_64-w64-mingw32-linux.tar.xz"
base = "https://dl.espressif.com/dl/esp-idf/downloads/tools/"
# 先试目录页判断连通性
for u in ["https://dl.espressif.com/dl/esp-idf/", base]:
    t = time.time()
    try:
        r = urllib.request.urlopen(u, timeout=20)
        print("OK", r.status, u, round(time.time() - t, 1), "s")
    except Exception as e:
        print("ERR", u, type(e).__name__, str(e)[:120])
