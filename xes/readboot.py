import serial, time, sys
ser = serial.Serial('COM5', 115200, timeout=0.2)
t0 = time.time()
buf = []
while time.time() - t0 < 22:
    d = ser.read(4096)
    if d:
        buf.append(d)
ser.close()
txt = b''.join(buf).decode('utf-8', 'replace')
print(txt[-8000:])
