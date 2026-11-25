cd 'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi'
$env:IDF_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf'
$env:IDF_TOOLS_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif'
& "$env:IDF_PATH\export.ps1" *> $null
$env:IDF_COMPONENT_CACHE_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\cmpcache'
$env:IDF_GITHUB_ASSETS='dl.espressif.cn/github_assets'
$env:SDKCONFIG_DEFAULTS='sdkconfig.defaults;sdkconfig.defaults.esp32s3;sdkconfig.board.defaults'
$env:IDF_CCACHE_ENABLE='0'
$env:CCACHE_ENABLE='0'
$env:CCACHE_DIR='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\ccache'
# 关键：把临时目录放到项目内，避免编译器临时文件被沙箱拒绝
$tmp='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP=$tmp; $env:TEMP=$tmp; $env:TMPDIR=$tmp
$env:CMAKE_BUILD_PARALLEL_LEVEL='1'
idf.py build *>&1 | Tee-Object -FilePath 'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\log_build4.txt' | Out-Null
"exit=$LASTEXITCODE"
