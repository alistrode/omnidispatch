$ProgressPreference='SilentlyContinue'
wevtutil.exe sl Microsoft-Windows-TaskScheduler/Operational /e:true
Start-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'
Start-Sleep -Seconds 4
$service=New-Object -ComObject 'Schedule.Service';$service.Connect();$registered=$service.GetFolder('\').GetTask('OmniDispatch-Hub-Agent')
$registered.GetInstances(0) | ForEach-Object { Write-Output ('Instance state='+$_.State+' currentAction='+$_.CurrentAction) }
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational';StartTime=(Get-Date).AddMinutes(-5)} -MaxEvents 30 -ErrorAction SilentlyContinue | Where-Object {$_.Message -match 'OmniDispatch'} | Select-Object Id,Message | ConvertTo-Json -Compress
Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625;StartTime=(Get-Date).AddMinutes(-15)} -MaxEvents 30 -ErrorAction SilentlyContinue | ForEach-Object {
  $x=[xml]$_.ToXml();$values=@{};foreach($d in $x.Event.EventData.Data){$values[$d.Name]=$d.'#text'}
  if($values.TargetUserName -eq 'OmniDispatchRun'){@{User=$values.TargetUserName;Status=$values.Status;SubStatus=$values.SubStatus;LogonType=$values.LogonType}|ConvertTo-Json -Compress}
}
exit 0
