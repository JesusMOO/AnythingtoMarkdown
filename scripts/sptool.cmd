@echo off
if /I "%~1"=="ultra" (
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
python -m sptool.cli %*
exit /b %ERRORLEVEL%
