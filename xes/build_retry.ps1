cd 'C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi'
$env:IDF_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\esp-idf'
$env:IDF_TOOLS_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif'
& "$env:IDF_PATH\export.ps1" *> $null
$tmp='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP=$tmp; $env:TEMP=$tmp; $env:TMPDIR=$tmp
$env:IDF_COMPONENT_CACHE_PATH='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\cmpcache'
$env:IDF_GITHUB_ASSETS='dl.espressif.cn/github_assets'
$env:SDKCONFIG_DEFAULTS='sdkconfig.defaults;sdkconfig.defaults.esp32s3;sdkconfig.board.defaults'
$env:IDF_CCACHE_ENABLE='0'; $env:CCACHE_ENABLE='0'
$env:CMAKE_BUILD_PARALLEL_LEVEL='1'
$build='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi\build'
$log='C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\log_retry.txt'
$ninja=Join-Path $env:IDF_TOOLS_PATH 'tools\ninja\1.12.1\ninja.exe'
if(-not (Test-Path $ninja)){ $ninja=(Get-Command ninja).Source }
Set-Location $build
for($pass=1; $pass -le 10; $pass++){
    "===== 第 $pass 轮 $(Get-Date -Format 'HH:mm:ss') =====" | Out-File -Append -Encoding utf8 $log
    $out = & $ninja -k 0 -j 1 all 2>&1
    $out | Out-File -Append -Encoding utf8 $log
    if(Test-Path (Join-Path $build 'xiaozhi.elf')){ "完成：xiaozhi.elf 已生成" | Out-File -Append -Encoding utf8 $log; break }
    # 若本轮没有 FAILED 但仍结束，说明有其它问题，读最后几行
    $failed = ($out | Select-String -Pattern 'FAILED:' | Measure-Object).Count
    "本轮失败文件数: $failed" | Out-File -Append -Encoding utf8 $log
    if($failed -eq 0){ break }
}
"脚本结束" | Out-File -Append -Encoding utf8 $log
