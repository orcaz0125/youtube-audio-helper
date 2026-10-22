#!/bin/zsh
cd -- "${0:A:h}"
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "当前分享版仅支持 macOS。"
  read -r "?按回车关闭窗口…"
  exit 1
fi
found_python=""
for candidate in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3; do
  if "$candidate" -c 'import sys;sys.exit(0 if sys.version_info >= (3,12) else 1)' >/dev/null 2>&1; then
    found_python="$candidate"
    break
  fi
done
if [[ -z "$found_python" ]]; then
  echo "需要 Python 3.12 或更新版本。请安装后重新运行。"
  echo "官方网站：https://www.python.org/downloads/macos/"
  read -r "?按回车关闭窗口…"
  exit 1
fi
"$found_python" host/install.py
result=$?
if [[ "$result" -ne 0 ]]; then
  echo "安装未完成。请保留上面的报错，并查看「先看这里.txt」里的环境要求。"
fi
read -r "?按回车关闭窗口…"
exit "$result"
