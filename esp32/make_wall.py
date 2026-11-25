"""把壁纸转成 ST7789 用的 RGB565 原始数据，并预先旋转 180°（抵消屏幕的 180° 旋转）"""
from PIL import Image

W, H = 240, 320

img = Image.open("wall_src.png").convert("RGB")
# 先缩放到 240x320（等比裁剪填满）
src_ratio = img.width / img.height
dst_ratio = W / H
if src_ratio > dst_ratio:
    # 太宽，裁左右
    new_w = int(img.height * dst_ratio)
    left = (img.width - new_w) // 2
    img = img.crop((left, 0, left + new_w, img.height))
else:
    new_h = int(img.width / dst_ratio)
    top = (img.height - new_h) // 2
    img = img.crop((0, top, img.width, top + new_h))

img = img.resize((W, H), Image.LANCZOS)

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
print("wallpaper.bin", len(buf), "bytes")
