param([string]$Root='E:\xxm\OmniDispatch')
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$url='https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/b7919cc9-680d-4253-bf32-732988e68aa6/Microsoft.WebView2.FixedVersionRuntime.156.0.4314.58.x64.cab'
$cache=Join-Path $Root 'dev\.runtime-cache\webview2-fixed'
New-Item $cache -ItemType Directory -Force | Out-Null
$cab=Join-Path $cache 'Microsoft.WebView2.FixedVersionRuntime.156.0.4314.58.x64.cab'
if(-not (Test-Path $cab)){Invoke-WebRequest $url -OutFile $cab -UseBasicParsing}
$stage=Join-Path $cache 'expanded'
New-Item $stage -ItemType Directory -Force | Out-Null
& "$env:WINDIR\System32\expand.exe" '-F:*' $cab $stage | Out-Null
if($LASTEXITCODE -ne 0){throw 'Fixed browser extraction failed'}
$binary=Get-ChildItem $stage -Filter msedgewebview2.exe -Recurse | Select-Object -First 1
if(-not $binary){throw 'Fixed browser executable missing'}
$dest=Join-Path $Root 'release\desktop\webview2-runtime'
if(Test-Path $dest){Move-Item $dest (Join-Path $cache ('previous-'+(Get-Date -Format 'yyyyMMddHHmmss')))}
Move-Item $binary.Directory.FullName $dest
& icacls.exe $dest /grant '*S-1-15-2-1:(OI)(CI)(RX)' '*S-1-15-2-2:(OI)(CI)(RX)' /T /Q | Out-Null
@{source=$url;version='156.0.4314.58';architecture='x64';sha256=(Get-FileHash $cab -Algorithm SHA256).Hash;kind='Microsoft official Fixed Version Runtime'} | ConvertTo-Json | Set-Content (Join-Path $Root 'release\desktop\WEBVIEW2-RUNTIME.json') -Encoding UTF8
Write-Output 'Official fixed WebView2 runtime installed locally'
