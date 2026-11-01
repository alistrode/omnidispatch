param([string]$ReleaseRoot='E:\xxm\OmniDispatch\release')
$ErrorActionPreference='Stop'
$user=(Get-CimInstance Win32_ComputerSystem).UserName
$username=$user.Split('\')[-1]
$profile=(Get-CimInstance Win32_UserProfile | Where-Object {$_.LocalPath -like ('*\'+$username)} | Select-Object -First 1).LocalPath
if(-not $profile){throw 'Signed-in desktop profile unavailable'}
$desktop=Join-Path $profile 'Desktop'
if(Test-Path $desktop){
 $shell=New-Object -ComObject WScript.Shell
 $link=$shell.CreateShortcut((Join-Path $desktop 'OmniDispatch.lnk'))
 $link.TargetPath=Join-Path $ReleaseRoot 'OmniDispatch.exe';$link.WorkingDirectory=$ReleaseRoot;$link.IconLocation=(Join-Path $ReleaseRoot 'desktop\omnidispatch.ico')+',0';$link.Description='OmniDispatch local publishing workbench';$link.Save()
}
$service=New-Object -ComObject Schedule.Service;$service.Connect();$folder=$service.GetFolder('\');$task=$service.NewTask(0)
$task.Principal.UserId=$user;$task.Principal.LogonType=3;$task.Principal.RunLevel=0
$task.Settings.Enabled=$true;$task.Settings.DisallowStartIfOnBatteries=$false;$task.Settings.StopIfGoingOnBatteries=$false;$task.Settings.ExecutionTimeLimit='PT0S'
$action=$task.Actions.Create(0);$action.Path=Join-Path $ReleaseRoot 'OmniDispatch.exe';$action.WorkingDirectory=$ReleaseRoot
$registered=$folder.RegisterTaskDefinition('OmniDispatch-Desktop',$task,6,$null,$null,3,$null)
$registered.Run($null) | Out-Null
Write-Output 'Desktop shortcut created and local workbench opened in the signed-in session'
