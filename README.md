# YouTube 音频助手

一个在 YouTube 视频页面下载 MP3 的 macOS Chrome 扩展。下载后使用 **libkeyfinder** 分析整首源音频的调性，并把调性与 BPM 自动写入文件名。

```text
歌名 [F# Minor] [128 BPM].mp3
```

只保存 MP3，不生成额外的 JSON 分析文件，也没有调性确认步骤。

## 功能

- 在 YouTube 视频页面显示下载按钮，也可从扩展弹窗下载当前视频。
- 固定输出 MP3，下载完成后可直接在访达中定位。
- libkeyfinder 2.2.8 对整首音频进行调性分析，实际音频结果优先于标题和介绍里的标注。
- 调性分析无法给出结果时，回退读取视频里的无冲突标注。
- BPM 优先读取明确的视频标注，缺失时由 librosa 节拍跟踪估计。
- 调性、大小调和 BPM 直接写入文件名，结果显示对应来源。
- 在本机完成下载和分析，不向第三方 AI 服务上传音频。

## 环境要求

目前支持 **macOS + Google Chrome**，已在 Apple Silicon Mac 上验证。

- Python 3.12 或更新版本
- Homebrew
- Xcode Command Line Tools（`xcode-select --install`）
- Node.js 22 或更新版本，用于 YouTube 解析
- 能够访问 YouTube 与依赖下载源的网络

这是源码与联网安装包，不是免依赖的离线应用。目前不支持 Windows。

## 安装

1. 下载本仓库：点击 **Code → Download ZIP**，解压到固定位置。
2. 在 Chrome 地址栏输入 `chrome://extensions`，打开右上角的「开发者模式」。
3. 点击「加载已解压的扩展程序」，选择仓库中的 **extension** 文件夹。
4. 双击根目录的 **安装本机程序.command**。安装程序会自动计算扩展 ID、安装依赖、编译 libkeyfinder 适配程序，并注册本机连接。
5. 等待安装成功，刷新 YouTube 视频页面，点击「下载音频」。

如果 command 文件无法直接打开，可在终端输入 `zsh `，再把该文件拖入终端并回车。

请保留 extension 文件夹的位置；移动后需要在 Chrome 中重新加载。

## 文件位置

| 内容 | 位置 |
| --- | --- |
| MP3 音频 | `~/Music/YouTube Audio` |
| 本机程序与依赖 | `~/Library/Application Support/YouTube Audio/host` |
| 启动日志 | `~/Library/Application Support/YouTube Audio/host/native.log` |

## 排查连接问题

在扩展弹窗中点击「检查连接」，会同时检查本机依赖与 libkeyfinder。

连接失败时，重新运行安装脚本，然后到 `chrome://extensions` 重新加载扩展并刷新视频页面。

Chrome 内的代理设置不一定覆盖本机程序。需要登录、年龄验证或机器人验证的视频可能无法下载；本扩展不读取浏览器 Cookie。

## 工作原理

```text
Chrome 扩展
    ↓ Native Messaging
本机 Python 程序
    ├─ yt-dlp 下载源音频
    ├─ FFmpeg 转换 MP3
    ├─ libkeyfinder 分析整首源音频的调性
    └─ 读取视频标注 / librosa 估计 BPM
    ↓
自动命名并保存 MP3
```

libkeyfinder 只负责调性，不负责 BPM。当前输出整体大小调，不能用一个结果覆盖歌曲所有转调段落，自动测调也可能存在误判。

## 源码结构

```text
extension/                 Chrome 扩展、弹窗和页面按钮
host/native_host.py        下载与 Native Messaging 服务
host/analysis.py           测调和节拍分析流程
host/keyfinder_backend.py  整曲流式分析接口
host/metadata.py           标题、介绍中的调性与 BPM 标注解析
host/keyfinder/            C++ 适配源码及许可
host/build_keyfinder.py    本机编译脚本
host/install.py            安装与连接注册脚本
```

适配程序在接收方电脑上编译，仓库不包含开发者的 Python 环境、日志、浏览器资料或机器专用启动脚本。

## 更新与卸载

更新下载器：

```sh
"$HOME/Library/Application Support/YouTube Audio/host/.venv/bin/python" -m pip install -U 'yt-dlp[default]'
```

卸载：运行 **卸载本机连接.command**，再从 Chrome 移除扩展。已下载音频会保留，本机程序目录可按需移除。

## 依赖与许可

- [libkeyfinder](https://github.com/mixxxdj/libkeyfinder)：GPL-3.0-or-later；相关适配源码与许可在 `host/keyfinder/` 中。
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [librosa](https://github.com/librosa/librosa)
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)

请仅下载你有权保存的内容。
