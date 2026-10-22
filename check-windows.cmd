@echo off
chcp 65001 >nul
setlocal
if not exist "%LOCALAPPDATA%\YouTube Audio\host\.venv\Scripts\python.exe" (
  echo 请先运行 install-windows.cmd。
  pause
  exit /b 1
)
"%LOCALAPPDATA%\YouTube Audio\host\.venv\Scripts\python.exe" "%~dp0host\windows\smoke_test.py"
if errorlevel 1 echo 检查未通过，请保存上面的完整报错。
pause
