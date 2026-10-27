$ProgressPreference='SilentlyContinue'
$path='E:\xxm\OmniDispatch\release\state\tunnel.log'
Get-Content $path -Tail 65
Get-CimInstance Win32_Process -Filter "Name='cloudflared.exe'" | ForEach-Object { $owner=Invoke-CimMethod -InputObject $_ -MethodName GetOwner;if($owner.User -eq 'OmniDispatchRun'){@{Pid=$_.ProcessId;Name=$_.Name;Executable=$_.ExecutablePath}|ConvertTo-Json -Compress} }
exit 0
