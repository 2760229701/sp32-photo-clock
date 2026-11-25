import machine
import time


def log(m):
    with open("log.txt", "a") as f:
        f.write(m + "\n")
    print(m)


open("log.txt", "w").close()
log("start")
spi = machine.SPI(2, baudrate=20_000_000, polarity=0, phase=0,
                  sck=machine.Pin(12), mosi=machine.Pin(11), miso=machine.Pin(13))
log("spi ok")

dc = machine.Pin(10, machine.Pin.OUT)
cs = machine.Pin(8, machine.Pin.OUT)
rst = machine.Pin(9, machine.Pin.OUT)
bl = machine.Pin(7, machine.Pin.OUT)
bl.value(1)
log("pins ok")

from st7789 import ST7789
lcd = ST7789(spi, dc, cs, rst, 240, 240, 0, 0, 0)
log("lcd init ok")

lcd.fill(0xF800)
log("fill RED")
time.sleep(1)
lcd.fill(0x07E0)
log("fill GREEN")
time.sleep(1)
lcd.fill(0x001F)
log("fill BLUE")
time.sleep(1)
lcd.fill(0xFFFF)
log("fill WHITE")
time.sleep(1)
lcd.fill(0x0000)
log("fill BLACK")
log("done")
