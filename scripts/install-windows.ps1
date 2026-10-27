param([string]$Root='E:\xxm\OmniDispatch',[switch]$PublicTunnel)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$release=Join-Path $Root 'release'
$python=Join-Path $release 'runtime\python.exe'
if (!(Test-Path $python)) { throw 'Portable runtime missing' }
$state=Join-Path $release 'state'
New-Item -ItemType Directory -Force -Path $state | Out-Null
# Dedicated non-administrator local account. Task Scheduler stores its password in Windows credentials.
$name='OmniDispatchRun'
$existing=Get-LocalUser -Name $name -ErrorAction SilentlyContinue
if($existing -and $existing.Description -ne 'OmniDispatch isolated non-admin runtime'){throw 'Account belongs to another installation'}
if($existing -and (Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent' -ErrorAction SilentlyContinue)){Write-Output 'Existing application task preserved';return}
$random=New-Object byte[] 36
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($random)
$password=[Convert]::ToBase64String($random)+'aA9!'
if($existing){Set-LocalUser -Name $name -Password (ConvertTo-SecureString $password -AsPlainText -Force);$user=$existing}
else{$user=New-LocalUser -Name $name -Password (ConvertTo-SecureString $password -AsPlainText -Force) -Description 'OmniDispatch isolated non-admin runtime' -PasswordNeverExpires}
$group=Get-LocalGroup -SID 'S-1-5-32-545'
if(!(Get-LocalGroupMember -Group $group | Where-Object {$_.SID -eq $user.SID})){Add-LocalGroupMember -Group $group -Member $user}
$interactive=(Get-CimInstance Win32_ComputerSystem).UserName
& icacls.exe $Root /grant ('*'+$user.SID.Value+':(OI)(CI)RX') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Runtime read ACL failed'}
& icacls.exe $state /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' ('*'+$user.SID.Value+':(OI)(CI)M') | Out-Null
if($LASTEXITCODE -ne 0){throw 'Private state ACL failed'}
if($interactive){& icacls.exe $state /grant ($interactive+':(OI)(CI)M') | Out-Null}
& $python -m omnidispatch.cli --state $state init
if($LASTEXITCODE -ne 0){throw 'Initialization failed'}
& $python -m omnidispatch.cli --state $state register-agent
if($LASTEXITCODE -ne 0){throw 'Agent registration failed'}
$settings=@{environment=@{OMNI_SECURE_COOKIE='0'}}
if($PublicTunnel){
  $cloud=Get-Command cloudflared -ErrorAction SilentlyContinue
  if(!$cloud){throw 'cloudflared missing'}
  $settings.cloudflared=$cloud.Source
  $settings.environment.OMNI_SECURE_COOKIE='1'
}
$settings | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $state 'runtime-settings.json') -Encoding UTF8
& (Join-Path $PSScriptRoot 'grant-batch-logon.ps1')
$keydir=Join-Path $Root 'backups\update-signer-private'
New-Item -ItemType Directory -Force -Path $keydir | Out-Null
& icacls.exe $keydir /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' | Out-Null
if($LASTEXITCODE -ne 0){throw 'Publisher key ACL failed'}
if($interactive){& icacls.exe $keydir /grant ($interactive+':(OI)(CI)M') | Out-Null}
& $python (Join-Path $release 'scripts\provision-local.py') $Root
if($LASTEXITCODE -ne 0){throw 'Local engine provisioning failed'}
$task='OmniDispatch-Hub-Agent'
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+(Join-Path $release 'scripts\runtime-entry.ps1')+'"') -WorkingDirectory $release
$trigger=New-ScheduledTaskTrigger -AtStartup
$taskSettings=New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Settings $taskSettings -User ($env:COMPUTERNAME+'\'+$name) -Password $password -RunLevel Limited -Description 'OmniDispatch Hub and Agent only' | Out-Null
$password=$null
Start-ScheduledTask -TaskName $task
if($interactive){
  $profile=Get-CimInstance Win32_UserProfile | Where-Object { $_.SID -eq ([System.Security.Principal.NTAccount]$interactive).Translate([System.Security.Principal.SecurityIdentifier]).Value } | Select-Object -First 1
  if($profile){
    $desktop=Join-Path $profile.LocalPath 'Desktop'
    if(Test-Path $desktop){
      $shell=New-Object -ComObject WScript.Shell
      $shortcut=$shell.CreateShortcut((Join-Path $desktop 'OmniDispatch.lnk'))
      $shortcut.TargetPath='http://127.0.0.1:8791';$shortcut.Save()
    }
  }
}
Write-Output ('Installed task: '+$task)
Write-Output ('Private credentials: '+(Join-Path $state 'ADMIN-CREDENTIALS.private.txt'))
