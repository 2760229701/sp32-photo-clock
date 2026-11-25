from PIL import Image, ImageEnhance
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3.jpg")
# 屏幕左上区域（时钟应该在的地方）
c = im.crop((690, 780, 1400, 1100)).resize((710, 320))
ImageEnhance.Contrast(c).enhance(1.6).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\zoom_clock.png")
print("ok")
