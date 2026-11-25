#include "clock_panel.h"

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>
#include <esp_log.h>
#include <esp_sntp.h>
#include <esp_http_client.h>
#include <esp_crt_bundle.h>
#include <esp_netif.h>

#define TAG "ClockPanel"

/* 等 WiFi 真的拿到 IP 之后再碰 socket/SNTP，否则 lwip 还没起来会 assert */
static bool NetReady() {
    esp_netif_t* n = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
    if (n == nullptr) {
        return false;
    }
    esp_netif_ip_info_t ip = {};
    return esp_netif_get_ip_info(n, &ip) == ESP_OK && ip.ip.addr != 0;
}

static void InitSntpOnce() {
    static bool done = false;
    if (done) {
        return;
    }
    done = true;
    /* BUGFIX: 之前没设时区，localtime 按 UTC 走，时钟比北京时间慢 8 小时 */
    setenv("TZ", "CST-8", 1);
    tzset();

    esp_sntp_setoperatingmode(ESP_SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, "ntp.aliyun.com");
    esp_sntp_setservername(1, "ntp.tencent.com");
    esp_sntp_setservername(2, "cn.pool.ntp.org");
    sntp_set_time_sync_notification_cb([](struct timeval* tv) {
        ESP_LOGI(TAG, "time synced: %lld", (long long)tv->tv_sec);
    });
    esp_sntp_init();
}

#define WALLPAPER_W 240
#define WALLPAPER_H 320
#define WALLPAPER_BYTES (WALLPAPER_W * WALLPAPER_H * 2)

extern const uint8_t clock_wallpaper_bin_start[] asm("_binary_clock_wallpaper_bin_start");

/* 自己用 lv_font_conv 生成的大号数字字体（内置 montserrat 在这套 LVGL 里不可用） */
extern "C" {
extern const lv_font_t clock48;
extern const lv_font_t clock28;
extern const lv_font_t font_clock72;      /* 72px 数字，备用 */
extern const lv_font_t font_clock44;      /* 44px 数字（simhei），时钟用 */
extern const lv_font_t font_cjk20;        /* 20px 中文（月/日/周/湿/度/小雨…） */
extern const lv_font_t font_cjk16;        /* 16px 中文小字，日期用 */
extern const lv_font_t font_noto_sans_basic_20_4;
}

/* 国内可直连的免费天气源（深圳 101280601），无需 key */
static const char* kWeatherUrl =
    "http://t.weather.itboy.net/api/weather/city/101280601";

/* 天气任务和 LVGL 任务之间共享的数据 */
static SemaphoreHandle_t s_weather_mutex = nullptr;
static int s_temp_x10 = -9999;   // 温度 ×10，避免浮点
static int s_humi = -1;
static char s_weather[24] = "";
static bool s_weather_ok = false;

static lv_image_dsc_t s_wallpaper = {};

/* 从 JSON 里抓一个字符串值，避免引入 cJSON 依赖 */
static bool JsonString(const char* body, const char* key, char* out, int out_len) {
    const char* p = strstr(body, key);
    if (p == nullptr) {
        return false;
    }
    p += strlen(key);
    while (*p == ':' || *p == ' ') {
        p++;
    }
    if (*p != '"') {
        return false;
    }
    p++;
    int i = 0;
    while (*p != '"' && *p != '\0' && i < out_len - 1) {
        out[i++] = *p++;
    }
    out[i] = '\0';
    return i > 0;
}

/* 时间兜底：NTP 有时被运营商挡住不响应，但天气接口每次都能通，
   它返回的 "time" 就是北京时间，用它把系统时间校准过来 */
