@echo off
cd /d "%~dp0"
set PYTHONUTF8=1
if not exist state\ADMIN-CREDENTIALS.private.txt runtime\python.exe -m omnidispatch.cli --state state init
if not exist state\agent.json runtime\python.exe -m omnidispatch.cli --state state register-agent
start "OmniDispatch" /min runtime\pythonw.exe -m omnidispatch.supervisor
start "" http://127.0.0.1:8791
