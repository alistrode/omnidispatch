$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$root='E:\xxm\OmniDispatch'
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
if(Get-ChildItem (Join-Path $root 'dev') -Force){Compress-Archive -LiteralPath (Join-Path $root 'dev') -DestinationPath (Join-Path $root ('backups\before-implementation-'+$stamp+'.zip'))}
Expand-Archive -LiteralPath (Join-Path $root 'backups\omni-deploy.zip') -DestinationPath $root -Force
$python=Join-Path $root 'release\runtime\python.exe'
& $python --version
if($LASTEXITCODE -ne 0){throw 'Portable Python failed'}
Set-Location (Join-Path $root 'dev')
$testCode=@'
import sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'validation-tools'))
import pytest
raise SystemExit(pytest.main(['-q',str(root/'tests')]))
'@
$testCode | Set-Content -LiteralPath (Join-Path $root 'dev\scripts\windows-test.py') -Encoding UTF8
& $python (Join-Path $root 'dev\scripts\windows-test.py')
if($LASTEXITCODE -ne 0){throw 'Windows safety tests failed'}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'dev\scripts\install-windows.ps1') -Root $root -PublicTunnel
if($LASTEXITCODE -ne 0){throw 'Installer failed'}
Write-Output 'WINDOWS_DEPLOYMENT_COMPLETED'
