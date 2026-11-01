@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\delivery\start-packaged-app.ps1" %*
if errorlevel 1 pause
