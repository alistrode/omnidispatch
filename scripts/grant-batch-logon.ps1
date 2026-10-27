$ErrorActionPreference='Stop'
$user=Get-LocalUser -Name 'OmniDispatchRun'
if($user.Description -ne 'OmniDispatch isolated non-admin runtime'){throw 'Account ownership mismatch'}
Add-Type @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Principal;
public static class OmniBatchRight {
 [StructLayout(LayoutKind.Sequential)] struct Attributes { public uint Length; public IntPtr Root; public IntPtr Name; public uint Flags; public IntPtr Descriptor; public IntPtr Qos; }
 [StructLayout(LayoutKind.Sequential)] struct LsaString { public ushort Length; public ushort MaximumLength; public IntPtr Buffer; }
 [DllImport("advapi32.dll")] static extern uint LsaOpenPolicy(IntPtr system, ref Attributes attributes, uint access, out IntPtr handle);
 [DllImport("advapi32.dll")] static extern uint LsaAddAccountRights(IntPtr handle, byte[] sid, LsaString[] rights, uint count);
 [DllImport("advapi32.dll")] static extern uint LsaClose(IntPtr handle);
 [DllImport("advapi32.dll")] static extern uint LsaNtStatusToWinError(uint status);
 static void Check(uint status) { if(status!=0) throw new Win32Exception((int)LsaNtStatusToWinError(status)); }
 public static void Grant(string sidText) {
  var sid=new SecurityIdentifier(sidText); var bytes=new byte[sid.BinaryLength]; sid.GetBinaryForm(bytes,0);
  var attrs=new Attributes();attrs.Length=(uint)Marshal.SizeOf(attrs);IntPtr handle;
  Check(LsaOpenPolicy(IntPtr.Zero,ref attrs,0x810,out handle));
  string name="SeBatchLogonRight";IntPtr text=Marshal.StringToHGlobalUni(name);
  try { var right=new LsaString { Length=(ushort)(name.Length*2),MaximumLength=(ushort)((name.Length+1)*2),Buffer=text };Check(LsaAddAccountRights(handle,bytes,new[]{right},1)); }
  finally { Marshal.FreeHGlobal(text);LsaClose(handle); }
 }
}
'@
[OmniBatchRight]::Grant($user.SID.Value)
Write-Output 'Granted batch-logon right to the dedicated OmniDispatch account only'
