$ErrorActionPreference='Continue'
$ProgressPreference='SilentlyContinue'
$url=(Get-Content 'E:\xxm\OmniDispatch\release\state\PUBLIC-URL.txt' -Raw).Trim()
try {$r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 25 -Uri ($url+'/api/health');Write-Output ('PUBLIC_STATUS='+[int]$r.StatusCode);Write-Output $r.Content} catch {Write-Output ('PUBLIC_FAILED='+$_.Exception.GetType().Name);if($_.Exception.Response){Write-Output ([int]$_.Exception.Response.StatusCode)}}
Get-Content 'E:\xxm\OmniDispatch\release\state\tunnel.log' -Tail 5
Get-Content 'E:\xxm\OmniDispatch\release\state\resin.log' -Tail 5
exit 0
