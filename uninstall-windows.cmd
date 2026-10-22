@echo off
chcp 65001 >nul
reg delete "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.local.youtube_audio" /f >nul 2>&1
echo 已移除当前用户的 Chrome 本机连接。请在 chrome://extensions 移除扩展。
echo 下载的 MP3 会保留，本机程序位于 %LOCALAPPDATA%\YouTube Audio。
pause
