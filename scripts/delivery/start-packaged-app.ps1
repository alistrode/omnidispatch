param([switch]$PrepareDevelopment,[switch]$NoLaunch,[string]$ReleaseBase='https://github.com/alistrode/omnidispatch/releases/download/v1.1.0')
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$source=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$name='OmniDispatch-Desktop-Windows-x64.zip'
$archive=Join-Path $source ('packages\'+$name);$checksum=[IO.Path]::ChangeExtension($archive,'.sha256')
if(-not(Test-Path $checksum)){throw 'Missing packages\OmniDispatch-Desktop-Windows-x64.sha256; the checkout is incomplete.'}
$expected=((Get-Content $checksum -Raw).Trim() -split '\s+')[0]
if(-not(Test-Path $archive)){
 New-Item (Split-Path $archive -Parent) -ItemType Directory -Force|Out-Null
 $url=$ReleaseBase.TrimEnd('/')+'/'+$name
 Write-Output ('Downloading the self-contained bundle: '+$url)
 [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
 $done=$false
 try{Import-Module BitsTransfer -ErrorAction Stop;Start-BitsTransfer -Source $url -Destination $archive -DisplayName 'OmniDispatch bundle';$done=$true}
 catch{Write-Output 'BITS unavailable; falling back to a streamed HTTPS download.'}
 if(-not $done){
  $client=New-Object Net.Http.HttpClient;$client.Timeout=[TimeSpan]::FromMinutes(60)
  $response=$client.GetAsync($url,[Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
  if(-not $response.IsSuccessStatusCode){throw ('Download failed: HTTP '+[int]$response.StatusCode+' '+$url)}
  $stream=$response.Content.ReadAsStreamAsync().GetAwaiter().GetResult();$target=[IO.File]::Create($archive)
  try{$stream.CopyTo($target)}finally{$target.Dispose();$stream.Dispose();$client.Dispose()}
 }
 Write-Output ('Downloaded '+('{0:N0}' -f ((Get-Item $archive).Length/1MB))+' MB')
}
if((Get-FileHash $archive -Algorithm SHA256).Hash.ToLower() -ne $expected.ToLower()){throw 'Runtime ZIP checksum mismatch. Delete packages\OmniDispatch-Desktop-Windows-x64.zip and download it again.'}
$cache=Join-Path $source '.runtime-cache\packaged-app';$app=Join-Path $cache 'OmniDispatch';$marker=Join-Path $cache 'archive.sha256'
if(-not(Test-Path $marker) -or (Get-Content $marker -Raw).Trim() -ne $expected -or -not(Test-Path (Join-Path $app 'OmniDispatch.exe'))){
 if(Test-Path $cache){throw 'An older extracted app exists; retain its state and choose a fresh checkout for this package.'}
 Add-Type -AssemblyName System.IO.Compression.FileSystem
 $zip=[IO.Compression.ZipFile]::OpenRead($archive)
 try{foreach($entry in $zip.Entries){$entryName=$entry.FullName.Replace('\','/');if(-not $entryName.StartsWith('OmniDispatch/') -or $entryName -match '(^|/)\.\.(/|$)' -or $entryName.Contains(':')){throw 'Unsafe archive entry'}}}finally{$zip.Dispose()}
 New-Item $cache -ItemType Directory -Force|Out-Null
 [IO.Compression.ZipFile]::ExtractToDirectory($archive,$cache)
 [IO.File]::WriteAllText($marker,$expected,[Text.UTF8Encoding]::new($false))
}
if($PrepareDevelopment){
 $runtime=Join-Path $source '.runtime'
 if(-not(Test-Path (Join-Path $runtime 'python.exe'))){Copy-Item (Join-Path $app 'runtime') $runtime -Recurse}
 $testTools=Join-Path $source 'development\test-tools'
 if(-not(Test-Path $testTools)){throw 'Original test dependencies missing'}
 $validation=Join-Path $source 'validation-tools';New-Item $validation -ItemType Directory -Force|Out-Null
 Copy-Item (Join-Path $testTools '*') $validation -Recurse -Force
 Get-ChildItem $runtime -Filter 'python*._pth'|ForEach-Object {$text=Get-Content $_.FullName -Raw;if(-not $text.Contains('..\validation-tools')){Add-Content $_.FullName '..\validation-tools'}}
 Write-Output 'Local development interpreter and original test dependencies restored; no private application state copied.'
 return
}
if(-not $NoLaunch){Start-Process (Join-Path $app 'OmniDispatch.exe') -WorkingDirectory $app}
Write-Output ('Verified self-contained application: '+$app)
