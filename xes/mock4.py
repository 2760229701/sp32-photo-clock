from PIL import Image, ImageDraw, ImageFont
W,H=240,320
bg=Image.open(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\壁纸原图.png").convert("RGB").resize((W,H))
ft=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",48)
fc=ImageFont.truetype(r"C:\Windows\Fonts\simhei.ttf",20)
d=ImageDraw.Draw(bg)
def ol(x,y,t,f,a="la"):
    for dx,dy in((-1,-1),(1,-1),(-1,1),(1,1)):
        d.text((x+dx,y+dy),t,font=f,fill=(0,0,0),anchor=a)
    d.text((x,y),t,font=f,fill=(255,255,255),anchor=a)
ol(W-8,6,"11月25日",fc,"ra")
ol(W-8,28,"15.8°C",fc,"ra")
ol(W-8,50,"湿度56%",fc,"ra")
ol(W-8,72,"周三",fc,"ra")
ol(8,34,"02:44",ft,"la")
bg.save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\时钟效果预览.png")
print("ok")