static void SetTimeFromWeather(const char* body) {
    char ts[32] = "";
    if (!JsonString(body, "\"time\"", ts, sizeof(ts))) {
        return;
    }
    int Y = 0, M = 0, D = 0, h = 0, m = 0, s = 0;
    if (sscanf(ts, "%d-%d-%d %d:%d:%d", &Y, &M, &D, &h, &m, &s) != 6) {
        return;
    }
    struct tm tm_set = {};
    tm_set.tm_year = Y - 1900;
    tm_set.tm_mon = M - 1;
    tm_set.tm_mday = D;
    tm_set.tm_hour = h;
    tm_set.tm_min = m;
    tm_set.tm_sec = s;
    time_t want = mktime(&tm_set);
    time_t now = time(nullptr);
    /* 注意：这个接口的 time 字段可能是 CDN 缓存的（实测慢 1 小时），
       所以只在"完全没校过时"时才用它兜底，NTP 成功过就绝对不覆盖 */
    if (want > 1600000000L && now < 1700000000L) {
        struct timeval tv = {};
        tv.tv_sec = want;
        tv.tv_usec = 0;
        settimeofday(&tv, nullptr);
        ESP_LOGI(TAG, "time set from weather api: %s", ts);
    }
}

static bool FetchWeather() {
    char* buf = (char*)malloc(4096);
    if (buf == nullptr) {
        return false;
    }
    esp_http_client_config_t cfg = {};
    cfg.url = kWeatherUrl;
    cfg.timeout_ms = 10000;
    cfg.buffer_size = 512;
    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    if (client == nullptr) {
        free(buf);
        return false;
    }
    bool ok = false;
    if (esp_http_client_open(client, 0) == ESP_OK) {
        esp_http_client_fetch_headers(client);
        int total = 0;
        const int cap = 4096 - 1;
        while (total < cap) {
            int r = esp_http_client_read(client, buf + total, cap - total);
            if (r <= 0) {
                break;
            }
            total += r;
        }
        buf[total] = '\0';
        SetTimeFromWeather(buf);
        char wendu[16] = "", shidu[16] = "", type[24] = "";
        if (JsonString(buf, "\"wendu\"", wendu, sizeof(wendu)) && JsonString(buf, "\"type\"", type, sizeof(type))) {
            JsonString(buf, "\"shidu\"", shidu, sizeof(shidu));
            xSemaphoreTake(s_weather_mutex, portMAX_DELAY);
            s_temp_x10 = (int)(atof(wendu) * 10.0);
            s_humi = atoi(shidu);
            strncpy(s_weather, type, sizeof(s_weather) - 1);
            s_weather[sizeof(s_weather) - 1] = '\0';
            s_weather_ok = true;
            xSemaphoreGive(s_weather_mutex);
            ok = true;
            ESP_LOGI(TAG, "weather %s C, %s, humi %d%%", wendu, type, s_humi);
        } else {
            ESP_LOGW(TAG, "weather parse failed (%d bytes): %.120s", total, buf);
        }
    } else {
        ESP_LOGW(TAG, "weather http open failed");
    }
    esp_http_client_close(client);
    esp_http_client_cleanup(client);
    free(buf);
    return ok;
}

void ClockPanelWeatherTask(void* arg) {
    (void)arg;
    /* 先等联网（配网阶段可能很久），拿到 IP 之后再开 SNTP 和天气请求 */
    while (!NetReady()) {
        vTaskDelay(pdMS_TO_TICKS(2000));
    }
    InitSntpOnce();
    vTaskDelay(pdMS_TO_TICKS(8000));
    int fail = 0;
    while (true) {
        if (FetchWeather()) {
            fail = 0;
            vTaskDelay(pdMS_TO_TICKS(10 * 60 * 1000));
        } else {
            fail++;
            vTaskDelay(pdMS_TO_TICKS((fail < 5 ? 60 : 300) * 1000));
        }
    }
}

ClockPanel& ClockPanel::Instance() {
    static ClockPanel instance;
    return instance;
}

