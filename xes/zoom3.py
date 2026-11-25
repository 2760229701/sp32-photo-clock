from PIL import Image, ImageEnhance
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3.jpg")
c = im.crop((650, 600, 2400, 1500))
c = c.resize((1175, 675))
c.save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\zoom3.png")
print(c.size)
