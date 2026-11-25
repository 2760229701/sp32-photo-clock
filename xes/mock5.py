from PIL import Image, ImageDraw, ImageFont
import os

W, H = 240, 320
base = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\壁纸原图.png").convert("RGB").resize((W, H))
d = ImageDraw.Draw(base)

cjk = ImageFont.truetype(r"C:\Windows\Fonts\simhei.ttf", 20)
cjk16 = ImageFont.truetype(r"C:\Windows\Fonts\simhei.ttf", 16)
clk = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 44)


def text_right(s, y, font=cjk, right=W - 8):
    w = d.textlength(s, font=font)
    x = right - w
    # 黑描边
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            d.text((x + dx, y + dy), s, font=font, fill=(0, 0, 0))
    d.text((x, y), s, font=font, fill=(255, 255, 255))


def text_left(s, x, y, font=clk):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            d.text((x + dx, y + dy), s, font=font, fill=(0, 0, 0))
    d.text((x, y), s, font=font, fill=(255, 255, 255))


text_right("11月25日", 6, font=cjk16, right=W - 4)
text_right("15.8°C", 33)
text_right("湿度56%", 55)
text_right("周三", 77)
text_left("11:25", 8, 36)

out = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\时钟效果预览.png"
base.save(out)
print(out)

