import time


class ST7789:
    """Minimal ST7789 SPI driver for MicroPython."""

    def __init__(self, spi, dc, cs, rst, width=240, height=240,
                 rotation=0, xstart=0, ystart=0, invert=True):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.w = width
        self.h = height
        self.xstart = xstart
        self.ystart = ystart
        self.rotation = rotation
        self.invert = invert
        self.reset()
        self.init()

    def reset(self):
        self.cs(1)
        self.rst(1)
        time.sleep_ms(20)
        self.rst(0)
        time.sleep_ms(20)
        self.rst(1)
        time.sleep_ms(60)

    def _cmd(self, cmd, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytes([cmd]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            self.spi.write(bytes([data]))
        else:
            self.spi.write(data)
        self.cs(1)

    def init(self):
        self._cmd(0x01)
        time.sleep_ms(150)
        self._cmd(0x11)
        time.sleep_ms(150)
        self._cmd(0x3A, bytes([0x55]))          # 16bit color
        self._cmd(0x36, bytes([[0x00, 0x60, 0xC0, 0xA0][self.rotation & 3]]))
        if self.invert:
            self._cmd(0x21)
        self._cmd(0x13)
        self._cmd(0x29)
        time.sleep_ms(60)

    def set_window(self, x, y, w, h):
        x0 = x + self.xstart
        y0 = y + self.ystart
        x1 = x0 + w - 1
        y1 = y0 + h - 1
        self._cmd(0x2A, bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self._cmd(0x2B, bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self._cmd(0x2C)

    def _fill_px(self, px, color, chunks=8):
        c = bytes([(color >> 8) & 0xFF, color & 0xFF])
        n = (px // chunks) + 1
        buf = c * n
        self.dc(1)
        self.cs(0)
        left = px
        while left > 0:
            if left >= n:
                self.spi.write(buf)
                left -= n
            else:
                self.spi.write(c * left)
                left = 0
        self.cs(1)

    def fill(self, color, chunks=8):
        self.set_window(0, 0, self.w, self.h)
        self._fill_px(self.w * self.h, color, chunks)

    def fill_rect(self, x, y, w, h, color, chunks=8):
        if w <= 0 or h <= 0:
            return
        self.set_window(x, y, w, h)
        self._fill_px(w * h, color, chunks)

    def blit(self, buf, x=0, y=0, w=None, h=None):
        w = w or self.w
        h = h or self.h
        self.set_window(x, y, w, h)
        self.dc(1)
        self.cs(0)
        mv = memoryview(buf)
        n = w * h * 2
        step = 4096
        i = 0
        while i < n:
            end = i + step
            if end > n:
                end = n
            self.spi.write(mv[i:end])
            i = end
        self.cs(1)

    def off(self):
        self._cmd(0x28)
