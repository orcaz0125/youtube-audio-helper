// SPDX-License-Identifier: GPL-3.0-or-later
// Streaming adapter for libkeyfinder. Input: 44100 Hz mono float32 LE PCM.
#include <keyfinder/keyfinder.h>
#include <keyfinder/workspace.h>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <vector>
#ifndef KEYFINDER_LIBRARY_VERSION
#define KEYFINDER_LIBRARY_VERSION "unknown"
#endif
int main(int argc, char** argv) {
  if (argc == 2 && std::strcmp(argv[1], "--version") == 0) {
    std::cout << "libkeyfinder " KEYFINDER_LIBRARY_VERSION << '\n'; return 0;
  }
  if (argc != 1) { std::cerr << "usage: keyfinder-audio < mono-44100-f32le.pcm\n"; return 2; }
  try {
    KeyFinder::KeyFinder detector;
    KeyFinder::Workspace workspace;
    std::vector<float> buffer(65536);
    std::uint64_t total = 0;
    while (std::cin.read(reinterpret_cast<char*>(buffer.data()), buffer.size() * sizeof(float)) || std::cin.gcount()) {
      const auto bytes = std::cin.gcount();
      if (bytes % sizeof(float)) { std::cerr << "Incomplete PCM sample\n"; return 3; }
      const auto count = static_cast<unsigned int>(bytes / sizeof(float));
      KeyFinder::AudioData audio;
      audio.setFrameRate(44100); audio.setChannels(1); audio.addToSampleCount(count);
      for (unsigned int i = 0; i < count; ++i) audio.setSample(i, std::isfinite(buffer[i]) ? buffer[i] : 0.0f);
      detector.progressiveChromagram(audio, workspace);
      total += count;
    }
    if (std::cin.bad()) { std::cerr << "PCM input failed\n"; return 3; }
    auto key = KeyFinder::SILENCE;
    if (total) { detector.finalChromagram(workspace); key = detector.keyOfChromagram(workspace); }
    // libkeyfinder enums start at A and alternate major/minor. Normalize flats
    // to their enharmonic sharps to match the existing Auto-Tune file naming.
    static const char* tonics[] = {"A","A#","B","C","C#","D","D#","E","F","F#","G","G#"};
    const int index = static_cast<int>(key);
    if (index >= 0 && index < 24) {
      std::cout << "{\"key\":\"" << tonics[index / 2] << "\",\"scale\":\"" << (index % 2 ? "Minor" : "Major") << '"';
    } else { std::cout << "{\"key\":null,\"scale\":null"; }
    std::cout << ",\"engine\":\"libkeyfinder\",\"version\":\"" KEYFINDER_LIBRARY_VERSION "\",\"frames\":" << total << ",\"sample_rate\":44100}\n";
    return 0;
  } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
