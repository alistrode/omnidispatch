$ProgressPreference='SilentlyContinue'
try {Invoke-RestMethod -Uri 'http://127.0.0.1:8791/api/health' -TimeoutSec 10 | ConvertTo-Json -Compress} catch {Write-Output ('Health failed '+$_.Exception.GetType().Name)}
Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent' | Select-Object TaskName,State | ConvertTo-Json -Compress
Get-ChildItem 'E:\xxm\OmniDispatch\release\state' -Filter '*.log' | ForEach-Object {Write-Output $_.Name;Get-Content $_.FullName -Tail 10}
exit 0
