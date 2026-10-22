#!/bin/zsh
rm -f "$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.local.youtube_audio.json"
echo "本机连接已移除。你也可以在 chrome://extensions 移除扩展。已下载的音频会保留。"
read -r "?按回车关闭窗口…"
