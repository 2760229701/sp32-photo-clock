from PIL import Image
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\board_new.jpg")
im = im.crop((690, 500, 2270, 1050)).resize((1580//1, 550//1))
im.save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\crop_top.png")
print(im.size)
