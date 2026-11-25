"""照片 -> 240x320 壁纸（不加暗角、不加暗底，只做极轻微整体调整，保持原图观感）"""
from PIL import Image, ImageEnhance

W, H = 240, 320

img = Image.open("photo_src.jpg").convert("RGB")
img = img.resize((W, H), Image.LANCZOS)
img = ImageEnhance.Brightness(img).enhance(0.92)
img = ImageEnhance.Contrast(img).enhance(1.04)

buf = bytearray(W * H * 2)
i = 0
px = img.load()
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        buf[i] = (c >> 8) & 0xFF
        buf[i + 1] = c & 0xFF
        i += 2

with open("wallpaper.bin", "wb") as f:
    f.write(buf)
img.save("wall_preview.png")
print("ok", len(buf))
