$ProgressPreference='SilentlyContinue'
Get-Service Schedule | Select-Object Name,Status,StartType | ConvertTo-Json -Compress
$task=Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'
$task.Settings | Select-Object Enabled,AllowDemandStart,DisallowStartIfOnBatteries,StopIfGoingOnBatteries,RunOnlyIfIdle,RunOnlyIfNetworkAvailable,ExecutionTimeLimit,MultipleInstances | ConvertTo-Json -Compress
$task.Actions | Select-Object Execute,Arguments,WorkingDirectory | ConvertTo-Json -Compress
schtasks.exe /Run /TN 'OmniDispatch-Hub-Agent'
Start-Sleep -Seconds 3
Get-ScheduledTaskInfo -TaskName 'OmniDispatch-Hub-Agent' | Select-Object LastRunTime,LastTaskResult | ConvertTo-Json -Compress
try {Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational';StartTime=(Get-Date).AddMinutes(-30)} -MaxEvents 15 -ErrorAction Stop | Where-Object {$_.Message -match 'OmniDispatch'} | Select-Object Id,Message | ConvertTo-Json -Compress} catch {Write-Output 'No scheduler events available'}
exit 0
