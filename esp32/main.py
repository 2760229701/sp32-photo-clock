# ESP32-S3 (N16R8) + 2.4寸 ST7789 240x320
# 时钟 + 天气 + 壁纸
SCK = 47
MOSI = 48
MISO = 41
DC = 39
RST = 38
CS = 40

WIDTH = 240
HEIGHT = 320
ROTATION = 0
SPI_HZ = 20_000_000

import machine
import time
import framebuf
from st7789 import ST7789

try:
    import config
except ImportError:
    config = None

# ---------------- 显示 ----------------
spi = machine.SPI(2, baudrate=SPI_HZ, polarity=0, phase=0,
                  sck=machine.Pin(SCK), mosi=machine.Pin(MOSI), miso=machine.Pin(MISO))
lcd = ST7789(spi, machine.Pin(DC, machine.Pin.OUT), machine.Pin(CS, machine.Pin.OUT),
             machine.Pin(RST, machine.Pin.OUT), WIDTH, HEIGHT, ROTATION, 0, 0, False)
print("lcd ok")

WHITE = 0xFFFF
GREY = 0x8410
BLUE = 0x5CDF
YELL = 0xFFE0

# ---------------- 壁纸 ----------------
WALL = None
try:
    WALL = bytearray(WIDTH * HEIGHT * 2)
    with open("wallpaper.bin", "rb") as f:
        f.readinto(WALL)
    print("wallpaper ok")
except Exception as e:
    print("wallpaper fail", e)
    WALL = None


def draw_bg():
    if WALL:
        lcd.blit(WALL, 0, 0, WIDTH, HEIGHT)
    else:
        for y in range(0, HEIGHT, 4):
            t = y / HEIGHT
            r = int(10 + 20 * t)
            g = int(14 + 10 * t)
            b = int(40 + 60 * t)
            c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            lcd.fill_rect(0, y, WIDTH, 4, c)


# ---------------- 放大字 ----------------
_glyphs = {}


def glyph(ch, scale, color):
    key = (ch, scale, color)
    g = _glyphs.get(key)
    if g:
        return g
    small = framebuf.FrameBuffer(bytearray(8), 8, 8, framebuf.MONO_VLSB)
    small.fill(0)
    small.text(ch, 0, 0, 1)
    w = 8 * scale
    c = bytes([(color >> 8) & 0xFF, color & 0xFF])
    out = bytearray()
    for y in range(8):
        row = bytearray(w * 2)
        for x in range(8):
            if small.pixel(x, y):
                row[x * scale * 2:(x + 1) * scale * 2] = c * scale
        for _ in range(scale):
            out.extend(row)
    _glyphs[key] = out
    return out


def text(x, y, s, scale=1, color=WHITE, shadow=True):
    step = 8 * scale
    off = 1 if scale <= 2 else 2
    for ch in s:
        g = glyph(ch, scale, color)
        if x >= 0 and x + step <= WIDTH:
            if shadow:
                gs = glyph(ch, scale, 0x0000)
                sx = x + off
                if sx + step <= WIDTH:
                    lcd.blit(gs, sx, min(y + off, HEIGHT - step), step, step)
            lcd.blit(g, x, y, step, step)
        x += step
    return x


# ---------------- WiFi ----------------
def wifi_connect():
    if not config or not getattr(config, "WIFI_SSID", ""):
        return False
    import network
    w = network.WLAN(network.STA_IF)
    w.active(True)
    if w.isconnected():
        return True
    w.connect(config.WIFI_SSID, config.WIFI_PASS)
    for _ in range(30):
        if w.isconnected():
            print("wifi ok")
            return True
        time.sleep(0.5)
    return False


# ---------------- 天气 ----------------
WCODE = {
    0: "CLEAR", 1: "MOSTLY CLEAR", 2: "PARTLY CLOUDY", 3: "OVERCAST",
    45: "FOG", 48: "FOG", 51: "DRIZZLE", 53: "DRIZZLE", 55: "DRIZZLE",
    61: "RAIN", 63: "RAIN", 65: "HEAVY RAIN", 66: "SLEET", 67: "SLEET",
    71: "SNOW", 73: "SNOW", 75: "HEAVY SNOW", 77: "SNOW",
    80: "SHOWERS", 81: "SHOWERS", 82: "HEAVY SHOWERS",
    85: "SNOW SHOWERS", 86: "SNOW SHOWERS",
    95: "THUNDER", 96: "THUNDER", 99: "THUNDER",
}

