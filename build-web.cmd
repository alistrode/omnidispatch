@echo off
rem Rebuild the web frontend into omnidispatch\static. No npm install needed.
setlocal
cd /d "%~dp0apps\web"
node build.mjs
echo.
echo   built into ..\..\omnidispatch\static
