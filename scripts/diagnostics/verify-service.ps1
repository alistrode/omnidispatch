$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$root='E:\xxm\OmniDispatch'
$user=Get-LocalUser -Name 'OmniDispatchRun'
& icacls.exe $root /grant ('*'+$user.SID.Value+':(OI)(CI)RX') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Runtime ACL failed'}
$state=Join-Path $root 'release\state'
& icacls.exe $state /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' ('*'+$user.SID.Value+':(OI)(CI)M') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Private state ACL failed'}
$interactive=(Get-CimInstance Win32_ComputerSystem).UserName
if($interactive){& icacls.exe $state /grant ($interactive+':(OI)(CI)M') | Out-Null}
Start-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'
$task=Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'
$task | Select-Object TaskName,State
$task.Principal | Select-Object UserId,RunLevel,LogonType
Get-ScheduledTaskInfo -TaskName 'OmniDispatch-Hub-Agent' | Select-Object LastRunTime,LastTaskResult
try {Invoke-RestMethod -Uri 'http://127.0.0.1:8791/api/health' -TimeoutSec 5 | ConvertTo-Json -Compress} catch {Write-Output 'Health not ready yet'}
Get-ChildItem $state -Filter '*.log' | ForEach-Object {Write-Output $_.Name;Get-Content $_.FullName -Tail 8}