wx = {"temp": None, "code": 0, "humid": None, "tmax": None, "tmin": None, "ts": 0}


def weather_fetch():
    try:
        import urequests
        import ujson
        url = ("http://api.open-meteo.com/v1/forecast?latitude=%.2f&longitude=%.2f"
               "&current=temperature_2m,relative_humidity_2m,weather_code"
               "&daily=temperature_2m_max,temperature_2m_min,weather_code"
               "&timezone=Asia%%2FShanghai&forecast_days=1" % (config.LAT, config.LON))
        r = urequests.get(url, timeout=10)
        data = ujson.loads(r.text)
        r.close()
        cur = data["current"]
        daily = data["daily"]
        wx["temp"] = cur["temperature_2m"]
        wx["humid"] = cur["relative_humidity_2m"]
        wx["code"] = int(cur["weather_code"])
        wx["tmax"] = daily["temperature_2m_max"][0]
        wx["tmin"] = daily["temperature_2m_min"][0]
        wx["ts"] = time.time()
        print("weather ok", wx)
        return True
    except Exception as e:
        print("weather fail", e)
        return False


# ---------------- NTP ----------------
SYNCED = False
NTP_HOSTS = ("ntp.aliyun.com", "ntp1.aliyun.com", "cn.pool.ntp.org",
             "pool.ntp.org", "time.apple.com", "ntp.tencent.com")


def time_sync():
    global SYNCED
    import ntptime
    for host in NTP_HOSTS:
        try:
            ntptime.host = host
            ntptime.settime()
            SYNCED = True
            print("ntp ok", host, localtime())
            return True
        except Exception as e:
            print("ntp fail", host, e)
            time.sleep(0.4)
    return False


def localtime():
    tz = config.TZ if config else 8
    return time.localtime(time.time() + tz * 3600)


WD = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


def render():
    lt = localtime()
    draw_bg()

    # 顶部：城市 + 星期（放在时钟下面一行）
    city = (config.CITY if config else "SHENZHEN")
    text(10, 62, city, 1, BLUE)
    d = "%02d/%02d %s" % (lt[1], lt[2], WD[lt[6] % 7])
    text(WIDTH - 10 - len(d) * 8, 62, d, 1, WHITE)

    # 大时间 HH:MM：放在头顶上方
    if SYNCED:
        hm = "%02d:%02d" % (lt[3], lt[4])
    else:
        hm = "--:--"
    sc = 5
    w = len(hm) * 8 * sc
    x0 = (WIDTH - w) // 2
    text(x0, 16, hm, sc, WHITE)

    # 天气
    if wx["temp"] is not None:
        t = "%.0fC" % wx["temp"]
        text((WIDTH - len(t) * 8 * 3) // 2, 238, t, 3, WHITE)
        cond = WCODE.get(wx["code"], "N/A")
        text((WIDTH - len(cond) * 8) // 2, 276, cond, 1, WHITE)
        if wx["tmax"] is not None:
            lo = "L%.0f H%.0f RH%d%%" % (wx["tmin"], wx["tmax"], wx["humid"])
            text((WIDTH - len(lo) * 8) // 2, 296, lo, 1, GREY)
    else:
        msg = "NO WIFI / NO DATA"
        text((WIDTH - len(msg) * 8) // 2, 240, msg, 1, GREY)


# ---------------- 主流程 ----------------
online = False


def boot():
    global online
    lcd.fill(0x0000)
    text((WIDTH - 8 * 16) // 2, 140, "CONNECTING...", 1, WHITE)
    online = wifi_connect()
    if online:
        time_sync()
        weather_fetch()
    elif not config or not getattr(config, "WIFI_SSID", ""):
        # 没配 WiFi：照样显示，时间从开机算
        pass
    render()


boot()
print("first render done")

last_min = -1
last_wx = time.time()
last_sync_try = time.time()

while True:
    try:
        lt = localtime()
        # 每分钟才重画一次，避免频繁刷新闪烁
        if lt[4] != last_min or last_min < 0:
            last_min = lt[4]
            render()
        if online and not SYNCED and time.time() - last_sync_try > 30:
            last_sync_try = time.time()
            time_sync()
            render()
        if online and time.time() - last_wx > 600:
            weather_fetch()
            last_wx = time.time()
            render()
        if not online and config and getattr(config, "WIFI_SSID", ""):
            online = wifi_connect()
            if online:
                time_sync()
                weather_fetch()
                render()
        time.sleep(0.2)
    except Exception as e:
        print("loop err", e)
        time.sleep(2)
