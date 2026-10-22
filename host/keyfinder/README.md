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
Homebrew libkeyfinder if needed. The macOS adapter is built locally; it dynamically links to the locally installed Homebrew library and FFTW.
The complete adapter source and build script are included for rebuilding.


Windows x64 distribution: `../windows-x64/` contains statically linked adapters
and a native host launcher. Complete, unmodified libkeyfinder 2.2.8 and FFTW
3.3.11 sources (including their licenses) are bundled in `sources/`.
The GPL-3.0-or-later launcher source is in `../windows/native_host_launcher.cpp`.
Rebuild both binaries from the project root with
`python3 host/windows/build_cross.py` using MinGW-w64 and make.
The build script validates source hashes, records binary SHA256 checksums, and
requires no additional FFTW, C++ or pthread DLLs. Windows execution is pending
real-machine validation; see the root README.
