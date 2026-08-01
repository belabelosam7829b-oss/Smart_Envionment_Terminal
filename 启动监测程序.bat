@echo off
title STM32 Monitor
cd /d "%~dp0"

:: 优先使用打包好的 exe（无黑窗口），否则用 Python 脚本
if exist "dist\monitor.exe" (
    echo Starting monitor.exe ...
    start "" "dist\monitor.exe" %*
    goto :EOF
)

:: 检查.venv Python
set PY_CMD=
if exist ".venv\Scripts\python.exe" set PY_CMD=.venv\Scripts\python.exe
if not defined PY_CMD (
    python --version >nul 2>&1 && set PY_CMD=python
)
if not defined PY_CMD (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

echo Installing/checking dependencies...
%PY_CMD% -m pip install pyserial matplotlib -q

echo Starting monitor.py ...
%PY_CMD% monitor.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Program failed. Check COM port.
    pause
)
