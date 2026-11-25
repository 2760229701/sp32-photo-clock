import base64, re
from PIL import Image
raw = open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\bootlog.txt", "rb").read().decode("utf-8", "ignore")
s = raw.find("@@SHOT_BEGIN@@")
e = raw.find("@@SHOT_END@@")
print("begin", s, "end", e, "seg len", e - s)
seg = raw[s + len("@@SHOT_BEGIN@@"):e]
seg = re.sub(r"[^A-Za-z0-9+/=]", "", seg)
print("b64 chars", len(seg))
data = base64.b64decode(seg + "=" * (-len(seg) % 4))
print("bytes", len(data))
w, h = 240, 120
img = Image.new("RGB", (w, len(data) // (w * 2)))
px = img.load()
for i in range(0, min(len(data), w * h * 2) - 1, 2):
    v = data[i] | (data[i + 1] << 8)
    r = ((v >> 11) & 0x1F) * 255 // 31
    g = ((v >> 5) & 0x3F) * 255 // 63
    b = (v & 0x1F) * 255 // 31
    idx = i // 2
    px[idx % w, idx // w] = (r, g, b)
img.resize((480, img.size[1] * 2), Image.NEAREST).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\screen_shot.png")
print("saved", img.size)
