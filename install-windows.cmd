@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
py -3 -c "import sys;raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0host\install.py"
  if errorlevel 1 goto failed
  goto done
)
python -c "import sys;raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>&1
if not errorlevel 1 (
  python "%~dp0host\install.py"
  if errorlevel 1 goto failed
  goto done
)
echo 需要先安装 Python 3.12 或更新版本的 x64 版本。
echo 下载：https://www.python.org/downloads/windows/
echo 安装时请勾选 Add python.exe to PATH。
goto end
:failed
echo 安装未完成，请保留上面的错误信息，检查 Python、Node.js 和网络后重试。
goto end
:done
echo 已完成。请重新加载 Chrome 扩展并刷新 YouTube 页面。
:end
pause
