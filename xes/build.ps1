cd 'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi'
$env:IDF_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf'
$env:IDF_TOOLS_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif'
$env:IDF_COMPONENT_CACHE_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\cmpcache'
$env:IDF_GITHUB_ASSETS='dl.espressif.cn/github_assets'
$env:SDKCONFIG_DEFAULTS='sdkconfig.defaults;sdkconfig.defaults.esp32s3;sdkconfig.board.defaults'
& "$env:IDF_PATH\export.ps1" *> $null
idf.py reconfigure 2>&1 | Select-Object -Last 6
idf.py build 2>&1 | Select-Object -Last 45
