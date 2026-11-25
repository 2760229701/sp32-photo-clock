from PIL import Image, ImageDraw, ImageFont

W, H = 240, 320
bg = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\壁纸原图.png").convert("RGB")
bg = bg.resize((W, H))

f_time = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 72)
f_cjk = ImageFont.truetype(r"C:\Windows\Fonts\simhei.ttf", 20)

img = bg.copy()
d = ImageDraw.Draw(img)

def outlined(x, y, text, font, anchor="la"):
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), text, font=font, fill=(255, 255, 255), anchor=anchor)

# 日期：右上角
outlined(W - 6, 0, "11月25日 周三", f_cjk, anchor="ra")
# 大时钟：左上
outlined(8, 18, "11:25", f_time, anchor="la")
# 天气：时钟下面
outlined(10, 78, "15.8°C 阴 湿度56%", f_cjk, anchor="la")

out = r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\时钟效果预览.png"
img.save(out)
print("saved", out)