ClockPanel::OutlinedLabel* ClockPanel::NewLabel(lv_obj_t* parent, const lv_font_t* font,
                                                lv_align_t align, int x, int y) {
    /* 返回一个静态池里的槽位，调用者自行记录 */
    static OutlinedLabel pool[8];
    static int used = 0;
    if (used >= 8) {
        return nullptr;
    }
    OutlinedLabel* lb = &pool[used++];
    lb->main = lv_label_create(parent);
    lv_obj_set_style_text_font(lb->main, font, 0);
    lv_obj_set_style_text_color(lb->main, lv_color_white(), 0);
    lv_obj_set_width(lb->main, WALLPAPER_W);
    lv_obj_set_style_text_align(lb->main, LV_TEXT_ALIGN_CENTER, 0);
    lv_label_set_text(lb->main, "");
    lv_obj_align(lb->main, align, x, y);

    /* 黑色描边：4 个方向的副本垫在白字下面 */
    const int dx[4] = {-1, 1, -1, 1};
    const int dy[4] = {-1, -1, 1, 1};
    for (int i = 0; i < 4; i++) {
        lb->shadow[i] = lv_label_create(parent);
        lv_obj_set_style_text_font(lb->shadow[i], font, 0);
        lv_obj_set_style_text_color(lb->shadow[i], lv_color_black(), 0);
        lv_obj_set_width(lb->shadow[i], WALLPAPER_W);
        lv_obj_set_style_text_align(lb->shadow[i], LV_TEXT_ALIGN_CENTER, 0);
        lv_label_set_text(lb->shadow[i], "");
        lv_obj_align(lb->shadow[i], align, x + dx[i], y + dy[i]);
    }
    lb->used = true;
    return lb;
}

void ClockPanel::SetText(OutlinedLabel* label, const char* text) {
    if (label == nullptr || label->main == nullptr) {
        return;
    }
    const char* old = lv_label_get_text(label->main);
    if (old != nullptr && strcmp(old, text) == 0) {
        return;   // 没变化就不重绘，避免闪烁
    }
    lv_label_set_text(label->main, text);
    for (int i = 0; i < 4; i++) {
        lv_label_set_text(label->shadow[i], text);
    }
}

void ClockPanel::Create(lv_obj_t* screen, const lv_font_t* cjk_font, bool has_big_font) {
    if (created_ || screen == nullptr) {
        return;
    }
    screen_ = screen;
    /* 只用编译进 flash 的静态字体：主题里的字体对象可能在换皮时被释放，指针会失效 */
    (void)cjk_font;
    (void)has_big_font;
    const lv_font_t* text_font = (const lv_font_t*)&font_cjk20;
    big_font_ = (const lv_font_t*)&font_clock44;   /* 44px 数字 */
    cjk_font_ = text_font;

    if (s_weather_mutex == nullptr) {
        s_weather_mutex = xSemaphoreCreateMutex();
    }

    /* 壁纸：240×320 的 RGB565 原始数据，直接放进 LVGL 图片描述符 */
    s_wallpaper.header.magic = LV_IMAGE_HEADER_MAGIC;
    s_wallpaper.header.cf = LV_COLOR_FORMAT_RGB565_SWAPPED;
    s_wallpaper.header.w = WALLPAPER_W;
    s_wallpaper.header.h = WALLPAPER_H;
    s_wallpaper.header.stride = WALLPAPER_W * 2;
    s_wallpaper.data_size = WALLPAPER_BYTES;
    s_wallpaper.data = clock_wallpaper_bin_start;

    bg_ = lv_image_create(screen);
    lv_image_set_src(bg_, &s_wallpaper);
    lv_obj_set_pos(bg_, 0, 0);

    /* 版面：
       右上角：日期“11月25日”
       右侧一列（从上到下）：温度 → 湿度 → 星期
       左侧：时钟，位置在日期下面一点，避开屏幕白边 */
    auto right_align = [](OutlinedLabel& lb, int y, int pad_r) {
        lv_obj_t* objs[5] = {lb.main, lb.shadow[0], lb.shadow[1], lb.shadow[2], lb.shadow[3]};
        const int ox[5] = {0, -1, 1, -1, 1};
        const int oy[5] = {0, -1, -1, 1, 1};
        for (int i = 0; i < 5; i++) {
            lv_obj_set_width(objs[i], WALLPAPER_W);
            lv_obj_set_style_text_align(objs[i], LV_TEXT_ALIGN_RIGHT, 0);
            lv_obj_set_style_pad_right(objs[i], pad_r, 0);
            lv_obj_set_pos(objs[i], ox[i], y + oy[i]);
        }
    };

    date_label_ = *NewLabel(screen, &font_cjk16, LV_ALIGN_TOP_LEFT, 0, 6);
    right_align(date_label_, 6, 4);
    temp_label_ = *NewLabel(screen, cjk_font_, LV_ALIGN_TOP_LEFT, 0, 34);
    right_align(temp_label_, 34, 8);
    humi_label_ = *NewLabel(screen, cjk_font_, LV_ALIGN_TOP_LEFT, 0, 56);
    right_align(humi_label_, 56, 8);
    week_label_ = *NewLabel(screen, cjk_font_, LV_ALIGN_TOP_LEFT, 0, 78);
    right_align(week_label_, 78, 8);

    /* 时钟：靠左，字比之前小一号（44px），整体下移到 y=38 避开白边 */
    time_label_ = *NewLabel(screen, big_font_, LV_ALIGN_TOP_LEFT, 0, 38);
    {
        lv_obj_t* objs[5] = {time_label_.main, time_label_.shadow[0], time_label_.shadow[1],
                             time_label_.shadow[2], time_label_.shadow[3]};
        for (int i = 0; i < 5; i++) {
            lv_obj_set_width(objs[i], WALLPAPER_W);
            lv_obj_set_style_text_align(objs[i], LV_TEXT_ALIGN_LEFT, 0);
            lv_obj_set_style_pad_left(objs[i], 8, 0);
        }
    }

    /* 把文字层抬到最上面：放在最底层时，时钟那块会被小智的不透明层挡住 */
    {
        auto raise = [](lv_obj_t* main_obj, lv_obj_t* sh[4]) {
            for (int i = 0; i < 4; i++) {
                lv_obj_move_foreground(sh[i]);
            }
            lv_obj_move_foreground(main_obj);
        };
        raise(time_label_.main, time_label_.shadow);
        raise(date_label_.main, date_label_.shadow);
        raise(temp_label_.main, temp_label_.shadow);
        raise(humi_label_.main, humi_label_.shadow);
        raise(week_label_.main, week_label_.shadow);
        lv_obj_move_background(bg_);
    }

    created_ = true;

    xTaskCreate(ClockPanelWeatherTask, "clock_weather", 6144, nullptr, 3, nullptr);
    ESP_LOGI(TAG, "clock panel created");
}

