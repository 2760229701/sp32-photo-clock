#include "emoji_collection.h"

#include <string.h>

#include <esp_log.h>

#define TAG "EmojiCollection"

void EmojiCollection::AddEmoji(const std::string& name, LvglImage* image) {
    emoji_collection_[name] = image;
}

const LvglImage* EmojiCollection::GetEmojiImage(const char* name) {
    auto it = emoji_collection_.find(name);
    if (it != emoji_collection_.end()) {
        return it->second;
    }

    /* 固件启动时固定问一次 robot_2，但资源包（含官方默认包）里通常只有 neutral，
       这里做个兜底，免得待机时那个表情位置是空白 */
    if (strcmp(name, "robot_2") == 0) {
        auto fallback = emoji_collection_.find("neutral");
        if (fallback != emoji_collection_.end()) {
            return fallback->second;
        }
    }

    ESP_LOGW(TAG, "Emoji not found: %s", name);
    return nullptr;
}

EmojiCollection::~EmojiCollection() {
    for (auto it = emoji_collection_.begin(); it != emoji_collection_.end(); ++it) {
        delete it->second;
    }
    emoji_collection_.clear();
}
