import serial, time, sys
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60
s = serial.Serial('COM5', 115200, timeout=0.2)
t0 = time.time(); buf = []
while time.time() - t0 < dur:
    d = s.read(4096)
    if d: buf.append(d)
s.close()
txt = b''.join(buf).decode('utf-8', 'replace')
open(r'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\bootlog.txt', 'w', encoding='utf-8').write(txt)
print('Guru count:', txt.count('Guru'))
print('rst count:', txt.count('rst:0x'))
bad = [l for l in txt.splitlines() if any(k in l for k in ('panic', 'abort', 'assert', 'Guru', 'Backtrace', 'rst:'))]
print('\n'.join(bad[:25]))
print('---- tail ----')
print(txt[-800:])