void ClockPanel::Tick() {
    if (!created_) {
        return;
    }
    time_t now = time(NULL);
    struct tm tm_now = {};
    localtime_r(&now, &tm_now);

    if (tm_now.tm_year >= 2025 - 1900) {
        int cur_min = tm_now.tm_hour * 60 + tm_now.tm_min;
        if (cur_min != last_min_) {
            last_min_ = cur_min;
            char buf[16];
            strftime(buf, sizeof(buf), "%H:%M", &tm_now);
            SetText(&time_label_, buf);

            static const char* week[] = {"周日", "周一", "周二", "周三", "周四", "周五", "周六"};
            char date[24];
            snprintf(date, sizeof(date), "%d月%d日", tm_now.tm_mon + 1, tm_now.tm_mday);
            SetText(&date_label_, date);
            SetText(&week_label_, week[tm_now.tm_wday]);
        }
    } else {
        static int dots = 0;
        if (dots != (int)(now % 2) + 1) {   // 没对时之前显示 --:--，不闪
            dots = (int)(now % 2) + 1;
            SetText(&time_label_, "--:--");
        }
    }

    if (s_weather_mutex != nullptr && xSemaphoreTake(s_weather_mutex, 0) == pdTRUE) {
        int t = s_temp_x10, h = s_humi;
        bool ok = s_weather_ok;
        xSemaphoreGive(s_weather_mutex);
        if (ok) {
            /* 右侧一列：温度在上，湿度在下（星期在它们下面，由时间分支更新） */
            char buf[24];
            snprintf(buf, sizeof(buf), "%d.%d°C", t / 10, abs(t % 10));
            SetText(&temp_label_, buf);
            snprintf(buf, sizeof(buf), "湿度%d%%", h);
            SetText(&humi_label_, buf);
        }
    }
}
