import machine
import time


def log(msg):
    with open("log.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)


open("log.txt", "w").close()
log("1 start")
try:
    import framebuf
    log("2 framebuf ok")
    spi = machine.SPI(2, baudrate=20_000_000, polarity=0, phase=0,
                      sck=machine.Pin(12), mosi=machine.Pin(11))
    log("3 spi ok")
    dc = machine.Pin(10, machine.Pin.OUT)
    cs = machine.Pin(8, machine.Pin.OUT)
    rst = machine.Pin(9, machine.Pin.OUT)
    bl = machine.Pin(7, machine.Pin.OUT)
    bl.value(1)
    log("4 pins ok")
    from st7789 import ST7789
    log("5 import drv ok")
    lcd = ST7789(spi, dc, cs, rst, 240, 240, 0, 0, 0)
    log("6 lcd init ok")
    lcd.fill(0xF800)
    log("7 fill red ok")
    time.sleep(1)
    lcd.fill(0x07E0)
    log("8 fill green ok")
    lcd.fill(0x001F)
    log("9 fill blue ok")
    lcd.fill(0xFFFF)
    log("10 fill white ok")
    log("done")
except Exception as e:
    log("EXC: %r" % (e,))
    time.sleep(0.2)
    raise
