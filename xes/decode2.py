import base64, re
from PIL import Image
raw = open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\bootlog.txt","rb").read().decode("utf-8","ignore")
s = raw.find("@@SHOT_BEGIN@@"); e = raw.find("@@SHOT_END@@")
seg = re.sub(r"[^A-Za-z0-9+/=]", "", raw[s+14:e])
data = base64.b64decode(seg + "="*(-len(seg)%4))
print("bytes", len(data))
w = 240
for name, swap, order in [("swap_rgb", True, "rgb"), ("noswap_rgb", False, "rgb"), ("noswap_bgr", False, "bgr"), ("swap_bgr", True, "bgr")]:
    h = len(data)//(w*2)
    img = Image.new("RGB", (w, h)); px = img.load()
    for i in range(0, w*h*2-1, 2):
        v = (data[i+1] | (data[i]<<8)) if swap else (data[i] | (data[i+1]<<8))
        c1 = ((v>>11)&0x1F)*255//31; c2 = ((v>>5)&0x3F)*255//63; c3 = (v&0x1F)*255//31
        r,g,b = (c1,c2,c3) if order=="rgb" else (c3,c2,c1)
        idx = i//2
        px[idx%w, idx//w] = (r,g,b)
    img.save(rf"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\shot_{name}.png")
    print(name, img.size)
