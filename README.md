# YouTube 音频助手

work by orcaz

在 YouTube 视频页面下载 MP3，使用 **libkeyfinder 2.2.8** 分析整首音频的调性，并把调性与 BPM 自动写入文件名：

```text
歌名 [F# Minor] [128 BPM].mp3
```

只保存 MP3，不生成 JSON 分析文件，不需要确认调性。界面保留简洁浅色样式。

## 支持环境

| 系统 | 状态 | 安装要求 |
| --- | --- | --- |
| macOS | 已在 Apple Silicon Mac 验证 | Chrome、Python 3.12+、Node.js 22+、Homebrew、Xcode Command Line Tools |
| Windows 10/11 x64 | 预览版，待 Windows 实机验证 | Chrome、x64 Python 3.12+、Node.js 22+ |

Windows 包已附带 x64 的 libkeyfinder 程序和本机启动程序，无需 Homebrew、Visual Studio 或自行编译。当前不提供原生 Windows ARM64、32 位 Windows 或 Linux 包。

这是需要联网安装依赖的安装包，不是免依赖的离线应用。安装 Python 时，Windows 用户请勾选 **Add python.exe to PATH**。安装程序只注册当前用户，不需要管理员权限。

- Python：https://www.python.org/downloads/
- Node.js：https://nodejs.org/

## 安装

可直接下载仓库中的 [0.4.0 跨平台分享包](./YouTube-Audio-Helper-0.4.0-macOS-Windows.zip)，或使用 Code → Download ZIP 获取完整源码。

1. 下载并完整解压到固定位置，保留文件夹结构。
2. Chrome 打开 `chrome://extensions`，开启「开发者模式」。
3. 点击「加载已解压的扩展程序」，选择 **extension** 文件夹。
4. Windows 双击 **install-windows.cmd**；macOS 双击 **安装本机程序.command**。
5. 等待安装完成，在 Chrome 重新加载扩展并刷新 YouTube 视频页面。
6. 点击「下载音频」。

macOS 的 command 文件无法直接打开时，可在终端输入 `zsh `，把脚本拖入终端并回车。Windows 必须先解压，不能在 ZIP 预览里直接运行安装程序。

不要随意移动已加载的 extension 文件夹；移动后需要在 Chrome 重新加载。

## Windows 检查

安装后可运行 **check-windows.cmd**。它会检查真实 EXE 的本机通信、C 大调 / A 小调 / F# 小调、整曲读取以及中文和空格路径，然后再用 Chrome 实际下载一首有权保存的音频。

开发环境已完成跨平台路径、注册表配置、程序校验等 6 项测试，Windows x64 EXE 已成功交叉编译并检查依赖；未在 Windows 实机上运行上述检查，因此 Windows 包标为预览版。Mac 的 libkeyfinder、全曲读取与 MP3 下载流程已回归验证。

## 文件位置

| 内容 | Windows | macOS |
| --- | --- | --- |
| MP3 | 用户目录下 `Music/YouTube Audio` | `~/Music/YouTube Audio` |
| 本机程序 | `%LOCALAPPDATA%/YouTube Audio/host` | `~/Library/Application Support/YouTube Audio/host` |
| 日志 | 本机程序目录的 `native.log` | 本机程序目录的 `native.log` |

Windows 本机连接注册在当前用户的 `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.local.youtube_audio`，不修改浏览器个人资料。

## 分析与隐私

- libkeyfinder 分析整首源音频，实际音频调性优先于标题、介绍里的标注。
- 音频无法识别调性时，回退读取无冲突的视频标注。
- BPM 优先读取明确的视频标注；缺失时使用 librosa 节拍跟踪估计。
- 自动测调可能误判，只输出整体大小调，无法用单个结果覆盖歌曲中的所有转调。
- 下载和分析在本机完成，不向第三方 AI 服务上传音频，不读取浏览器 Cookie。
- Chrome 内的代理不一定覆盖本机程序；需要登录、年龄验证或机器人验证的视频可能无法下载。

## 排查和卸载

连接失败时，重新运行安装程序，然后在 Chrome 重新加载扩展并刷新页面。扩展弹窗的「检查连接」会检查本机依赖与 libkeyfinder。

Windows 运行 **uninstall-windows.cmd** 取消本机连接；macOS 运行 **卸载本机连接.command**。再从 Chrome 移除扩展。下载的 MP3 会保留，本机程序文件夹可按需删除。

## 源码与构建

- `extension/`：Chrome 扩展与页面按钮。
- `host/native_host.py`：下载、命名与 Native Messaging。
- `host/analysis.py`、`metadata.py`：分析与视频标注解析。
- `host/keyfinder_backend.py`：libkeyfinder 全曲流式接口。
- `host/platform_config.py`、`process_utils.py`：平台路径、当前用户注册与后台进程。
- `host/keyfinder/`：适配源码、GPL 许可与上游源码归档。
- `host/windows-x64/`：Windows x64 程序及 SHA256 校验。
- `host/windows/build_cross.py`：使用 MinGW-w64 和随附源码重建 Windows 程序。
- `host/windows/native_host_launcher.cpp`：Unicode 路径与二进制管道启动程序。
- `host/windows/smoke_test.py`：Windows 实机检查。
- `host/build_keyfinder.py`：macOS 本机编译。

Windows 重建命令：安装 MinGW-w64 和 make 后，在项目根目录运行 `python3 host/windows/build_cross.py`。脚本校验源码归档摘要，静态构建 FFTW 和 libkeyfinder，不依赖额外的 FFTW、C++ 或 pthread DLL。Mac 版动态链接 Homebrew 提供的库。

## 依赖与许可

- [libkeyfinder](https://github.com/mixxxdj/libkeyfinder)：GPL-3.0-or-later，适配源码及许可在 `host/keyfinder/`。
- [FFTW](https://www.fftw.org/)：Windows 构建使用 FFTW 3.3.11；许可及完整源码在随附源码归档中。
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)、[librosa](https://github.com/librosa/librosa)、[imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)。

请仅下载你有权保存的内容。
