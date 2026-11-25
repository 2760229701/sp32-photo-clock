@echo off
set IDF_PATH=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf
set IDF_TOOLS_PATH=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif
set IDF_PYTHON_ENV_PATH=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\python_env\idf6.0_py3.13_env
set ESP_IDF_VERSION=6.0.2
set IDF_COMPONENT_CACHE_PATH=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\cmpcache
set IDF_GITHUB_ASSETS=dl.espressif.cn/github_assets
set SDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.defaults.esp32s3;sdkconfig.board.defaults
set IDF_CCACHE_ENABLE=0
set CCACHE_ENABLE=0
set TMP=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\tmp
set TEMP=%TMP%
set PATH=%IDF_PYTHON_ENV_PATH%\Scripts;C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\tools\ninja\1.12.1;C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\tools\cmake\4.0.3\bin;C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\tools\xtensa-esp-elf\esp-15.2.0_20251204\xtensa-esp-elf\bin;%PATH%
cd /d C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi
"%IDF_PYTHON_ENV_PATH%\Scripts\python.exe" "%IDF_PATH%\tools\idf.py" -B build2 reconfigure > C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\log_reconf2.txt 2>&1
echo RECONF_EXIT=%ERRORLEVEL%
