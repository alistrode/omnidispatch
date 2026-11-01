@echo off
rem Dev server: runs the code in this folder against an isolated state dir.
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set OMNI_STATE=%~dp0_state

if not exist "%OMNI_STATE%" mkdir "%OMNI_STATE%"

if not exist "%OMNI_STATE%\hub.db" (
  ".runtime\python.exe" -m omnidispatch.cli --state "%OMNI_STATE%" init
)

echo.
echo   OmniDispatch dev  -^>  http://127.0.0.1:8793
echo   state: %OMNI_STATE%
echo.
".runtime\python.exe" -m omnidispatch.cli --state "%OMNI_STATE%" serve --port 8793
