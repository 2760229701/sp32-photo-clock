from PIL import Image, ImageEnhance
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3.jpg")
im.crop((730, 950, 1290, 1230)).resize((1120, 460)).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\zoom_clock2.png")
print("ok")
