from PIL import Image
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\board_new.jpg")
im.crop((660, 520, 2300, 1250)).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\crop_clock.png")
print("ok")
