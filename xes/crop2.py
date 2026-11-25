from PIL import Image
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\board_new.jpg")
im.crop((690, 950, 2270, 1500)).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\crop_mid.png")
print("ok")
