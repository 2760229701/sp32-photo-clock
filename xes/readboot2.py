import serial, time
s = serial.Serial('COM5', 115200, timeout=0.2)
t0 = time.time(); buf = []
while time.time() - t0 < 25:
    d = s.read(4096)
    if d: buf.append(d)
s.close()
txt = b''.join(buf).decode('utf-8', 'replace')
open(r'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\bootlog.txt', 'w', encoding='utf-8').write(txt)
bad = [l for l in txt.splitlines() if any(k in l for k in ('panic', 'abort', 'assert', 'Guru', 'Backtrace', 'LoadProhibited', 'rst:'))]
print('\n'.join(bad[:20]))
print('---- tail ----')
print(txt[-1500:])
