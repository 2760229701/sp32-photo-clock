@echo off
set PY=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\espressif\python_env\idf6.0_py3.13_env\Scripts\python.exe
set B=C:\Users\Administrator\Doubao\chats\2026-11-24\new-chat\xes\xiaozhi\build2
"%PY%" -m esptool --chip esp32s3 -p COM5 -b 921600 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_freq 80m --flash_size 16MB ^
 0x0 "%B%\bootloader\bootloader.bin" ^
 0x8000 "%B%\partition_table\partition-table.bin" ^
 0xd000 "%B%\ota_data_initial.bin" ^
 0x800000 "%B%\generated_assets.bin" ^
 0x20000 "%B%\xiaozhi.bin"
echo FLASH_EXIT=%ERRORLEVEL%
