import os, subprocess

BUILD = r'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi\build2'
NINJA = os.path.join(BUILD, 'build.ninja')
GXX = r'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\tools\xtensa-esp-elf\esp-15.2.0_20251204\xtensa-esp-elf\bin\xtensa-esp32s3-elf-g++.exe'
SRC = r'C:/Users/Administrator/Doubao/chats/2026-11-24/new-chat/xes/xiaozhi/main/display/lcd_display.cc'
TARGET = 'build esp-idf/main/CMakeFiles/__idf_main.dir/display/lcd_display.cc.obj:'

lines = open(NINJA, encoding='utf-8', errors='replace').read().splitlines()
idx = next(i for i, l in enumerate(lines) if l.startswith(TARGET))
vars = {}
for l in lines[idx+1:idx+9]:
    if l.startswith('  ') and '=' in l:
        k, v = l.strip().split('=', 1)
        vars[k] = v.strip()

def unesc(s):
    s = s.replace('$$', '\x00').replace('$ ', ' ').replace('$:', ':')
    return s.replace('\x00', '$')

content = ' '.join(unesc(vars.get(k, '')) for k in ('DEFINES', 'INCLUDES', 'FLAGS'))
rsp = os.path.join(BUILD, 'my.rsp')
open(rsp, 'w', encoding='utf-8').write(content)
print('rsp size', len(content), 'XZ in rsp', 'XZ_CLOCK_PANEL' in content)

res = subprocess.run([GXX, '@' + rsp, '-E', SRC], capture_output=True, text=True, errors='replace')
print('rc', res.returncode, 'stderr', res.stderr[:400])
out = res.stdout
print('ClockPanel in pp:', 'ClockPanel' in out, '| clock_panel.h:', 'clock_panel.h' in out)
open(os.path.join(BUILD, 'pre_lcd.i'), 'w', encoding='utf-8').write(out)
