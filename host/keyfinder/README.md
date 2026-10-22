# libkeyfinder adapter

`keyfinder_audio.cpp` is a GPL-3.0-or-later streaming adapter for the unmodified
libkeyfinder library maintained by Mixxx. It reads the complete track as 44100 Hz
mono float32 little-endian PCM from stdin and invokes `progressiveChromagram`,
`finalChromagram`, and `keyOfChromagram`. It writes one protocol response to stdout;
no analysis file is created.

Upstream: https://github.com/mixxxdj/libkeyfinder (installed version: 2.2.8).
Library and adapter licensing: GPL-3.0-or-later; see COPYING.txt.

Build on macOS: install Homebrew and Xcode Command Line Tools, then run
`python3 ../build_keyfinder.py` from this directory. The build script installs
Homebrew libkeyfinder if needed. Only the adapter binary is included in this
package; it dynamically links to the locally installed Homebrew library and FFTW.
The complete adapter source and build script are included for rebuilding.
