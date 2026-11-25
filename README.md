# ESP32-S3 照片时钟 + 小智语音助手（同一固件）

一块 **ESP32-S3 N16R8（16MB Flash / 8MB PSRAM）+ 2.4 寸 ST7789 240×320 竖屏**，
在一个固件里同时做到两件事：

- 待机时是「照片壁纸 + 大时钟 + 日期 + 天气」的桌面时钟
- 按下 BOOT 键可以对它说话，小智语音助手正常对话（麦克风 + 功放）

屏幕上所有文字都是 **白色 + 黑色描边、无底色**，时间只显示 `HH:MM`（无秒、每分钟才重绘一次，不闪）。
壁纸、时钟、天气全部集中在屏幕顶部 96 像素内，下面整片区域留给小智的表情和对话文字，互不遮挡。

## 硬件

| 部件 | 型号/说明 |
|---|---|
| 主控 | ESP32-S3 N16R8，MAC `ec:d6:1b:32:e7:38`，串口 COM5 |
| 屏幕 | 2.4" ST7789 240×320 竖屏（丝印上排 GND SCK RES CS，下排 3V3 SDA DC BL） |
| 麦克风 | INMP441 类 I2S 数字麦克风 |
| 功放 | MAX98357A 类 I2S 功放 + 小喇叭 |

### 接线

屏幕（SPI）：

```
SDA/MOSI -> GPIO48    SCK/CLK -> GPIO47    DC -> GPIO39
RES/RST  -> GPIO38    CS      -> GPIO40    BL -> 3V3（常亮）
```

麦克风（INMP441）：

```
VDD -> 3V3    GND -> GND    L/R -> GND（选左声道）
SCK/BCLK -> GPIO5    WS/LRCLK -> GPIO4    SD/DATA -> GPIO6
```

功放（MAX98357A）：

```
VIN -> 3V3（想更响可接 5V）    GND -> GND
BCLK -> GPIO15    LRC -> GPIO16    DIN -> GPIO7
SD -> 3V3（必须接高，悬空会静音/异常）    GAIN -> 悬空（默认 9dB）
```

## 目录

```
esp32/                     MicroPython 版照片时钟（可单独刷回，见下）
xes/xiaozhi/               xiaozhi-esp32 源码（已按本板卡改过，见“改动清单”）
xes/*.bat, *.py            本机的编译/烧录/串口抓日志脚本
时钟效果预览.png           最终屏幕排布预览
固件备份/                  已验证可用的固件镜像（不入库，见 .gitignore）
```

## 编译

需要 ESP-IDF v6.0.2 + xtensa-esp-elf 工具链。本仓库不包含 IDF 与工具链，请自行 `install`/`export`，
或参考 `xes/` 下脚本里用到的环境变量：

```
IDF_PATH=xes/esp-idf
IDF_TOOLS_PATH=xes/espressif
IDF_COMPONENT_CACHE_PATH=xes/cmpcache
IDF_GITHUB_ASSETS=dl.espressif.cn/github_assets      # github 下载失败的替代源
SDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.defaults.esp32s3;sdkconfig.board.defaults
IDF_CCACHE_ENABLE=0                                  # 本机 ccache 会挂死
```

```
cd xes/xiaozhi
idf.py -B build2 reconfigure
idf.py -B build2 build
```

注意两点（本机踩过的坑）：

- 根 `CMakeLists.txt` 里开了 `CMAKE_NINJA_FORCE_RESPONSE_FILE`，否则 main 组件 include 路径超过 Windows 32767 字符命令行上限会报 `CreateProcess: The parameter is incorrect`
- 换了源码位置后**必须换一个全新的 build 目录**重新 configure，否则极易拿到陈旧对象（旧 build 里的 `.rsp` 不会重新生成）

## 烧录

```
esptool --chip esp32s3 -p COM5 -b 921600 write_flash --flash_mode dio --flash_freq 80m --flash_size 16MB \
  0x0      build2/bootloader/bootloader.bin \
  0x8000   build2/partition_table/partition-table.bin \
  0xd000   build2/ota_data_initial.bin \
  0x800000 build2/generated_assets.bin \
  0x20000  build2/xiaozhi.bin
```

## 改动清单（相对 upstream xiaozhi-esp32）

- `main/boards/bread-compact-wifi-lcd/config.h`：屏幕/音频引脚、`BUILTIN_LED_GPIO=NC`、`XZ_CLOCK_PANEL` 宏兜底
- `main/display/clock_panel.h|.cc`：**新增**。壁纸 + 5 组“黑描边 + 白字”标签、每分钟刷新、SNTP、天气抓取任务
- `main/display/font_clock48.c` / `font_clock28.c`：**新增**。用 `lv_font_conv` 生成的数字字体（内置 montserrat 在这套 LVGL 里不可用）
- `main/display/lcd_display.cc`：在**真正被编译的** `SetupUI()` 里创建时钟面板，并把容器/顶栏/状态栏背景设成透明
- `main/display/lvgl_display/lvgl_display.cc`：idle 时隐藏中间那行 `HH:MM`、每帧调 `ClockPanel::Tick()`
- `main/CMakeLists.txt`：加入 `clock_panel.cc`、`font_clock*.c`，嵌入 `clock_wallpaper.bin`，`PRIV_REQUIRES` 加 `esp_http_client`
- `sdkconfig.board.defaults`：板卡类型、屏幕型号、中文、LVGL 字体开关

## 已知问题

1. **唤醒词不可用**：`MODEL_LOADER: Can not find model in partition table`，wakenet 模型没进分区表，
   目前只能按 BOOT 键（GPIO0）开始对话，喊“小智小智”没反应。
2. 天气用的是国内免费接口 `http://t.weather.itboy.net/api/weather/city/101280601`（深圳），
   换城市需要改这个 id。

## 踩坑记录（值得记住的几条）

- 壁纸 `clock_wallpaper.bin` 是 **字节交换过的 RGB565**，LVGL 里必须用 `LV_COLOR_FORMAT_RGB565_SWAPPED`，
  否则屏幕上是一团彩噪。
- 曾经无限重启（`InstrFetchProhibited`，PC=0）：把**主题里的字体对象指针**存进了自己的标签，
  小智刷新主题时那个字体对象被释放 → 野指针。改成只用编译进 flash 的静态字体后才稳定。
- `esp_sntp_init()` 不能在 WiFi 拿到 IP 之前调，否则 `assert failed: tcpip_callback (Invalid mbox)`。
- `esp_http_client_read` 的缓冲区长度千万别写 `sizeof(指针)`（等于 4），会只读到几个字符。

## MicroPython 版

`esp32/` 下是早期的 MicroPython 实现（`main.py` / `st7789.py` / `config.py` / `push.py` / `wallpaper.bin`），
效果与现在一致，可作为对照或临时替换方案。刷回需要先 `erase_flash` 写入 MicroPython 固件。
