@echo off
"%~dp0..\python.exe" -m sptool.cli %*
exit /b %ERRORLEVEL%
