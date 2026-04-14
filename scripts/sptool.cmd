@echo off
set "SPTOOL_PYTHON=%~dp0..\ .venv\Scripts\python.exe"
set "SPTOOL_PYTHON=%SPTOOL_PYTHON: =%"
if "%~1"=="ultra" (
  if /I "%~2"=="start" (
    set "TOOL_MODE=ultra"
    echo ultra mode enabled
    exit /b 0
  )
  if /I "%~2"=="exit" (
    set "TOOL_MODE="
    echo ultra mode disabled
    exit /b 0
  )
)
"%SPTOOL_PYTHON%" -m sptool.cli %*
