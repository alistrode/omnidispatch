param([string]$SourceRoot='E:\xxm\OmniDispatch\dev')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient;Add-Type -AssemblyName UIAutomationTypes;Add-Type -AssemblyName System.Drawing;Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices;
public static class GitHubDesktopPointer {
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h,out uint id);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a,uint b,bool attach);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint dx,uint dy,uint data,UIntPtr extra);
}
'@
$folder=Join-Path $SourceRoot '_state\github-desktop';New-Item $folder -ItemType Directory -Force|Out-Null
$requestFile=Join-Path $folder 'window-request.json';$stop=Join-Path $folder 'window-worker.stop';$seen='';$shell=New-Object -ComObject WScript.Shell
@{state='ready';pid=$PID}|ConvertTo-Json -Compress|Set-Content (Join-Path $folder 'window-worker-status.json') -Encoding UTF8
while(-not(Test-Path $stop)){
 if(-not(Test-Path $requestFile)){Start-Sleep -Milliseconds 200;continue}
 try{$request=Get-Content $requestFile -Raw|ConvertFrom-Json}catch{Start-Sleep -Milliseconds 200;continue}
 if($request.id -eq $seen){Start-Sleep -Milliseconds 200;continue};$seen=$request.id
 try{
  $windows=[Windows.Automation.AutomationElement]::RootElement.FindAll([Windows.Automation.TreeScope]::Children,[Windows.Automation.Condition]::TrueCondition);$window=$null
  foreach($candidate in $windows){if($candidate.Current.Name -eq 'GitHub Desktop'){$p=Get-Process -Id $candidate.Current.ProcessId -ErrorAction SilentlyContinue;if($p.ProcessName -eq 'GitHubDesktop'){$window=$candidate;break}}}
  if(-not $window){throw 'Actual GitHub Desktop window not found'}
  $handle=[IntPtr]$window.Current.NativeWindowHandle;$ownerId=$window.Current.ProcessId
  [GitHubDesktopPointer]::ShowWindow($handle,9)|Out-Null
  [uint32]$foregroundId=0;$foregroundThread=[GitHubDesktopPointer]::GetWindowThreadProcessId([GitHubDesktopPointer]::GetForegroundWindow(),[ref]$foregroundId);$selfThread=[GitHubDesktopPointer]::GetCurrentThreadId();$attached=$false
  try{if($foregroundThread -and $foregroundThread -ne $selfThread){$attached=[GitHubDesktopPointer]::AttachThreadInput($selfThread,$foregroundThread,$true)};[GitHubDesktopPointer]::SetForegroundWindow($handle)|Out-Null}finally{if($attached){[GitHubDesktopPointer]::AttachThreadInput($selfThread,$foregroundThread,$false)|Out-Null}}
  Start-Sleep -Milliseconds 150
  [GitHubDesktopPointer]::GetWindowThreadProcessId([GitHubDesktopPointer]::GetForegroundWindow(),[ref]$foregroundId)|Out-Null
  if($foregroundId -ne $ownerId){throw 'Desktop is not foreground; no input was sent'}
  foreach($operation in $request.operations){
   if($operation.action -eq 'keys'){$shell.SendKeys([string]$operation.keys)}
   elseif($operation.action -eq 'text'){$literal='';foreach($character in ([string]$operation.text).ToCharArray()){if('{}+^%~()[]'.Contains([string]$character)){$literal+='{'+$character+'}'}else{$literal+=$character}};$shell.SendKeys($literal)}
   elseif($operation.action -eq 'click'){$rect=$window.Current.BoundingRectangle;$x=[int]$operation.x;$y=[int]$operation.y;if($x -lt $rect.X -or $y -lt $rect.Y -or $x -gt $rect.Right -or $y -gt $rect.Bottom){throw 'Pointer outside Desktop window'};[GitHubDesktopPointer]::SetCursorPos($x,$y)|Out-Null;[GitHubDesktopPointer]::mouse_event(2,0,0,0,[UIntPtr]::Zero);[GitHubDesktopPointer]::mouse_event(4,0,0,0,[UIntPtr]::Zero)}
   elseif($operation.action -ne 'capture'){throw 'Unsupported Desktop operation'}
   Start-Sleep -Milliseconds 200
  }
  Start-Sleep -Milliseconds ([Math]::Min(3000,[Math]::Max(500,[int]$request.settle_ms)))
  $bounds=[Windows.Forms.Screen]::PrimaryScreen.Bounds;$rect=$window.Current.BoundingRectangle;$left=[Math]::Max($bounds.Left,[int]$rect.Left);$top=[Math]::Max($bounds.Top,[int]$rect.Top);$right=[Math]::Min($bounds.Right,[int]$rect.Right);$bottom=[Math]::Min($bounds.Bottom,[int]$rect.Bottom)
  $bitmap=[Drawing.Bitmap]::new($right-$left,$bottom-$top);$graphics=[Drawing.Graphics]::FromImage($bitmap);$graphics.CopyFromScreen($left,$top,0,0,$bitmap.Size)
  $image=Join-Path $folder ('window-'+$request.id+'.png');$bitmap.Save($image,[Drawing.Imaging.ImageFormat]::Png);$graphics.Dispose();$bitmap.Dispose()
  $result=@{id=$request.id;state='complete';image=$image;left=$left;top=$top;width=$right-$left;height=$bottom-$top;client_pid=$ownerId}
 }catch{$result=@{id=$request.id;state='failed';message=$_.Exception.Message}}
 $result|ConvertTo-Json -Compress|Set-Content (Join-Path $folder ('window-result-'+$request.id+'.json')) -Encoding UTF8
}
