from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 780
img = Image.new("RGB", (W, H), (250, 250, 248))
d = ImageDraw.Draw(img)

f = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)
fb = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 26)
fs = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)


def box(x, y, w, h, title, lines, fill=(255, 255, 255), border=(60, 60, 60)):
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=fill, outline=border, width=2)
    d.text((x + 14, y + 10), title, font=fb, fill=(20, 20, 20))
    yy = y + 46
    for ln in lines:
        d.text((x + 14, yy), ln, font=fs, fill=(60, 60, 60))
        yy += 24


def arrow(x1, y1, x2, y2, label, color=(200, 40, 40), lx=None, ly=None):
    d.line([x1, y1, x2, y2], fill=color, width=4)
    # 箭头
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (-0.5, 0.5):
        d.line([x2, y2, x2 - 14 * math.cos(a + s), y2 - 14 * math.sin(a + s)], fill=color, width=4)
    if label:
        d.text((lx if lx else (x1 + x2) / 2 - 60, ly if ly else (y1 + y2) / 2 - 26), label, font=fs, fill=color)


d.text((40, 24), "ESP32-S3 时钟：加 18650 电池 + USB 充电模块 接线图", font=fb, fill=(0, 0, 0))
d.text((40, 62), "（只画电源部分，屏幕/麦克风/功放的数据线保持原样不动）", font=fs, fill=(90, 90, 90))

# 电池
box(40, 150, 260, 150, "18650 电池（3.7V）", ["正极 → B+", "负极 → B-", "必须带保护板 或 模块带保护"], fill=(255, 245, 230))
# 充电模块
box(370, 130, 330, 190, "USB 充电模块（推荐 IP5306 类）", [
    "USB-C 口：插线充电",
    "B+ / B-：接电池",
    "OUT+ / OUT-：输出 5V",
    "自带升压 + 保护 + 边充边用",
], fill=(232, 244, 255))
# 开发板
box(780, 130, 380, 190, "ESP32-S3 开发板", [
    "5V / VIN 脚 ← 接模块 5V 输出",
    "GND 脚 ← 接模块 GND",
    "3V3 脚 → 屏 VCC / 麦 VDD",
    "（不要把 3.7V 直接接 3V3）",
], fill=(236, 255, 238))

arrow(300, 225, 366, 225, "B+ / B-", lx=300, ly=190)
arrow(704, 225, 776, 225, "5V 与 GND", lx=700, ly=190, color=(30, 120, 200))

# 外设
box(40, 400, 520, 210, "屏幕 / 麦克风 / 功放", [
    "屏 VCC   → 3V3     屏 GND → GND",
    "麦 VDD   → 3V3     麦 GND → GND",
    "功放 VIN → 3V3（安静）或 5V（更响）",
    "所有 GND 必须和电池 GND 连在一起（共地）",
], fill=(255, 255, 255))
arrow(900, 320, 900, 400, "", color=(30, 160, 80))
d.text((912, 340), "3V3 / GND", font=fs, fill=(30, 160, 80))

# 电容
box(620, 410, 520, 180, "电源加两个电容（很重要）", [
    "模块 5V 输出处：并 100µF 电解（正对正）",
    "再并 0.1µF 瓷片（滤高频）",
    "功放 VIN 附近：再并 100µF",
    "作用：播放时电流冲击大，不加会花屏/重启",
], fill=(255, 250, 235))

# 文字备注
d.text((40, 650), "顺序：先接电池到模块 → 模块输出接板子 5V → 最后插 USB 充电。接反会烧模块，务必看清丝印。",
       font=f, fill=(180, 40, 40))
d.text((40, 700), "续航参考：2500mAh 电池约 5~7 小时（常亮屏 + WiFi + 偶尔对话）；用 IP5306 可边充边用。",
       font=f, fill=(60, 60, 60))

img.save(r"C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\电池接线图.png")
print("ok")
