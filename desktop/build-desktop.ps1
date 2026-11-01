param([string]$ReleaseRoot=(Join-Path $PSScriptRoot '..\..\release'))
$ErrorActionPreference='Stop'
$csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$refs=Join-Path $PSScriptRoot 'vendor'
$out=Join-Path $ReleaseRoot 'OmniDispatch.exe'
& $csc /nologo /codepage:65001 /target:winexe /platform:x64 /optimize+ /win32icon:"$PSScriptRoot\omnidispatch.ico" /out:$out /r:System.dll /r:System.Core.dll /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:System.Web.Extensions.dll /r:"$refs\Microsoft.Web.WebView2.Core.dll" /r:"$refs\Microsoft.Web.WebView2.WinForms.dll" "$PSScriptRoot\OmniDispatch.cs"
if($LASTEXITCODE -ne 0){throw 'Desktop compilation failed'}
Copy-Item "$refs\*.dll" $ReleaseRoot -Force
New-Item (Join-Path $ReleaseRoot 'desktop') -ItemType Directory -Force | Out-Null
Copy-Item "$PSScriptRoot\omnidispatch.ico" (Join-Path $ReleaseRoot 'desktop') -Force
Write-Output 'OmniDispatch.exe built'

# Official Fixed Version package, not a copy of an Evergreen installation.
$dest=Join-Path $ReleaseRoot 'desktop\webview2-runtime'
if(-not (Test-Path (Join-Path $dest 'msedgewebview2.exe'))){throw 'Install the official fixed browser with install-browser.ps1 first'}
& icacls.exe $dest /grant '*S-1-15-2-1:(OI)(CI)(RX)' '*S-1-15-2-2:(OI)(CI)(RX)' /T /Q | Out-Null
if($LASTEXITCODE -ne 0){throw 'Browser runtime read permissions could not be set'}
