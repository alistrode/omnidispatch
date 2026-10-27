$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$root='E:\xxm\OmniDispatch'
& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $root 'release\scripts\stop-windows.ps1') -Root $root
if($LASTEXITCODE -ne 0){throw 'Owned shutdown failed'}
Copy-Item -LiteralPath (Join-Path $root 'backups\supervisor-final.py') -Destination (Join-Path $root 'release\omnidispatch\supervisor.py') -Force
Copy-Item -LiteralPath (Join-Path $root 'backups\supervisor-final.py') -Destination (Join-Path $root 'dev\omnidispatch\supervisor.py') -Force
Start-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'
& (Join-Path $root 'release\runtime\python.exe') (Join-Path $root 'release\scripts\runtime-health.py') $root
if($LASTEXITCODE -ne 0){throw 'Smoke failed'}
$deadline=(Get-Date).AddSeconds(40)
$public=Join-Path $root 'release\state\PUBLIC-URL.txt'
while(!(Test-Path $public) -and (Get-Date) -lt $deadline){Start-Sleep -Seconds 2}
if(Test-Path $public){
  $url=(Get-Content $public -Raw).Trim();Write-Output ('PUBLIC_URL='+$url)
  try {$r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 25 -Uri ($url+'/api/health');Write-Output ('PUBLIC_HEALTH='+[int]$r.StatusCode)}catch{Write-Output ('PUBLIC_PROBE='+$_.Exception.GetType().Name)}
}
