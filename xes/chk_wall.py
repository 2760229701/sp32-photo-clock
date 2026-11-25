from PIL import Image
import numpy as np
d = open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi\main\clock_wallpaper.bin","rb").read()
a = np.frombuffer(d, dtype="<u2").reshape(320,240)
def render(arr, path):
    r = ((arr >> 11) & 0x1F) * 255 // 31
    g = ((arr >> 5) & 0x3F) * 255 // 63
    b = (arr & 0x1F) * 255 // 31
    img = np.stack([r,g,b], axis=2).astype(np.uint8)
    Image.fromarray(img).save(path)
    print(path, "mean RGB", img.reshape(-1,3).mean(axis=0))
a2 = ((a >> 8) | (a << 8)) & 0xFFFF
render(a, r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\wall_normal.png")
render(a2, r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\wall_swapped.png")
print("len", len(d))
