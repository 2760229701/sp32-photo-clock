from PIL import Image, ImageDraw, ImageFont
base = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\wall_swapped.png").convert("RGB")
d = ImageDraw.Draw(base)
def draw(t, y, size, f):
    fnt = ImageFont.truetype(f, size)
    w = d.textlength(t, font=fnt)
    x = (240 - w) / 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            d.text((x+dx, y+dy), t, font=fnt, fill=(0,0,0))
    d.text((x, y), t, font=fnt, fill=(255,255,255))
draw("11:25", 0, 48, r"C:\Windows\Fonts\arialbd.ttf")
draw("11月25日 周三", 38, 20, r"C:\Windows\Fonts\msyh.ttc")
draw("14.6°C 阴 湿度60%", 68, 20, r"C:\Windows\Fonts\msyh.ttc")
base.save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\clock_preview.png")
print("ok")
