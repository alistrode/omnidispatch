$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$root=Split-Path $PSScriptRoot -Parent
Set-Location $root
& (Join-Path $root 'runtime\python.exe') -m omnidispatch.supervisor *> (Join-Path $root 'state\launcher.log')
exit $LASTEXITCODE
