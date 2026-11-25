"""用户照片 -> 240x320 RGB565 壁纸（整图压暗 + 上下渐变暗角，保证白字可读）"""
from PIL import Image, ImageEnhance

W, H = 240, 320

img = Image.open("photo_src.jpg").convert("RGB")

# 原图 1290x1720 = 3:4，正好等于 240:320，等比缩放即可
img = img.resize((W, H), Image.LANCZOS)

# 1) 整体压暗
img = ImageEnhance.Brightness(img).enhance(0.52)
img = ImageEnhance.Contrast(img).enhance(1.05)

# 2) 上下渐变暗角（顶部和底部更暗，中间保持通透）
px = img.load()
TOP = 70
BOT = 110
for y in range(H):
    if y < TOP:
        k = 1.0 - 0.55 * (1 - y / TOP)      # 越靠顶越暗
    elif y > H - BOT:
        k = 1.0 - 0.62 * ((y - (H - BOT)) / BOT)
    else:
        k = 1.0
        for x in range(W):
            r, g, b = px[x, y]
            px[x, y] = (int(r * k), int(g * k), int(b * k))
        continue
    for x in range(W):
        r, g, b = px[x, y]
        px[x, y] = (int(r * k), int(g * k), int(b * k))

buf = bytearray(W * H * 2)
i = 0
prepare = img.load()
for y in range(H):
    for x in range(W):
        r, g, b = prepare[x, y]
        c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        buf[i] = (c >> 8) & 0xFF
        buf[i + 1] = c & 0xFF
        i += 2

with open("wallpaper.bin", "wb") as f:
    f.write(buf)

img.save("wall_preview.png")
print("ok", len(buf))
