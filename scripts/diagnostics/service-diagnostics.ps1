$ProgressPreference='SilentlyContinue'
Get-ScheduledTaskInfo -TaskName 'OmniDispatch-Hub-Agent' | Select-Object LastRunTime,LastTaskResult,NextRunTime,NumberOfMissedRuns | ConvertTo-Json -Compress
(Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent').Principal | Select-Object UserId,RunLevel,LogonType | ConvertTo-Json -Compress
Get-LocalUser -Name 'OmniDispatchRun' | Select-Object Name,Enabled,Description | ConvertTo-Json -Compress
Get-Acl 'E:\xxm\OmniDispatch\release\state' | Select-Object -ExpandProperty Access | Select-Object IdentityReference,FileSystemRights,IsInherited | ConvertTo-Json -Compress
Get-ChildItem 'E:\xxm\OmniDispatch\release\state' -Filter '*.log' | ForEach-Object { Write-Output $_.Name;Get-Content $_.FullName -Tail 10 }
exit 0
