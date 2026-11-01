@echo off
rem Run the test suite with the bundled runtime.
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
".runtime\python.exe" -m pytest -q -p no:cacheprovider %*
