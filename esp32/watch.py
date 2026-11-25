import time

import serial

s = serial.Serial("COM5", 115200, timeout=0.2, rtscts=False, dsrdtr=False)
s.dtr = False
s.rts = False
time.sleep(0.2)
# 硬复位：拉低 RTS
s.rts = True
time.sleep(0.15)
s.rts = False
s.reset_input_buffer()
t0 = time.time()
buf = b""
while time.time() - t0 < 8:
    buf += s.read(64)
text = buf.decode("utf-8", "replace").replace("\r", "")
print(text)
print("---- resets:", text.count("ESP-ROM"))
s.close()
