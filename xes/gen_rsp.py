import os, re, io

BUILD = r'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi\build'
NINJA = os.path.join(BUILD, 'build.ninja')

def unesc(s):
    # ninja escaping: $$ -> $, "$ " -> space, "$:" -> :
    s = s.replace('$$', '\x00')
    s = s.replace('$ ', ' ').replace('$:', ':')
    s = s.replace('\x00', '$')
    return s

edges = {}
cur = None
with open(NINJA, 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.rstrip('\n')
        m = re.match(r'build ([^:]+): (CXX_COMPILER|C_COMPILER|ASM|CXX_COMPILER__|C_COMPILER__)', line)
        if m:
            cur = m.group(1).strip()
            edges[cur] = {}
            continue
        if cur and line.startswith('  ') and '=' in line:
            k, v = line.strip().split('=', 1)
            edges[cur][k.strip()] = v.strip()
            continue
        if line and not line.startswith(' '):
            cur = None

written = 0
for out, vars in edges.items():
    rsp = vars.get('RSP_FILE')
    if not rsp:
        continue
    content = ' '.join(unesc(vars.get(k, '')) for k in ('DEFINES', 'INCLUDES', 'FLAGS'))
    content = content.strip() + '\n'
    path = os.path.join(BUILD, rsp.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    written += 1

print('edges:', len(edges), 'rsp written:', written)
