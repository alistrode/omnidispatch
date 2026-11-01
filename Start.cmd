@echo off
cd /d "%~dp0"
if not exist "OmniDispatch.exe" (
  echo OmniDispatch.exe is missing. Please extract the complete desktop package.
  pause
  exit /b 1
)
start "" "%~dp0OmniDispatch.exe"
