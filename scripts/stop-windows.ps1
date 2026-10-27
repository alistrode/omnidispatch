param([string]$Root='E:\xxm\OmniDispatch')
$ErrorActionPreference='Stop'
$task=Get-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent' -ErrorAction SilentlyContinue
if($task){Stop-ScheduledTask -TaskName 'OmniDispatch-Hub-Agent'}
# Recover children left by the initial supervisor before Job Object support.
# Every candidate must belong to the dedicated app account and this app's executable scope.
$release=Join-Path $Root 'release'
foreach($process in (Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe' OR Name='cloudflared.exe' OR Name='resin.exe'")){
    if(!$process.ExecutablePath){continue}
    $inScope=$process.ExecutablePath.StartsWith($release,[StringComparison]::OrdinalIgnoreCase)
    $isTunnel=($process.Name -eq 'cloudflared.exe' -and $process.CommandLine -match '--url\s+http://127\.0\.0\.1:8791')
    if(!$inScope -and !$isTunnel){continue}
    try{$owner=Invoke-CimMethod -InputObject $process -MethodName GetOwner -ErrorAction Stop}catch{continue}
    if($owner.User -ne 'OmniDispatchRun'){continue}
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Output ('Stopped owned app process '+$process.ProcessId+' '+$process.Name)
}
