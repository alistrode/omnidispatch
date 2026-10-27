$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$root='E:\xxm\OmniDispatch'
& (Join-Path $root 'release\runtime\python.exe') (Join-Path $root 'dev\scripts\engine-install.py') (Join-Path $root 'release\engines')
if($LASTEXITCODE -ne 0){throw 'Engine installer failed'}
