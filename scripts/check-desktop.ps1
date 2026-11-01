param([string]$ReleaseRoot='E:\xxm\OmniDispatch\release')
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$user=(Get-CimInstance Win32_ComputerSystem).UserName
if(-not $user){throw 'No signed-in desktop session'}
$service=New-Object -ComObject Schedule.Service
$service.Connect();$folder=$service.GetFolder('\');$task=$service.NewTask(0)
$task.RegistrationInfo.Description='OmniDispatch local desktop render check; no platform publication'
$task.Principal.UserId=$user;$task.Principal.LogonType=3;$task.Principal.RunLevel=0
$task.Settings.Enabled=$true;$task.Settings.AllowDemandStart=$true;$task.Settings.DisallowStartIfOnBatteries=$false;$task.Settings.StopIfGoingOnBatteries=$false;$task.Settings.ExecutionTimeLimit='PT3M'
$action=$task.Actions.Create(0);$action.Path=Join-Path $ReleaseRoot 'OmniDispatch.exe';$action.Arguments='--smoke';$action.WorkingDirectory=$ReleaseRoot
$username=$user.Split('\')[-1]
$profile=(Get-CimInstance Win32_UserProfile | Where-Object {$_.LocalPath -like ('*\'+$username)} | Select-Object -First 1).LocalPath
if(-not $profile){throw 'Current desktop profile not found'}
$diagnostics=Join-Path $profile 'AppData\Local\OmniDispatch\Diagnostics'
$report=Join-Path $diagnostics 'desktop-check.json'
if(Test-Path $report){Move-Item $report ($report+'.previous-'+(Get-Date -Format 'HHmmss'))}
$registered=$folder.RegisterTaskDefinition('OmniDispatch-Desktop-Check',$task,6,$null,$null,3,$null)
$running=$registered.Run($null)
$deadline=(Get-Date).AddSeconds(90)
while((Get-Date) -lt $deadline -and -not (Test-Path $report)){Start-Sleep -Seconds 2}
if(-not (Test-Path $report)){throw ('Desktop check did not return; last task result '+$registered.LastTaskResult)}
New-Item (Join-Path $ReleaseRoot 'logs') -ItemType Directory -Force | Out-Null
Copy-Item $report (Join-Path $ReleaseRoot 'logs\desktop-check.json') -Force
Copy-Item (Join-Path $diagnostics 'desktop-preview.png') (Join-Path $ReleaseRoot 'logs\desktop-preview.png') -Force -ErrorAction SilentlyContinue
Get-Content $report -Raw -Encoding UTF8
$folder.DeleteTask('OmniDispatch-Desktop-Check',0)
