#ifndef CLOCK_PANEL_H
#define CLOCK_PANEL_H

#include "lvgl.h"

/*
 * 照片壁纸 + 大时钟 + 日期 + 天气 的待机页面。
 * 只在开启了 XZ_CLOCK_PANEL 的板子上编译，所有函数都要求在已持有 LVGL 锁的情况下调用。
 */
class ClockPanel {
public:
    static ClockPanel& Instance();

    /* 在屏幕上铺一层壁纸和文字（贴在最底层，位于小智原有 UI 之下） */
    void Create(lv_obj_t* screen, const lv_font_t* cjk_font, bool has_big_font);

    /* 每秒调用一次，内部只在“分钟变化/天气变化”时才真正改文字 */
    void Tick();

    bool created() const { return created_; }

private:
    ClockPanel() = default;
    struct OutlinedLabel {
        lv_obj_t* main = nullptr;
        lv_obj_t* shadow[4] = {nullptr, nullptr, nullptr, nullptr};
        bool used = false;
    };

    OutlinedLabel* NewLabel(lv_obj_t* parent, const lv_font_t* font, int align_ofs_y);
    void SetText(OutlinedLabel* label, const char* text);

    lv_obj_t* screen_ = nullptr;
    lv_obj_t* bg_ = nullptr;
    const lv_font_t* cjk_font_ = nullptr;
    const lv_font_t* big_font_ = nullptr;
    bool created_ = false;

    OutlinedLabel time_label_;
    OutlinedLabel date_label_;
    OutlinedLabel temp_label_;
    OutlinedLabel weather_label_;
    OutlinedLabel humi_label_;

    int last_min_ = -1;
    int last_temp_x10_ = -9999;
    int last_code_ = -1;
    int last_humi_ = -1;
    int time_retry_ = 0;

    friend void ClockPanelWeatherTask(void* arg);
};

#endif  // CLOCK_PANEL_H
