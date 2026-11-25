from PIL import Image
im = Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3.jpg")
im.resize((800, int(800*im.size[1]/im.size[0]))).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3_small.jpg", quality=82)
im.crop((600, 600, 2400, 1400)).save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\b3_top.png")
print("ok")
